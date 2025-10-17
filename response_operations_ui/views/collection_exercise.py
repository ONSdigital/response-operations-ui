import json
import logging
from collections import defaultdict
from datetime import datetime

import iso8601
from dateutil import tz
from dateutil.parser import parse
from flask import Blueprint, abort
from flask import current_app as app
from flask import (
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required
from structlog import wrap_logger
from werkzeug.wrappers import Response
from wtforms import ValidationError

from response_operations_ui.common.date_restriction_generator import (
    get_date_restriction_text,
)
from response_operations_ui.common.dates import localise_datetime
from response_operations_ui.common.filters import get_collection_exercise_by_period
from response_operations_ui.common.mappers import (
    convert_events_to_new_format,
    format_short_name,
    get_event_name,
    map_collection_exercise_state,
)
from response_operations_ui.common.redis_cache import RedisCache
from response_operations_ui.common.uaa import verify_permission
from response_operations_ui.common.validators import valid_date_for_event
from response_operations_ui.contexts.collection_exercise import build_ce_context
from response_operations_ui.controllers import (
    cir_controller,
    collection_exercise_controllers,
    collection_instrument_controllers,
    party_controller,
    sample_controllers,
    survey_controllers,
)
from response_operations_ui.controllers.uaa_controller import user_has_permission
from response_operations_ui.exceptions.error_codes import (
    ErrorCode,
    get_error_code_message,
)
from response_operations_ui.exceptions.exceptions import (
    ApiError,
    ExternalApiError,
    InternalError,
)
from response_operations_ui.forms import (
    CreateCollectionExerciseDetailsForm,
    EditCollectionExercisePeriodDescriptionForm,
    EditCollectionExercisePeriodIDForm,
    EventDateForm,
    LinkCollectionInstrumentForm,
    RemoveLoadedSample,
)

logger = wrap_logger(logging.getLogger(__name__))

collection_exercise_bp = Blueprint(
    "collection_exercise_bp", __name__, static_folder="static", template_folder="templates"
)

CIR_ERROR_MESSAGES = {
    ErrorCode.NOT_FOUND: "There are no CIR versions to display. The version you want to select "
    "may not yet be published or available in the Collection Instrument "
    "Registry (CIR). If you need help contact the testing team.",
    ErrorCode.API_CONNECTION_ERROR: "Unable to connect to CIR",
}


def get_sample_summary(collection_exercise_id):
    summary_id = collection_exercise_controllers.get_linked_sample_summary_id(collection_exercise_id)
    sample_summary = sample_controllers.get_sample_summary(summary_id) if summary_id else None
    return sample_summary


def get_collection_exercise_and_survey_details(short_name, period):
    survey = survey_controllers.get_survey_by_shortname(short_name)
    survey["shortName"] = format_short_name(survey["shortName"])
    collection_exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey["id"])
    collection_exercise = get_collection_exercise_by_period(collection_exercises, period)
    return collection_exercise, survey


def _build_collection_instruments_details(collection_exercise_id: str, survey_id: str) -> dict:
    collection_instruments = collection_instrument_controllers.get_collection_instruments_by_classifier(
        collection_exercise_id=collection_exercise_id, survey_id=survey_id
    )
    collection_instruments_by_survey_mode = defaultdict(list)
    for ci in collection_instruments:
        collection_instruments_by_survey_mode[ci.get("type")].append(ci)

    return collection_instruments_by_survey_mode


@collection_exercise_bp.route("/<short_name>/<period>", methods=["GET"])
@login_required
def view_collection_exercise(short_name, period):
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
    sample = get_sample_summary(collection_exercise["id"])
    formatted_sample = _format_sample_summary(sample)
    events = convert_events_to_new_format(
        collection_exercise_controllers.get_collection_exercise_events_by_id(collection_exercise["id"])
    )
    collection_instruments = _build_collection_instruments_details(collection_exercise["id"], survey["id"])
    sample_load_status = None
    if sample_controllers.sample_summary_state_check_required(collection_exercise["state"], sample):
        try:
            sample_load_status = sample_controllers.check_if_all_sample_units_present_for_sample_summary(sample["id"])
            if sample_load_status["areAllSampleUnitsLoaded"]:
                formatted_sample = _format_sample_summary(sample)
        except ApiError:
            flash("Sample summary check failed.  Refresh page to try again", category="error")

    ce_state = collection_exercise["state"]
    survey_mode = survey["surveyMode"]
    show_sds = True if collection_exercise.get("supplementaryDatasetEntity") else False
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")
    processing = ce_state in ("EXECUTION_STARTED", "EXECUTED", "VALIDATED")
    validation_failed = ce_state == "FAILEDVALIDATION"
    collection_exercise["mapped_state"] = map_collection_exercise_state(ce_state)

    show_msg = request.args.get("show_msg")
    success_panel = request.args.get("success_panel")
    info_panel = request.args.get("info_panel")
    error_json = _get_error_from_session()
    _delete_sample_data_if_required()
    has_edit_permission = user_has_permission("surveys.edit")
    context = build_ce_context(collection_exercise, survey, collection_instruments, events, has_edit_permission, locked)

    if survey_mode in ("EQ", "EQ_AND_SEFT"):
        show_set_live_button = (
            ce_state in "READY_FOR_REVIEW"
            and "ref_period_start" in events
            and "ref_period_end" in events
            and context["ci_table"]["valid_cir_count"]
        )
    else:
        show_set_live_button = ce_state in "READY_FOR_REVIEW"

    breadcrumbs = [
        {"text": "Surveys", "url": url_for("surveys_bp.view_surveys")},
        {"text": "Collection exercises", "url": url_for("surveys_bp.view_survey", short_name=short_name)},
        {},
    ]
    return render_template(
        "collection_exercise/collection-exercise.html",
        has_edit_permission=has_edit_permission,
        ce=collection_exercise,
        error=error_json,
        locked=locked,
        processing=processing,
        sample_load_status=sample_load_status,
        sample=sample,
        formatted_sample=formatted_sample,
        show_set_live_button=show_set_live_button,
        survey=survey,
        success_panel=success_panel,
        validation_failed=validation_failed,
        show_msg=show_msg,
        info_panel=info_panel,
        show_sds=show_sds,
        context=context,
        breadcrumbs=breadcrumbs,
    )


