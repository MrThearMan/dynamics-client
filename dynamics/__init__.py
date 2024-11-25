"""Dynamics Web API Client."""

from .apply_functions import apl
from .client import DynamicsClient
from .query_functions import ftr

__all__ = [
    "DynamicsClient",
    "apl",
    "ftr",
]
