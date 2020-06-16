from datetime import datetime, timezone
import logging

from iso8601 import parse_date
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def get_collection_exercise_by_period(exercises, period):
    for exercise in exercises:
        if exercise['exerciseRef'] == period:
            return exercise


def get_current_collection_exercise(collection_exercises):  # noqa: C901
    """
    Figures out what the most 'current' collection exercise is from a list of them.
    This is done with the following 4 steps:
      - If there are no collection exercises, return an empty dict
      - Search for the nearest to today past scheduledStartDateTime.
      - If there are none in the past, search for the nearest scheduledStartDateTime in the future
      - Finally, if nothing has been found then return an empty dict as none of the collection exercises
        have been set up properly
    Note:  If there are 2 collection exercises scheduled to start at the same time then it will display the first one
    it comes across.

    :param collection_exercises: A dictionary containing collection exercises for a survey
    :type collection_exercises: list
    :return: A dictionary with the most 'current' collection exercise
    :rtype: dict
    """
    if len(collection_exercises) == 0:
        return {}

    # Find the most recent one in the past
    now = datetime.now(timezone.utc)
    closest_time_delta = 0
    closest_collection_exercise = None
    for collection_exercise in collection_exercises:
        start_date = collection_exercise.get('scheduledStartDateTime')
        if start_date is None:
            continue
        delta = (parse_date(start_date) - now).total_seconds()
        if delta < 0:
            if closest_time_delta == 0 or delta > closest_time_delta:
                closest_time_delta = delta
                closest_collection_exercise = collection_exercise

    # If it's empty then there aren't any in progress and we find the nearest one that's going to start
    if not closest_collection_exercise:
        for collection_exercise in collection_exercises:
            start_date = collection_exercise.get('scheduledStartDateTime')
            if start_date is None:
                continue
            delta = (parse_date(start_date) - now).total_seconds()
            if delta > 0:
                if closest_time_delta == 0 or delta < closest_time_delta:
                    closest_time_delta = delta
                    closest_collection_exercise = collection_exercise

    # If we didn't find a nearest one in the past or future and list isn't empty then none of the collection exercises
    # have been set up properly and we'll just return nothing.
    if not closest_collection_exercise:
        return {}

    logger.info("About to return most current collection exercise",
                collection_exercise_id=closest_collection_exercise['id'])
    return closest_collection_exercise