def _delete_sample_data_if_required():
    """
    If a sample data deletion failed as part of the 'remove sample' functionality, then we can try again without having
    to get the user involved.  If the deletion succeeds on this, or a later attempt, then we remove it from the session.
    If it fails then we leave it in the session, so we can try again.
    """
    sample_summary_id = session.get("retry_sample_delete_id")
    if sample_summary_id:
        try:
            sample_controllers.delete_sample(sample_summary_id)
            session.pop("retry_sample_delete_id")
        except ApiError:
            logger.error(
                "Sample deletion failed, will try again on next exercise load", sample_summary_id=sample_summary_id
            )


def get_existing_sorted_nudge_events(events):
    sorted_nudge_list = []
    nudge_tags = ["nudge_email_0", "nudge_email_1", "nudge_email_2", "nudge_email_3", "nudge_email_4"]
    nudge_events = {}
    for nudge in nudge_tags:
        if nudge in events:
            nudge_events[nudge] = events[nudge].copy()
    for key, val in nudge_events.items():
        for k, v in val.items():
            if k == "date":
                nudge_events[key][k] = str(parse(v, fuzzy=True).date())
    nudge_events = sorted(
        nudge_events.items(),
        key=lambda x: (
            x[1]["date"],
            x[1]["time"],
        ),
    )
    for k, v in nudge_events:
        sorted_nudge_list.append(k)
    return sorted_nudge_list


def _get_error_from_session():
    """
    This is an ugly fix for errors being written permanently to the session. This guarantees that an error
    will be displayed once and then removed. If errors are ever tidied up (using flash for instance) then this code
    can go.
    """
    if session.get("error"):
        error_json = json.loads(session.get("error"))
        session.pop("error")
        return error_json
    return None


@collection_exercise_bp.route("/<short_name>/<period>", methods=["POST"])
@login_required
def post_collection_exercise(short_name, period):

    if "ready-for-live" in request.form:
        return _set_ready_for_live(short_name, period)
    return view_collection_exercise(short_name, period)


@collection_exercise_bp.route("/<short_name>/<period>/view-sample-ci", methods=["POST"])
@login_required
def post_sample_ci(short_name, period):
    if "load-seft-ci" in request.form:
        return _upload_seft_collection_instrument(short_name, period)
    elif "select-eq-ci" in request.form:
        return _select_eq_collection_instrument(short_name, period)
    elif "add-eq-ci" in request.form:
        return _add_collection_instrument(short_name, period)
    return get_view_sample_ci(short_name, period)


@collection_exercise_bp.route("response_chasing/<document_type>/<ce_id>/<survey_id>", methods=["GET"])
@login_required
def response_chasing(document_type, ce_id, survey_id):
    logger.info("Response chasing", ce_id=ce_id, survey_id=survey_id)
    response = collection_exercise_controllers.download_report(document_type, ce_id, survey_id)
    return response.content, response.status_code, response.headers.items()


def _set_ready_for_live(short_name, period):
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)

    try:
        collection_exercise_controllers.execute_collection_exercise(collection_exercise["id"])
        success_panel = "Collection exercise executed"

    except ApiError:
        session["error"] = json.dumps(
            {
                "section": "head",
                "header": "Error: Failed to execute Collection Exercise",
                "message": "Error processing collection exercise",
            }
        )
        success_panel = None

    return redirect(
        url_for(
            "collection_exercise_bp.view_collection_exercise",
            short_name=short_name,
            period=period,
            success_panel=success_panel,
        )
    )


def _select_eq_collection_instrument(short_name, period):
    cis_selected = request.form.getlist("checkbox-answer")
    if app.config["CIR_ENABLED"]:
        if not cis_selected:
            return _redirect_with_error("Choose one or more EQ formtypes to continue.", period, short_name)

    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)

    success_panel = None
    if "EQ" in survey["surveyMode"]:
        ce_id = collection_exercise["id"]
        response = collection_instrument_controllers.update_collection_exercise_eq_instruments(cis_selected, ce_id)
        if response[0] != 200:
            if cis_selected:
                return _redirect_with_error(
                    "Error: Failed to add and remove collection instrument(s)", period, short_name
                )
            return _redirect_with_error(response[1], period, short_name)

        if app.config["CIR_ENABLED"]:
            return redirect(
                url_for(
                    "collection_exercise_bp.view_sample_ci_summary",
                    short_name=short_name,
                    period=period,
                    success_panel=success_panel,
                )
            )
    return redirect(
        url_for(
            "collection_exercise_bp.view_collection_exercise",
            short_name=short_name,
            period=period,
            success_panel=success_panel,
        )
    )


