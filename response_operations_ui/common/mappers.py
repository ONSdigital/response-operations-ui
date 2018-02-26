import calendar
import iso8601


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
            "time": time
        }
    return formatted_events


def map_collection_exercise_state(ce_state):
    return {
        'CREATED': 'Created',
        'SCHEDULED': 'Scheduled',
        'READY_FOR_REVIEW': 'Ready for Review',
        'FAILEDVALIDATION': 'Ready for Review',
        'EXECUTION_STARTED': 'Setting Ready for Live',
        'VALIDATED': 'Setting Ready for Live',
        'EXECUTED': 'Setting Ready for Live',
        'READY_FOR_LIVE': 'Ready for Live',
        'LIVE': 'Live',
    }.get(ce_state, ce_state)
