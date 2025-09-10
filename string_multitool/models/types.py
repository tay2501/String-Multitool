"""
Core type definitions and data classes for String_Multitool.

This module contains all the data classes and type definitions used
throughout the application, providing type safety and clear interfaces.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from pathlib import Path

# Import ValidationError for TypeGuard functions
# Note: This creates a circular import, so we'll use TYPE_CHECKING
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypeGuard,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from ..exceptions import ValidationError
else:
    # Define a minimal ValidationError for runtime use
    class ValidationError(Exception):
        def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
            super().__init__(message)
            self.context = context or {}


# Type variables for generic classes
T = TypeVar("T")
ConfigT = TypeVar("ConfigT", bound=dict[str, Any])

# Type variables for callback functions and generic constraints
CallbackT = TypeVar("CallbackT", bound=Callable[..., Any])
TextCallbackT = TypeVar("TextCallbackT", bound=Callable[[str], Any])
RuleCallbackT = TypeVar("RuleCallbackT", bound=Callable[[str], str])
ValidationCallbackT = TypeVar("ValidationCallbackT", bound=Callable[[Any], bool])

# Additional type variables for generic operations
ProcessorT = TypeVar("ProcessorT", bound=Callable[[Any], Any])
StateT = TypeVar("StateT")
ResultT = TypeVar("ResultT")
CacheableT = TypeVar("CacheableT")
ValidatableT = TypeVar("ValidatableT")

# Type aliases for frequently used complex types
ConfigDict = dict[str, Any]
RuleDict = dict[str, "TransformationRule"]
RuleTuple = tuple[str, list[str]]
RuleList = list[RuleTuple]
ErrorContext = dict[str, Any]
ThreadCallback = Callable[[str], None] | None
ValidationResult = tuple[bool, str | None]


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


@dataclass(frozen=True, kw_only=True)
class TSVConversionOptions:
    """TSV変換オプションの型安全なデータクラス.

    Enterprise-grade設計により、TSV変換の動作を細かく制御できます。
    不変オブジェクトとして設計され、スレッドセーフな処理を保証します。
    """

    case_insensitive: bool = False
    """大文字小文字を区別しない変換を実行するかどうか"""

    preserve_original_case: bool = True
    """元のテキストの大文字小文字を保持するかどうか（case_insensitive有効時のみ）"""

    match_whole_words_only: bool = False
    """単語境界のみでマッチングを行うかどうか（将来の拡張用）"""

    enable_regex_patterns: bool = False
    """正規表現パターンの使用を許可するかどうか（将来の拡張用）"""


@runtime_checkable
class TSVConversionStrategyProtocol(Protocol):
    """TSV変換戦略のプロトコル定義.

    Strategy Patternの実装により、異なる変換アルゴリズムを
    統一的なインターフェースで使用できます。
    """

    def convert_text(
        self, text: str, conversion_dict: dict[str, str], options: TSVConversionOptions
    ) -> str:
        """テキスト変換を実行.

        Args:
            text: 変換対象のテキスト
            conversion_dict: 変換辞書（キー: 変換前, 値: 変換後）
            options: 変換オプション

        Returns:
            変換されたテキスト

        Raises:
            TransformationError: 変換処理に失敗した場合
        """
        ...

    def prepare_conversion_dict(
        self, raw_dict: dict[str, str], options: TSVConversionOptions
    ) -> dict[str, str]:
        """変換辞書を前処理.

        Args:
            raw_dict: 元の変換辞書
            options: 変換オプション

        Returns:
            前処理済みの変換辞書
        """
        ...


@dataclass(kw_only=True, frozen=True)
class SessionState:
    """Represents current interactive session state."""

    current_text: str
    text_source: TextSource
    last_update_time: datetime
    character_count: int
    auto_detection_enabled: bool
    clipboard_monitor_active: bool


@dataclass(kw_only=True, frozen=True)
class CommandResult:
    """Result of command processing."""

    success: bool
    message: str
    should_continue: bool = True
    updated_text: str | None = None


# Protocol definitions for dependency injection
@runtime_checkable
class ConfigManagerProtocol(Protocol):
    """Protocol for configuration management."""

    config_dir: Path

    def load_transformation_rules(self) -> ConfigDict:
        """Load transformation rules from configuration.

        Returns:
            Dictionary containing transformation rules

        Raises:
            ConfigurationError: If rules file cannot be loaded or parsed
        """
        ...

    def load_security_config(self) -> ConfigDict:
        """Load security configuration.

        Returns:
            Dictionary containing security configuration

        Raises:
            ConfigurationError: If security config file cannot be loaded or parsed
        """
        ...

    def load_hotkey_config(self) -> ConfigDict:
        """Load hotkey configuration.

        Returns:
            Dictionary containing hotkey configuration

        Raises:
            ConfigurationError: If hotkey config file cannot be loaded or parsed
        """
        ...

    def validate_config(self) -> bool:
        """Validate all configuration files.

        Returns:
            True if all configurations are valid

        Raises:
            ConfigurationError: If any configuration is invalid
        """
        ...


class IOManagerProtocol(Protocol):
    """Protocol for input/output operations."""

    def get_input_text(self) -> str:
        """Get input text from appropriate source.

        Returns:
            Input text from clipboard, pipe, or manual input

        Raises:
            IOError: If input cannot be retrieved
        """
        ...

    def get_clipboard_text(self) -> str:
        """Get text from clipboard.

        Returns:
            Current clipboard text content

        Raises:
            ClipboardError: If clipboard access fails
        """
        ...

    @staticmethod
    def set_output_text(text: str) -> None:
        """Set output text to clipboard.

        Args:
            text: Text to copy to clipboard

        Raises:
            ClipboardError: If clipboard write fails
        """
        ...

    def get_pipe_input(self) -> str | None:
        """Get input from pipe if available.

        Returns:
            Piped input text or None if no pipe input
        """
        ...


@runtime_checkable
class TransformationEngineProtocol(Protocol):
    """Protocol for text transformation operations."""

    config_manager: ConfigManagerProtocol
    crypto_manager: CryptoManagerProtocol | None

    def apply_transformations(self, text: str, rule_string: str) -> str:
        """Apply transformation rules to text.

        Args:
            text: Input text to transform
            rule_string: Rule string (e.g., '/t/l/u')

        Returns:
            Transformed text

        Raises:
            ValidationError: If input parameters are invalid
            TransformationError: If transformation fails
        """
        ...

    def parse_rule_string(self, rule_string: str) -> RuleList:
        """Parse rule string into list of (rule, arguments) tuples.

        Args:
            rule_string: Rule string to parse (e.g., '/t/l/r "old" "new"')

        Returns:
            List of (rule_name, arguments) tuples

        Raises:
            ValidationError: If rule string format is invalid
        """
        ...

    def get_available_rules(self) -> RuleDict:
        """Get all available transformation rules.

        Returns:
            Dictionary mapping rule names to TransformationRule objects
        """
        ...

    def set_crypto_manager(self, crypto_manager: CryptoManagerProtocol) -> None:
        """Set the cryptography manager for encryption/decryption operations.

        Args:
            crypto_manager: Cryptography manager instance
        """
        ...

    def validate_rule_string(self, rule_string: str) -> ValidationResult:
        """Validate rule string format.

        Args:
            rule_string: Rule string to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        ...

    def get_rule_help(self, rule_name: str | None = None) -> str:
        """Get help information for rules.

        Args:
            rule_name: Specific rule name or None for all rules

        Returns:
            Help text for the rule(s)
        """
        ...


