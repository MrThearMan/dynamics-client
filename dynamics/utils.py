from typing import Tuple
from datetime import datetime

from .query_functions import ftr


__all__ = [
    "DateRange",
    "to_dynamics_date_format",
    "from_dynamics_date_format",
]


def to_dynamics_date_format(date: datetime) -> str:
    """Convert a datetime-object to a Dynamics compatible ISO formatted date string."""
    return date.isoformat(timespec="seconds") + "Z"


def from_dynamics_date_format(date: str) -> datetime:
    """Convert a Dynamics compatible ISO formatted date string to a datetime-object."""
    return datetime.fromisoformat(date.replace("Z", ""))


class DateRange:
    """Object for creating now, start, and end dates in datetime and dynamics
    compatible ISO string format. Also compiles an appropriate dynamics filter,
    but note that this only takes into account the date, and not the time part.
    """

    def __init__(self, start: str = None, end: str = None, start_key: str = None, end_key: str = None):

        if start and not start_key:
            raise ValueError("Dynamics table date start key needed if start defined.")
        if end and not end_key:
            raise ValueError("Dynamics table date end key needed if end defined.")

        self.now_date = datetime.now()
        self.now_string = to_dynamics_date_format(self.now_date)

        self.filter_range = []
        self.start_date = None
        self.end_date = None
        self.start_string = start
        self.end_string = end

        if start == "now":
            self.start_date = self.now_date
            self.filter_range.append(ftr.on_or_after(end_key, self.now_string))
        elif start:
            self.start_date = from_dynamics_date_format(start)
            self.filter_range.append(ftr.on_or_after(end_key, start))

        if end == "now":
            self.end_date = self.now_date
            self.filter_range.append(ftr.on_or_before(start_key, self.now_string))
        elif end:
            self.end_date = from_dynamics_date_format(start)
            self.filter_range.append(ftr.on_or_before(start_key, end))

    def __contains__(self, item: Tuple[str, str]) -> bool:
        """Check if (start, end) dynamics ISO formatted strings are in the defined range."""
        booking_start = from_dynamics_date_format(item[0])
        booking_end = from_dynamics_date_format(item[1])

        if self.start_date and booking_end < self.start_date:
            return False
        if self.end_date and booking_start >= self.end_date:
            return False

        return True