def _redirect_with_error(error_message: str, period: str, short_name: str) -> Response:
    session["error"] = json.dumps(
        {
            "section": "ciSelect",
            "header": error_message,
            "message": "Please try again",
        }
    )
    return redirect(
        url_for(
            "collection_exercise_bp.get_view_sample_ci",
            short_name=short_name,
            period=period,
            survey_mode="EQ",
        )
    )


def _upload_seft_collection_instrument(short_name, period):
    success_panel = None
    error = _validate_collection_instrument()

    if not error:
        file = request.files["ciFile"]
        is_ru_specific_instrument = False
        if file.filename.split(".")[0].isdigit():
            is_ru_specific_instrument = True

        logger.info("Collection instrument about to be uploaded", filename=file.filename)
        collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)

        if not collection_exercise:
            return make_response(jsonify({"message": "Collection exercise not found"}), 404)

        if is_ru_specific_instrument:
            ru_ref = file.filename.split(".")[0]
            upload_success, error_text = collection_instrument_controllers.upload_ru_specific_collection_instrument(
                collection_exercise["id"], file, ru_ref
            )
        else:
            form_type = _get_form_type(file.filename)
            upload_success, error_text = collection_instrument_controllers.upload_collection_instrument(
                collection_exercise["id"], file, form_type
            )

        if upload_success:
            success_panel = "Collection instrument loaded"
        else:
            message = error_text if error_text else "Please try again"
            session["error"] = json.dumps(
                {"section": "ciFile", "header": "Error: Failed to upload collection instrument", "message": message}
            )
    else:
        session["error"] = json.dumps(error)

    return redirect(
        url_for(
            "collection_exercise_bp.get_seft_collection_instrument",
            period=period,
            short_name=short_name,
            success_panel=success_panel,
        )
    )


def _validate_collection_instrument():
    if "ciFile" in request.files:
        file = request.files["ciFile"]

        error = validate_file_extension_is_correct(file)

        if error is None:
            ci_name = file.filename.split(".")[0]
            if ci_name.isdigit():
                error = validate_ru_specific_collection_instrument(file, ci_name)
            else:
                # file name format is surveyId_period_formType
                form_type = _get_form_type(file.filename) if file.filename.count("_") == 2 else ""
                if not form_type.isdigit() or len(form_type) != 4:
                    logger.info("Invalid file format uploaded", filename=file.filename)
                    error = {
                        "section": "ciFile",
                        "header": "Error: Invalid file name format for collection instrument",
                        "message": "Please provide file with correct form type in file name",
                    }
    else:
        logger.info("No file uploaded")
        error = {
            "section": "ciFile",
            "header": "Error: No collection instrument supplied",
            "message": "Please provide a collection instrument",
        }
    return error


def validate_ru_specific_collection_instrument(file, ci_name):
    logger.info("Ru specific collection instrument detected", filename=file.filename)
    if len(ci_name) == 11:
        return None

    logger.info("Invalid ru specific file format uploaded", filename=file.filename)
    error = {
        "section": "ciFile",
        "header": "Error: Invalid file name format for ru specific collection instrument",
        "message": "Please provide a file with a valid 11 digit ru ref in the file name",
    }
    return error


def validate_file_extension_is_correct(file):
    if str.endswith(file.filename, ".xlsx"):
        return None
    if str.endswith(file.filename, ".xls"):
        return None

    logger.info("Invalid file format uploaded", filename=file.filename)
    error = {
        "section": "ciFile",
        "header": "Error: Wrong file type for collection instrument",
        "message": "Please use XLSX file only",
    }
    return error


def _validate_sample() -> bool:
    """
    Does some light touch validation around the sample file.  It ensures a file got uploaded and that it has the
    right extension.
    :return: True if sample is valid, False if it's invalid
    """
    if "sampleFile" not in request.files:
        logger.info("No file uploaded")
        flash("No file uploaded", "error")
        return False

    file = request.files["sampleFile"]
    if not str.endswith(file.filename, ".csv"):
        logger.info("Invalid file format uploaded", filename=file.filename)
        flash("Invalid file format", "error")
        return False
    return True


def _format_sample_summary(sample):
    if sample and sample.get("ingestDateTime"):
        submission_value = sample["ingestDateTime"]
        if isinstance(submission_value, str):
            try:
                submission_datetime = localise_datetime(iso8601.parse_date(submission_value))
                submission_time = submission_datetime.strftime("%d %B %Y %I:%M%p")
                sample["ingestDateTime"] = submission_time
            except ValueError:
                sample["ingestDateTime"] = submission_value
        else:
            sample["ingestDateTime"] = submission_value
    return sample


def _format_ci_file_name(collection_instruments, survey_details):
    for ci in collection_instruments:
        if "xlsx" not in str(ci.get("file_name", "")):
            ci["file_name"] = f"{survey_details['surveyRef']} {ci['file_name']} eQ"


