import html
import json
import logging
import math
from datetime import datetime

from flask import (
    Blueprint,
    Markup,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required
from flask_paginate import Pagination
from structlog import wrap_logger

from config import FDI_LIST, VACANCIES_LIST
from response_operations_ui.common.dates import get_formatted_date, localise_datetime
from response_operations_ui.common.mappers import format_short_name
from response_operations_ui.controllers import (
    message_controllers,
    party_controller,
    survey_controllers,
)
from response_operations_ui.controllers.survey_controllers import (
    get_business_survey_shortname_list,
    get_grouped_surveys_list,
    get_survey_ref_by_id,
    get_survey_short_name_by_id,
)
from response_operations_ui.controllers.uaa_controller import user_has_permission
from response_operations_ui.exceptions.exceptions import (
    ApiError,
    InternalError,
    NoPermissionError,
)
from response_operations_ui.forms import (
    ChangeThreadCategoryForm,
    SecureMessageForm,
    SecureMessageRuFilterForm,
)

logger = wrap_logger(logging.getLogger(__name__))

messages_bp = Blueprint("messages_bp", __name__, static_folder="static", template_folder="templates")

CACHE_HEADERS = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}


@messages_bp.route("/create-message", methods=["POST"])
@login_required
def create_message():
    if not user_has_permission("messages.edit"):
        raise NoPermissionError("messages.edit")
    form = SecureMessageForm(request.form)
    breadcrumbs = _build_create_message_breadcrumbs()

    if "create-message" in request.form:
        form = _populate_hidden_form_fields_from_post(form, request.form)
        form = _populate_form_details_from_hidden_fields(form)
    elif form.validate_on_submit():
        # Keep the message subject and body when message sent
        g.form_subject_data = form.subject.data
        g.form_body_data = form.body.data

        try:
            message_controllers.send_message(_get_message_json(form))
            ru_ref = request.form.get("hidden_ru_ref")
            flash("Message sent.")
            if ru_ref:
                return redirect(url_for("reporting_unit_bp.view_reporting_unit", ru_ref=ru_ref))
            # Very unlikely for the ru_ref to not be present, but if not, redirect somewhere sensible.
            return redirect(url_for("messages_bp.view_select_survey"))
        except (ApiError, InternalError):
            form = _repopulate_form_with_submitted_data(form)
            flash("Message failed to send, something has gone wrong with the website.", "sending")
            return render_template("create-message.html", form=form, breadcrumbs=breadcrumbs)

    return render_template("create-message.html", form=form, breadcrumbs=breadcrumbs)