@runtime_checkable
class CryptoManagerProtocol(Protocol):
    """Protocol for cryptography operations."""

    def encrypt_text(self, text: str) -> str:
        """Encrypt text using RSA.

        Args:
            text: Plain text to encrypt

        Returns:
            Base64 encoded encrypted text

        Raises:
            CryptographyError: If encryption fails
        """
        ...

    def decrypt_text(self, text: str) -> str:
        """Decrypt text using RSA.

        Args:
            text: Base64 encoded encrypted text

        Returns:
            Decrypted plain text

        Raises:
            CryptographyError: If decryption fails
        """
        ...

    def generate_key_pair(self) -> None:
        """Generate new RSA key pair.

        Raises:
            CryptographyError: If key generation fails
        """
        ...

    def load_keys(self) -> bool:
        """Load existing RSA key pair.

        Returns:
            True if keys loaded successfully, False otherwise
        """
        ...


class ClipboardMonitorProtocol(Protocol):
    """Protocol for clipboard monitoring operations."""

    io_manager: IOManagerProtocol
    is_monitoring: bool
    last_content: str
    check_interval: float
    max_content_size: int

    def start_monitoring(self, change_callback: ThreadCallback = None) -> None:
        """Start clipboard monitoring in background.

        Args:
            change_callback: Optional callback function called when clipboard changes

        Raises:
            ClipboardError: If monitoring cannot be started
        """
        ...

    def stop_monitoring(self) -> None:
        """Stop clipboard monitoring.

        Raises:
            ClipboardError: If monitoring cannot be stopped
        """
        ...

    def check_for_changes(self) -> bool:
        """Check for clipboard changes manually.

        Returns:
            True if clipboard content has changed

        Raises:
            ClipboardError: If clipboard check fails
        """
        ...

    def set_check_interval(self, interval: float) -> None:
        """Set clipboard check interval.

        Args:
            interval: Check interval in seconds (minimum 0.1)

        Raises:
            ValidationError: If interval is invalid
        """
        ...

    def set_max_content_size(self, size: int) -> None:
        """Set maximum clipboard content size.

        Args:
            size: Maximum size in bytes (minimum 1024)

        Raises:
            ValidationError: If size is invalid
        """
        ...


class InteractiveModeProtocol(Protocol):
    """Protocol for interactive mode operations."""

    def run(self) -> None:
        """Run interactive mode.

        Raises:
            InteractiveModeError: If interactive mode fails
        """
        ...

    def process_command(self, command: str) -> CommandResult:
        """Process user command.

        Args:
            command: User input command

        Returns:
            Command processing result
        """
        ...

    def display_help(self) -> None:
        """Display help information."""
        ...

    def display_status(self) -> None:
        """Display current session status."""
        ...


class DaemonModeProtocol(Protocol):
    """Protocol for daemon mode operations."""

    def start_daemon(self) -> None:
        """Start daemon mode.

        Raises:
            DaemonModeError: If daemon mode fails to start
        """
        ...

    def stop_daemon(self) -> None:
        """Stop daemon mode.

        Raises:
            DaemonModeError: If daemon mode fails to stop
        """
        ...

    def is_running(self) -> bool:
        """Check if daemon is running.

        Returns:
            True if daemon is active
        """
        ...


