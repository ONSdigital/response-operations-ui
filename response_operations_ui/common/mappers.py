import re
from datetime import datetime, timezone

import iso8601

from response_operations_ui.common.dates import localise_datetime


def format_short_name(short_name):
    """
    This regex function returns a pretty-printed short name value WITH spaces
    e.g. Sand&Gravel -> Sand & Gravel
    """
    return re.sub('(&)', r' \1 ', short_name)


def convert_events_to_new_format(events):
    formatted_events = {}
    for event in events:
        date_time_utc = iso8601.parse_date(event['timestamp'])
        localised_datetime = localise_datetime(date_time_utc)
        formatted_events[event['tag']] = {
            "day": localised_datetime.strftime('%A'),
            "date": localised_datetime.strftime('%d %b %Y'),
            "month": localised_datetime.strftime('%m'),
            "time": localised_datetime.strftime('%H:%M'),
            "is_in_future": date_time_utc > iso8601.parse_date(datetime.now(timezone.utc).isoformat())
        }
    return formatted_events


def convert_event_list_to_dictionary(events):
    """
    This function converts a list of events, which are dicts, for a collection exercise into a dictionary where
    the key is the name of the event and the value is the timestamp.
    This can aid in finding the exact event you want without having to loop through the
    entire list to find the one you want.

    :param events: A list of events for a collection exercise
    :raises KeyError: If the 'tag' or 'timestamp' keys aren't present in the list of dicts
    :return: A dictionary of events where the name of the events are the keys and the values are the timestamps
    """
    if events is None:
        return {}
    return {event['tag']: event['timestamp'] for event in events}


def map_collection_exercise_state(ce_state):
    return {
        'CREATED': 'Created',
        'SCHEDULED': 'Scheduled',
        'READY_FOR_REVIEW': 'Ready for review',
        'FAILEDVALIDATION': 'Ready for review',
        'EXECUTION_STARTED': 'Setting ready for live',
        'VALIDATED': 'Setting ready for live',
        'EXECUTED': 'Setting ready for live',
        'READY_FOR_LIVE': 'Ready for live',
        'LIVE': 'Live',
    }.get(ce_state, ce_state)


def map_ce_response_status(ce_response_status):
    return {
        'NOTSTARTED': "Not started",
        'INPROGRESS': "In progress",
        'COMPLETE': "Completed",
        'COMPLETEDBYPHONE': 'Completed by phone',
        'NOLONGERREQUIRED': 'No longer required',
    }.get(ce_response_status, ce_response_status)


def map_region(region):
    return "NI" if region == "YY" else "GB"
