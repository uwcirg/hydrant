from datetime import datetime
from flask import current_app
from dateutil import parser

WRAP_YEAR = 2022


def parse_datetime(data, error_subject=None, none_safe=False):
    """Parse input string to generate a UTC datetime instance

    NB - date must be more recent than year 1900 or a ValueError
    will be raised.  (library limitation)

    WRAP_YEAR (defined above) is used to determine how a 2 digit
    year should be treated.  Values below WRAP year are assumed
    to belong in year 20?? where as values above in 19??.

    :param data: the datetime string to parse
    :param error_subject: Subject string to use in error message
    :param none_safe: set true to sanely handle None values
     (None in, None out).  By default, ValueError is raised.

    :return: UTC datetime instance from given data

    """
    if none_safe and data is None:
        return None

    try:
        dt = parser.parse(data)
    except (TypeError, ValueError) as e:
        msg = "Unable to parse {}: {}".format(error_subject, e)
        current_app.logger.warning(msg)
        raise ValueError(msg)

    if dt.tzinfo:
        # Convert to UTC if necessary
        if dt.tzinfo != "UTC":
            dt = dt.astimezone("UTC")
        # Delete tzinfo for safe comparisons with other non tz aware objs
        # All datetime values stored in the db are expected to be in
        # UTC, and timezone unaware.
        dt = dt.replace(tzinfo=None)

    # As we use datetime.strftime for display, and it can't handle dates
    # older than 1900, treat all such dates as an error
    epoch = datetime.strptime('1900-01-01', '%Y-%m-%d')
    if dt < epoch:
        raise ValueError("Dates prior to year 1900 not supported")

    # Correct for python's inappropriate WRAP_YEAR of '69
    if dt.year > WRAP_YEAR:
        dt = dt.replace(year=dt.year-100)

    return dt