# TypeGuard functions for runtime validation
def is_valid_config_dict(obj: Any) -> TypeGuard[ConfigDict]:
    """Type guard for configuration dictionary validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid configuration dictionary
    """
    return isinstance(obj, dict) and all(isinstance(k, str) for k in obj.keys())


def is_valid_rule_string(obj: Any) -> TypeGuard[str]:
    """Type guard for rule string validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid rule string
    """
    return isinstance(obj, str) and bool(obj.strip()) and obj.startswith("/")


def is_valid_text_input(obj: Any) -> TypeGuard[str]:
    """Type guard for text input validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is valid text input
    """
    return isinstance(obj, str)


def is_transformation_rule(obj: Any) -> TypeGuard[TransformationRule]:
    """Type guard for TransformationRule validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid TransformationRule
    """
    return (
        isinstance(obj, TransformationRule)
        and hasattr(obj, "name")
        and hasattr(obj, "function")
        and callable(obj.function)
    )


# Additional TypeGuard functions for comprehensive runtime validation


def is_session_state(obj: Any) -> TypeGuard[SessionState]:
    """Type guard for SessionState validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid SessionState
    """
    return (
        isinstance(obj, SessionState)
        and hasattr(obj, "current_text")
        and hasattr(obj, "text_source")
        and hasattr(obj, "last_update_time")
        and isinstance(obj.current_text, str)
        and isinstance(obj.text_source, TextSource)
        and isinstance(obj.last_update_time, datetime)
    )


def is_command_result(obj: Any) -> TypeGuard[CommandResult]:
    """Type guard for CommandResult validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid CommandResult
    """
    return (
        isinstance(obj, CommandResult)
        and hasattr(obj, "success")
        and hasattr(obj, "message")
        and isinstance(obj.success, bool)
        and isinstance(obj.message, str)
    )


def is_rule_list(obj: Any) -> TypeGuard[RuleList]:
    """Type guard for RuleList validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid RuleList
    """
    return isinstance(obj, list) and all(
        isinstance(item, tuple)
        and len(item) == 2
        and isinstance(item[0], str)
        and isinstance(item[1], list)
        and all(isinstance(arg, str) for arg in item[1])
        for item in obj
    )


def is_rule_dict(obj: Any) -> TypeGuard[RuleDict]:
    """Type guard for RuleDict validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid RuleDict
    """
    return (
        isinstance(obj, dict)
        and all(isinstance(k, str) for k in obj.keys())
        and all(is_transformation_rule(v) for v in obj.values())
    )


def is_error_context(obj: Any) -> TypeGuard[ErrorContext]:
    """Type guard for ErrorContext validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid ErrorContext
    """
    return isinstance(obj, dict) and all(isinstance(k, str) for k in obj.keys())


def is_validation_result(obj: Any) -> TypeGuard[ValidationResult]:
    """Type guard for ValidationResult validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid ValidationResult
    """
    return (
        isinstance(obj, tuple)
        and len(obj) == 2
        and isinstance(obj[0], bool)
        and (obj[1] is None or isinstance(obj[1], str))
    )


def is_text_source(obj: Any) -> TypeGuard[TextSource]:
    """Type guard for TextSource validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid TextSource
    """
    return isinstance(obj, TextSource)


def is_transformation_rule_type(obj: Any) -> TypeGuard[TransformationRuleType]:
    """Type guard for TransformationRuleType validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid TransformationRuleType
    """
    return isinstance(obj, TransformationRuleType)


def is_thread_callback(obj: Any) -> TypeGuard[ThreadCallback]:
    """Type guard for ThreadCallback validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid ThreadCallback
    """
    return obj is None or (callable(obj) and callable(obj))


def is_config_manager(obj: Any) -> TypeGuard[ConfigManagerProtocol]:
    """Type guard for ConfigManagerProtocol validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj implements ConfigManagerProtocol
    """
    return (
        hasattr(obj, "load_transformation_rules")
        and hasattr(obj, "load_security_config")
        and hasattr(obj, "load_hotkey_config")
        and hasattr(obj, "validate_config")
        and callable(obj.load_transformation_rules)
        and callable(obj.load_security_config)
        and callable(obj.load_hotkey_config)
        and callable(obj.validate_config)
    )


def is_io_manager(obj: Any) -> TypeGuard[IOManagerProtocol]:
    """Type guard for IOManagerProtocol validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj implements IOManagerProtocol
    """
    return (
        hasattr(obj, "get_input_text")
        and hasattr(obj, "get_clipboard_text")
        and hasattr(obj, "set_output_text")
        and hasattr(obj, "get_pipe_input")
        and callable(obj.get_input_text)
        and callable(obj.get_clipboard_text)
        and callable(obj.set_output_text)
        and callable(obj.get_pipe_input)
    )


def is_transformation_engine(obj: Any) -> TypeGuard[TransformationEngineProtocol]:
    """Type guard for TransformationEngineProtocol validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj implements TransformationEngineProtocol
    """
    return (
        hasattr(obj, "apply_transformations")
        and hasattr(obj, "parse_rule_string")
        and hasattr(obj, "get_available_rules")
        and hasattr(obj, "set_crypto_manager")
        and callable(obj.apply_transformations)
        and callable(obj.parse_rule_string)
        and callable(obj.get_available_rules)
        and callable(obj.set_crypto_manager)
    )


