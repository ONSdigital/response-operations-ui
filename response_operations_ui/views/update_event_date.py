import logging
from datetime import datetime

from dateutil import tz
from flask import abort, redirect, render_template, request, url_for, flash
from flask_login import login_required
from wtforms import ValidationError

from structlog import wrap_logger
from structlog.processors import JSONRenderer

from response_operations_ui.common.date_restriction_generator import get_date_restriction_text
from response_operations_ui.common.filters import get_collection_exercise_by_period
from response_operations_ui.common.mappers import convert_events_to_new_format
from response_operations_ui.common.validators import valid_date_for_event
from response_operations_ui.controllers import collection_exercise_controllers, survey_controllers
from response_operations_ui.forms import EventDateForm
from response_operations_ui.views.collection_exercise import collection_exercise_bp, get_event_name

logger = wrap_logger(logging.getLogger(__name__),
                     processors=[JSONRenderer(indent=1, sort_keys=True)])


@collection_exercise_bp.route('/<short_name>/<period>/event/<tag>', methods=['GET'])
@login_required
def update_event_date(short_name, period, tag):
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
    date_restriction_text = get_date_restriction_text(tag, formatted_events)

    try:
        event = formatted_events[tag]

        form = EventDateForm(day=event['date'][:2],
                             month=event['month'],
                             year=event['date'][-4:],
                             hour=event['time'][:2],
                             minute=event['time'][3:5])

    except KeyError:
        form = EventDateForm()

    return render_template('update-event-date.html',
                           form=form,
                           ce=exercise,
                           period=period,
                           survey=survey,
                           event_name=event_name,
                           date_restriction_text=date_restriction_text)


@collection_exercise_bp.route('/<short_name>/<period>/event/<tag>', methods=['POST'])
@login_required
def update_event_date_submit(short_name, period, tag):
    form = EventDateForm(form=request.form)

    if not form.validate():
        flash('Please enter a valid value', 'error')
        return redirect(url_for('collection_exercise_bp.update_event_date',
                                short_name=short_name, period=period, tag=tag))

    try:
        valid_date_for_event(tag, form)
    except ValidationError as exception:
        flash(exception, 'error')
        return redirect(url_for('collection_exercise_bp.update_event_date',
                                short_name=short_name, period=period, tag=tag))

    survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)
    exercise = get_collection_exercise_by_period(exercises, period)
    if not exercise:
        logger.error('Failed to find collection exercise by period',
                     short_name=short_name, period=period)
        abort(404)

    submitted_dt = datetime(year=int(form.year.data),
                            month=int(form.month.data),
                            day=int(form.day.data),
                            hour=int(form.hour.data),
                            minute=int(form.minute.data),
                            tzinfo=tz.gettz('Europe/London'))

    """Attempts to create the event, returns None if success or returns an error message upon failure."""
    error_message = collection_exercise_controllers.update_event(
        collection_exercise_id=exercise['id'], tag=tag, timestamp=submitted_dt)

    if error_message:
        flash(error_message, 'error')
        return redirect(url_for('collection_exercise_bp.update_event_date',
                                short_name=short_name, period=period, tag=tag))

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            short_name=short_name, period=period, success_panel='Event date updated.'))
