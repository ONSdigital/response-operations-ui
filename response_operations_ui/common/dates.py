import logging
from datetime import datetime, date

from dateutil import tz
from structlog import wrap_logger
from iso8601 import parse_date
from iso8601.iso8601 import ParseError


logger = wrap_logger(logging.getLogger(__name__))


def get_formatted_date(datetime_string: str, string_format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Takes a string date in given format returns a string 'today', 'yesterday' at the time in format '%H:%M'
    if the given date is today or yesterday respectively otherwise returns the full date in the format '%b %d %Y %H:%M'.
    If datetime_string is not a valid date in the given format it is returned with no formatting.

    :param datetime_string: A string representing a datetime
    :param string_format: A strptime string that should match the format of the datetime string that is to be converted
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

    :param datetime_parsed: A datetime object
    :type datetime_parsed: datetime
    :return: Returns adjusted datetime
    :rtype: datetime
    """
    return datetime_parsed.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('Europe/London'))


def format_datetime_to_string(timestamp, date_format='%A %d %b %Y', localise=True):
    """
    Converts a iso8601 datetime string into a user friendly datetime string.
    By default this will turn the datetime representation of '2020-06-22T06:00:00.000Z' into 'Monday 22 Jun 2020'
    but this will take any valid strftime string and convert it.

    :param timestamp: An iso8601 datetime string
    :param localise: adjust for any daylight savings, defaults to true
    :type timestamp: str
    :param date_format: A strftime string representing the format the datetime will be converted to.
    :type date_format: str
    :return: A string representation of the datetime object based on either the default or provided strftime format.  If
    there is an error parsing it, it will return the string 'N/A'
    """
    try:
        datetime_obj = parse_date(timestamp)
        if localise:
            datetime_obj = localise_datetime(datetime_obj)
        return datetime_obj.strftime(date_format)
    except ParseError:
        return 'N/A'
