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
    This decorator then updates a 'sef.cur' object inside the class to the current cursor-object.
    After the method is finished, or if it raises an exception, the connection is closed and the
    return value or exception propagated.
    """

    @wraps(method)
    def inner(*args, **kwargs):
        self = args[0]
        con = sqlite3.connect(self.connection_string)

        try:
            self.cur = con.cursor()
            value = method(*args, **kwargs)
            con.commit()
        except Exception as e:
            con.close()
            raise e

        con.close()
        return value

    return inner


class SQLiteCache:
    """Dymmy cache to use if Django's cache is not installed."""

    DEFAULT_TIMEOUT = 300

    _create_sql = (
        "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value BLOB, exp FLOAT)"
    )
    _add_sql = (
        "INSERT INTO cache (key, value, exp) VALUES (:key, :value, :exp) "
        "ON CONFLICT(key) DO UPDATE SET value=:value, exp=:exp "
        "WHERE DATETIME(exp, 'unixepoch') <= DATETIME('now')"
    )
    _get_sql = (
        "SELECT value, exp FROM cache WHERE key=:key"
    )
    _set_sql = (
        "INSERT INTO cache (key, value, exp) VALUES (:key, :value, :exp) "
        "ON CONFLICT(key) DO UPDATE SET value=:value, exp=:exp"
    )
    _check_sql = (
        "SELECT value, exp FROM cache WHERE key=:key AND DATETIME(exp, 'unixepoch') > DATETIME('now')"
    )
    _update_sql = (
        "UPDATE cache SET value=:value WHERE key=:key AND DATETIME(exp, 'unixepoch') > DATETIME('now')"
    )

    # TODO: add 'RETURNING COUNT(*)!=0' to these when sqlite3 version >=3.35.0
    _delete_sql = (
        "DELETE FROM cache WHERE key=:key"
    )
    _touch_sql = (
        "UPDATE cache SET exp=:exp WHERE key=:key AND DATETIME(exp, 'unixepoch') > DATETIME('now')"
    )
    _clear_sql = (
        "DELETE FROM cache"
    )

    _add_many_sql = (
        "INSERT INTO cache (key, value, exp) VALUES {}"
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, exp=excluded.exp "
        "WHERE DATETIME(exp, 'unixepoch') <= DATETIME('now')"
    )
    _get_many_sql = (
        "SELECT key, value, exp FROM cache WHERE key IN ({})"
    )
    _set_many_sql = (
        "INSERT INTO cache (key, value, exp) VALUES {}"
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, exp=excluded.exp"
    )
    _delete_many_sql = (
        "DELETE FROM cache WHERE key IN ({})"
    )

    def __init__(self, *, filename: str = ".cache", path: str = None, in_memory: bool = True):
        """Create a cache with sqlite3.

        :param filename: Cache file name.
        :param path: Path string to the wanted db location. If None, use current directory.
        :param in_memory: Create database in-memory only. File is still created, but nothing is stored in it.
        """

        self.filepath = filename if path is None else str(Path(path) / filename)
        self.suffix = ":?mode=memory&cache=shared" if in_memory else ""
        self.connection_string = f"{self.filepath}{self.suffix}"

        con = sqlite3.connect(self.connection_string)
        self.cur = con.cursor()
        self.cur.execute(self._create_sql)
        con.commit()
        con.close()

    @staticmethod
    def _exp_timestamp(timeout: int = DEFAULT_TIMEOUT) -> float:
        return (datetime.now(timezone.utc) + timedelta(seconds=timeout)).timestamp()

    @staticmethod
    def _stream(value: Any) -> bytes:
        return pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def _unstream(value: bytes) -> Any:
        return pickle.loads(value)

    @sqlite_method
    def add(self, key: str, value: Any, timeout: int = DEFAULT_TIMEOUT) -> None:
        data = {"key": key, "value": self._stream(value), "exp": self._exp_timestamp(timeout)}
        self.cur.execute(self._add_sql, data)

    @sqlite_method
    def get(self, key: str, default: Any = None) -> Any:
        self.cur.execute(self._get_sql, {"key": key})
        result: Optional[tuple] = self.cur.fetchone()

        if result is None:
            return default

        exp = datetime.utcfromtimestamp(result[1])

        if datetime.utcnow() >= exp:
            self.cur.execute(self._delete_sql, {"key": key})
            return default

        return self._unstream(result[0])

    @sqlite_method
    def set(self, key: str, value: Any, timeout: int = DEFAULT_TIMEOUT) -> None:
        data = {"key": key, "value": self._stream(value), "exp": self._exp_timestamp(timeout)}
        self.cur.execute(self._set_sql, data)

    @sqlite_method
    def update(self, key: str, value: Any) -> None:
        data = {"key": key, "value": self._stream(value)}
        self.cur.execute(self._update_sql, data)

    @sqlite_method
    def add_many(self, dict_: dict, timeout: int = DEFAULT_TIMEOUT) -> None:
        command = self._add_many_sql.format(
            ", ".join([f"(:key{n}, :value{n}, :exp{n})" for n in range(len(dict_))])
        )

        data = {}
        for i, (key, value) in enumerate(dict_.items()):
            data[f"key{i}"] = key
            data[f"value{i}"] = self._stream(value)
            data[f"exp{i}"] = self._exp_timestamp(timeout)

        self.cur.execute(command, data)

    @sqlite_method
    def get_or_set(self, key: str, default: Any, timeout: int = DEFAULT_TIMEOUT) -> Any:
        self.cur.execute(self._get_sql, {"key": key})
        result: Optional[tuple] = self.cur.fetchone()

        if result is not None:
            exp = datetime.utcfromtimestamp(result[1])

            if datetime.utcnow() >= exp:
                self.cur.execute(self._delete_sql, {"key": key})
            else:
                return self._unstream(result[0])

        data = {"key": key, "value": self._stream(default), "exp": self._exp_timestamp(timeout)}
        self.cur.execute(self._set_sql, data)
        return default

    @sqlite_method
    def get_many(self, keys: list) -> dict:
        self.cur.execute(self._get_many_sql.format(", ".join([f"'{value}'" for value in keys])))
        fetched: Optional[list] = self.cur.fetchall()

        if fetched is None:
            return {}

        results = {}
        to_delete = []
        for key, value, exp in fetched:
            exp = datetime.utcfromtimestamp(exp)

            if datetime.utcnow() >= exp:
                to_delete.append(key)
                continue

            results[key] = self._unstream(value)

        if to_delete:
            self.cur.execute(self._delete_many_sql.format(", ".join([f"'{value}'" for value in to_delete])))

        return results

    @sqlite_method
    def set_many(self, dict_: dict, timeout: int = DEFAULT_TIMEOUT) -> None:
        command = self._set_many_sql.format(
            ", ".join([f"(:key{n}, :value{n}, :exp{n})" for n in range(len(dict_))])
        )

        data = {}
        for i, (key, value) in enumerate(dict_.items()):
            data[f"key{i}"] = key
            data[f"value{i}"] = self._stream(value)
            data[f"exp{i}"] = self._exp_timestamp(timeout)

        self.cur.execute(command, data)

    @sqlite_method
    def delete_many(self, keys: list) -> None:
        self.cur.execute(self._delete_many_sql.format(", ".join([f"'{value}'" for value in keys])))

    @sqlite_method
    def update_many(self, dict_: dict):
        for key, value in dict_.items():
            data = {"key": key, "value": self._stream(value)}
            self.cur.execute(self._update_sql, data)

    @sqlite_method
    def touch(self, key: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        data = {"exp": self._exp_timestamp(timeout), "key": key}
        self.cur.execute(self._touch_sql, data)

    @sqlite_method
    def delete(self, key: str) -> None:
        self.cur.execute(self._delete_sql, {"key": key})

    @sqlite_method
    def clear(self) -> None:
        self.cur.execute(self._clear_sql)

    @sqlite_method
    def incr(self, key: str, delta: int = 1) -> None:
        self.cur.execute(self._check_sql, {"key": key})
        result: Optional[tuple] = self.cur.fetchone()

        if result is None:
            raise ValueError("Nonexistent or expired cache key.")

        value = self._unstream(result[0])
        if not isinstance(value, int):
            raise ValueError("Value is not an integer")

        data = {"key": key, "value": self._stream(value + delta)}
        self.cur.execute(self._update_sql, data)

    @sqlite_method
    def decr(self, key: str, delta: int = 1) -> None:
        self.cur.execute(self._check_sql, {"key": key})
        result: Optional[tuple] = self.cur.fetchone()

        if result is None:
            raise ValueError("Nonexistent or expired cache key.")

        value = self._unstream(result[0])
        if not isinstance(value, int):
            raise ValueError("Value is not an integer")

        data = {"key": key, "value": self._stream(value - delta)}
        self.cur.execute(self._update_sql, data)


cache = SQLiteCache()