def is_crypto_manager(obj: Any) -> TypeGuard[CryptoManagerProtocol]:
    """Type guard for CryptoManagerProtocol validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj implements CryptoManagerProtocol
    """
    return (
        hasattr(obj, "encrypt_text")
        and hasattr(obj, "decrypt_text")
        and hasattr(obj, "generate_key_pair")
        and hasattr(obj, "load_keys")
        and callable(obj.encrypt_text)
        and callable(obj.decrypt_text)
        and callable(obj.generate_key_pair)
        and callable(obj.load_keys)
    )


def is_clipboard_monitor(obj: Any) -> TypeGuard[ClipboardMonitorProtocol]:
    """Type guard for ClipboardMonitorProtocol validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj implements ClipboardMonitorProtocol
    """
    return (
        hasattr(obj, "start_monitoring")
        and hasattr(obj, "stop_monitoring")
        and hasattr(obj, "check_for_changes")
        and hasattr(obj, "is_monitoring")
        and callable(obj.start_monitoring)
        and callable(obj.stop_monitoring)
        and callable(obj.check_for_changes)
    )


# Complex validation TypeGuards for nested data structures


def is_daemon_config(obj: Any) -> TypeGuard[dict[str, Any]]:
    """Type guard for daemon configuration validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid daemon configuration
    """
    if not isinstance(obj, dict):
        return False

    # Check required sections
    required_sections = ["daemon_mode", "clipboard_monitoring", "auto_transformation"]
    if not all(section in obj for section in required_sections):
        return False

    # Validate daemon_mode section
    daemon_mode = obj.get("daemon_mode", {})
    if not isinstance(daemon_mode, dict):
        return False

    # Validate clipboard_monitoring section
    clipboard_monitoring = obj.get("clipboard_monitoring", {})
    if not isinstance(clipboard_monitoring, dict):
        return False

    # Validate auto_transformation section
    auto_transformation = obj.get("auto_transformation", {})
    if not isinstance(auto_transformation, dict):
        return False

    return True


def is_security_config(obj: Any) -> TypeGuard[dict[str, Any]]:
    """Type guard for security configuration validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid security configuration
    """
    if not isinstance(obj, dict):
        return False

    # Check for expected security configuration structure
    # This is flexible to allow for different security configurations
    return all(isinstance(k, str) for k in obj.keys())


def is_transformation_rules_config(obj: Any) -> TypeGuard[dict[str, Any]]:
    """Type guard for transformation rules configuration validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid transformation rules configuration
    """
    if not isinstance(obj, dict):
        return False

    # Validate that all keys are strings and values are appropriate
    return all(isinstance(k, str) for k in obj.keys())


def is_hotkey_config(obj: Any) -> TypeGuard[dict[str, Any]]:
    """Type guard for hotkey configuration validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a valid hotkey configuration
    """
    if not isinstance(obj, dict):
        return False

    # Check for expected hotkey configuration structure
    # This is flexible to allow for different hotkey configurations
    return all(isinstance(k, str) for k in obj.keys())


def is_list_of_strings(obj: Any) -> TypeGuard[list[str]]:
    """Type guard for list of strings validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a list of strings
    """
    return isinstance(obj, list) and all(isinstance(item, str) for item in obj)


def is_dict_of_strings(obj: Any) -> TypeGuard[dict[str, str]]:
    """Type guard for dictionary of strings validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a dictionary with string keys and values
    """
    return isinstance(obj, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in obj.items()
    )


def is_numeric_value(obj: Any) -> TypeGuard[int | float]:
    """Type guard for numeric value validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a numeric value (int or float)
    """
    return isinstance(obj, (int, float))


def is_positive_number(obj: Any) -> TypeGuard[int | float]:
    """Type guard for positive number validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a positive number
    """
    return is_numeric_value(obj) and obj > 0


def is_non_empty_string(obj: Any) -> TypeGuard[str]:
    """Type guard for non-empty string validation.

    Args:
        obj: Object to validate

    Returns:
        True if obj is a non-empty string
    """
    return isinstance(obj, str) and bool(obj.strip())


# Generic base classes for type-safe operations


class ConfigurableComponent(Generic[ConfigT]):
    """Base class for components that require configuration.

    This class provides a common interface for components that need
    configuration management with type safety.
    """

    def __init__(self, config: ConfigT) -> None:
        """Initialize configurable component.

        Args:
            config: Configuration object
        """
        self.config: ConfigT = config

    def validate_config(self) -> bool:
        """Validate the configuration. Override in subclasses.

        Returns:
            True if configuration is valid
        """
        return isinstance(self.config, dict)

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value with default fallback.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if isinstance(self.config, dict):
            return self.config.get(key, default)
        return default


class DataProcessor(Generic[T]):
    """Generic data processor for type-safe data transformations.

    This class provides a reusable pattern for processing data of any type
    with validation and error handling.
    """

    def __init__(self, validator: Callable[[Any], TypeGuard[T]] | None = None) -> None:
        """Initialize data processor.

        Args:
            validator: Optional type guard function for input validation
        """
        self.validator: Callable[[Any], TypeGuard[T]] | None = validator
        self.processed_count: int = 0
        self.error_count: int = 0

    def process(self, data: Any, processor_func: Callable[[T], T]) -> T:
        """Process data with type safety.

        Args:
            data: Input data to process
            processor_func: Function to apply to validated data

        Returns:
            Processed data of type T

        Raises:
            ValidationError: If data validation fails
        """
        if self.validator and not self.validator(data):
            self.error_count += 1
            raise ValidationError("Data validation failed for provided type")

        try:
            result = processor_func(data)
            self.processed_count += 1
            return result
        except Exception as e:
            self.error_count += 1
            raise ValidationError(f"Processing failed: {e}") from e

    def get_stats(self) -> dict[str, int]:
        """Get processing statistics.

        Returns:
            Dictionary with processing statistics
        """
        return {
            "processed_count": self.processed_count,
            "error_count": self.error_count,
        }


