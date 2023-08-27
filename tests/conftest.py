import os
from contextlib import contextmanager

import pytest

from dynamics.test import (
    _dynamics_async_cache_constructor,
    _dynamics_cache_constructor,
    async_dynamics_cache,
    async_dynamics_client,
    dynamics_cache,
    dynamics_client,
)

__all__ = [
    "_dynamics_async_cache_constructor",
    "_dynamics_cache_constructor",
    "async_dynamics_cache",
    "async_dynamics_client",
    "dynamics_cache",
    "dynamics_client",
    "environ",
]


@pytest.fixture
def environ():
    @contextmanager
    def set_environ(**kwargs):
        try:
            for key, value in kwargs.items():
                os.environ[key] = value
            yield
        finally:
            for key in kwargs:
                del os.environ[key]

    return set_environ