def _get_form_type(file_name):
    file_name = file_name.split(".")[0]
    return file_name.split("_")[2]  # file name format is surveyId_period_formType


@collection_exercise_bp.route("/<short_name>/<period>/edit-collection-exercise-period-id", methods=["GET"])
@login_required
def edit_collection_exercise_period_id(short_name, period):
    verify_permission("surveys.edit")
    logger.info("Retrieving collection exercise data for form", short_name=short_name, period=period)
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)

    form = EditCollectionExercisePeriodIDForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    ce_state = collection_exercise["state"]
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")

    return render_template(
        "edit-collection-exercise-period-id.html",
        survey_ref=survey["surveyRef"],
        form=form,
        short_name=short_name,
        period=period,
        locked=locked,
        ce_state=collection_exercise["state"],
        collection_exercise_id=collection_exercise["id"],
        survey_id=survey_details["id"],
    )


@collection_exercise_bp.route("/<short_name>/<period>/edit-collection-exercise-period-description", methods=["GET"])
@login_required
def edit_collection_exercise_period_description(short_name, period):
    verify_permission("surveys.edit")
    logger.info("Retrieving collection exercise data for form", short_name=short_name, period=period)
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
    form = EditCollectionExercisePeriodIDForm(form=request.form)
    locked = collection_exercise["state"] in (
        "LIVE",
        "READY_FOR_LIVE",
        "EXECUTION_STARTED",
        "VALIDATED",
        "EXECUTED",
        "ENDED",
    )

    return render_template(
        "edit-collection-exercise-period-description.html",
        survey_ref=survey["surveyRef"],
        form=form,
        short_name=short_name,
        period=period,
        user_description=collection_exercise["userDescription"],
        locked=locked,
        ce_state=collection_exercise["state"],
        collection_exercise_id=collection_exercise["id"],
        survey_id=survey["id"],
    )


@collection_exercise_bp.route("/<short_name>/<period>/edit-collection-exercise-period-id", methods=["POST"])
@login_required
def submit_collection_exercise_period_id(short_name, period):
    verify_permission("surveys.edit")
    form = EditCollectionExercisePeriodIDForm(form=request.form)
    if not form.validate():
        logger.info(
            "Failed validation, retrieving collection exercise data for form", short_name=short_name, period=period
        )
        collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
        ce_state = collection_exercise["state"]
        locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")

        return render_template(
            "edit-collection-exercise-period-id.html",
            survey_ref=survey["surveyRef"],
            form=form,
            short_name=short_name,
            period=period,
            locked=locked,
            ce_state=collection_exercise["state"],
            errors=form.errors,
            collection_exercise_id=collection_exercise["id"],
            survey_id=survey["id"],
        )

    else:
        logger.info("Updating collection exercise period ID", short_name=short_name, period=period)
        form = request.form

        if form.get("period") != period:
            collection_exercise_controllers.update_collection_exercise_period(
                form.get("collection_exercise_id"), form.get("period")
            )

        return redirect(
            url_for("collection_exercise_bp.view_collection_exercise", short_name=short_name, period=form.get("period"))
        )


@collection_exercise_bp.route("/<short_name>/<period>/edit-collection-exercise-period-description", methods=["POST"])
@login_required
def submit_collection_exercise_period_description(short_name, period):
    verify_permission("surveys.edit")
    form = EditCollectionExercisePeriodDescriptionForm(form=request.form)

    if not form.validate():
        logger.info(
            "Failed validation, retrieving collection exercise data for form", short_name=short_name, period=period
        )
        collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
        ce_state = collection_exercise["state"]
        locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")

        return render_template(
            "edit-collection-exercise-period-description.html",
            survey_ref=survey["surveyRef"],
            form=form,
            short_name=short_name,
            period=period,
            locked=locked,
            ce_state=collection_exercise["state"],
            errors=form.errors,
            user_description=collection_exercise["userDescription"],
            collection_exercise_id=collection_exercise["id"],
            survey_id=survey["survey_id"],
        )

    else:
        logger.info("Updating collection exercise period description", short_name=short_name, period=period)
        form = request.form
        collection_exercise_controllers.update_collection_exercise_user_description(
            form.get("collection_exercise_id"), form.get("user_description")
        )

        return redirect(
            url_for("collection_exercise_bp.view_collection_exercise", short_name=short_name, period=period)
        )


@collection_exercise_bp.route("/<survey_ref>/<short_name>/create-collection-exercise", methods=["GET"])
@login_required
def get_create_collection_exercise_form(survey_ref, short_name):
    previous_period = request.args.get("previous_period")
    verify_permission("surveys.edit")
    logger.info("Retrieving survey data for form", short_name=short_name, survey_ref=survey_ref)
    form = CreateCollectionExerciseDetailsForm(form=request.form)

    return render_template(
        "create-collection-exercise.html",
        form=form,
        short_name=short_name,
        survey_ref=survey_ref,
        previous_period=previous_period,
    )


