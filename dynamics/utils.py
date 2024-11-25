import logging
from datetime import datetime
from functools import wraps
from typing import TYPE_CHECKING
from uuid import UUID

from .cache import AsyncSQLiteCache, SQLiteCache
from .exceptions import DynamicsException

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

from .typing import Any, Awaitable, Callable, Coroutine, List, Optional, P, T, Type, Union

if TYPE_CHECKING:
    from django.core.cache import BaseCache

    from . import DynamicsClient


__all__ = [
    "Singletons",
    "error_simplification_available",
    "from_dynamics_date_format",
    "is_valid_uuid",
    "sentinel",
    "to_coroutine",
    "to_dynamics_date_format",
]


logger = logging.getLogger(__name__)


class sentinel:  # noqa: N801
    """Sentinel value."""


def is_valid_uuid(value: str) -> bool:
    try:
        uuid = UUID(value)
        return str(uuid) == value
    except Exception:  # noqa: BLE001
        return False


def to_dynamics_date_format(date: datetime, from_timezone: Optional[str] = None) -> str:
    """
    Convert a datetime-object to a Dynamics compatible ISO formatted date string.

    :param date: Datetime object.
    :param from_timezone: Time zone name from the IANA Time Zone Database the date is in.
                          Dynamics dates are in UCT, so timezoned values need to be converted to it.
    """
    if from_timezone is not None and date.tzinfo is None:
        date: datetime = date.replace(tzinfo=ZoneInfo(from_timezone))

    if date.tzinfo is not None:
        date -= date.utcoffset()

    return date.replace(tzinfo=None).isoformat(timespec="seconds") + "Z"


def from_dynamics_date_format(date: str, to_timezone: str = "UCT") -> datetime:
    """
    Convert a Dynamics compatible ISO formatted date string to a datetime-object.

    :param date: Date string in form: YYYY-mm-ddTHH:MM:SSZ
    :param to_timezone: Time zone name from the IANA Time Zone Database to convert the date to.
                        This won't add 'tzinfo', instead the actual time part will be changed from UCT
                        to what the time is at 'to_timezone'.
    """
    local_time = datetime.fromisoformat(date.replace("Z", "")).replace(tzinfo=ZoneInfo(to_timezone))
    local_time += local_time.utcoffset()
    return local_time.replace(tzinfo=None)


class Singletons:
    """A static Singleton interface; any future singleton objects should be included here."""

    filename: str = "dynamics.cache"
    _cache: Union[SQLiteCache, Any] = None
    _async_cache: Optional[AsyncSQLiteCache] = None

    @staticmethod
    def cache() -> Union[SQLiteCache, "BaseCache"]:
        if Singletons._cache is None:
            try:
                from django.core.cache import cache
            except ImportError:
                cache = SQLiteCache(filename=Singletons.filename)
            Singletons._cache = cache

        return Singletons._cache

    @staticmethod
    def async_cache() -> Union[AsyncSQLiteCache, "BaseCache"]:
        if Singletons._async_cache is None:
            try:
                from django.core.cache import cache
            except ImportError:
                cache = AsyncSQLiteCache(filename=Singletons.filename)
            Singletons._async_cache = cache

        return Singletons._async_cache


def error_simplification_available(func: Callable[P, T]) -> Callable[P, T]:
    """
    Errors in the function decorated with this decorator can be simplified to just a
    DynamicsException with default error message using the keyword: 'simplify_errors'.
    This is useful if you want to hide error details from frontend users.

    You can use the 'raise_separately' keyword to list exception types to exclude from this
    simplification, if separate handling is needed.

    :param func: Decorated function.
    """

    @wraps(func)
    def inner(*args: P.args, **kwargs: P.kwargs) -> T:
        simplify_errors: bool = kwargs.pop("simplify_errors", False)
        raise_separately: List[Type[Exception]] = kwargs.pop("raise_separately", [])

        try:
            return func(*args, **kwargs)
        except Exception as error:
            logger.warning(error)
            if not simplify_errors or any(isinstance(error, exception) for exception in raise_separately):
                raise
            self: "DynamicsClient" = args[0]
            raise DynamicsException(self.simplified_error_message) from error

    return inner


def to_coroutine(func: Callable[P, T]) -> Callable[P, Coroutine[Awaitable[T], Any, Any]]:
    """Convert passed callable into a coroutine."""

    @wraps(func)
    async def wrapper(*args: P.args, **kw: P.kwargs) -> Any:
        return func(*args, **kw)

    return wrapper
