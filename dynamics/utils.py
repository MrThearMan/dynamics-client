import pytz
import logging
import sqlite3
import pickle
from pathlib import Path
from functools import wraps
from datetime import datetime, timedelta, timezone
from typing import Optional, Any


__all__ = [
    "to_dynamics_date_format",
    "from_dynamics_date_format",
    "sentinel",
    "cache",
]


logger = logging.getLogger(__name__)


class sentinel:
    """Sentinel value."""

    def __bool__(self):
        return False


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


def sqlite_method(method):
    """Wrapped method is executed under an open sqlite3 connection.
    Method's class should contain a 'self.connection_string' that is used to make the connection.
    This decorator then updates a 'self.con' object inside the class to the current connection.
    After the method is finished, or if it raises an exception, the connection is closed and the
    return value or exception propagated.
    """

    @wraps(method)
    def inner(*args, **kwargs):
        self = args[0]
        self.con = sqlite3.connect(self.connection_string)
        self._apply_pragma()

        try:
            value = method(*args, **kwargs)
            self.con.commit()
        except Exception as e:
            self.con.execute(self._set_pragma.format("optimize"))
            self.con.close()
            raise e

        self.con.execute(self._set_pragma.format("optimize"))
        self.con.close()
        return value

    return inner


class SQLiteCache:
    """Dymmy cache to use if Django's cache is not installed."""

    DEFAULT_TIMEOUT = 300
    DEFAULT_PRAGMA = {
        "mmap_size": 2 ** 26,           # https://www.sqlite.org/pragma.html#pragma_mmap_size
        "cache_size": 8192,             # https://www.sqlite.org/pragma.html#pragma_cache_size
        "wal_autocheckpoint": 1000,     # https://www.sqlite.org/pragma.html#pragma_wal_autocheckpoint
        "auto_vacuum": "none",          # https://www.sqlite.org/pragma.html#pragma_auto_vacuum
        "synchronous": "off",           # https://www.sqlite.org/pragma.html#pragma_synchronous
        "journal_mode": "wal",          # https://www.sqlite.org/pragma.html#pragma_journal_mode
        "temp_store": "memory",         # https://www.sqlite.org/pragma.html#pragma_temp_store
    }

    _create_sql = (
        "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value BLOB, exp REAL)"
    )
    _create_index_sql = (
        "CREATE UNIQUE INDEX IF NOT EXISTS cache_key ON cache(key)"
    )
    _set_pragma = (
        "PRAGMA {}"
    )
    _set_pragma_equal = (
        "PRAGMA {}={}"
    )

    _get_sql = (
        "SELECT value, exp FROM cache WHERE key = :key"
    )
    _set_sql = (
        "INSERT INTO cache (key, value, exp) VALUES (:key, :value, :exp) "
        "ON CONFLICT(key) DO UPDATE SET value = :value, exp = :exp"
    )
    _delete_sql = (
        "DELETE FROM cache WHERE key = :key"
    )

    def __init__(self, *, filename: str = "dynamics.cache", path: str = None):
        """Create a cache using sqlite3.

        :param filename: Cache file name.
        :param path: Path string to the wanted db location. If None, use current directory.
        """

        filepath = filename if path is None else str(Path(path) / filename)
        self.connection_string = f"{filepath}:?mode=memory&cache=shared"

        self.con = sqlite3.connect(self.connection_string)
        self.con.execute(self._create_sql)
        self.con.execute(self._create_index_sql)
        self.con.commit()
        self.con.close()

    @staticmethod
    def _exp_timestamp(timeout: int = DEFAULT_TIMEOUT) -> float:
        return (datetime.now(timezone.utc) + timedelta(seconds=timeout)).timestamp()

    @staticmethod
    def _stream(value: Any) -> bytes:
        return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def _unstream(value: bytes) -> Any:
        return pickle.loads(value)

    def _apply_pragma(self):
        for key, value in self.DEFAULT_PRAGMA.items():
            self.con.execute(self._set_pragma_equal.format(key, value))

    @sqlite_method
    def get(self, key: str, default: Any = None) -> Any:
        result: Optional[tuple] = self.con.execute(self._get_sql, {"key": key}).fetchone()

        if result is None:
            return default

        if datetime.utcnow() >= datetime.utcfromtimestamp(result[1]):
            self.con.execute(self._delete_sql, {"key": key})
            return default

        return self._unstream(result[0])

    @sqlite_method
    def set(self, key: str, value: Any, timeout: int = DEFAULT_TIMEOUT) -> None:
        data = {"key": key, "value": self._stream(value), "exp": self._exp_timestamp(timeout)}
        self.con.execute(self._set_sql, data)


cache = SQLiteCache()
