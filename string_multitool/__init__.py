"""String_Multitool - Advanced text transformation tool."""

from __future__ import annotations

# Exceptions
from .exceptions import (
    ClipboardError,
    ConfigurationError,
    CryptographyError,
    StringMultitoolError,
    TransformationError,
    ValidationError,
)

# I/O Components
from .io.clipboard import ClipboardMonitor
from .io.manager import InputOutputManager

# Main Application Interface
from .main import ApplicationInterface

# Model Components (Business Logic)
from .models.config import ConfigurationManager
from .models.crypto import CryptographyManager
from .models.transformations import TextTransformationEngine
from .models.types import (
    CommandResult,
    ConfigManagerProtocol,
    CryptoManagerProtocol,
    IOManagerProtocol,
    SessionState,
    TextSource,
    TransformationEngineProtocol,
    TransformationRule,
    TransformationRuleType,
)

__version__ = "2.1.0"
__author__ = "String_Multitool Development Team"

__all__ = [
    "ApplicationInterface",
    "ClipboardError",
    "ClipboardMonitor",
    "CommandResult",
    "ConfigManagerProtocol",
    "ConfigurationError",
    "ConfigurationManager",
    "CryptoManagerProtocol",
    "CryptographyError",
    "CryptographyManager",
    "IOManagerProtocol",
    "InputOutputManager",
    "SessionState",
    "StringMultitoolError",
    "TextSource",
    "TextTransformationEngine",
    "TransformationEngineProtocol",
    "TransformationError",
    "TransformationRule",
    "TransformationRuleType",
    "ValidationError",
]
