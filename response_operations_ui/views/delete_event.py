import logging
from datetime import datetime

from dateutil import tz
from flask import abort, redirect, render_template, request, url_for, flash
from flask_login import login_required
from structlog import wrap_logger
from wtforms import ValidationError

from response_operations_ui.common.date_restriction_generator import get_date_restriction_text
from response_operations_ui.common.filters import get_collection_exercise_by_period
from response_operations_ui.common.mappers import convert_events_to_new_format
from response_operations_ui.common.validators import valid_date_for_event
from response_operations_ui.controllers import collection_exercise_controllers, survey_controllers
from response_operations_ui.forms import EventDateForm
from response_operations_ui.views.collection_exercise import collection_exercise_bp, get_event_name

logger = wrap_logger(logging.getLogger(__name__))


@collection_exercise_bp.route('/<short_name>/<period>/event/<tag>/', methods=['DELETE'])
@login_required
def delete_event(short_name, period, tag):
    survey_id = survey_controllers.get_survey_id_by_short_name(short_name)
    exercises = collection_exercise_controllers.get_collection_exercises_by_survey(survey_id)
    exercise = get_collection_exercise_by_period(exercises, period)

    if not exercise:
        logger.error('Failed to find collection exercise to delete',
                     short_name=short_name, period=period)
        abort(404)

    """Attempts to create the event, returns None if success or returns an error message upon failure."""
    error_message = collection_exercise_controllers.delete_event(
        collection_exercise_id=exercise['id'], tag=tag)

    if error_message:
        flash(error_message, 'error')
        return redirect(url_for('collection_exercise_bp.update_event_date',
                                short_name=short_name, period=period, tag=tag))

    return redirect(url_for('collection_exercise_bp.view_collection_exercise',
                            short_name=short_name, period=period, success_panel='Event deleted.'))