@messages_bp.route("/threads/<thread_id>", methods=["GET", "POST"])
@login_required
def view_conversation(thread_id):
    conversation_tab = request.args.get("conversation_tab")
    page = request.args.get("page")
    ru_ref_filter = request.args.get("ru_ref_filter")
    business_id_filter = request.args.get("business_id_filter")

    if request.method == "POST" and request.form.get("reopen"):
        if not user_has_permission("messages.edit"):
            raise NoPermissionError("messages.edit")
        payload = {"is_closed": False}
        message_controllers.patch_thread(thread_id, payload)
        thread_url = (
            url_for(
                "messages_bp.view_conversation",
                thread_id=thread_id,
                conversation_tab=conversation_tab,
                page=page,
                ru_ref_filter=ru_ref_filter,
                business_id_filter=business_id_filter,
            )
            + "#latest-message"
        )
        flash(Markup(f"Conversation re-opened. <a href={thread_url}>View conversation</a>"))
        return redirect(
            url_for(
                "messages_bp.view_select_survey",
                conversation_tab=conversation_tab,
                page=page,
                ru_ref_filter=ru_ref_filter,
                business_id_filter=business_id_filter,
            )
        )

    thread_conversation = message_controllers.get_conversation(thread_id)
    category = thread_conversation["category"]
    refined_thread = [_refine(message, category) for message in reversed(thread_conversation["messages"])]
    latest_message = refined_thread[-1]
    closed_at = _format_closed_at(thread_conversation)
    breadcrumbs = _get_conversation_breadcrumbs(thread_conversation["messages"])

    respondent_key = "to" if latest_message["internal"] else "from"
    respondent_is_deleted = True if latest_message[respondent_key] == "Deleted respondent" else False

    if latest_message["unread"] and _can_mark_as_unread(latest_message):
        message_controllers.remove_unread_label(latest_message["message_id"])

    form = SecureMessageForm(request.form)

    if form.validate_on_submit():
        if not user_has_permission("messages.edit"):
            raise NoPermissionError("messages.edit")
        form = _populate_form_details_from_hidden_fields(form)
        g.form_subject_data = form.subject.data
        g.form_body_data = form.body.data

        try:
            if category != "SURVEY":
                message_controllers.send_message(
                    _get_non_survey_message_json(
                        form, thread_id=refined_thread[0]["thread_id"], category=thread_conversation["category"]
                    )
                )
            else:
                message_controllers.send_message(_get_message_json(form, thread_id=refined_thread[0]["thread_id"]))
            thread_url = (
                url_for(
                    "messages_bp.view_conversation",
                    thread_id=thread_id,
                    page=page,
                    conversation_tab=conversation_tab,
                    ru_ref_filter=ru_ref_filter,
                    business_id_filter=business_id_filter,
                )
                + "#latest-message"
            )
            flash(Markup(f"Message sent. <a href={thread_url}>View Message</a>"))
            return redirect(
                url_for(
                    "messages_bp.view_select_survey",
                    page=page,
                    conversation_tab=conversation_tab,
                    ru_ref_filter=ru_ref_filter,
                    business_id_filter=business_id_filter,
                )
            )

        except (ApiError, InternalError) as e:
            error = "Message failed to send, something has gone wrong with the website."
            if e.status_code == 404 and "Respondent not found" in e.message:
                error = "Cannot send message to respondent as they have been deleted"

            form = _repopulate_form_with_submitted_data(form)
            flash(error, "sending")
            return render_template(
                "conversation-view/conversation-view.html",
                form=form,
                breadcrumbs=breadcrumbs,
                messages=refined_thread,
                respondent_is_deleted=respondent_is_deleted,
                thread_data=thread_conversation,
            )

    close_conversation_url = url_for(
        "messages_bp.close_conversation",
        thread_id=refined_thread[0]["thread_id"],
        page=page,
        conversation_tab=conversation_tab,
        business_id=refined_thread[0]["business_id"],
        ru_ref_filter=ru_ref_filter,
        business_id_filter=business_id_filter,
        category=thread_conversation["category"],
    )

    return render_template(
        "conversation-view/conversation-view.html",
        breadcrumbs=breadcrumbs,
        messages=refined_thread,
        respondent_is_deleted=respondent_is_deleted,
        form=form,
        selected_survey=refined_thread[0]["survey"],
        page=page,
        closed_at=closed_at,
        thread_data=thread_conversation,
        show_mark_unread=_can_mark_as_unread(latest_message),
        conversation_tab=conversation_tab,
        close_conversation_url=close_conversation_url,
        ru_ref_filter=ru_ref_filter,
        business_id_filter=business_id_filter,
    )


@messages_bp.route("/threads/<thread_id>/change-category", methods=["GET"])
@login_required
def get_change_thread_category(thread_id):
    if not user_has_permission("messages.edit"):
        raise NoPermissionError("messages.edit")
    thread = message_controllers.get_conversation(thread_id)
    form = ChangeThreadCategoryForm()
    breadcrumbs = [{"text": "Messages", "url": "/messages"}, {"text": "Filter by survey"}]

    survey_list = get_business_survey_shortname_list()

    return render_template(
        "secure-message/change-thread-category.html",
        thread=thread,
        thread_id=thread_id,
        breadcrumbs=breadcrumbs,
        survey_list=survey_list,
        form=form,
    )


@messages_bp.route("/threads/<thread_id>/change-category", methods=["POST"])
@login_required
def post_change_thread_category(thread_id):  # noqa: C901
    if not user_has_permission("messages.edit"):
        raise NoPermissionError("messages.edit")
    thread = message_controllers.get_conversation(thread_id)
    form = ChangeThreadCategoryForm(request.form)

    if form.validate():
        category = form.category.data

        # If the category is SURVEY then we need to go to another page to set the business_id for the thread also.
        if category == "SURVEY":
            session["secure-message-change-survey-shortname"] = form.select_survey.data
            return redirect(url_for("messages_bp.get_change_reporting_unit", thread_id=thread_id))

        payload = {"category": category}
        try:
            message_controllers.patch_thread(thread_id, payload)
        except ApiError:
            flash("Something went wrong updating the category. Please try again.", category="error")
            return redirect(url_for("messages_bp.get_change_thread_category", thread_id=thread_id))

        flash("The category has been successfully updated")
        return redirect(url_for("messages_bp.view_select_survey"))

    breadcrumbs = [{"text": "Messages", "url": "/messages"}, {"text": "Filter by survey"}]
    survey_list = get_business_survey_shortname_list()

    return render_template(
        "secure-message/change-thread-category.html",
        thread=thread,
        thread_id=thread_id,
        breadcrumbs=breadcrumbs,
        survey_list=survey_list,
        form=form,
    )


@messages_bp.route("/threads/<thread_id>/change-reporting-unit", methods=["GET"])
@login_required
def get_change_reporting_unit(thread_id):
    thread = message_controllers.get_conversation(thread_id)
    reporting_units = get_respondent_enrolments_from_thread(thread)

    breadcrumbs = [{"text": "Messages", "url": "/messages"}, {"text": "Filter by survey"}]

    return render_template(
        "secure-message/change-reporting-unit.html",
        thread=thread,
        thread_id=thread_id,
        breadcrumbs=breadcrumbs,
        reporting_units=reporting_units,
    )