class ResultContainer(Generic[T]):
    """Generic container for operation results with error handling.

    This class provides a type-safe way to handle operation results
    that may succeed or fail.
    """

    def __init__(self, success: bool, data: T | None = None, error: str | None = None) -> None:
        """Initialize result container.

        Args:
            success: Whether the operation was successful
            data: Result data if successful
            error: Error message if failed
        """
        self.success: bool = success
        self.data: T | None = data
        self.error: str | None = error
        self.timestamp: datetime = datetime.now()

    def is_success(self) -> bool:
        """Check if result represents success.

        Returns:
            True if operation was successful
        """
        return self.success

    def get_data(self) -> T:
        """Get result data.

        Returns:
            Result data

        Raises:
            ValidationError: If result was not successful
        """
        if not self.success:
            raise ValidationError(f"Cannot get data from failed result: {self.error}")
        if self.data is None:
            raise ValidationError("Result data is None despite success status")
        return self.data

    def get_error(self) -> str:
        """Get error message.

        Returns:
            Error message or empty string if successful
        """
        return self.error or ""

    @classmethod
    def success_result(cls, data: T) -> ResultContainer[T]:
        """Create a successful result.

        Args:
            data: Result data

        Returns:
            Successful ResultContainer
        """
        return cls(success=True, data=data)

    @classmethod
    def error_result(cls, error: str) -> ResultContainer[T]:
        """Create an error result.

        Args:
            error: Error message

        Returns:
            Failed ResultContainer
        """
        return cls(success=False, error=error)


class StateManager(Generic[T]):
    """Generic state manager for type-safe state handling.

    This class provides a reusable pattern for managing application state
    with validation and change tracking.
    """

    def __init__(self, initial_state: T, validator: Callable[[T], bool] | None = None) -> None:
        """Initialize state manager.

        Args:
            initial_state: Initial state value
            validator: Optional state validation function
        """
        self.validator: Callable[[T], bool] | None = validator
        self._current_state: T = initial_state
        self._previous_state: T | None = None
        self._change_count: int = 0
        self._last_change_time: datetime = datetime.now()

        if self.validator and not self.validator(initial_state):
            raise ValidationError("Initial state validation failed")

    def get_state(self) -> T:
        """Get current state.

        Returns:
            Current state value
        """
        return self._current_state

    def set_state(self, new_state: T) -> bool:
        """Set new state with validation.

        Args:
            new_state: New state value

        Returns:
            True if state was changed successfully

        Raises:
            ValidationError: If state validation fails
        """
        if self.validator and not self.validator(new_state):
            raise ValidationError("State validation failed")

        if new_state != self._current_state:
            self._previous_state = self._current_state
            self._current_state = new_state
            self._change_count += 1
            self._last_change_time = datetime.now()
            return True

        return False

    def get_previous_state(self) -> T | None:
        """Get previous state.

        Returns:
            Previous state value or None if no previous state
        """
        return self._previous_state

    def revert_state(self) -> bool:
        """Revert to previous state.

        Returns:
            True if state was reverted successfully
        """
        if self._previous_state is not None:
            temp_state = self._current_state
            self._current_state = self._previous_state
            self._previous_state = temp_state
            self._change_count += 1
            self._last_change_time = datetime.now()
            return True
        return False

    def get_change_count(self) -> int:
        """Get number of state changes.

        Returns:
            Number of state changes
        """
        return self._change_count

    def get_last_change_time(self) -> datetime:
        """Get timestamp of last state change.

        Returns:
            Timestamp of last change
        """
        return self._last_change_time


class CacheManager(Generic[T]):
    """Generic cache manager for type-safe caching operations.

    This class provides a reusable caching pattern with TTL support
    and type safety.
    """

    def __init__(self, default_ttl: float = 300.0) -> None:
        """Initialize cache manager.

        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl: float = default_ttl
        self._cache: dict[str, tuple[T, datetime]] = {}
        self._hit_count: int = 0
        self._miss_count: int = 0

    def get(self, key: str) -> T | None:
        """Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            if (datetime.now() - timestamp).total_seconds() <= self.default_ttl:
                self._hit_count += 1
                return value
            else:
                # Remove expired entry
                del self._cache[key]

        self._miss_count += 1
        return None

    def set(self, key: str, value: T, ttl: float | None = None) -> None:
        """Set cached value.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        self._cache[key] = (value, datetime.now())

    def invalidate(self, key: str) -> bool:
        """Invalidate cached value.

        Args:
            key: Cache key to invalidate

        Returns:
            True if key was found and removed
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        self._hit_count = 0
        self._miss_count = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._hit_count + self._miss_count
        hit_rate = (self._hit_count / total_requests) if total_requests > 0 else 0.0

        return {
            "size": len(self._cache),
            "hit_count": self._hit_count,
            "miss_count": self._miss_count,
            "hit_rate": hit_rate,
        }


