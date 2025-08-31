"""Core utilities and base classes.

Foundation layer providing reusable components following
SOLID principles and clean architecture patterns.
"""

from .exceptions import TSVTranslateError, ValidationError, SyncError
from .types import ConversionResult, SyncResult

__all__ = [
    "TSVTranslateError", "ValidationError", "SyncError",
    "ConversionResult", "SyncResult"
]