@collection_exercise_bp.route("/<survey_ref>/<short_name>/create-collection-exercise", methods=["POST"])
@login_required
def create_collection_exercise(survey_ref, short_name):
    verify_permission("surveys.edit")
    logger.info("Attempting to create collection exercise", survey_ref=survey_ref, survey=short_name)
    ce_form = CreateCollectionExerciseDetailsForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    survey_id = survey_details["id"]
    survey_name = survey_details["shortName"]

    if not ce_form.validate():
        logger.info("Failed validation, retrieving survey data for form", survey=short_name, survey_ref=survey_ref)
        error = None

        if ce_form.errors["period"][1] == "Please enter numbers only for the period":
            error = ce_form.errors["period"][1]

        return render_template(
            "create-collection-exercise.html",
            form=ce_form,
            short_name=short_name,
            errors=error,
            survey_ref=survey_ref,
            survey_id=survey_id,
            survey_name=survey_name,
        )

    form = request.form
    created_period = form.get("period")
    ce_details = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)

    for ce in ce_details:
        if ce["exerciseRef"] == str(created_period):
            error = "Use a period that is not in use by any collection exercise for this survey."
            return render_template(
                "create-collection-exercise.html",
                form=ce_form,
                short_name=short_name,
                errors=error,
                survey_ref=survey_ref,
                survey_id=survey_id,
                survey_name=survey_name,
            )

    logger.info(
        "Creating collection exercise for survey",
        survey=short_name,
        survey_ref=survey_ref,
    )

    collection_exercise_controllers.create_collection_exercise(
        survey_id, survey_name, form.get("user_description"), form.get("period")
    )

    logger.info("Successfully created collection exercise", survey=short_name, survey_ref=survey_ref)
    return redirect(
        url_for("collection_exercise_bp.view_collection_exercise", short_name=short_name, period=form.get("period"))
    )


@collection_exercise_bp.route("/<short_name>/<period>/<ce_id>/confirm-create-event/<tag>", methods=["GET"])
@login_required
def get_create_collection_event_form(short_name, period, ce_id, tag):
    verify_permission("surveys.edit")
    logger.info(
        "Retrieving form for create collection exercise event",
        short_name=short_name,
        period=period,
        ce_id=ce_id,
        tag=tag,
    )
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)

    if not collection_exercise:
        logger.error("Failed to find collection exercise by period", short_name=short_name, period=period)
        abort(404)

    events = collection_exercise_controllers.get_collection_exercise_events_by_id(collection_exercise["id"])
    form = EventDateForm()
    event_name = get_event_name(tag)
    formatted_events = convert_events_to_new_format(events)
    date_restriction_text = get_date_restriction_text(tag, formatted_events)

    logger.info(
        "Successfully retrieved form for create collection exercise event",
        short_name=short_name,
        period=period,
        ce_id=ce_id,
        tag=tag,
    )

    return render_template(
        "create-ce-event.html",
        ce_id=ce_id,
        short_name=short_name,
        period=period,
        survey=survey,
        event_name=event_name,
        date_restriction_text=date_restriction_text,
        tag=tag,
        form=form,
    )


@collection_exercise_bp.route("/<short_name>/<period>/<ce_id>/create-event/<tag>", methods=["POST", "GET"])
@login_required
def create_collection_exercise_event(short_name, period, ce_id, tag):
    verify_permission("surveys.edit")
    if request.method == "GET":
        redirect(
            url_for(
                "collection_exercise_bp.get_create_collection_event_form",
                period=period,
                short_name=short_name,
                ce_id=ce_id,
                tag=tag,
            )
        )
    logger.info(
        "Creating collection exercise event",
        short_name=short_name,
        period=period,
        collection_exercise_id=ce_id,
        tag=tag,
    )

    form = EventDateForm(request.form)

    if not form.validate():
        flash("Please enter a valid value", "error")
        return get_create_collection_event_form(short_name=short_name, period=period, ce_id=ce_id, tag=tag)

    try:
        valid_date_for_event(tag, form)
    except ValidationError as exception:
        flash(exception, "error")
        return get_create_collection_event_form(short_name=short_name, period=period, ce_id=ce_id, tag=tag)

    submitted_dt = datetime(
        year=int(form.year.data),
        month=int(form.month.data),
        day=int(form.day.data),
        hour=int(form.hour.data),
        minute=int(form.minute.data),
        tzinfo=tz.gettz("Europe/London"),
    )

    """Attempts to create the event, returns None if success or returns an error message upon failure."""
    error_message = collection_exercise_controllers.create_collection_exercise_event(
        collection_exercise_id=ce_id, tag=tag, timestamp=submitted_dt
    )

    if error_message:
        flash(error_message, "error")
        return get_create_collection_event_form(short_name=short_name, period=period, ce_id=ce_id, tag=tag)

    return redirect(
        url_for(
            "collection_exercise_bp.view_collection_exercise",
            period=period,
            short_name=short_name,
            success_panel="Event date added.",
        )
    )


