import logging
from datetime import datetime, date

from dateutil import tz
from structlog import wrap_logger
from structlog.processors import JSONRenderer


logger = wrap_logger(logging.getLogger(__name__),
                     processors=[JSONRenderer(indent=1, sort_keys=True)])


def get_formatted_date(datetime_string, string_format='%Y-%m-%d %H:%M:%S'):
    """Takes a string date in given format returns a string 'today', 'yesterday' at the time in format '%H:%M'
    if the given date is today or yesterday respectively otherwise returns the full date in the format '%b %d %Y %H:%M'.
    If datetime_string is not a valid date in the given format it is returned with no formatting.
    """
    try:
        datetime_parsed = datetime.strptime(datetime_string, string_format)
    except (OverflowError, ValueError, AttributeError):
        # Passed value wasn't date-ish or date arguments out of range
        logger.exception("Failed to parse date", sent_date=datetime_string)
        return datetime_string

    time_difference = datetime.date(datetime_parsed) - date.today()

    time = localise_datetime(datetime_parsed).strftime('%H:%M')

    if time_difference.days == 0:
        return f"Today at {time}"
    elif time_difference.days == -1:
        return f"Yesterday at {time}"
    return f"{datetime_parsed.strftime('%d %b %Y')} {time}"


def localise_datetime(datetime_parsed):
    """Takes a datetime and adjusts based on BST or GMT.
    Returns adjusted datetime
    """
    return datetime_parsed.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('Europe/London'))