@messages_bp.route("/threads/<thread_id>/change-reporting-unit", methods=["POST"])
@login_required
def post_change_reporting_unit(thread_id):  # noqa: C901
    thread = message_controllers.get_conversation(thread_id)
    reporting_unit = request.form.get("reporting-units")
    if reporting_unit:
        message_patch_payload = {"business_id": reporting_unit}

        # You can come to this page after changing a thread category to SURVEY, so we'll add the survey_id to
        # the message patch
        survey_shortname = session.get("secure-message-change-survey-shortname")
        if survey_shortname:
            survey_id = survey_controllers.get_survey_id_by_short_name(survey_shortname)
            message_patch_payload["survey_id"] = survey_id

        # Patch messages first. It's the most 'risky' as it does multiple calls
        for message in thread["messages"]:
            message_id = message["msg_id"]
            try:
                message_controllers.patch_message(message_id, message_patch_payload)
            except ApiError:
                flash("Something went wrong updating the survey.  Please try again.", category="error")
                return redirect(url_for("messages_bp.get_change_reporting_unit", thread_id=thread_id))

        flash("The survey has been successfully updated.")

        # Next, if there a survey_id in the session, patch the category to SURVEY as that's the only thing
        # it can be
        if survey_shortname:
            payload = {"category": "SURVEY"}
            try:
                message_controllers.patch_thread(thread_id, payload)
            except ApiError:
                flash("Something went wrong updating the category. Please try again.", category="error")
                return redirect(url_for("messages_bp.get_change_thread_category", thread_id=thread_id))
            flash("The category has been successfully updated")
            del session["secure-message-change-survey-shortname"]

        return redirect(url_for("messages_bp.view_select_survey"))

    flash("An option must be selected", category="error")
    reporting_units = get_respondent_enrolments_from_thread(thread)
    breadcrumbs = [{"text": "Messages", "url": "/messages"}, {"text": "Filter by survey"}]

    return render_template(
        "secure-message/change-reporting-unit.html",
        thread=thread,
        thread_id=thread_id,
        breadcrumbs=breadcrumbs,
        reporting_units=reporting_units,
    )


def get_respondent_enrolments_from_thread(thread: dict) -> list[dict]:
    if thread["messages"][0]["from_internal"]:
        party_id = thread["messages"][0]["msg_to"][0]
    else:
        party_id = thread["messages"][0]["msg_from"]
    respondent = party_controller.get_respondent_by_party_id(party_id)
    enrolments = party_controller.get_respondent_enrolments(respondent)
    reporting_units = [enrolment["business"] for enrolment in enrolments]
    return reporting_units


@messages_bp.route("/mark_unread/<message_id>", methods=["GET"])
@login_required
def mark_message_unread(message_id):
    msg_from = request.args.get("from", default="", type=str)
    msg_to = request.args.get("to", default="", type=str)
    conversation_tab = request.args.get("conversation_tab")
    ru_ref_filter = request.args.get("ru_ref_filter")
    business_id_filter = request.args.get("business_id_filter")
    flash(f"Message from {msg_from} to {msg_to} marked unread")
    message_controllers.add_unread_label(message_id)

    return _view_select_survey(conversation_tab, ru_ref_filter, business_id_filter)


@messages_bp.route("/", methods=["GET"])
@login_required
def view_select_survey():
    return _view_select_survey(
        request.args.get("conversation_tab"), request.args.get("ru_ref_filter"), request.args.get("business_id_filter")
    )


def _view_select_survey(conversation_tab, ru_ref_filter, business_id_filter):
    """
    Redirects to either a survey stored in the session under the 'messages_survey_selection'
    key or to the survey selection screen if the key isn't present in the session
    """
    try:
        selected_survey = session["messages_survey_selection"]
    except KeyError:
        return redirect(url_for("messages_bp.select_inbox"))

    if selected_survey == "technical":
        return redirect(
            url_for(
                "messages_bp.view_technical_inbox",
                page=request.args.get("page"),
                conversation_tab=conversation_tab,
                ru_ref_filter=ru_ref_filter,
                business_id_filter=business_id_filter,
            )
        )
    elif selected_survey == "misc":
        return redirect(
            url_for(
                "messages_bp.view_misc_inbox",
                page=request.args.get("page"),
                conversation_tab=conversation_tab,
                ru_ref_filter=ru_ref_filter,
                business_id_filter=business_id_filter,
            )
        )
    else:
        return redirect(
            url_for(
                "messages_bp.view_selected_survey",
                selected_survey=selected_survey,
                page=request.args.get("page"),
                conversation_tab=conversation_tab,
                ru_ref_filter=ru_ref_filter,
                business_id_filter=business_id_filter,
            )
        )


