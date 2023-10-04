import asyncio
import pickle
import sqlite3
import tempfile
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiosqlite

from .typing import Any, Coroutine, Dict, Optional, Union

__all__ = [
    "SQLiteCache",
    "AsyncSQLiteCache",
]


class SQLiteCacheBase(ABC):
    """Dummy cache to use if Django's cache is not installed."""

    DEFAULT_TIMEOUT = 300
    DEFAULT_PRAGMA = {
        "mmap_size": 2**26,  # https://www.sqlite.org/pragma.html#pragma_mmap_size
        "cache_size": 8192,  # https://www.sqlite.org/pragma.html#pragma_cache_size
        "wal_autocheckpoint": 1000,  # https://www.sqlite.org/pragma.html#pragma_wal_autocheckpoint
        "auto_vacuum": "none",  # https://www.sqlite.org/pragma.html#pragma_auto_vacuum
        "synchronous": "off",  # https://www.sqlite.org/pragma.html#pragma_synchronous
        "journal_mode": "wal",  # https://www.sqlite.org/pragma.html#pragma_journal_mode
        "temp_store": "memory",  # https://www.sqlite.org/pragma.html#pragma_temp_store
        "busy_timeout": 1000,  # https://www.sqlite.org/pragma.html#pragma_busy_timeout
    }

    _check_table = "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='cache';"
    _create_sql = "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value BLOB, exp REAL)"
    _create_index_sql = "CREATE UNIQUE INDEX IF NOT EXISTS cache_key ON cache(key)"
    _set_pragma = "PRAGMA {}"
    _set_pragma_equal = "PRAGMA {}={}"

    _get_sql = "SELECT value, exp FROM cache WHERE key = :key"
    _set_sql = (
        "INSERT INTO cache (key, value, exp) VALUES (:key, :value, :exp) "
        "ON CONFLICT(key) DO UPDATE SET value = :value, exp = :exp"
    )
    _delete_sql = "DELETE FROM cache WHERE key = :key"
    _clear_sql = "DELETE FROM cache"

    def __init__(self, *, filename: str, path: str = None):
        """Create a cache using sqlite.

        :param filename: Cache file name.
        :param path: Path string to the wanted db location. If None, use system temp folder.
        """

        if path is None:
            path = tempfile.gettempdir()

        filepath = filename if path is None else str(Path(path) / filename)
        self.connection_string = f"{filepath}:?mode=memory&cache=shared"
        self.create_table_if_not_exist()

    def create_table_if_not_exist(self) -> None:
        with sqlite3.connect(self.connection_string) as connection:
            if connection.execute(self._check_table).fetchone()[0] == 1:
                return

            connection.execute(self._create_sql)
            connection.execute(self._create_index_sql)
            for key, value in self.DEFAULT_PRAGMA.items():
                connection.execute(self._set_pragma_equal.format(key, value))

    @staticmethod
    def _exp_timestamp(timeout: int = DEFAULT_TIMEOUT) -> float:
        return (datetime.now(timezone.utc) + timedelta(seconds=timeout)).timestamp()

    @staticmethod
    def _stream(value: Any) -> bytes:
        return pickle.dumps(value)

    @staticmethod
    def _unstream(value: bytes) -> Any:
        return pickle.loads(value)  # noqa: S301

    @property
    @abstractmethod
    def con(self) -> Union[sqlite3.Connection, aiosqlite.Connection]:
        """Get or create connection."""

    @abstractmethod
    def close_blocking_connections(self, thead_id: int) -> None:
        """Close blocking sqlite connections between the sync and async implementations."""

    @abstractmethod
    def get(self, key: str, default: Any = None) -> Union[Any, Coroutine[Any, Any, Any]]:
        """Get item from cache."""

    @abstractmethod
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> Union[None, Coroutine[Any, Any, None]]:
        """Get item from cache."""

    @abstractmethod
    def clear(self) -> Union[None, Coroutine[Any, Any, None]]:
        """Clear cache."""

    @abstractmethod
    def close(self) -> Union[None, Coroutine[Any, Any, None]]:
        """Close the cache."""


