import os
import random
import string
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
from dynamics.utils import Singletons

__all__ = [
    "_dynamics_async_cache_constructor",
    "_dynamics_cache_constructor",
    "async_dynamics_cache",
    "async_dynamics_client",
    "dynamics_cache",
    "dynamics_client",
    "environ",
]


@pytest.fixture(scope="session", autouse=True)
def create_cache_table():
    # Set unique cache filename for each test session
    # to prevent issues with database being locked when tests fail unexpectedly
    Singletons.filename = "".join(random.choices(string.ascii_lowercase))
    Singletons.cache()


@pytest.fixture()
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
