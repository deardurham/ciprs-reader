import datetime as dt
import logging


logger = logging.getLogger(__name__)


def parse_datetime(value, fmt):
    try:
        datetime = dt.datetime.strptime(value, fmt)
    except ValueError as err:
        logger.error(err)
        datetime = None
    return datetime


def parse_date_isoformat(value, fmt, include_time=False):
    """Returns date in string form 'YYYY-MM-DD'."""
    datetime = parse_datetime(value, fmt)
    if datetime is None:
        return ""
    return datetime.isoformat() if include_time else datetime.date().isoformat()
