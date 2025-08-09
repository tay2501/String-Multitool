"""
Core type definitions and data classes for String_Multitool.

This module contains all the data classes and type definitions used
throughout the application, providing type safety and clear interfaces.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Any, Protocol, TypeVar, Generic
from enum import Enum, auto


# Type variables for generic classes
T = TypeVar('T')
ConfigT = TypeVar('ConfigT', bound=dict[str, Any])


class TextSource(Enum):
    """Enumeration of text input sources."""
    CLIPBOARD = "clipboard"
    PIPE = "pipe"
    MANUAL = "manual"


class TransformationRuleType(Enum):
    """Enumeration of transformation rule categories."""
    BASIC = auto()
    CASE = auto()
    STRING_OPS = auto()
    ENCRYPTION = auto()
    ADVANCED = auto()


@dataclass(kw_only=True, frozen=True)
class TransformationRule:
    """Data class representing a transformation rule.
    
    This class is immutable to ensure rule definitions cannot be
    accidentally modified during runtime.
    """
    name: str
    description: str
    example: str
    function: Callable[[str], str]
    requires_args: bool = False
    default_args: list[str] | None = None
    rule_type: TransformationRuleType = TransformationRuleType.BASIC


@dataclass(kw_only=True)
class SessionState:
    """Represents current interactive session state."""
    current_text: str
    text_source: TextSource
    last_update_time: datetime
    character_count: int
    auto_detection_enabled: bool
    clipboard_monitor_active: bool


@dataclass(kw_only=True)
class CommandResult:
    """Result of command processing."""
    success: bool
    message: str
    should_continue: bool = True
    updated_text: str | None = None


# Protocol definitions for dependency injection
class ConfigManagerProtocol(Protocol):
    """Protocol for configuration management."""
    
    def load_transformation_rules(self) -> dict[str, Any]:
        """Load transformation rules from configuration."""
        ...
    
    def load_security_config(self) -> dict[str, Any]:
        """Load security configuration."""
        ...


class IOManagerProtocol(Protocol):
    """Protocol for input/output operations."""
    
    def get_input_text(self) -> str:
        """Get input text from appropriate source."""
        ...
    
    def get_clipboard_text(self) -> str:
        """Get text from clipboard."""
        ...
    
    @staticmethod
    def set_output_text(text: str) -> None:
        """Set output text to clipboard."""
        ...


class TransformationEngineProtocol(Protocol):
    """Protocol for text transformation operations."""
    
    def apply_transformations(self, text: str, rule_string: str) -> str:
        """Apply transformation rules to text."""
        ...
    
    def parse_rule_string(self, rule_string: str) -> list[tuple[str, list[str]]]:
        """Parse rule string into components."""
        ...
    
    def get_available_rules(self) -> dict[str, TransformationRule]:
        """Get all available transformation rules."""
        ...


class CryptoManagerProtocol(Protocol):
    """Protocol for cryptography operations."""
    
    def encrypt_text(self, text: str) -> str:
        """Encrypt text using RSA."""
        ...
    
    def decrypt_text(self, text: str) -> str:
        """Decrypt text using RSA."""
        ...


# Generic base class for configuration-based components
class ConfigurableComponent(Generic[ConfigT]):
    """Base class for components that require configuration."""
    
    def __init__(self, config: ConfigT) -> None:
        self.config = config
    
    def validate_config(self) -> bool:
        """Validate the configuration. Override in subclasses."""
        return isinstance(self.config, dict)