class SQLiteCache(SQLiteCacheBase):
    """Sync cache"""

    connections: Dict[int, sqlite3.Connection] = {}

    @property
    def con(self) -> sqlite3.Connection:
        thead_id = threading.get_ident()
        self.close_blocking_connections(thead_id)
        connection = self.connections.get(thead_id)
        if connection is None:
            self.connections[thead_id] = connection = sqlite3.connect(self.connection_string)
        return connection

    def close_blocking_connections(self, thead_id: int) -> None:
        connection = AsyncSQLiteCache.connections.pop(thead_id, None)
        if connection is None:
            return

        try:
            asyncio.run(connection.close())
        except RuntimeError:  # Raised if already in an async event loop.
            try:
                # Submit the connection-close task to the aiosqlite.Connection Thread-object,
                # since only that thread is allowed to close the sqlite connection.
                connection._tx.put_nowait(
                    (
                        asyncio.get_running_loop().create_future(),
                        connection._connection.close,
                    )
                )
            finally:
                # These inform the aiosqlite.Connection Thread-object to stop running.
                connection._running = False
                connection._connection = None

    def get(self, key: str, default: Any = None) -> Any:
        result: Optional[tuple] = self.con.execute(self._get_sql, {"key": key}).fetchone()

        if result is None:
            return default

        if datetime.utcnow() >= datetime.utcfromtimestamp(result[1]):
            self.con.execute(self._delete_sql, {"key": key})
            return default

        return self._unstream(result[0])

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        data = {"key": key, "value": self._stream(value), "exp": self._exp_timestamp(timeout)}
        self.con.execute(self._set_sql, data)

    def clear(self) -> None:
        self.con.execute(self._clear_sql)

    def close(self) -> None:
        self.con.execute(self._set_pragma.format("optimize"))  # https://www.sqlite.org/pragma.html#pragma_optimize
        self.con.close()
        thead_id = threading.get_ident()
        self.connections.pop(thead_id, None)

    def __del__(self) -> None:  # pragma: no cover
        self.close()


class AsyncSQLiteCache(SQLiteCacheBase):
    """Async cache"""

    connections: Dict[int, aiosqlite.Connection] = {}

    @property
    async def con(self) -> aiosqlite.Connection:
        thead_id = threading.get_ident()
        self.close_blocking_connections(thead_id)
        connection = self.connections.get(thead_id)
        if connection is None:
            connection = await aiosqlite.connect(self.connection_string)
            self.connections[thead_id] = connection
        return connection

    def close_blocking_connections(self, thead_id: int) -> None:
        sync_connection = SQLiteCache.connections.pop(thead_id, None)
        if sync_connection is not None:
            sync_connection.close()

    async def get(self, key: str, default: Any = None) -> Any:
        con = await self.con
        cur: aiosqlite.Cursor
        async with con.execute(self._get_sql, {"key": key}) as cur:
            result: Optional[tuple] = await cur.fetchone()

        if result is None:
            return default

        if datetime.utcnow() >= datetime.utcfromtimestamp(result[1]):
            await con.execute(self._delete_sql, {"key": key})
            return default

        return self._unstream(result[0])

    async def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        timeout = timeout if timeout is not None else self.DEFAULT_TIMEOUT
        data = {"key": key, "value": self._stream(value), "exp": self._exp_timestamp(timeout)}
        con = await self.con
        await con.execute(self._set_sql, data)

    async def clear(self) -> None:
        con = await self.con
        await con.execute(self._clear_sql)

    async def close(self) -> None:
        con = await self.con
        await con.execute(self._set_pragma.format("optimize"))  # https://www.sqlite.org/pragma.html#pragma_optimize
        await con.close()
        thead_id = threading.get_ident()
        self.connections.pop(thead_id, None)

    # Django compatibility

    async def aget(self, key: str, default: Any = None) -> Any:  # pragma: no cover
        return await self.get(key=key, default=default)

    async def aset(self, key: str, value: Any, timeout: Optional[int] = None) -> None:  # pragma: no cover
        return await self.set(key=key, value=value, timeout=timeout)

    async def aclear(self) -> None:  # pragma: no cover
        return await self.clear()

    async def aclose(self) -> None:  # pragma: no cover
        return await self.close()