class RuleProcessor(Generic[T]):
    """Generic rule processor for type-safe rule application.

    This class provides a reusable pattern for applying rules to data
    with validation and error handling.
    """

    def __init__(self, rule_validator: Callable[[str], bool] | None = None) -> None:
        """Initialize rule processor.

        Args:
            rule_validator: Optional rule validation function
        """
        self.rule_validator: Callable[[str], bool] | None = rule_validator
        self.applied_rules: list[str] = []
        self.processing_stats: dict[str, int] = {"success": 0, "failed": 0}

    def apply_rule(
        self, data: T, rule: str, rule_func: Callable[[T, str], T]
    ) -> ResultContainer[T]:
        """Apply a rule to data with type safety.

        Args:
            data: Input data
            rule: Rule string to apply
            rule_func: Function that applies the rule

        Returns:
            ResultContainer with the result
        """
        if self.rule_validator and not self.rule_validator(rule):
            self.processing_stats["failed"] += 1
            return ResultContainer.error_result(f"Rule validation failed: {rule}")

        try:
            result = rule_func(data, rule)
            self.applied_rules.append(rule)
            self.processing_stats["success"] += 1
            return ResultContainer.success_result(result)
        except Exception as e:
            self.processing_stats["failed"] += 1
            return ResultContainer.error_result(f"Rule application failed: {e}")

    def get_applied_rules(self) -> list[str]:
        """Get list of successfully applied rules.

        Returns:
            List of applied rule strings
        """
        return self.applied_rules.copy()

    def get_processing_stats(self) -> dict[str, int]:
        """Get rule processing statistics.

        Returns:
            Dictionary with processing statistics
        """
        return self.processing_stats.copy()


class ConfigurationContainer(Generic[ConfigT]):
    """Generic configuration container with validation and defaults.

    This class provides a type-safe way to handle configuration data
    with validation, defaults, and change tracking.
    """

    def __init__(
        self,
        config: ConfigT,
        defaults: ConfigT | None = None,
        validator: Callable[[ConfigT], bool] | None = None,
    ) -> None:
        """Initialize configuration container.

        Args:
            config: Configuration data
            defaults: Default configuration values
            validator: Optional configuration validator
        """
        self.defaults: ConfigT | None = defaults
        self.validator: Callable[[ConfigT], bool] | None = validator
        self._config: ConfigT = config
        self._is_modified: bool = False
        self._modification_time: datetime = datetime.now()

        if self.validator and not self.validator(config):
            raise ValidationError("Configuration validation failed")

    def get_config(self) -> ConfigT:
        """Get current configuration.

        Returns:
            Current configuration data
        """
        return self._config

    def update_config(self, new_config: ConfigT) -> bool:
        """Update configuration with validation.

        Args:
            new_config: New configuration data

        Returns:
            True if configuration was updated

        Raises:
            ValidationError: If validation fails
        """
        if self.validator and not self.validator(new_config):
            raise ValidationError("Configuration validation failed")

        if new_config != self._config:
            self._config = new_config
            self._is_modified = True
            self._modification_time = datetime.now()
            return True

        return False

    def is_modified(self) -> bool:
        """Check if configuration has been modified.

        Returns:
            True if configuration has been modified
        """
        return self._is_modified

    def get_modification_time(self) -> datetime:
        """Get last modification time.

        Returns:
            Timestamp of last modification
        """
        return self._modification_time

    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults.

        Returns:
            True if reset was successful

        Raises:
            ValidationError: If no defaults are available
        """
        if self.defaults is None:
            raise ValidationError("No default configuration available")

        return self.update_config(self.defaults)


# Enhanced Protocol definitions for comprehensive structural typing


class TextProcessorProtocol(Protocol):
    """Protocol for text processing operations."""

    def process_text(self, text: str) -> str:
        """Process text and return result.

        Args:
            text: Input text to process

        Returns:
            Processed text
        """
        ...

    def validate_input(self, text: str) -> bool:
        """Validate input text.

        Args:
            text: Text to validate

        Returns:
            True if text is valid for processing
        """
        ...


class StateManagerProtocol(Protocol):
    """Protocol for state management operations."""

    def get_current_state(self) -> Any:
        """Get current state.

        Returns:
            Current state value
        """
        ...

    def set_state(self, state: Any) -> bool:
        """Set new state.

        Args:
            state: New state value

        Returns:
            True if state was set successfully
        """
        ...

    def validate_state(self, state: Any) -> bool:
        """Validate state value.

        Args:
            state: State to validate

        Returns:
            True if state is valid
        """
        ...


class CacheProtocol(Protocol):
    """Protocol for caching operations."""

    def get(self, key: str) -> Any | None:
        """Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        ...

    def set(self, key: str, value: Any) -> None:
        """Set cached value.

        Args:
            key: Cache key
            value: Value to cache
        """
        ...

    def invalidate(self, key: str) -> bool:
        """Invalidate cached value.

        Args:
            key: Cache key

        Returns:
            True if key was invalidated
        """
        ...

    def clear(self) -> None:
        """Clear all cached values."""
        ...


