from datetime import datetime, date
import logging

from structlog import wrap_logger

logger = wrap_logger(logging.getLogger(__name__))


def get_formatted_date(datetime_string, string_format='%Y-%m-%d %H:%M:%S'):
    """Takes a string date in given format returns a string 'today', 'yesterday' at the time in format '%H:%M'
    if the given date is today or yesterday respectively otherwise returns the full date in the format '%b %d %Y %H:%M'
    """
    try:
        datetime_parsed = datetime.strptime(datetime_string, string_format)
    except (OverflowError, ValueError, AttributeError):
        # Passed value wasn't date-ish or date arguments out of range
        logger.exception("Failed to parse date from message", sent_date=datetime_string)
        return datetime_string

    time_difference = datetime.date(datetime_parsed) - date.today()

    if time_difference.days == 0:
        return f"Today at {datetime_parsed.strftime('%H:%M')}"
    elif time_difference.days == -1:
        return f"Yesterday at {datetime_parsed.strftime('%H:%M')}"
    return f"{datetime_parsed.strftime('%d %b %Y').title()} {datetime_parsed.strftime('%H:%M')}"
