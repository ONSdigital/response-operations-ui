import logging

from flask import abort, redirect, render_template, request, url_for
from flask_login import login_required
import iso8601
from structlog import wrap_logger

from response_operations_ui.common.filters import get_collection_exercise_by_period
from response_operations_ui.common.mappers import convert_events_to_new_format
from response_operations_ui.views.collection_exercise import collection_exercise_bp, get_event_name
from response_operations_ui.controllers import collection_exercise_controllers, survey_controllers
from response_operations_ui.forms import EventDateForm


logger = wrap_logger(logging.getLogger(__name__))


@collection_exercise_bp.route('/<short_name>/<period>/event/<tag>', methods=['GET'])
@login_required
def update_event_date(short_name, period, tag, errors=None):
    errors = request.args.get('errors') if not errors else errors
    survey = survey_controllers.get_survey_by_shortname(short_name)
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey['id'])
    exercise = get_collection_exercise_by_period(exercises, period)
    if not exercise:
        logger.error('Failed to find collection exercise by period',
                     short_name=short_name, period=period)
        abort(404)
    events = collection_exercise_controllers.get_collection_exercise_events_by_id(exercise['id'])
    event_name = get_event_name(tag)
    formatted_events = convert_events_to_new_format(events)
    date_restriction_text = _get_date_restriction_text(tag, formatted_events)

    try:
        event = formatted_events[tag]
    except KeyError:
        form = EventDateForm()
    else:
        form = EventDateForm(day=event['date'][:2],
                             month=event['month'],
                             year=event['date'][-4:],
                             hour=event['time'][:2],
                             minute=event['time'][2:4])

    return render_template('update-event-date.html',
                           form=form,
                           ce=exercise,
                           survey=survey,
                           event_name=event_name,
                           date_restriction_text=date_restriction_text,
                           errors=errors)


@collection_exercise_bp.route('/<short_name>/<period>/event/<tag>', methods=['POST'])
@login_required
def update_event_date_submit(short_name, period, tag):
    form = EventDateForm(form=request.form)

    survey = survey_controllers.get_survey_by_shortname(short_name)
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey['id'])
    exercise = get_collection_exercise_by_period(exercises, period)
    if not exercise:
        logger.error('Failed to find collection exercise by period',
                     short_name=short_name, period=period)
        abort(404)

    if not form.validate():
        return update_event_date(short_name, period, tag, errors=form.errors)

    day = form.day.data if not len(form.day.data) == 1 else f"0{form.day.data}"
    timestamp_string = f"{form.year.data}{form.month.data}{day}T{form.hour.data}{form.minute.data}"
    timestamp = iso8601.parse_date(timestamp_string)
    if not collection_exercise_controllers.update_event(exercise['id'], tag, timestamp):
        return redirect(url_for('collection_exercise_bp.update_event_date',
                                short_name=short_name, period=period, tag=tag, errors=True))

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            short_name=short_name, period=period))


def _get_date_restriction_text(tag, events):
    date_restriction_text = {
        "mps": [f"Must be before Go Live {_get_event_date_string('go_live', events)}"],
        "go_live": [f"Must be after MPS {_get_event_date_string('mps', events)}",
                    f"Must be before Return by {_get_event_date_string('return_by', events)}"],
        "return_by": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                      f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "exercise_end": [f"Must be after Return by {_get_event_date_string('return_by', events)}"],
        "reminder": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                     f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "reminder2": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                      f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "reminder3": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                      f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "ref_period_start": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                             f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"],
        "ref_period_end": [f"Must be after Go Live {_get_event_date_string('go_live', events)}",
                           f"Must be before Exercise end {_get_event_date_string('exercise_end', events)}"]
    }
    return date_restriction_text[tag]


def _get_event_date_string(tag, events):
    return f"{events[tag]['day']} {events[tag]['date']} {events[tag]['time']}"
