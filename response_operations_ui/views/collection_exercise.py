import json
import logging
from collections import defaultdict
from datetime import datetime

import iso8601
from dateutil import tz
from dateutil.parser import parse
from flask import (
    Blueprint,
    abort,
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
from wtforms import ValidationError

from response_operations_ui.common.date_restriction_generator import (
    get_date_restriction_text,
)
from response_operations_ui.common.dates import localise_datetime
from response_operations_ui.common.filters import (
    filter_eq_ci_selectors,
    get_collection_exercise_by_period,
)
from response_operations_ui.common.mappers import (
    convert_events_to_new_format,
    format_short_name,
    get_event_name,
    map_collection_exercise_state,
)
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
from response_operations_ui.exceptions.error_codes import get_error_code_message
from response_operations_ui.exceptions.exceptions import ApiError, ExternalApiError
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


def build_collection_exercise_details(short_name: str, period: str, include_ci: bool = False) -> dict:
    """
    :param short_name: short name of the survey (e.g., MBS, BRES, etc)
    :param period: Period for the collection exercise
    :param include_ci: Flag to include collection instrument data or not
    :return: A dict containing useful data about a given collection exercise
    """
    survey = survey_controllers.get_survey_by_shortname(short_name)
    survey_id = survey["id"]
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)
    exercise = get_collection_exercise_by_period(exercises, period)
    if not exercise:
        logger.error("Failed to find collection exercise by period", short_name=short_name, period=period)
        abort(404)

    collection_exercise_id = exercise["id"]
    survey["shortName"] = format_short_name(survey["shortName"])
    full_exercise = collection_exercise_controllers.get_collection_exercise_by_id(collection_exercise_id)
    exercise_events = collection_exercise_controllers.get_collection_exercise_events_by_id(collection_exercise_id)
    summary_id = collection_exercise_controllers.get_linked_sample_summary_id(collection_exercise_id)
    sample_summary = sample_controllers.get_sample_summary(summary_id) if summary_id else None

    exercise_dict = {
        "survey": survey,
        "collection_exercise": full_exercise,
        "events": convert_events_to_new_format(exercise_events),
        "sample_summary": _format_sample_summary(sample_summary),
    }

    if include_ci:
        exercise_dict["collection_instruments"] = _build_collection_instruments_details(
            collection_exercise_id, survey_id
        )
        if survey["surveyMode"] in ("EQ_AND_SEFT", "EQ"):
            exercise_dict["eq_ci_selectors"] = (
                collection_instrument_controllers.get_collection_instruments_by_classifier(
                    ci_type="EQ", survey_id=survey_id
                )
            )
    return exercise_dict


def _build_collection_instruments_details(collection_exercise_id: str, survey_id: str) -> dict:
    collection_instruments = collection_instrument_controllers.get_collection_instruments_by_classifier(
        collection_exercise_id=collection_exercise_id, survey_id=survey_id
    )
    collection_instruments_by_survey_mode = defaultdict(list)
    for ci in collection_instruments:
        collection_instruments_by_survey_mode[ci.get("type")].append(ci)

    return collection_instruments_by_survey_mode


def update_ce_details(ce_details: dict) -> dict:
    ce_details["collection_exercise"] = collection_exercise_controllers.get_collection_exercise_by_id(
        ce_details["collection_exercise"]["id"]
    )
    return ce_details


