import calendar
from datetime import datetime


def convert_events_to_new_format(events):
    formatted_events = {}
    for event in events:
        date_time = datetime.strptime(event['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
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
