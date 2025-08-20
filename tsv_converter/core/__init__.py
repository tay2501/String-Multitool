"""Core utilities and base classes.

Foundation layer providing reusable components following
SOLID principles and clean architecture patterns.
"""

from .exceptions import TSVConverterError, ValidationError, SyncError
from .types import ConversionResult, SyncResult

__all__ = [
    "TSVConverterError", "ValidationError", "SyncError",
    "ConversionResult", "SyncResult"
]