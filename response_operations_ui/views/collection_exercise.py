import json
import logging
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
from wtforms import ValidationError

from response_operations_ui.common.date_restriction_generator import (
    get_date_restriction_text,
)
from response_operations_ui.common.dates import localise_datetime
from response_operations_ui.common.filters import get_collection_exercise_by_period
from response_operations_ui.common.mappers import (
    convert_events_to_new_format,
    format_short_name,
    map_collection_exercise_state,
)
from response_operations_ui.common.validators import valid_date_for_event
from response_operations_ui.controllers import (
    collection_exercise_controllers,
    collection_instrument_controllers,
    party_controller,
    sample_controllers,
    survey_controllers,
    uaa_controller,
)
from response_operations_ui.controllers.collection_exercise_controllers import (
    update_collection_exercise_eq_version,
)
from response_operations_ui.exceptions.exceptions import ApiError
from response_operations_ui.forms import (
    CreateCollectionExerciseDetailsForm,
    EditCollectionExerciseDetailsForm,
    EventDateForm,
    RemoveLoadedSample,
)

logger = wrap_logger(logging.getLogger(__name__))

collection_exercise_bp = Blueprint(
    "collection_exercise_bp", __name__, static_folder="static", template_folder="templates"
)


def filter_eq_ci_selectors(eq_ci_selectors, collection_instruments):
    for collection_instrument in collection_instruments:
        if collection_instrument in eq_ci_selectors:
            eq_ci_selectors.remove(collection_instrument)
    return eq_ci_selectors


def build_collection_exercise_details(short_name, period):
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
    collection_instruments = collection_instrument_controllers.get_collection_instruments_by_classifier(
        collection_exercise_id=collection_exercise_id, survey_id=survey_id
    )

    eq_ci_selectors = collection_instrument_controllers.get_collection_instruments_by_classifier(
        ci_type="EQ", survey_id=survey_id
    )

    summary_id = collection_exercise_controllers.get_linked_sample_summary_id(collection_exercise_id)
    sample_summary = sample_controllers.get_sample_summary(summary_id) if summary_id else None
    ci_classifiers = survey_controllers.get_survey_ci_classifier(survey_id)

    return {
        "survey": survey,
        "collection_exercise": full_exercise,
        "events": convert_events_to_new_format(exercise_events),
        "collection_instruments": collection_instruments,
        "eq_ci_selectors": eq_ci_selectors,
        "sample_summary": _format_sample_summary(sample_summary),
        "ci_classifiers": ci_classifiers,
    }