@collection_exercise_bp.route("/<short_name>/<period>/view-sample-ci", methods=["GET"])
@login_required
def get_view_sample_ci(short_name, period):
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
    sample = get_sample_summary(collection_exercise["id"])

    collection_instruments = _build_collection_instruments_details(collection_exercise["id"], survey["id"])

    ce_state = collection_exercise["state"]
    ce_id = collection_exercise["id"]
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")
    all_cis_for_survey = []
    if survey["surveyMode"] in ("EQ_AND_SEFT", "EQ"):
        all_eq_survey_ci = collection_instrument_controllers.get_collection_instruments_by_classifier(
            ci_type="EQ", survey_id=survey["id"]
        )
        linked_eq_ci = collection_instruments.get("EQ", {})
        all_cis_for_survey = collection_instrument_controllers.get_linked_cis_and_cir_version(
            ce_id, linked_eq_ci, all_eq_survey_ci
        )
        _format_ci_file_name(linked_eq_ci, survey)
    error_json = _get_error_from_session()
    _delete_sample_data_if_required()
    show_msg = request.args.get("show_msg")

    success_panel = request.args.get("success_panel")
    info_panel = request.args.get("info_panel")

    # Once the CIR work is complete, this flag can be removed
    cir_enabled = app.config["CIR_ENABLED"]

    back_url = url_for("collection_exercise_bp.view_collection_exercise", short_name=short_name, period=period)
    breadcrumbs = [{"text": f"Back to {period} Collection exercise", "url": back_url}, {}]

    return render_template(
        "collection_exercise/ce-eq-instrument-section.html",
        ce=collection_exercise,
        collection_instruments=collection_instruments,
        error=error_json,
        locked=locked,
        sample=sample,
        survey=survey,
        success_panel=success_panel,
        show_msg=show_msg,
        info_panel=info_panel,
        all_cis_for_survey=all_cis_for_survey,
        breadcrumbs=breadcrumbs,
        cir_enabled=cir_enabled,
    )


@collection_exercise_bp.route("/<short_name>/<period>/upload-sample-file", methods=["GET"])
@login_required
def get_upload_sample_file(short_name, period):
    verify_permission("surveys.edit")
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
    sample = get_sample_summary(collection_exercise["id"])

    ce_state = collection_exercise["state"]
    collection_exercise["mapped_state"] = map_collection_exercise_state(ce_state)  # NOQA
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")
    success_panel = request.args.get("success_panel")
    show_msg = request.args.get("show_msg")
    error_json = _get_error_from_session()
    return render_template(
        "collection_exercise/ce-upload-sample-file.html",
        ce=collection_exercise,
        error=error_json,
        locked=locked,
        sample=sample,
        survey=survey,
        success_panel=success_panel,
        show_msg=show_msg,
    )


@collection_exercise_bp.route("/<short_name>/<period>/upload-sample-file", methods=["POST"])
@login_required
def post_upload_sample_file(short_name, period):
    verify_permission("surveys.edit")
    if _validate_sample():
        collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)

        if not collection_exercise:
            return make_response(jsonify({"message": "Collection exercise not found"}), 404)
        try:
            sample_summary = sample_controllers.upload_sample(short_name, period, request.files["sampleFile"])
            logger.info(
                "Linking sample summary with collection exercise",
                collection_exercise_id=collection_exercise["id"],
                sample_id=sample_summary["id"],
            )
            collection_exercise_controllers.link_sample_summary_to_collection_exercise(
                collection_exercise_id=collection_exercise["id"], sample_summary_id=sample_summary["id"]
            )
        except ApiError as e:
            if e.status_code == 400:
                flash(e.message, "error")
            else:
                # For a non-400, just let the error bubble up
                raise e

    return redirect(
        url_for(
            "collection_exercise_bp.view_collection_exercise",
            short_name=short_name,
            period=period,
            show_msg="true",
        )
    )


@collection_exercise_bp.route("/<short_name>/<period>/confirm-remove-sample", methods=["GET"])
@login_required
def get_confirm_remove_sample(short_name, period):
    logger.info("Retrieving confirm remove sample page", short_name=short_name, period=period)
    form = RemoveLoadedSample(form=request.form)
    return render_template("confirm-remove-sample.html", form=form, short_name=short_name, period=period)


@collection_exercise_bp.route("/<short_name>/<period>/confirm-remove-sample", methods=["POST"])
@login_required
def remove_loaded_sample(short_name, period):
    verify_permission("surveys.edit")
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
    sample = get_sample_summary(collection_exercise["id"])

    sample_summary_id = sample["id"]
    collection_exercise_id = collection_exercise["id"]

    logger.info(
        "Removing sample for collection exercise",
        short_name=short_name,
        period=period,
        collection_exercise_id=collection_exercise_id,
        sample_summary_id=sample_summary_id,
    )

    # The order for the deletion has to be party, collection exercise then sample.  If either of the first two fail,
    # then the link is still there, and the 'remove sample' button will be there for the user to click again.  If the
    # sample data was deleted before collection exercise, then the page would error as it tries to find sample data that
    # no longer exists.
    try:
        party_controller.delete_attributes_by_sample_summary_id(sample_summary_id)
        collection_exercise_controllers.unlink_sample_summary(collection_exercise_id, sample_summary_id)
    except ApiError:
        logger.info(
            "Failed to remove sample for collection exercise",
            short_name=short_name,
            period=period,
            collection_exercise_id=collection_exercise_id,
            sample_summary_id=sample_summary_id,
        )
        session["error"] = json.dumps(
            {"section": "head", "header": "Error: Failed to remove sample", "message": "Please try again"}
        )
        return redirect(url_for("collection_exercise_bp.get_view_sample_ci", short_name=short_name, period=period))

    # If the sample summary call fails, the only consequence will be orphaned data.  We'll write the id to the session,
    # and try again after the redirect, only removing it from the session once it's been deleted.  There's a chance
    # this might not be enough, as the next attempt could fail and the user could then log out, deleting the session.
    # But this is so unlikely to happen that it's an okay risk to take.
    try:
        sample_controllers.delete_sample(sample_summary_id)
    except ApiError:
        session["retry_sample_delete_id"] = sample_summary_id

    return redirect(
        url_for(
            "collection_exercise_bp.get_upload_sample_file",
            short_name=short_name,
            period=period,
            success_panel="Sample removed",
        )
    )