@messages_bp.route("/select-survey", methods=["GET", "POST"])
@login_required
def select_inbox():
    response_error = None
    if request.method == "POST":
        inbox = request.form.get("inbox-radio")
        if inbox == "technical":
            return redirect(url_for("messages_bp.view_technical_inbox"))
        if inbox == "surveys":
            selected_survey = request.form.get("select-survey")
            if selected_survey:
                return redirect(url_for("messages_bp.view_selected_survey", selected_survey=selected_survey))
            else:
                response_error = "Select a survey sub-selection for survey inbox"
        else:
            response_error = "Select an inbox"
        if inbox == "misc":
            return redirect(url_for("messages_bp.view_misc_inbox"))

    breadcrumbs = [{"text": "Messages", "url": "/messages"}, {"text": "Filter by survey"}]

    survey_list = get_grouped_surveys_list()

    return render_template(
        "message-select-survey.html", breadcrumbs=breadcrumbs, response_error=response_error, survey_list=survey_list
    )


@messages_bp.route("/clear_filter/<selected_survey>", methods=["GET"])
@login_required
def clear_filter(selected_survey):
    """Clear ru_ref filter by not passing it to view selected survey"""
    return redirect(
        url_for(
            "messages_bp.view_selected_survey",
            selected_survey=selected_survey,
            page=request.args.get("page"),
            conversation_tab=request.args["conversation_tab"],
        )
    )


@messages_bp.route("/technical", methods=["GET", "POST"])
@login_required
def view_technical_inbox():  # noqa: C901
    session["messages_survey_selection"] = "technical"
    breadcrumbs = [{"text": "Technical" + " Messages"}]
    return _process_non_survey_category_page(
        render_html="secure-message/technical-inbox.html",
        redirect_url="messages_bp.view_technical_inbox",
        breadcrumbs=breadcrumbs,
        category="TECHNICAL",
    )


@messages_bp.route("/<selected_survey>", methods=["GET", "POST"])
@login_required
def view_selected_survey(selected_survey):  # noqa: C901
    displayed_short_name = format_short_name(selected_survey)
    session["messages_survey_selection"] = selected_survey
    breadcrumbs = [{"text": displayed_short_name + " Messages"}]

    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    conversation_tab = request.args.get("conversation_tab", default="open")
    ru_ref_filter = request.args.get("ru_ref_filter", default="")
    business_id_filter = request.args.get("business_id_filter", default="")
    category = "SURVEY"

    try:
        if selected_survey == "FDI":
            survey_id = _get_FDI_survey_id()
        elif selected_survey == "Vacancies":
            survey_id = _get_vacancies_survey_ids()
        else:
            survey_id = _get_survey_id(selected_survey)

        form = SecureMessageRuFilterForm()

        if form.validate_on_submit():
            new_ru_ref = form.ru_ref_filter.data
            if new_ru_ref and new_ru_ref != ru_ref_filter:
                business_id_filter, ru_resolution_error = _try_get_party_id_from_filter_ru(new_ru_ref)
                if business_id_filter:
                    ru_ref_filter = new_ru_ref
                else:
                    ru_ref_filter = ""
                    flash(ru_resolution_error)

        form.ru_ref_filter.data = ru_ref_filter

        tab_counts = _get_tab_counts(business_id_filter, conversation_tab, ru_ref_filter, survey_id, category)

        # If the page is higher than possible, redirect users to the highest possible page.
        recalculated_page = _verify_requested_page_is_within_bounds(page, limit, tab_counts["current"])
        if recalculated_page != page:
            return redirect(
                url_for(
                    "messages_bp.view_selected_survey",
                    conversation_tab=conversation_tab,
                    selected_survey=selected_survey,
                    page=recalculated_page,
                    ru_ref_filter=ru_ref_filter,
                    business_id_filter=business_id_filter,
                )
            )

        messages = [
            _refine(message)
            for message in message_controllers.get_thread_list(
                survey_id, business_id_filter, conversation_tab, page, limit, category
            )
        ]

        pagination = _get_pagination_object(page, limit, tab_counts)

        return render_template(
            "messages.html",
            form=form,
            page=page,
            breadcrumbs=breadcrumbs,
            messages=messages,
            selected_survey=selected_survey,
            displayed_short_name=displayed_short_name,
            pagination=pagination,
            change_survey=True,
            conversation_tab=conversation_tab,
            business_id_filter=business_id_filter,
            ru_ref_filter=ru_ref_filter,
            tab_titles=_get_tab_titles(tab_counts, ru_ref_filter),
        )

    except (TypeError, KeyError):
        logger.error("Failed to retrieve messages", exc_info=True)
        return render_template(
            "messages.html",
            form=form,
            breadcrumbs=breadcrumbs,
            selected_survey=selected_survey,
            displayed_short_name=displayed_short_name,
            response_error=True,
            tab_titles=_get_tab_titles(),
        )