@collection_exercise_bp.route("/<short_name>/<period>", methods=["GET"])
@login_required
def view_collection_exercise(short_name, period):
    ce_details = build_collection_exercise_details(short_name, period)
    ce_state = ce_details["collection_exercise"]["state"]
    if ce_details["survey"]["surveyMode"] == "EQ":
        show_set_live_button = (
            ce_state in ("READY_FOR_REVIEW")
            and "ref_period_start" in ce_details["events"]
            and "ref_period_end" in ce_details["events"]
        )
    else:
        show_set_live_button = ce_state in ("READY_FOR_REVIEW", "FAILEDVALIDATION")

    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")
    processing = ce_state in ("EXECUTION_STARTED", "EXECUTED", "VALIDATED")
    validation_failed = ce_state == "FAILEDVALIDATION"
    validation_errors = ce_details["collection_exercise"]["validationErrors"]
    missing_ci = validation_errors and any(
        "MISSING_COLLECTION_INSTRUMENT" in unit["errors"] for unit in validation_errors
    )
    ce_details["collection_exercise"]["state"] = map_collection_exercise_state(ce_state)  # NOQA
    _format_ci_file_name(ce_details["collection_instruments"], ce_details["survey"])

    show_msg = request.args.get("show_msg")

    success_panel = request.args.get("success_panel")
    info_panel = request.args.get("info_panel")
    sorted_nudge_list = get_existing_sorted_nudge_events(ce_details["events"])
    error_json = _get_error_from_session()
    _delete_sample_data_if_required()

    return render_template(
        "collection_exercise/collection-exercise.html",
        ce=ce_details["collection_exercise"],
        collection_instruments=ce_details["collection_instruments"],
        eq_ci_selectors=ce_details["eq_ci_selectors"],
        error=error_json,
        events=ce_details["events"],
        locked=locked,
        missing_ci=missing_ci,
        processing=processing,
        sample=ce_details["sample_summary"],
        show_set_live_button=show_set_live_button,
        survey=ce_details["survey"],
        success_panel=success_panel,
        validation_failed=validation_failed,
        show_msg=show_msg,
        ci_classifiers=ce_details["ci_classifiers"]["classifierTypes"],
        info_panel=info_panel,
        existing_nudge=sorted_nudge_list if len(sorted_nudge_list) > 0 else [],
        is_eq_v3_enabled=app.config["EQ_VERSION_ENABLED"],
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
    if "load-sample" in request.form:
        return _upload_sample(short_name, period)
    elif "load-ci" in request.form:
        return _upload_collection_instrument(short_name, period)
    elif "select-ci" in request.form:
        return _select_collection_instrument(short_name, period)
    elif "unselect-ci" in request.form:
        return _unselect_collection_instrument(short_name, period)
    if "eq-version" in request.form:
        return _update_eq_version(short_name, period)
    return get_view_sample_ci(short_name, period)


@collection_exercise_bp.route("response_chasing/<ce_id>/<survey_id>", methods=["GET"])
@login_required
def response_chasing(ce_id, survey_id):
    logger.info("Response chasing", ce_id=ce_id, survey_id=survey_id)
    response = collection_exercise_controllers.download_report(ce_id, survey_id)
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


def _upload_sample(short_name, period):
    error = _validate_sample()

    if not error:
        survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
        exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)

        # Find the collection exercise for the given period
        exercise = get_collection_exercise_by_period(exercises, period)

        if not exercise:
            return make_response(jsonify({"message": "Collection exercise not found"}), 404)
        sample_summary = sample_controllers.upload_sample(short_name, period, request.files["sampleFile"])

        logger.info(
            "Linking sample summary with collection exercise",
            collection_exercise_id=exercise["id"],
            sample_id=sample_summary["id"],
        )

        collection_exercise_controllers.link_sample_summary_to_collection_exercise(
            collection_exercise_id=exercise["id"], sample_summary_id=sample_summary["id"]
        )

    return redirect(
        url_for(
            "collection_exercise_bp.get_view_sample_ci",
            short_name=short_name,
            period=period,
            error=error,
            show_msg="true",
        )
    )


def _select_collection_instrument(short_name, period):
    success_panel = None
    cis_selected = request.form.getlist("checkbox-answer")
    cis_added = []

    if cis_selected:
        for ci in cis_selected:
            ci_added = collection_instrument_controllers.link_collection_instrument(request.form["ce_id"], ci)
            cis_added.append(ci_added)

        if all(added for added in cis_added):
            success_panel = "Collection instruments added"
        else:
            session["error"] = json.dumps(
                {
                    "section": "ciSelect",
                    "header": "Error: Failed to add collection instrument(s)",
                    "message": "Please try again",
                }
            )

    else:
        session["error"] = json.dumps(
            {
                "section": "ciSelect",
                "header": "Error: No collection instruments selected",
                "message": "Please select a collection instrument",
            }
        )

    return redirect(
        url_for(
            "collection_exercise_bp.get_view_sample_ci",
            short_name=short_name,
            period=period,
            success_panel=success_panel,
        )
    )


def _update_eq_version(short_name, period):
    eq_version = request.form.get("eq-version")
    ce_details = build_collection_exercise_details(short_name, period)
    ce = ce_details["collection_exercise"]
    if ce["eqVersion"] != eq_version:
        update_collection_exercise_eq_version(ce["id"], eq_version)
        flash("eQ version updated successfully.")
        return redirect(
            url_for(
                "collection_exercise_bp.view_collection_exercise",
                period=period,
                short_name=short_name,
                success_panel=f"eQ version updated to {eq_version}.",
            )
        )
    return redirect(
        url_for(
            "collection_exercise_bp.view_collection_exercise",
            period=period,
            short_name=short_name,
        )
    )


