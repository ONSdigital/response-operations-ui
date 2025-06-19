import logging
from datetime import datetime, timezone

from iso8601 import parse_date
from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def get_collection_exercise_by_period(exercises, period):
    for exercise in exercises:
        if exercise["exerciseRef"] == period:
            return exercise


def get_current_collection_exercise(collection_exercises):  # noqa: C901
    """
    Figures out what the most 'current' collection exercise is from a list of them.
    This is done with the following 4 steps:
      - If there are no collection exercises, return an empty dict
      - Search for the nearest to today past scheduledStartDateTime in LIVE, READY FOR LIVE and ENDED state.
      - If there are none in the past, search for the nearest scheduledStartDateTime in the future
      - Finally, if nothing has been found then return an empty dict as none of the collection exercises
        have been set up properly
    Note:  If there are 2 collection exercises scheduled to start at the same time then it will display the first one
    it comes across.
    The reason we care about the state in the exercises in
    the past, but not in the future, is because if there are exercises in the past then they're likely to be set up
    correctly and give us useful information.  If there are none with a start date the past then it's likely that
    this is a new survey, and we just want whatever information we can get.

    Additionally, the responses dashboard doesn't handle not fully set up collection exercises too well, so we can
    try and save the user from giving them a dashboard link that won't work. Note:  If there are 2
    collection exercises scheduled to start at the same time then it will display the first one it comes across.

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
        start_date = collection_exercise.get("scheduledStartDateTime")
        if start_date is None:
            continue
        delta = (parse_date(start_date) - now).total_seconds()
        state = collection_exercise.get("state")
        if delta < 0 and state in {"READYFORLIVE", "LIVE", "ENDED"}:
            if closest_time_delta == 0 or delta > closest_time_delta:
                closest_time_delta = delta
                closest_collection_exercise = collection_exercise

    # If it's empty then there aren't any in progress and we find the nearest one that's going to start
    if not closest_collection_exercise:
        for collection_exercise in collection_exercises:
            start_date = collection_exercise.get("scheduledStartDateTime")
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

    logger.info(
        "About to return most current collection exercise",
        collection_exercise_id=closest_collection_exercise["id"],
        exercise_ref=closest_collection_exercise.get("exerciseRef"),
        user_description=closest_collection_exercise.get("userDescription"),
    )
    return closest_collection_exercise


def get_nearest_future_key_date(events):
    """
    Takes a list of events (key dates) from a collection exercise and returns the nearest future event.

    :param events: A list of dictionaries representing events for a collection exercise
    :type events: list
    :return: The dictionary with the event in the future closest to today
    :rtype: dict
    """
    if not events:
        return {}

    # These are returned as events in a collection exercise, but aren't key dates.
    excluded_events = ["ref_period_start", "ref_period_end", "employment"]
    now = datetime.now(timezone.utc)
    closest_time_delta = 0
    closest_key_date = {}

    for event in events:
        if event["tag"] in excluded_events:
            continue
        timestamp = event.get("timestamp")
        if timestamp is None:
            continue
        delta = (parse_date(timestamp) - now).total_seconds()
        # A delta greater than 0 indicates a future date
        if delta > 0:
            # If the delta is 0 (it's the first one) or if this one is smaller then the closest one we've found so far
            # (smaller delta indicates a date closer to today) then we say this is the new nearest event
            if closest_time_delta == 0 or delta < closest_time_delta:
                closest_time_delta = delta
                closest_key_date = event

    # We either found one, or there were none in the future, so we return an empty dict.
    return closest_key_date


def build_eq_ci_selectors(
    eq_ci_selectors: list[dict], collection_instruments: list[dict], ci_versions: list[dict]
) -> list[dict]:
    """
    Builds a list of available eQ collection instruments for a collection exercise,
    marking those already linked as checked and attaching their ci_version if available.

    :param eq_ci_selectors: Available eQ CIs for the survey
    :param collection_instruments: CIs already linked to the collection exercise
    :param ci_versions: CI version info, keyed by form_type
    :return: List of CIs enriched with 'checked' and 'ci_version' values
    """
    ci_version_lookup = {ci["form_type"]: ci.get("ci_version") for ci in ci_versions}
    linked_ids = {ci["id"] for ci in collection_instruments}

    return [
        {
            "id": eq_ci["id"],
            "form_type": eq_ci["classifiers"]["form_type"],
            "checked": "true" if eq_ci["id"] in linked_ids else "false",
            "ci_version": ci_version_lookup.get(eq_ci["classifiers"]["form_type"]),
        }
        for eq_ci in eq_ci_selectors
    ]