def _get_tab_titles(all_tab_titles=None, ru_ref_filter=None):
    """Populates a dictionary of tab titles for display. Needed because the titles can vary by message count.
    The name of the title (open, closed etc) is used as a key to a dictionary that looks up the displayed title
    which may include counts. This simplifies selection of the highlighted tab in the html"""

    tab_titles = {"my messages": "My messages", "open": "Open", "closed": "Closed", "initial": "Initial"}

    if ru_ref_filter:
        for key, value in tab_titles.items():
            tab_titles[key] = f"{value} ({all_tab_titles[key]})"
    return tab_titles


def _get_tab_counts(business_id_filter, conversation_tab, ru_ref_filter, survey_id, category) -> dict:
    """gets the thread count for either the current conversation tab, or, if the ru_ref_filter is active it returns
    the current conversation tab and all other tabs. i.e the value for the 'current' tab is always populated.
    Calls two different secure message endpoints depending on if ru_ref_filter is set
    as the get all is more expensive"""
    if ru_ref_filter:
        return message_controllers.get_all_conversation_type_counts(
            survey_id=survey_id, conversation_tab=conversation_tab, business_id=business_id_filter, category=category
        )

    thread_count = message_controllers.get_conversation_count(
        survey_id=survey_id, business_id=business_id_filter, conversation_tab=conversation_tab, category=category
    )
    return {"current": thread_count}


@messages_bp.route("/threads/<thread_id>/close-conversation", methods=["GET", "POST"])
@login_required
def close_conversation(thread_id):
    if not user_has_permission("messages.edit"):
        raise NoPermissionError("messages.edit")
    conversation_tab = request.args.get("conversation_tab")
    page = request.args.get("page")
    ru_ref_filter = request.args.get("ru_ref_filter")
    business_id_filter = request.args.get("business_id_filter")
    category = request.args.get("category")

    if request.method == "POST":
        payload = {"is_closed": True}
        message_controllers.patch_thread(thread_id, payload)
        thread_url = (
            url_for(
                "messages_bp.view_conversation",
                thread_id=thread_id,
                conversation_tab=conversation_tab,
                page=page,
                ru_ref_filter=ru_ref_filter,
                business_id_filter=business_id_filter,
            )
            + "#latest-message"
        )

        flash(Markup(f"Conversation closed. <a href={thread_url}>View conversation</a>"))
        return redirect(
            url_for(
                "messages_bp.view_select_survey",
                page=request.args.get("page"),
                conversation_tab=conversation_tab,
                ru_ref_filter=ru_ref_filter,
                business_id_filter=business_id_filter,
            )
        )

    thread_conversation = message_controllers.get_conversation(thread_id)
    last_message = _refine(thread_conversation["messages"][-1])
    respondent_key = "to" if last_message["internal"] else "from"
    respondent = last_message[respondent_key]

    return render_template(
        "close-conversation.html",
        subject=last_message["subject"],
        business=last_message["business_name"],
        ru_ref=last_message["ru_ref"],
        respondent=respondent,
        thread_id=thread_id,
        page=page,
        conversation_tab=conversation_tab,
        ru_ref_filter=ru_ref_filter,
        business_id_filter=business_id_filter,
        category=category,
    )


@messages_bp.route("/miscellaneous", methods=["GET", "POST"])
@login_required
def view_misc_inbox():  # noqa: C901
    session["messages_survey_selection"] = "misc"
    breadcrumbs = [{"text": "Miscellaneous" + " Messages"}]
    return _process_non_survey_category_page(
        render_html="secure-message/misc-inbox.html",
        redirect_url="messages_bp.view_misc_inbox",
        breadcrumbs=breadcrumbs,
        category="MISC",
    )


def _get_pagination_object(page, limit, tab_counts) -> Pagination:
    return Pagination(
        page=page,
        per_page=limit,
        total=tab_counts["current"],
        record_name="messages",
        prev_label="Previous",
        next_label="Next",
        outer_window=0,
        format_total=True,
        format_number=True,
    )


def _try_get_party_id_from_filter_ru(ru_ref: str):
    """Attempts to get party by the ru_ref entered in the UI as an ru to filter by.
    Not finding a party is not an error, since the user may have entered anything.
    If party returns a 404 it returns an unknown ru message, else returns a message assuming party unresponsive
    or erroring. No exceptions raised in this case since get_by_party_ref logs errors, and raising another error to the
    user adds no value, so we display a message on the UI and carry on.
    """
    try:
        response = party_controller.get_business_by_ru_ref(ru_ref)
        return response["id"], ""

    except ApiError as api_error:  # If error, select a message for the UI
        if api_error.status_code == 404:
            ru_resolution_error = f"Filter not applied: {ru_ref} is an unknown RU ref"
        else:
            ru_resolution_error = "Could not resolve RU ref, please try again later"

    return "", ru_resolution_error


