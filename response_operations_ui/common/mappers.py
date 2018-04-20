from datetime import datetime
import calendar
import iso8601
import re


def format_short_name(short_name):
    """
    This regex function returns a short name value without spaces
    e.g. Sand & Gravel -> Sand&Gravel
    """
    return re.sub('(&)', r' \1 ', short_name)


def convert_events_to_new_format(events):
    formatted_events = {}
    for event in events:
        date_time = iso8601.parse_date(event['timestamp'])
        day = calendar.day_name[date_time.weekday()]
        month = calendar.month_name[date_time.month][:3]
        date = f"{date_time.strftime('%d')} {month} {date_time.strftime('%Y')}"
        time = f"{date_time.strftime('%H:%M')} GMT"
        formatted_events[event['tag']] = {
            "day": day,
            "date": date,
            "month": str(date_time.month) if len(str(date_time.month)) == 2 else f"0{date_time.month}",
            "time": time,
            "is_in_future": date_time > iso8601.parse_date(datetime.now().isoformat())
        }
    return formatted_events


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
    if ce_response_status == "NOTSTARTED":
        ce_response_status = "Not started"
    elif ce_response_status == "COMPLETE":
        ce_response_status = "Completed"
    elif ce_response_status == "COMPLETEDBYPHONE":
        ce_response_status = "Completed by phone"
    elif ce_response_status == "INPROGRESS":
        ce_response_status = "In progress"

    return ce_response_status
