"""
String_Multitool - Advanced text transformation tool.

A powerful command-line text transformation tool with intuitive rule-based syntax,
pipe support, and secure RSA encryption capabilities.
"""

from __future__ import annotations

from typing import Final

from .core.config import ConfigurationManager
from .core.crypto import CryptographyManager
from .core.transformations import TextTransformationEngine
from .core.types import (
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
from .exceptions import (
    ClipboardError,
    ConfigurationError,
    CryptographyError,
    StringMultitoolError,
    TransformationError,
    ValidationError,
)
from .io.clipboard import ClipboardMonitor
from .io.manager import InputOutputManager

__version__: Final[str] = "2.1.0"
__author__: Final[str] = "String_Multitool Development Team"

__all__ = [
    # Exceptions
    "StringMultitoolError",
    "ConfigurationError",
    "TransformationError",
    "CryptographyError",
    "ClipboardError",
    "ValidationError",
    # Types and Protocols
    "TransformationRule",
    "SessionState",
    "CommandResult",
    "TextSource",
    "TransformationRuleType",
    "ConfigManagerProtocol",
    "IOManagerProtocol",
    "TransformationEngineProtocol",
    "CryptoManagerProtocol",
    # Core Components
    "ConfigurationManager",
    "CryptographyManager",
    "TextTransformationEngine",
    # I/O Components
    "InputOutputManager",
    "ClipboardMonitor",
]