@collection_exercise_bp.route("/<short_name>/<period>", methods=["GET"])
@login_required
def view_collection_exercise(short_name, period):
    ce_details = build_collection_exercise_details(short_name, period, include_ci=True)

    # If there's a sample summary, but we're still in a state where we're setting up the collection exercise, then check
    # the sample summary and change it to ACTIVE all sample units are present.
    sample_load_status = None
    if sample_controllers.sample_summary_state_check_required(ce_details):
        try:
            sample_load_status = sample_controllers.check_if_all_sample_units_present_for_sample_summary(
                ce_details["sample_summary"]["id"]
            )
            if sample_load_status["areAllSampleUnitsLoaded"]:
                sample_summary = sample_controllers.get_sample_summary(ce_details["sample_summary"]["id"])
                ce_details["sample_summary"] = _format_sample_summary(sample_summary)
                ce_details = update_ce_details(ce_details)
        except ApiError:
            flash("Sample summary check failed.  Refresh page to try again", category="error")

    ce_state = ce_details["collection_exercise"]["state"]
    survey_mode = ce_details["survey"]["surveyMode"]
    show_sds = True if ce_details["collection_exercise"].get("supplementaryDatasetEntity") else False
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")
    processing = ce_state in ("EXECUTION_STARTED", "EXECUTED", "VALIDATED")
    validation_failed = ce_state == "FAILEDVALIDATION"
    ce_details["collection_exercise"]["state"] = map_collection_exercise_state(ce_state)

    if survey_mode in ("EQ", "EQ_AND_SEFT"):
        show_set_live_button = (
            ce_state in "READY_FOR_REVIEW"
            and "ref_period_start" in ce_details["events"]
            and "ref_period_end" in ce_details["events"]
        )
    else:
        show_set_live_button = ce_state in "READY_FOR_REVIEW"

    show_msg = request.args.get("show_msg")
    success_panel = request.args.get("success_panel")
    info_panel = request.args.get("info_panel")
    error_json = _get_error_from_session()
    _delete_sample_data_if_required()

    has_edit_permission = user_has_permission("surveys.edit")
    context = build_ce_context(ce_details, has_edit_permission, locked)

    return render_template(
        "collection_exercise/collection-exercise.html",
        has_edit_permission=has_edit_permission,
        ce=ce_details["collection_exercise"],
        error=error_json,
        locked=locked,
        processing=processing,
        sample_load_status=sample_load_status,
        sample=ce_details["sample_summary"],
        show_set_live_button=show_set_live_button,
        survey=ce_details["survey"],
        success_panel=success_panel,
        validation_failed=validation_failed,
        show_msg=show_msg,
        info_panel=info_panel,
        show_sds=show_sds,
        context=context,
    )