def _split_list(list_to_split, num_of_lists):
    k, m = divmod(len(list_to_split), num_of_lists)
    return (list_to_split[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(num_of_lists))


def _create_seft_ci_table(collection_instruments):
    collection_instruments = [ci for ci in collection_instruments]
    ci_columns = list(_split_list(collection_instruments, 3))
    table_columns = {"left": ci_columns[0], "middle": ci_columns[1], "right": ci_columns[2]}
    return table_columns


@collection_exercise_bp.route("/<short_name>/<period>/load-collection-instruments", methods=["GET"])
@login_required
def get_seft_collection_instrument(short_name, period):
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
    collection_instruments = _build_collection_instruments_details(collection_exercise["id"], survey["id"]).get(
        "SEFT", {}
    )
    show_msg = request.args.get("show_msg")
    success_panel = request.args.get("success_panel")
    info_panel = request.args.get("info_panel")
    locked = collection_exercise["state"] in (
        "LIVE",
        "READY_FOR_LIVE",
        "EXECUTION_STARTED",
        "VALIDATED",
        "EXECUTED",
        "ENDED",
    )

    table_columns = _create_seft_ci_table(collection_instruments)

    back_url = url_for("collection_exercise_bp.view_collection_exercise", short_name=short_name, period=period)
    breadcrumbs = [{"text": "Back", "url": back_url}, {"text": "View sample"}]
    error_json = _get_error_from_session()
    return render_template(
        "ce-seft-instrument.html",
        breadcrumbs=breadcrumbs,
        survey=survey,
        ce=collection_exercise,
        collection_instruments=collection_instruments,
        success_panel=success_panel,
        error=error_json,
        info_panel=info_panel,
        show_msg=show_msg,
        period=period,
        locked=locked,
        table_columns=table_columns,
    )


@collection_exercise_bp.route("/<short_name>/<period>/load-collection-instruments", methods=["POST"])
@login_required
def post_seft_collection_instrument(short_name, period):
    verify_permission("surveys.edit")
    if "delete-ci" in request.form:
        return _delete_seft_collection_instrument(short_name, period)
    return _upload_seft_collection_instrument(short_name, period)


def _delete_seft_collection_instrument(short_name, period):
    success_panel = "Collection instrument removed"
    ci_id = request.form.get("ci_id")
    delete_seft_collection = collection_instrument_controllers.delete_seft_collection_instrument(ci_id)

    if not delete_seft_collection:
        success_panel = None
        session["error"] = json.dumps(
            {
                "section": "collection-instruments-table",
                "header": "Error: Failed to remove collection instrument",
                "message": "Please try again",
            }
        )

    return redirect(
        url_for(
            "collection_exercise_bp.get_seft_collection_instrument",
            short_name=short_name,
            period=period,
            success_panel=success_panel,
        )
    )


def _add_collection_instrument(short_name, period):
    form = LinkCollectionInstrumentForm(form=request.form)
    try:
        # The eq_id of a collection instrument will ALWAYS be its shortname.
        short_name_lower = str(short_name).lower()
        survey_uuid = survey_controllers.get_survey_by_shortname(short_name_lower)["id"]
        if not form.validate():
            unique_error = list(dict.fromkeys(form.formtype.errors))

            session["error"] = json.dumps(
                {
                    "section": "add-ci-error",
                    "header": unique_error[0],
                    "message": unique_error[0],
                }
            )
            return get_view_sample_ci(short_name, period)

        collection_instrument_controllers.link_collection_instrument_to_survey(
            survey_uuid, short_name_lower, form.formtype.data
        )
    except ApiError as error_response:
        json_error = json.loads(error_response.message)
        session["error"] = json.dumps(
            {
                "section": "add-ci-error",
                "header": json_error["errors"][0],
                "message": json_error["errors"][0],
            }
        )

        return get_view_sample_ci(short_name, period)

    form.formtype.data = ""  # Reset the value on successful submission
    return get_view_sample_ci(short_name, period)


@collection_exercise_bp.route("<short_name>/<period>/view-sample-ci/summary", methods=["GET"])
@login_required
def view_sample_ci_summary(short_name: str, period: str) -> str:
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
    long_name = survey.get("longName")
    collection_instruments = collection_instrument_controllers.get_cis_and_cir_version(collection_exercise["id"])

    back_url = url_for("collection_exercise_bp.get_view_sample_ci", short_name=short_name, period=period)
    breadcrumbs = [{"text": "Back to EQ formtypes", "url": back_url}, {}]

    return render_template(
        "collection_exercise/view-sample-ci-summary.html",
        collection_instruments=collection_instruments,
        short_name=short_name,
        exercise=collection_exercise,
        long_name=long_name,
        period=period,
        breadcrumbs=breadcrumbs,
    )


@collection_exercise_bp.route("/<short_name>/<period>/view-sample-ci/summary/<form_type>", methods=["GET"])
@login_required
def view_ci_versions(short_name: str, period: str, form_type: str) -> str:
    verify_permission("surveys.edit")
    redis_cache = RedisCache()
    survey = redis_cache.get_survey_by_shortname(short_name)
    long_name = survey.get("longName")
    cir_metadata, error_message = _build_cir_metadata(form_type, period, redis_cache, survey)
    back_url = url_for("collection_exercise_bp.view_sample_ci_summary", short_name=short_name, period=period)
    breadcrumbs = [{"text": "Back to CIR versions", "url": back_url}, {}]

    return render_template(
        "collection_exercise/ci-versions.html",
        form_type=form_type,
        cir_metadata=cir_metadata,
        period=period,
        long_name=long_name,
        error_message=error_message,
        breadcrumbs=breadcrumbs,
        has_edit_permission=user_has_permission("surveys.edit"),
    )


@collection_exercise_bp.route("/<short_name>/<period>/view-sample-ci/summary/<form_type>", methods=["POST"])
@login_required
def save_ci_versions(short_name: str, period: str, form_type: str):
    verify_permission("surveys.edit")
    selected_registry_instrument_guid = request.form.get("ci-versions")
    collection_exercise, survey = get_collection_exercise_and_survey_details(short_name, period)
    collection_instruments = _build_collection_instruments_details(collection_exercise["id"], survey["id"])

    if "nothing-selected" == selected_registry_instrument_guid:

        collection_instrument_controllers.delete_registry_instruments(collection_exercise["id"], form_type)
        return redirect(url_for("collection_exercise_bp.view_sample_ci_summary", short_name=short_name, period=period))
    else:

        redis_cache = RedisCache()
        survey_ref = survey.get("surveyRef")
        if survey_ref:
            try:
                list_of_cir_metadata_objects = redis_cache.get_cir_metadata(survey_ref, form_type)
            except ExternalApiError as e:
                logger.info("Error Retrieving CIR metadata", survey_ref=survey_ref, form_type=form_type, error=e)
                raise InternalError(e)
            selected_cir_metadata_object = _get_selected_cir_metadata_object(
                selected_registry_instrument_guid, list_of_cir_metadata_objects
            )

            instrument_id = _get_instrument_id_by_formtype(collection_instruments["EQ"], form_type)

            collection_instrument_controllers.save_registry_instrument(
                collection_exercise["id"],
                form_type,
                selected_cir_metadata_object["ci_version"],
                selected_cir_metadata_object["guid"],
                instrument_id,
                selected_cir_metadata_object["published_at"],
                survey["id"],
            )

        return redirect(url_for("collection_exercise_bp.view_sample_ci_summary", short_name=short_name, period=period))


def _build_cir_metadata(form_type, period, redis_cache, survey):
    error_message = None
    cir_metadata = None
    collection_exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey.get("id"))
    collection_exercise = get_collection_exercise_by_period(collection_exercises, period)
    registry_instrument = collection_instrument_controllers.get_registry_instrument(
        collection_exercise.get("id"), form_type
    )
    try:
        cir_metadata = redis_cache.get_cir_metadata(survey.get("surveyRef"), form_type)
        # Conversion to make displaying the datetime easier in the template
        for ci in cir_metadata:
            ci["published_at"] = datetime.fromisoformat(ci["published_at"]).strftime("%d/%m/%Y at %H:%M:%S")
            ci["selected"] = ci["guid"] == (registry_instrument["guid"] if registry_instrument else False)
    except ExternalApiError as e:
        error_message = CIR_ERROR_MESSAGES.get(e.error_code, get_error_code_message(e.error_code))
    return cir_metadata, error_message


