import pytz
import logging
from datetime import datetime


__all__ = [
    "to_dynamics_date_format",
    "from_dynamics_date_format",
]


logger = logging.getLogger(__name__)


def to_dynamics_date_format(date: datetime, from_timezone: str = None) -> str:
    """Convert a datetime-object to a Dynamics compatible ISO formatted date string.

    :param date: Datetime object.
    :param from_timezone: Name of the timezone, from 'pytz.all_timezones', the date is in.
                          Dynamics dates are in UCT, so timezoned values need to be converted to it.
    """

    if from_timezone is not None and date.tzinfo is None:
        tz = pytz.timezone(from_timezone)
        date: datetime = tz.localize(date)

    if date.tzinfo is not None:
        date -= date.utcoffset()

    return date.replace(tzinfo=None).isoformat(timespec="seconds") + "Z"


def from_dynamics_date_format(date: str, to_timezone: str = "UCT") -> datetime:
    """Convert a Dynamics compatible ISO formatted date string to a datetime-object.

    :param date: Date string in form: YYYY-mm-ddTHH:MM:SSZ
    :param to_timezone: Name of the timezone, from 'pytz.all_timezones', to convert the date to.
                        This won't add 'tzinfo', instead the actual time part will be changed from UCT
                        to what the time is at 'to_timezone'.
    """
    tz = pytz.timezone(to_timezone)
    local_time: datetime = tz.localize(datetime.fromisoformat(date.replace("Z", "")))
    local_time += local_time.utcoffset()
    local_time = local_time.replace(tzinfo=None)
    return local_time