def _format_closed_at(thread_conversation):
    """
    Takes a date and formats converts it into the string 'dd/mm/yyyy at HH:MM'
    """
    try:
        closed_time = localise_datetime(datetime.strptime(thread_conversation["closed_at"], "%Y-%m-%dT%H:%M:%S.%f"))
        return closed_time.strftime("%d/%m/%Y" + " at %H:%M")
    except (KeyError, TypeError):
        return None


def _build_create_message_breadcrumbs():
    return [{"text": "Messages", "url": "/messages"}, {"text": "Create Message"}]


def _get_conversation_breadcrumbs(messages):
    try:
        return [{"text": "Messages", "url": "/messages"}, {"text": messages[-1].get("subject", "No Subject")}]
    except IndexError:
        return [{"text": "Messages", "url": "/messages"}, {"text": "Unavailable"}]


def _repopulate_form_with_submitted_data(form):
    form.survey_id.text = form.hidden_survey.data
    form.ru_ref.text = form.hidden_ru_ref.data
    form.business.text = form.hidden_business.data
    form.to.text = form.hidden_to.data
    form.body.data = g.form_body_data
    form.subject.data = g.form_subject_data
    return form


def _get_message_json(form, thread_id=""):
    return json.dumps(
        {
            "msg_from": current_user.id,
            "msg_to": [form.hidden_to_uuid.data],
            "subject": form.subject.data,
            "body": form.body.data,
            "thread_id": thread_id,
            "case_id": "",
            "survey_id": form.hidden_survey_id.data,
            "business_id": form.hidden_to_business_id.data,
        }
    )


def _get_non_survey_message_json(form, thread_id="", category=""):
    return json.dumps(
        {
            "msg_from": current_user.id,
            "msg_to": [form.hidden_to_uuid.data],
            "subject": form.subject.data,
            "body": form.body.data,
            "thread_id": thread_id,
            "category": category,
        }
    )


def _populate_hidden_form_fields_from_post(current_view_form: SecureMessageForm, calling_form):
    """
    :param current_view_form: is the form just create when land in the view
    :param calling_form: is the form that is actually sent from the caller
    :return: a form with all the hidden data filled in.
    """
    try:
        current_view_form.hidden_survey.data = calling_form["survey"]
        current_view_form.hidden_survey_id.data = calling_form["survey_id"]
        current_view_form.hidden_ru_ref.data = calling_form["ru_ref"]
        current_view_form.hidden_business.data = calling_form["business"]
        current_view_form.hidden_to_uuid.data = calling_form["msg_to"]
        current_view_form.hidden_to.data = calling_form["msg_to_name"]
        current_view_form.hidden_to_business_id.data = calling_form["business_id"]
    except KeyError as ex:
        logger.exception("Failed to load create message page")
        raise InternalError(ex)
    return current_view_form


def _populate_form_details_from_hidden_fields(form: SecureMessageForm) -> SecureMessageForm:
    form.survey_id.text = form.hidden_survey.data
    form.ru_ref.text = form.hidden_ru_ref.data
    form.business.text = form.hidden_business.data
    form.to.text = form.hidden_to.data
    return form


def _get_message_subject(thread: dict):
    try:
        subject = thread["subject"]
        subject = html.escape(subject)
        return subject
    except KeyError:
        logger.exception("Failed to retrieve Subject from thread")
        return None


def _refine(message: dict, category: str = "SURVEY") -> dict:
    """
    Refine a message into a cleaner version that can be more easily used by the display layer
    :param message: A message from secure-message
    """
    refined_message = {
        "thread_id": message.get("thread_id"),
        "subject": _get_message_subject(message),
        "body": message.get("body"),
        "internal": message.get("from_internal"),
        "username": _get_user_summary_for_message(message, category),
        "survey_id": message.get("survey_id"),
        "ru_ref": _get_ru_ref_from_message(message),
        "to_id": _get_to_id(message),
        "from_id": message.get("msg_from"),
        "business_name": _get_business_name_from_message(message),
        "from": _get_from_name(message),
        "to": _get_to_name(message),
        "sent_date": _get_human_readable_date(message.get("sent_date")),
        "unread": _get_unread_status(message),
        "message_id": message.get("msg_id"),
        "business_id": message.get("business_id"),
    }
    if message.get("@msg_from"):
        refined_message["from_email"] = message["@msg_from"].get("emailAddress")
    else:
        refined_message["from_email"] = ""
    if message.get("@msg_to"):
        refined_message["to_email"] = message["@msg_to"][0].get("emailAddress")
    else:
        refined_message["to_email"] = ""

    if message.get("from_internal"):
        refined_message["from_internal"] = message["from_internal"]
    else:
        refined_message["from_internal"] = False

    if message.get("survey_id"):
        refined_message["survey"] = get_survey_short_name_by_id(message.get("survey_id"))
        refined_message["survey_ref"] = get_survey_ref_by_id(message.get("survey_id"))
    else:
        refined_message["survey"] = ""
        refined_message["survey_ref"] = ""

    return refined_message