def _get_selected_cir_metadata_object(guid, list_of_cir_metadata_objects):
    """
    Iterates over a list of registry instrument version objects and returns the one matching the given guid.
    :param ci_version: the guid of the registry instrument version selected by the user in the UI
    :param list_of_cir_metadata_objects: the list of registry instrument version objects for this CE form type
    :return: the registry instrument version object selected by the user
    """
    return next(
        (
            cir_metadata_object
            for cir_metadata_object in list_of_cir_metadata_objects
            if cir_metadata_object["guid"] == guid
        ),
        None,
    )


def _get_instrument_id_by_formtype(eq_list, form_type):
    """
    Iterates over a list of CE collection instruments and returns the instrument_id matching the given form type.
    :param eq_list: The list of collection instruments selected for the collection exercise
    :param form_type: The form type to search for in the list of collection instruments
    :return: the instrument_id of the form type if found in the list, otherwise None
    """
    return next((ci["id"] for ci in eq_list if ci["classifiers"].get("form_type") == form_type), None)


@collection_exercise_bp.route("/cir", methods=["GET"])
@login_required
def get_cir_service_status():
    logger.info("Get CIR service status")
    error_message = None
    response_content = None
    try:
        response_content = cir_controller.get_cir_service_status()
    except ExternalApiError as e:
        error_message = (
            f"Error: {e.error_code.value} "
            f"{get_error_code_message(e.error_code)} "
            f"Service: {e.target_service} "
            f"Cause Exception: {e.__cause__ if e.__cause__ else 'None'}"
        )

    return render_template(
        "collection_exercise/cir.html",
        error_message=error_message,
        response_content=response_content,
    )
