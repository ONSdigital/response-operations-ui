import iso8601
import logging

from flask import redirect, render_template, request, url_for
from flask_login import login_required
from structlog import wrap_logger

from response_operations_ui.common.mappers import convert_events_to_new_format
from response_operations_ui.controllers import collection_exercise_controllers
from response_operations_ui.forms import UpdateEventDateForm
from response_operations_ui.views.collection_exercise import collection_exercise_bp


logger = wrap_logger(logging.getLogger(__name__))


@collection_exercise_bp.route('/<short_name>/<period>/event/<tag>', methods=['GET'])
@login_required
def update_event_date(short_name, period, tag, errors=None):
    errors = request.args.get('errors') if not errors else errors
    ce_details = collection_exercise_controllers.get_collection_exercise_event_page_info(short_name, period)
    event_name = _get_event_name(tag)
    formatted_events = convert_events_to_new_format(ce_details['events'])
    date_restriction_text = _get_date_restriction_text(tag, formatted_events)

    form = UpdateEventDateForm(day=formatted_events[tag]['date'][:2],
                               month=formatted_events[tag]['month'],
                               year=formatted_events[tag]['date'][-4:],
                               hour=formatted_events[tag]['time'][:2],
                               minute=formatted_events[tag]['time'][2:4])
    return render_template('update-event-date.html',
                           form=form,
                           ce=ce_details['collection_exercise'],
                           survey=ce_details['survey'],
                           event_name=event_name,
                           event_date=formatted_events[tag],
                           date_restriction_text=date_restriction_text,
                           errors=errors)


@collection_exercise_bp.route('/<short_name>/<period>/event/<tag>', methods=['POST'])
@login_required
def update_event_date_submit(short_name, period, tag):
    form = UpdateEventDateForm(form=request.form)

    if not form.validate():
        return update_event_date(short_name, period, tag, errors=form.errors)

    day = form.day.data if not len(form.day.data) == 1 else f"0{form.day.data}"
    timestamp_string = f"{form.year.data}{form.month.data}{day}T{form.hour.data}{form.minute.data}"
    timestamp = iso8601.parse_date(timestamp_string)
    updated = collection_exercise_controllers.update_event(short_name, period, tag, timestamp)
    if not updated:
        return redirect(url_for('collection_exercise_bp.update_event_date',
                                short_name=short_name, period=period, tag=tag, errors=True))

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            short_name=short_name, period=period))


def _get_event_name(tag):
    event_names = {
        "mps": "Main print selection",
        "go_live": "Go Live",
        "return_by": "Return by",
        "exercise_end": "Exercise end"
    }
    return event_names.get(tag)


def _get_date_restriction_text(tag, events):
    date_restriction_text = {
        "mps": [f"Must be before Go Live {_get_event_date_string('go_live', events)}"],
        "go_live": [f"Must be after MPS {_get_event_date_string('mps', events)}",
                    f"Must be before Return by {_get_event_date_string('return_by', events)}"],
        "return_by": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                      f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "exercise_end": [f"Must be after Return by {_get_event_date_string('return_by', events)}"]
    }
    return date_restriction_text[tag]


def _get_event_date_string(tag, events):
    return f"{events[tag]['day']} {events[tag]['date']} {events[tag]['time']}"