class ValidationProtocol(Protocol):
    """Protocol for validation operations."""

    def validate(self, data: Any) -> ValidationResult:
        """Validate data.

        Args:
            data: Data to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        ...

    def get_validation_rules(self) -> dict[str, Any]:
        """Get validation rules.

        Returns:
            Dictionary of validation rules
        """
        ...


class EventHandlerProtocol(Protocol):
    """Protocol for event handling operations."""

    def handle_event(self, event_type: str, event_data: Any) -> bool:
        """Handle an event.

        Args:
            event_type: Type of event
            event_data: Event data

        Returns:
            True if event was handled successfully
        """
        ...

    def register_handler(self, event_type: str, handler: Callable[[Any], bool]) -> None:
        """Register event handler.

        Args:
            event_type: Type of event to handle
            handler: Handler function
        """
        ...

    def unregister_handler(self, event_type: str) -> bool:
        """Unregister event handler.

        Args:
            event_type: Type of event

        Returns:
            True if handler was unregistered
        """
        ...


class LoggerProtocol(Protocol):
    """Protocol for logging operations."""

    def log(self, level: str, message: str, context: dict[str, Any] | None = None) -> None:
        """Log a message.

        Args:
            level: Log level (debug, info, warning, error)
            message: Log message
            context: Optional context data
        """
        ...

    def debug(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log debug message.

        Args:
            message: Debug message
            context: Optional context data
        """
        ...

    def info(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log info message.

        Args:
            message: Info message
            context: Optional context data
        """
        ...

    def warning(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log warning message.

        Args:
            message: Warning message
            context: Optional context data
        """
        ...

    def error(self, message: str, context: dict[str, Any] | None = None) -> None:
        """Log error message.

        Args:
            message: Error message
            context: Optional context data
        """
        ...


class MonitorProtocol(Protocol):
    """Protocol for monitoring operations."""

    is_monitoring: bool

    def start_monitoring(self, callback: Callable[[Any], None] | None = None) -> None:
        """Start monitoring.

        Args:
            callback: Optional callback for monitoring events
        """
        ...

    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        ...

    def get_monitoring_status(self) -> dict[str, Any]:
        """Get monitoring status.

        Returns:
            Dictionary with monitoring status information
        """
        ...


class SerializerProtocol(Protocol):
    """Protocol for serialization operations."""

    def serialize(self, data: Any) -> str:
        """Serialize data to string.

        Args:
            data: Data to serialize

        Returns:
            Serialized string representation
        """
        ...

    def deserialize(self, data: str) -> Any:
        """Deserialize string to data.

        Args:
            data: Serialized string data

        Returns:
            Deserialized data object
        """
        ...

    def validate_serialized(self, data: str) -> bool:
        """Validate serialized data format.

        Args:
            data: Serialized data to validate

        Returns:
            True if data format is valid
        """
        ...


class PluginProtocol(Protocol):
    """Protocol for plugin system operations."""

    name: str
    version: str

    def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize plugin.

        Args:
            config: Plugin configuration

        Returns:
            True if initialization was successful
        """
        ...

    def execute(self, input_data: Any) -> Any:
        """Execute plugin functionality.

        Args:
            input_data: Input data for plugin

        Returns:
            Plugin execution result
        """
        ...

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        ...

    def get_capabilities(self) -> list[str]:
        """Get plugin capabilities.

        Returns:
            List of capability names
        """
        ...


class SecurityProtocol(Protocol):
    """Protocol for security operations."""

    def authenticate(self, credentials: dict[str, Any]) -> bool:
        """Authenticate user credentials.

        Args:
            credentials: User credentials

        Returns:
            True if authentication successful
        """
        ...

    def authorize(self, user: str, resource: str, action: str) -> bool:
        """Authorize user action on resource.

        Args:
            user: User identifier
            resource: Resource identifier
            action: Action to authorize

        Returns:
            True if action is authorized
        """
        ...

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data.

        Args:
            data: Data to encrypt

        Returns:
            Encrypted data
        """
        ...

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data.

        Args:
            encrypted_data: Encrypted data

        Returns:
            Decrypted data
        """
        ...


# Application-specific Protocol definitions for dependency injection


class ApplicationProtocol(Protocol):
    """Protocol for main application interface."""

    def initialize(self, args: list[str] | None = None) -> bool:
        """Initialize application with command line arguments.

        Args:
            args: Command line arguments

        Returns:
            True if initialization successful
        """
        ...

    def run(self) -> int:
        """Run the application.

        Returns:
            Exit code (0 for success)
        """
        ...

    def shutdown(self) -> None:
        """Shutdown application gracefully."""
        ...


class SessionProtocol(Protocol):
    """Protocol for session management."""

    current_text: str
    text_source: TextSource

    def initialize_with_text(self, text: str, source: str) -> None:
        """Initialize session with text.

        Args:
            text: Initial text
            source: Text source
        """
        ...

    def update_working_text(self, text: str, source: str) -> None:
        """Update working text.

        Args:
            text: New text
            source: Text source
        """
        ...

    def get_status_info(self) -> SessionState:
        """Get session status.

        Returns:
            Current session state
        """
        ...

    def cleanup(self) -> None:
        """Clean up session resources."""
        ...


class CommandProcessorProtocol(Protocol):
    """Protocol for command processing."""

    def is_command(self, input_text: str) -> bool:
        """Check if input is a command.

        Args:
            input_text: Input text to check

        Returns:
            True if input is a command
        """
        ...

    def process_command(self, command: str) -> CommandResult:
        """Process command.

        Args:
            command: Command to process

        Returns:
            Command result
        """
        ...

    def get_available_commands(self) -> dict[str, str]:
        """Get available commands.

        Returns:
            Dictionary of command names and descriptions
        """
        ...


class ModeProtocol(Protocol):
    """Protocol for application modes."""

    def start(self) -> None:
        """Start the mode."""
        ...

    def stop(self) -> None:
        """Stop the mode."""
        ...

    def is_running(self) -> bool:
        """Check if mode is running.

        Returns:
            True if mode is active
        """
        ...

    def get_status(self) -> dict[str, Any]:
        """Get mode status.

        Returns:
            Status information
        """
        ...


class RuleEngineProtocol(Protocol):
    """Protocol for rule engine operations."""

    def register_rule(self, name: str, rule: TransformationRule) -> bool:
        """Register a transformation rule.

        Args:
            name: Rule name
            rule: Rule definition

        Returns:
            True if rule was registered successfully
        """
        ...

    def unregister_rule(self, name: str) -> bool:
        """Unregister a transformation rule.

        Args:
            name: Rule name

        Returns:
            True if rule was unregistered
        """
        ...

    def get_rule(self, name: str) -> TransformationRule | None:
        """Get rule by name.

        Args:
            name: Rule name

        Returns:
            Rule definition or None if not found
        """
        ...

    def list_rules(self, rule_type: TransformationRuleType | None = None) -> list[str]:
        """List available rules.

        Args:
            rule_type: Optional rule type filter

        Returns:
            List of rule names
        """
        ...


# Helper functions for type-safe validation using TypeGuards


def validate_and_cast_config(obj: Any) -> ConfigDict:
    """Validate and cast object to ConfigDict.

    Args:
        obj: Object to validate and cast

    Returns:
        Validated ConfigDict

    Raises:
        ValidationError: If validation fails
    """
    if not is_valid_config_dict(obj):
        raise ValidationError(
            f"Invalid configuration dictionary: expected dict[str, Any], got {type(obj).__name__}",
            {"object_type": type(obj).__name__},
        )
    return obj


def validate_and_cast_rule_string(obj: Any) -> str:
    """Validate and cast object to rule string.

    Args:
        obj: Object to validate and cast

    Returns:
        Validated rule string

    Raises:
        ValidationError: If validation fails
    """
    if not is_valid_rule_string(obj):
        raise ValidationError(
            f"Invalid rule string: expected string starting with '/', got {type(obj).__name__}",
            {"object_type": type(obj).__name__, "value": str(obj)[:50]},
        )
    return obj


def validate_and_cast_text_input(obj: Any) -> str:
    """Validate and cast object to text input.

    Args:
        obj: Object to validate and cast

    Returns:
        Validated text input

    Raises:
        ValidationError: If validation fails
    """
    if not is_valid_text_input(obj):
        raise ValidationError(
            f"Invalid text input: expected string, got {type(obj).__name__}",
            {"object_type": type(obj).__name__},
        )
    return obj


def validate_protocol_implementation(obj: Any, protocol_name: str) -> bool:
    """Validate that an object implements a specific protocol.

    Args:
        obj: Object to validate
        protocol_name: Name of the protocol to check

    Returns:
        True if object implements the protocol

    Raises:
        ValidationError: If protocol is unknown
    """
    protocol_validators: dict[str, Callable[[Any], bool]] = {
        "ConfigManagerProtocol": is_config_manager,
        "IOManagerProtocol": is_io_manager,
        "TransformationEngineProtocol": is_transformation_engine,
        "CryptoManagerProtocol": is_crypto_manager,
        "ClipboardMonitorProtocol": is_clipboard_monitor,
    }

    if protocol_name not in protocol_validators:
        raise ValidationError(
            f"Unknown protocol: {protocol_name}",
            {
                "protocol_name": protocol_name,
                "available_protocols": list(protocol_validators.keys()),
            },
        )

    return protocol_validators[protocol_name](obj)


def safe_cast_with_validation(
    obj: Any, target_type: type, validator: Callable[[Any], bool]
) -> Any:
    """Safely cast object to target type with validation.

    Args:
        obj: Object to cast
        target_type: Target type for casting
        validator: TypeGuard function for validation

    Returns:
        Validated and cast object

    Raises:
        ValidationError: If validation fails
    """
    if not validator(obj):
        raise ValidationError(
            f"Validation failed for type {target_type.__name__}: got {type(obj).__name__}",
            {"target_type": target_type.__name__, "actual_type": type(obj).__name__},
        )
    return obj


def validate_configuration_structure(config: Any, required_keys: list[str]) -> ConfigDict:
    """Validate configuration structure with required keys.

    Args:
        config: Configuration to validate
        required_keys: List of required configuration keys

    Returns:
        Validated configuration dictionary

    Raises:
        ValidationError: If validation fails
    """
    if not is_valid_config_dict(config):
        raise ValidationError("Invalid configuration dictionary format")

    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValidationError(
            f"Missing required configuration keys: {missing_keys}",
            {"missing_keys": missing_keys, "required_keys": required_keys},
        )

    return config


def validate_rule_arguments(
    args: Any, min_args: int = 0, max_args: int | None = None
) -> list[str]:
    """Validate rule arguments structure.

    Args:
        args: Arguments to validate
        min_args: Minimum number of arguments required
        max_args: Maximum number of arguments allowed (None for unlimited)

    Returns:
        Validated arguments list

    Raises:
        ValidationError: If validation fails
    """
    if not is_list_of_strings(args):
        raise ValidationError(
            f"Rule arguments must be a list of strings, got {type(args).__name__}",
            {"args_type": type(args).__name__},
        )

    if len(args) < min_args:
        raise ValidationError(
            f"Insufficient arguments: expected at least {min_args}, got {len(args)}",
            {"expected_min": min_args, "actual": len(args)},
        )

    if max_args is not None and len(args) > max_args:
        raise ValidationError(
            f"Too many arguments: expected at most {max_args}, got {len(args)}",
            {"expected_max": max_args, "actual": len(args)},
        )

    return args
