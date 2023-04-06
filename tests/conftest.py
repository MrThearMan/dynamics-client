import os
from contextlib import contextmanager

import pytest

from dynamics.test import _dynamics_cache_constructor, dynamics_cache, dynamics_client

__all__ = [
    "_dynamics_cache_constructor",
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