def _upload_collection_instrument(short_name, period):
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

        error_text = None
        if is_ru_specific_instrument:
            ru_ref = file.filename.split(".")[0]
            upload_success, error_text = collection_instrument_controllers.upload_ru_specific_collection_instrument(
                exercise["id"], file, ru_ref
            )
        else:
            form_type = _get_form_type(file.filename)
            upload_success = collection_instrument_controllers.upload_collection_instrument(
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


def _unselect_collection_instrument(short_name, period):
    success_panel = _unlink_collection_instrument()
    return redirect(
        url_for(
            "collection_exercise_bp.get_view_sample_ci",
            short_name=short_name,
            period=period,
            success_panel=success_panel,
        )
    )


def _validate_collection_instrument():
    error = None
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


def _validate_sample():
    error = None
    if "sampleFile" in request.files:
        file = request.files["sampleFile"]
        if not str.endswith(file.filename, ".csv"):
            logger.info("Invalid file format uploaded", filename=file.filename)
            error = "Invalid file format"
    else:
        logger.info("No file uploaded")
        error = "File not uploaded"

    return error


def _format_sample_summary(sample):
    if sample and sample.get("ingestDateTime"):
        submission_datetime = localise_datetime(iso8601.parse_date(sample["ingestDateTime"]))
        submission_time = submission_datetime.strftime("%I:%M%p on %B %d, %Y")
        sample["ingestDateTime"] = submission_time

    return sample


def _format_ci_file_name(collection_instruments, survey_details):
    for ci in collection_instruments:
        if "xlsx" not in str(ci.get("file_name", "")):
            ci["file_name"] = f"{survey_details['surveyRef']} {ci['file_name']} eQ"


def _get_form_type(file_name):
    file_name = file_name.split(".")[0]
    return file_name.split("_")[2]  # file name format is surveyId_period_formType


@collection_exercise_bp.route("/<short_name>/<period>/edit-collection-exercise-details", methods=["GET"])
@login_required
def view_collection_exercise_details(short_name, period):
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
    logger.info("Retrieving collection exercise data for form", short_name=short_name, period=period)
    ce_details = build_collection_exercise_details(short_name, period)
    form = EditCollectionExerciseDetailsForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    ce_state = ce_details["collection_exercise"]["state"]
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")

    return render_template(
        "edit-collection-exercise-details.html",
        survey_ref=ce_details["survey"]["surveyRef"],
        form=form,
        short_name=short_name,
        period=period,
        locked=locked,
        ce_state=ce_details["collection_exercise"]["state"],
        user_description=ce_details["collection_exercise"]["userDescription"],
        collection_exercise_id=ce_details["collection_exercise"]["id"],
        survey_id=survey_details["id"],
    )


@collection_exercise_bp.route("/<short_name>/<period>/edit-collection-exercise-details", methods=["POST"])
@login_required
def edit_collection_exercise_details(short_name, period):
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
    form = EditCollectionExerciseDetailsForm(form=request.form)
    if not form.validate():
        logger.info(
            "Failed validation, retrieving collection exercise data for form", short_name=short_name, period=period
        )
        ce_details = build_collection_exercise_details(short_name, period)
        ce_state = ce_details["collection_exercise"]["state"]
        survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
        locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")

        return render_template(
            "edit-collection-exercise-details.html",
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
        logger.info("Updating collection exercise details", short_name=short_name, period=period)
        form = request.form
        collection_exercise_controllers.update_collection_exercise_user_description(
            form.get("collection_exercise_id"), form.get("user_description")
        )

        if form.get("period") != period:
            collection_exercise_controllers.update_collection_exercise_period(
                form.get("collection_exercise_id"), form.get("period")
            )

        return redirect(url_for("surveys_bp.view_survey", short_name=short_name, ce_updated="True"))


@collection_exercise_bp.route("/<survey_ref>/<short_name>/create-collection-exercise", methods=["GET"])
@login_required
def get_create_collection_exercise_form(survey_ref, short_name):
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
    logger.info("Retrieving survey data for form", short_name=short_name, survey_ref=survey_ref)
    form = CreateCollectionExerciseDetailsForm(form=request.form)
    survey_details = survey_controllers.get_survey(short_name)
    survey_eq_version = survey_details["eqVersion"] if survey_details["surveyMode"] != "SEFT" else ""
    return render_template(
        "create-collection-exercise.html",
        form=form,
        short_name=short_name,
        survey_ref=survey_ref,
        survey_id=survey_details["id"],
        survey_name=survey_details["shortName"],
        survey_eq_version=survey_eq_version,
    )


@collection_exercise_bp.route("/<survey_ref>/<short_name>/create-collection-exercise", methods=["POST"])
@login_required
def create_collection_exercise(survey_ref, short_name):
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
    logger.info("Attempting to create collection exercise", survey_ref=survey_ref, survey=short_name)
    ce_form = CreateCollectionExerciseDetailsForm(form=request.form)
    form = request.form

    survey_id = form.get("hidden_survey_id")
    survey_name = form.get("hidden_survey_name")
    survey_eq_version = form.get("hidden_eq_version")

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
            survey_eq_version=survey_eq_version,
        )

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
                survey_eq_version=survey_eq_version,
            )

    logger.info(
        "Creating collection exercise for survey",
        survey=short_name,
        survey_ref=survey_ref,
        survey_eq_version=survey_eq_version,
    )

    collection_exercise_controllers.create_collection_exercise(
        survey_id, survey_name, form.get("user_description"), form.get("period"), survey_eq_version
    )

    logger.info("Successfully created collection exercise", survey=short_name, survey_ref=survey_ref)
    return redirect(
        url_for("surveys_bp.view_survey", short_name=short_name, ce_created="True", new_period=form.get("period"))
    )