def _get_survey_id(selected_survey: str) -> list[str]:
    """
    Returns a survey_id from a survey shortname.

    :param selected_survey: A survey shortname (MBS, ASHE, etc)
    :returns: A list containing the single survey_id of the selected_survey.
    """

    return [survey_controllers.get_survey_id_by_short_name(selected_survey)]


def _get_FDI_survey_id() -> list[str]:
    """
    Returns a list of FDI survey ids.   This list is defined in the config

    :returns: A list of FDI survey_id's
    """
    return [survey_controllers.get_survey_id_by_short_name(fdi_survey) for fdi_survey in FDI_LIST]


def _get_vacancies_survey_ids() -> list[str]:
    """
    Returns a list of vacancies survey id's.   This list is defined in the config

    :returns: A list of vacancies survey_id's
    """
    return [survey_controllers.get_survey_id_by_short_name(vacancies_survey) for vacancies_survey in VACANCIES_LIST]


def _get_user_summary_for_message(message: dict, category: str) -> str:
    if message.get("from_internal"):
        return _get_from_name(message)
    elif category == "SURVEY":
        return f"{_get_from_name(message)} - {_get_ru_ref_from_message(message)}"
    else:
        return f"{_get_from_name(message)} - {_get_from_email_(message)}"


def _get_from_email_(message: dict) -> str:
    """
    Returns the email address of the from message
    :param message: a dict that represents a message
    :return: an string containing the email or an empty string
    """
    if message.get("@msg_from"):
        email = message["@msg_from"].get("emailAddress")
    else:
        email = ""
    return email


def _get_from_name(message):
    """
    Constructs a name from the @msg_from key of a message.  The value of the key needs to be a dict that contains
    a 'firstName' and 'lastName' key in order to have a name that isn't 'None None'.

    If the @msg_from key is missing, this will return the string 'Deleted respondent'

    :param message: A dict that represents a message
    :rtype: string
    """
    try:
        msg_from = message["@msg_from"]
        return f"{msg_from.get('firstName')} {msg_from.get('lastName')}"
    except KeyError:
        logger.info("Failed to retrieve message from name", message_id=message.get("msg_id"))
        return "Deleted respondent"


def _get_to_id(message: dict) -> str:
    try:
        return message.get("msg_to")[0]
    except (IndexError, TypeError):
        logger.error("No 'msg_to' in message.", message_id=message.get("msg_id"), exc_info=True)


def _get_to_name(message: dict) -> str:
    try:
        if message.get("msg_to")[0] == "GROUP":
            if message.get("survey_id") and get_survey_short_name_by_id(message.get("survey_id")):
                return f"{get_survey_short_name_by_id(message.get('survey_id'))} Team"
            return "ONS"
        return f"{message.get('@msg_to')[0].get('firstName')} {message.get('@msg_to')[0].get('lastName')}"
    except (IndexError, TypeError):
        logger.info("Failed to retrieve message to name", message_id=message.get("msg_id"))
        return "Deleted respondent"


def _get_ru_ref_from_message(message: dict) -> str:
    try:
        return message["@business_details"]["sampleUnitRef"]
    except (KeyError, TypeError):
        return ""


def _get_business_name_from_message(message: dict) -> str:
    try:
        return message["@business_details"]["name"]
    except (KeyError, TypeError):
        return ""


def _get_human_readable_date(sent_date: str) -> str:
    """
    Converts a datetime date (e.g., 2019-11-13 13:25:19.093378) and converts it into something
    easily read (e.g., Today at 13:25)
    """
    try:
        formatted_date = get_formatted_date(sent_date.split(".")[0])
        return formatted_date
    except (AttributeError, ValueError, IndexError, TypeError):
        logger.exception("Failed to parse sent date from message", sent_date=sent_date)


def _get_unread_status(message: dict) -> bool:
    return "UNREAD" in message.get("labels", [])


@messages_bp.after_request
def disable_caching(response):
    for k, v in CACHE_HEADERS.items():
        response.headers[k] = v
    return response


