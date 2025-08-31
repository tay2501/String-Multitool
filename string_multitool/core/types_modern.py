"""
Modern type definitions using Python 3.12+ features.

This module provides type definitions that leverage the latest Python 3.12+
typing features including PEP 695 type parameter syntax, improved generics,
and modern typing constructs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol, Self, TypedDict, override


# PEP 695: Type parameter syntax (Python 3.12+)
type ConfigValue = str | int | float | bool | list[Any] | dict[str, Any] | None
type TransformationResult[T] = T | TransformationError
type RuleApplicator[T, R] = Callable[[T], R]


class TransformationError(Exception):
    """Exception raised during text transformation operations."""
    
    def __init__(self, message: str, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


class ConfigurationDict(TypedDict, total=False):
    """Type-safe configuration dictionary using TypedDict."""
    transformation_rules: dict[str, Any]
    security_config: dict[str, Any]
    daemon_config: dict[str, Any]
    hotkey_config: dict[str, Any]


class TransformationRule(TypedDict):
    """Type-safe transformation rule definition."""
    name: str
    description: str
    example: str | None
    rule_type: str
    enabled: bool


class ModernTransformationBase[T](ABC):
    """Modern base class for transformations using Python 3.12+ generics.
    
    This class demonstrates the new type parameter syntax introduced in PEP 695,
    providing better type safety and cleaner generic definitions.
    """
    
    def __init__(self, input_text: T) -> None:
        """Initialize transformation with input text.
        
        Args:
            input_text: Input text to transform
        """
        self._input_text = input_text
        self._output_text: T | None = None
    
    @property
    def input_text(self) -> T:
        """Get input text."""
        return self._input_text
    
    @property
    def output_text(self) -> T | None:
        """Get output text."""
        return self._output_text
    
    @abstractmethod
    def transform(self) -> T:
        """Transform the input text.
        
        Returns:
            Transformed text
            
        Raises:
            TransformationError: If transformation fails
        """
        ...
    
    @override
    def __str__(self) -> str:
        """String representation of the transformation."""
        return f"{self.__class__.__name__}(input='{self._input_text}')"


class ConfigManagerProtocol[T](Protocol):
    """Protocol for configuration managers using modern syntax."""
    
    def load_config(self) -> T: ...
    def save_config(self, config: T) -> None: ...
    def get_config_value(self, key: str, default: ConfigValue = None) -> ConfigValue: ...


class CryptoManagerProtocol(Protocol):
    """Protocol for cryptographic operations with enhanced type safety."""
    
    def encrypt_text(self, plaintext: str) -> str: ...
    def decrypt_text(self, ciphertext: str) -> str: ...
    def generate_key_pair(self) -> tuple[bytes, bytes]: ...
    def is_key_pair_available(self) -> bool: ...


class IOManagerProtocol[T](Protocol):
    """Protocol for I/O operations with generic type support."""
    
    def get_input_text(self) -> T: ...
    def set_output_text(self, text: T) -> None: ...
    def get_clipboard_text(self) -> T: ...
    def set_clipboard_text(self, text: T) -> None: ...


class TransformationEngine[InputType, OutputType]:
    """Modern transformation engine with enhanced type safety.
    
    This class demonstrates the use of Python 3.12+ type parameters
    for better generic type support and improved type checking.
    """
    
    def __init__(
        self,
        config_manager: ConfigManagerProtocol[ConfigurationDict],
        crypto_manager: CryptoManagerProtocol | None = None,
    ) -> None:
        """Initialize transformation engine.
        
        Args:
            config_manager: Configuration manager instance
            crypto_manager: Optional crypto manager for encryption operations
        """
        self._config_manager = config_manager
        self._crypto_manager = crypto_manager
        self._rules: dict[str, RuleApplicator[InputType, OutputType]] = {}
    
    def apply_transformation(
        self,
        text: InputType,
        rule_name: str,
    ) -> OutputType:
        """Apply a single transformation rule.
        
        Args:
            text: Input text to transform
            rule_name: Name of the rule to apply
            
        Returns:
            Transformed text
            
        Raises:
            TransformationError: If rule is not found or transformation fails
        """
        try:
            rule = self._rules[rule_name]
            return rule(text)
        except KeyError as e:
            raise TransformationError(
                f"Unknown transformation rule: {rule_name}",
                {"available_rules": list(self._rules.keys())}
            ) from e
        except Exception as e:
            raise TransformationError(
                f"Transformation failed: {e}",
                {"rule_name": rule_name, "input_type": type(text).__name__}
            ) from e
    
    def chain_transformations(
        self,
        text: InputType,
        rule_names: Sequence[str],
    ) -> OutputType:
        """Apply multiple transformation rules in sequence.
        
        Args:
            text: Input text to transform
            rule_names: Sequence of rule names to apply
            
        Returns:
            Final transformed text after all rules applied
        """
        current_text = text
        for rule_name in rule_names:
            # Type narrowing would be handled by the actual implementation
            current_text = self.apply_transformation(current_text, rule_name)  # type: ignore
        return current_text  # type: ignore


class ModernStringTransformation(ModernTransformationBase[str]):
    """Modern string transformation using Python 3.12+ features."""
    
    def __init__(self, input_text: str, operation: Callable[[str], str]) -> None:
        """Initialize with a string operation.
        
        Args:
            input_text: Input string
            operation: Transformation operation to apply
        """
        super().__init__(input_text)
        self._operation = operation
    
    @override
    def transform(self) -> str:
        """Transform the input string.
        
        Returns:
            Transformed string
        """
        try:
            result = self._operation(self._input_text)
            self._output_text = result
            return result
        except Exception as e:
            raise TransformationError(
                f"String transformation failed: {e}",
                {"input_length": len(self._input_text)}
            ) from e


# Factory functions using modern type syntax
def create_transformation[T](
    input_text: T,
    operation: Callable[[T], T],
) -> ModernTransformationBase[T]:
    """Create a transformation instance with type safety.
    
    Args:
        input_text: Input to transform
        operation: Operation to apply
        
    Returns:
        Transformation instance
    """
    if isinstance(input_text, str):
        return ModernStringTransformation(input_text, operation)  # type: ignore
    else:
        raise TypeError(f"Unsupported input type: {type(input_text)}")


# Type aliases using the new syntax
type RuleDefinitionMap = Mapping[str, TransformationRule]
type ConfigurationMap = Mapping[str, ConfigValue]
type TransformationChain[T] = Sequence[RuleApplicator[T, T]]


class AsyncTransformationProtocol[T](Protocol):
    """Protocol for async transformations using modern type syntax."""
    
    async def transform_async(self, text: T) -> T: ...
    async def validate_input(self, text: T) -> bool: ...


# Union types using the modern | syntax (Python 3.10+, enhanced in 3.12)
type ProcessingResult[T] = T | TransformationError | ValueError
type InputSource = Path | str | bytes
type OutputDestination = Path | str | None


class EnhancedValidationMixin:
    """Mixin providing enhanced validation with modern type support."""
    
    def validate_input[T](self, value: T, expected_type: type[T]) -> T:
        """Validate input with generic type checking.
        
        Args:
            value: Value to validate
            expected_type: Expected type
            
        Returns:
            Validated value
            
        Raises:
            TypeError: If value doesn't match expected type
        """
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Expected {expected_type.__name__}, got {type(value).__name__}"
            )
        return value
    
    def ensure_string_input(self, value: Any) -> str:
        """Ensure input is a string with proper error handling.
        
        Args:
            value: Input value
            
        Returns:
            String representation of the value
        """
        if isinstance(value, str):
            return value
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif isinstance(value, bytes):
            try:
                return value.decode('utf-8')
            except UnicodeDecodeError as e:
                raise TransformationError(
                    f"Cannot decode bytes to string: {e}",
                    {"value_type": type(value).__name__}
                ) from e
        else:
            return str(value)


# Modern dataclass-style configuration with enhanced typing
class ModernTransformationConfig:
    """Modern configuration class with enhanced type safety."""
    
    def __init__(
        self,
        rules: RuleDefinitionMap,
        crypto_enabled: bool = False,
        debug_mode: bool = False,
        log_level: str = "INFO",
    ) -> None:
        """Initialize configuration.
        
        Args:
            rules: Rule definitions mapping
            crypto_enabled: Whether cryptographic features are enabled
            debug_mode: Whether debug mode is active
            log_level: Logging level
        """
        self.rules = rules
        self.crypto_enabled = crypto_enabled
        self.debug_mode = debug_mode
        self.log_level = log_level
    
    def get_rule(self, name: str) -> TransformationRule | None:
        """Get rule by name with type safety.
        
        Args:
            name: Rule name
            
        Returns:
            Rule definition or None if not found
        """
        return self.rules.get(name)
    
    def is_rule_enabled(self, name: str) -> bool:
        """Check if rule is enabled.
        
        Args:
            name: Rule name
            
        Returns:
            True if rule exists and is enabled
        """
        rule = self.get_rule(name)
        return rule is not None and rule.get("enabled", False)