@collection_exercise_bp.route("/<short_name>/<period>/<ce_id>/confirm-create-event/<tag>", methods=["GET"])
@login_required
def get_create_collection_event_form(short_name, period, ce_id, tag):
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
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
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
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


def get_event_name(tag):
    event_names = {
        "mps": "Main print selection",
        "go_live": "Go Live",
        "return_by": "Return by",
        "exercise_end": "Exercise end",
        "reminder": "First reminder",
        "reminder2": "Second reminder",
        "reminder3": "Third reminder",
        "ref_period_start": "Reference period start date",
        "ref_period_end": "Reference period end date",
        "employment": "Employment date",
        "nudge_email_0": "Schedule nudge email",
        "nudge_email_1": "Schedule nudge email",
        "nudge_email_2": "Schedule nudge email",
        "nudge_email_3": "Schedule nudge email",
        "nudge_email_4": "Schedule nudge email",
    }
    return event_names.get(tag)


@collection_exercise_bp.route("/<short_name>/<period>/view-sample-ci", methods=["GET"])
@login_required
def get_view_sample_ci(short_name, period):
    logger.info("Retrieving upload sample collection instrument page", short_name=short_name, period=period)
    ce_details = build_collection_exercise_details(short_name, period)
    ce_state = ce_details["collection_exercise"]["state"]

    ce_details["collection_exercise"]["state"] = map_collection_exercise_state(ce_state)  # NOQA
    ce_details["eq_ci_selectors"] = filter_eq_ci_selectors(
        ce_details["eq_ci_selectors"], ce_details["collection_instruments"]
    )
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")
    _format_ci_file_name(ce_details["collection_instruments"], ce_details["survey"])

    error_json = _get_error_from_session()
    _delete_sample_data_if_required()
    show_msg = request.args.get("show_msg")

    success_panel = request.args.get("success_panel")
    info_panel = request.args.get("info_panel")

    return render_template(
        "collection_exercise/ce-view-sample-ci.html",
        ce=ce_details["collection_exercise"],
        collection_instruments=ce_details["collection_instruments"],
        sample=ce_details["sample_summary"],
        survey=ce_details["survey"],
        eq_ci_selectors=ce_details["eq_ci_selectors"],
        error=error_json,
        success_panel=success_panel,
        info_panel=info_panel,
        show_msg=show_msg,
        locked=locked,
    )