def _verify_requested_page_is_within_bounds(requested_page: int, limit: int, thread_count):
    """
    If the requested page number is too large in relation to number of threads per page (limit) and the total number
    of threads (thread_count), this will return the largest acceptable page number that can be used.

    If there are 0 total threads, this will return 1 as the first page is the only acceptable page.

    :param requested_page: Page number that is being requested
    :param limit: Number of threads per page
    :param thread_count: Total number of threads
    :return: The requested page number if it's within bounds, or the highest acceptable page number if it's too large
    """
    page = requested_page

    if thread_count == 0:
        page = 1
    elif page * limit > thread_count:
        page = math.ceil(thread_count / limit)

    return page


def _can_mark_as_unread(message: dict) -> bool:
    return message["to_id"] == "GROUP" or message["to_id"] == session["user_id"]


def _process_category_page(
    render_html: str,
    redirect_url: str,
    selected_survey: str,
    displayed_short_name: str,
    breadcrumbs: list,
    category: str,
):
    """
    This method processes message category selected and returns appropriate inbox.
    :param render_html:
    :param redirect_url:
    :param selected_survey:
    :param displayed_short_name:
    :param breadcrumbs:
    :param category:
    :return: Returns a response object
    :rtype: WSGI application
    """
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    conversation_tab = request.args.get("conversation_tab", default="open")
    ru_ref_filter = request.args.get("ru_ref_filter", default="")
    business_id_filter = request.args.get("business_id_filter", default="")
    category = category
    form = SecureMessageRuFilterForm()
    try:
        if form.validate_on_submit():
            new_ru_ref = form.ru_ref_filter.data
            if new_ru_ref and new_ru_ref != ru_ref_filter:
                business_id_filter, ru_resolution_error = _try_get_party_id_from_filter_ru(new_ru_ref)
                if business_id_filter:
                    ru_ref_filter = new_ru_ref
                else:
                    ru_ref_filter = ""
                    flash(ru_resolution_error)

        form.ru_ref_filter.data = ru_ref_filter

        tab_counts = _get_tab_counts(business_id_filter, conversation_tab, ru_ref_filter, None, category)

        # If the page is higher then possible, redirect users to the highest possible page.
        recalculated_page = _verify_requested_page_is_within_bounds(page, limit, tab_counts["current"])
        if recalculated_page != page:
            return redirect(
                url_for(
                    redirect_url,
                    conversation_tab=conversation_tab,
                    page=recalculated_page,
                    ru_ref_filter=ru_ref_filter,
                    business_id_filter=business_id_filter,
                )
            )

        messages = [
            _refine(message)
            for message in message_controllers.get_thread_list(
                None, business_id_filter, conversation_tab, page, limit, category
            )
        ]

        pagination = _get_pagination_object(page, limit, tab_counts)

        return render_template(
            render_html,
            form=form,
            page=page,
            breadcrumbs=breadcrumbs,
            messages=messages,
            selected_survey=selected_survey,
            pagination=pagination,
            conversation_tab=conversation_tab,
            business_id_filter=business_id_filter,
            ru_ref_filter=ru_ref_filter,
            tab_titles=_get_tab_titles(tab_counts, ru_ref_filter),
        )

    except (TypeError, KeyError):
        logger.error("Failed to retrieve messages", exc_info=True)
        return render_template(
            render_html,
            form=form,
            breadcrumbs=breadcrumbs,
            selected_survey=selected_survey,
            displayed_short_name=displayed_short_name,
            response_error=True,
            tab_titles=_get_tab_titles(),
        )


def _process_non_survey_category_page(
    render_html: str,
    redirect_url: str,
    breadcrumbs: list,
    category: str,
):
    """
    This method processes message category selected and returns appropriate inbox.
    :param render_html:
    :param redirect_url:
    :param breadcrumbs:
    :param category:
    :return: Returns a response object
    :rtype: WSGI application
    """
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)
    conversation_tab = request.args.get("conversation_tab", default="open")
    category = category
    try:
        tab_counts = _get_tab_counts("", conversation_tab, "", None, category)

        # If the page is higher then possible, redirect users to the highest possible page.
        recalculated_page = _verify_requested_page_is_within_bounds(page, limit, tab_counts["current"])
        if recalculated_page != page:
            return redirect(
                url_for(
                    redirect_url,
                    conversation_tab=conversation_tab,
                    page=recalculated_page,
                )
            )

        messages = [
            _refine(message)
            for message in message_controllers.get_thread_list(None, "", conversation_tab, page, limit, category)
        ]
        pagination = _get_pagination_object(page, limit, tab_counts)

        return render_template(
            render_html,
            page=page,
            breadcrumbs=breadcrumbs,
            messages=messages,
            pagination=pagination,
            conversation_tab=conversation_tab,
            tab_titles=_get_tab_titles(tab_counts, ""),
        )

    except (TypeError, KeyError):
        logger.error("Failed to retrieve messages", exc_info=True)
        return render_template(
            render_html,
            breadcrumbs=breadcrumbs,
            response_error=True,
            tab_titles=_get_tab_titles(),
        )