def _validate_exercise(exercise: dict, period: str, short_name: str):
    if not exercise:
        logger.error("Failed to find collection exercise by period", short_name=short_name, period=period)
        abort(404)


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
    survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)
    exercise = get_collection_exercise_by_period(exercises, period)

    if not exercise:
        abort(404)
    try:
        collection_exercise_controllers.execute_collection_exercise(exercise["id"])
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
    success_panel = None
    cis_selected = request.form.getlist("checkbox-answer")
    ce_details = build_collection_exercise_details(short_name, period, include_ci=True)

    if "EQ" in ce_details["survey"]["surveyMode"]:
        ce_id = ce_details["collection_exercise"]["id"]
        response = collection_instrument_controllers.update_collection_exercise_eq_instruments(cis_selected, ce_id)

        if response[0] != 200:
            if cis_selected:
                error_message = "Error: Failed to add and remove collection instrument(s)"
            else:
                error_message = response[1]

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

    return redirect(
        url_for(
            "collection_exercise_bp.view_collection_exercise",
            short_name=short_name,
            period=period,
            success_panel=success_panel,
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
        survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
        exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)

        # Find the collection exercise for the given period
        exercise = get_collection_exercise_by_period(exercises, period)
        if not exercise:
            return make_response(jsonify({"message": "Collection exercise not found"}), 404)

        if is_ru_specific_instrument:
            ru_ref = file.filename.split(".")[0]
            upload_success, error_text = collection_instrument_controllers.upload_ru_specific_collection_instrument(
                exercise["id"], file, ru_ref
            )
        else:
            form_type = _get_form_type(file.filename)
            upload_success, error_text = collection_instrument_controllers.upload_collection_instrument(
                exercise["id"], file, form_type
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
        submission_datetime = localise_datetime(iso8601.parse_date(sample["ingestDateTime"]))
        submission_time = submission_datetime.strftime("%d %B %Y %I:%M%p")
        sample["ingestDateTime"] = submission_time

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
    ce_details = build_collection_exercise_details(short_name, period)
    form = EditCollectionExercisePeriodIDForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    ce_state = ce_details["collection_exercise"]["state"]
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")

    return render_template(
        "edit-collection-exercise-period-id.html",
        survey_ref=ce_details["survey"]["surveyRef"],
        form=form,
        short_name=short_name,
        period=period,
        locked=locked,
        ce_state=ce_details["collection_exercise"]["state"],
        collection_exercise_id=ce_details["collection_exercise"]["id"],
        survey_id=survey_details["id"],
    )


@collection_exercise_bp.route("/<short_name>/<period>/edit-collection-exercise-period-description", methods=["GET"])
@login_required
def edit_collection_exercise_period_description(short_name, period):
    verify_permission("surveys.edit")
    logger.info("Retrieving collection exercise data for form", short_name=short_name, period=period)
    ce_details = build_collection_exercise_details(short_name, period)
    form = EditCollectionExercisePeriodIDForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    ce_state = ce_details["collection_exercise"]["state"]
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")

    return render_template(
        "edit-collection-exercise-period-description.html",
        survey_ref=ce_details["survey"]["surveyRef"],
        form=form,
        short_name=short_name,
        period=period,
        user_description=ce_details["collection_exercise"]["userDescription"],
        locked=locked,
        ce_state=ce_details["collection_exercise"]["state"],
        collection_exercise_id=ce_details["collection_exercise"]["id"],
        survey_id=survey_details["id"],
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
        ce_details = build_collection_exercise_details(short_name, period)
        ce_state = ce_details["collection_exercise"]["state"]
        survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
        locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")

        return render_template(
            "edit-collection-exercise-period-id.html",
            survey_ref=ce_details["survey"]["surveyRef"],
            form=form,
            short_name=short_name,
            period=period,
            locked=locked,
            ce_state=ce_details["collection_exercise"]["state"],
            errors=form.errors,
            collection_exercise_id=ce_details["collection_exercise"]["id"],
            survey_id=survey_id,
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
        ce_details = build_collection_exercise_details(short_name, period)
        ce_state = ce_details["collection_exercise"]["state"]
        survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
        locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")

        return render_template(
            "edit-collection-exercise-period-description.html",
            survey_ref=ce_details["survey"]["surveyRef"],
            form=form,
            short_name=short_name,
            period=period,
            locked=locked,
            ce_state=ce_details["collection_exercise"]["state"],
            errors=form.errors,
            user_description=ce_details["collection_exercise"]["userDescription"],
            collection_exercise_id=ce_details["collection_exercise"]["id"],
            survey_id=survey_id,
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
    survey = survey_controllers.get_survey(short_name)
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey["id"])
    exercise = get_collection_exercise_by_period(exercises, period)
    if not exercise:
        logger.error("Failed to find collection exercise by period", short_name=short_name, period=period)
        abort(404)

    events = collection_exercise_controllers.get_collection_exercise_events_by_id(exercise["id"])
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
    ce_details = build_collection_exercise_details(short_name, period, include_ci=True)
    ce_state = ce_details["collection_exercise"]["state"]
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")
    sample_load_status = None
    all_cis_for_survey = []
    eq_ci_selectors = []
    if sample_controllers.sample_summary_state_check_required(ce_details):
        try:
            sample_load_status = sample_controllers.check_if_all_sample_units_present_for_sample_summary(
                ce_details["sample_summary"]["id"]
            )
            if sample_load_status["areAllSampleUnitsLoaded"]:
                sample_summary = sample_controllers.get_sample_summary(ce_details["sample_summary"]["id"])
                ce_details["sample_summary"] = _format_sample_summary(sample_summary)
        except ApiError:
            flash("Sample summary check failed.  Refresh page to try again", category="error")

    if ce_details["survey"]["surveyMode"] in ("EQ_AND_SEFT", "EQ"):
        linked_eq_ci = ce_details["collection_instruments"].get("EQ", {})
        all_eq_survey_ci = collection_instrument_controllers.get_collection_instruments_by_classifier(
            ci_type="EQ", survey_id=ce_details["survey"]["id"]
        )
        all_cis_for_survey = filter_eq_ci_selectors(all_eq_survey_ci, linked_eq_ci)
        _format_ci_file_name(linked_eq_ci, ce_details["survey"])
        eq_ci_selectors = ce_details.get("eq_ci_selectors", {})

    error_json = _get_error_from_session()
    _delete_sample_data_if_required()
    show_msg = request.args.get("show_msg")

    success_panel = request.args.get("success_panel")
    info_panel = request.args.get("info_panel")

    breadcrumbs = [{"text": "Back", "url": "/surveys/" + short_name + "/" + period}, {}]
    return render_template(
        "collection_exercise/ce-eq-instrument-section.html",
        ce=ce_details["collection_exercise"],
        collection_instruments=ce_details["collection_instruments"],
        error=error_json,
        locked=locked,
        sample=ce_details["sample_summary"],
        survey=ce_details["survey"],
        sample_load_status=sample_load_status,
        success_panel=success_panel,
        show_msg=show_msg,
        eq_ci_selectors=eq_ci_selectors,
        info_panel=info_panel,
        all_cis_for_survey=all_cis_for_survey,
        breadcrumbs=breadcrumbs,
    )


@collection_exercise_bp.route("/<short_name>/<period>/upload-sample-file", methods=["GET"])
@login_required
def get_upload_sample_file(short_name, period):
    verify_permission("surveys.edit")
    ce_details = build_collection_exercise_details(short_name, period)
    ce_state = ce_details["collection_exercise"]["state"]
    ce_details["collection_exercise"]["state"] = map_collection_exercise_state(ce_state)  # NOQA
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")
    success_panel = request.args.get("success_panel")
    show_msg = request.args.get("show_msg")
    error_json = _get_error_from_session()
    return render_template(
        "collection_exercise/ce-upload-sample-file.html",
        ce=ce_details["collection_exercise"],
        error=error_json,
        locked=locked,
        sample=ce_details["sample_summary"],
        survey=ce_details["survey"],
        success_panel=success_panel,
        show_msg=show_msg,
    )


@collection_exercise_bp.route("/<short_name>/<period>/upload-sample-file", methods=["POST"])
@login_required
def post_upload_sample_file(short_name, period):
    verify_permission("surveys.edit")
    if _validate_sample():
        survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
        exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)

        # Find the collection exercise for the given period
        exercise = get_collection_exercise_by_period(exercises, period)

        if not exercise:
            return make_response(jsonify({"message": "Collection exercise not found"}), 404)
        try:
            sample_summary = sample_controllers.upload_sample(short_name, period, request.files["sampleFile"])

            logger.info(
                "Linking sample summary with collection exercise",
                collection_exercise_id=exercise["id"],
                sample_id=sample_summary["id"],
            )
            collection_exercise_controllers.link_sample_summary_to_collection_exercise(
                collection_exercise_id=exercise["id"], sample_summary_id=sample_summary["id"]
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
    ce_details = build_collection_exercise_details(short_name, period)
    sample_summary_id = ce_details["sample_summary"]["id"]
    collection_exercise_id = ce_details["collection_exercise"]["id"]

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
    ce_details = build_collection_exercise_details(short_name, period, include_ci=True)
    collection_instruments = ce_details["collection_instruments"].get("SEFT", {})
    show_msg = request.args.get("show_msg")
    success_panel = request.args.get("success_panel")
    info_panel = request.args.get("info_panel")
    locked = ce_details["collection_exercise"]["state"] in (
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
        survey=ce_details["survey"],
        ce=ce_details["collection_exercise"],
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
    survey_id = survey_controllers.get_survey_by_shortname(short_name).get("id")
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)
    exercise = get_collection_exercise_by_period(exercises, period)

    _validate_exercise(exercise, period, short_name)
    eq_collection_instruments = _build_collection_instruments_details(exercise["id"], survey_id).get("EQ", [])

    return render_template(
        "collection_exercise/view-sample-ci-summary.html",
        collection_instruments=eq_collection_instruments,
    )


@collection_exercise_bp.route("/<short_name>/<period>/view-sample-ci/summary/<form_type>", methods=["GET"])
@login_required
def view_ci_versions(short_name: str, period: str, form_type: str) -> str:

    breadcrumbs = [
        {"text": "Back to CIR versions", "url": "/surveys/" + short_name + "/" + period + "/view-sample-ci/summary"},
        {},
    ]
    return render_template("collection_exercise/ci-versions.html", form_type=form_type, breadcrumbs=breadcrumbs)


@collection_exercise_bp.route("/<short_name>/<period>/view-sample-ci/summary/<form_type>", methods=["POST"])
@login_required
def save_ci_versions(short_name: str, period: str, form_type: str) -> str:
    return redirect(url_for("collection_exercise_bp.view_collection_exercise", short_name=short_name, period=period))


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