@collection_exercise_bp.route("/<short_name>/<period>/upload-sample-file", methods=["GET"])
@login_required
def get_upload_sample_file(short_name, period):
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
    logger.info("Retrieving upload sample file page", short_name=short_name, period=period)
    ce_details = build_collection_exercise_details(short_name, period)
    ce_state = ce_details["collection_exercise"]["state"]
    ce_details["collection_exercise"]["state"] = map_collection_exercise_state(ce_state)  # NOQA
    locked = ce_state in ("LIVE", "READY_FOR_LIVE", "EXECUTION_STARTED", "VALIDATED", "EXECUTED", "ENDED")
    success_panel = request.args.get("success_panel")
    error_json = _get_error_from_session()
    return render_template(
        "collection_exercise/ce-upload-sample-file.html",
        ce=ce_details["collection_exercise"],
        survey=ce_details["survey"],
        sample=ce_details["sample_summary"],
        eq_ci_selectors=ce_details["eq_ci_selectors"],
        error=error_json,
        locked=locked,
        success_panel=success_panel,
    )


@collection_exercise_bp.route("/<short_name>/<period>/upload-sample-file", methods=["POST"])
@login_required
def post_upload_sample_file(short_name, period):
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
    return _upload_sample(short_name, period)


@collection_exercise_bp.route("/<short_name>/<period>/confirm-remove-sample", methods=["GET"])
@login_required
def get_confirm_remove_sample(short_name, period):
    logger.info("Retrieving confirm remove sample page", short_name=short_name, period=period)
    form = RemoveLoadedSample(form=request.form)
    return render_template("confirm-remove-sample.html", form=form, short_name=short_name, period=period)


@collection_exercise_bp.route("/<short_name>/<period>/confirm-remove-sample", methods=["POST"])
@login_required
def remove_loaded_sample(short_name, period):
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
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


@collection_exercise_bp.route("/<short_name>/<period>/load-collection-instruments", methods=["GET"])
@login_required
def get_seft_collection_instrument(short_name, period):
    ce_details = build_collection_exercise_details(short_name, period)
    show_msg = request.args.get("show_msg")
    success_panel = request.args.get("success_panel")
    info_panel = request.args.get("info_panel")
    error_json = _get_error_from_session()
    return render_template(
        "ce-seft-instrument.html",
        survey=ce_details["survey"],
        ce=ce_details["collection_exercise"],
        collection_instruments=ce_details["collection_instruments"],
        success_panel=success_panel,
        error=error_json,
        info_panel=info_panel,
        show_msg=show_msg,
        period=period,
    )


@collection_exercise_bp.route("/<short_name>/<period>/load-collection-instruments", methods=["POST"])
@login_required
def post_seft_collection_instrument(short_name, period):
    if not uaa_controller.user_has_permission("surveys.edit"):
        logger.error("User has insufficient permissions to access this page", user_id=session["user_id"])
        abort(500)
    if "unselect-ci" in request.form:
        return _unselect_seft_collection_instrument(short_name, period)
    return _upload_seft_collection_instrument(short_name, period)


def _unselect_seft_collection_instrument(short_name, period):
    success_panel = _unlink_collection_instrument()

    return redirect(
        url_for(
            "collection_exercise_bp.get_seft_collection_instrument",
            short_name=short_name,
            period=period,
            success_panel=success_panel,
        )
    )


def _unlink_collection_instrument():
    success_panel = None
    ci_id = request.form.get("ci_id")
    ce_id = request.form.get("ce_id")
    ci_unlinked = collection_instrument_controllers.unlink_collection_instrument(ce_id, ci_id)
    if ci_unlinked:
        success_panel = "Collection instrument removed"
    else:
        session["error"] = json.dumps(
            {
                "section": "head",
                "header": "Error: Failed to remove collection instrument",
                "message": "Please try again",
            }
        )
    return success_panel


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

        error_text = None
        if is_ru_specific_instrument:
            ru_ref = file.filename.split(".")[0]
            upload_success, error_text = collection_instrument_controllers.upload_ru_specific_collection_instrument(
                exercise["id"], file, ru_ref
            )
        else:
            form_type = _get_form_type(file.filename)
            upload_success = collection_instrument_controllers.upload_collection_instrument(
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
            short_name=short_name,
            period=period,
            success_panel=success_panel,
        )
    )
