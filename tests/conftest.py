"""
Comprehensive pytest configuration and fixtures for String_Multitool.

This module provides modern pytest fixtures following 2024-2025 best practices
with proper scope management and dependency injection patterns.
"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from string_multitool.io.manager import InputOutputManager
from string_multitool.models.config import ConfigurationManager
from string_multitool.models.transformations import TextTransformationEngine


@pytest.fixture(scope="session")
def temp_config_dir() -> Generator[Path, None, None]:
    """Create temporary configuration directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "config"
        config_path.mkdir(exist_ok=True)

        # Create minimal test config files
        transformation_rules = {
            "basic_transformations": {
                "t": {"description": "Trim whitespace", "example": "/t"},
                "l": {"description": "Lowercase", "example": "/l"},
                "u": {"description": "Uppercase", "example": "/u"},
            },
            "case_transformations": {
                "p": {"description": "Pascal case", "example": "/p"},
                "c": {"description": "Camel case", "example": "/c"},
                "s": {"description": "Snake case", "example": "/s"},
            },
            "string_operations": {
                "r": {"description": "Replace text", "example": "/r 'old' 'new'"},
                "S": {"description": "Split lines", "example": "/S '+' "},
            },
            "advanced_rules": {
                "e": {"description": "Encrypt", "example": "/e"},
                "d": {"description": "Decrypt", "example": "/d"},
            },
        }

        security_config = {
            "rsa_encryption": {
                "key_size": 4096,
                "padding": "OAEP",
                "hash_algorithm": "SHA256",
                "key_directory": str(config_path / "keys"),
                "private_key_file": "private_key.pem",
                "public_key_file": "public_key.pem",
            }
        }

        hotkey_config = {"enabled": False, "hotkeys": {}}

        # Write config files
        import json

        (config_path / "transformation_rules.json").write_text(
            json.dumps(transformation_rules, indent=2)
        )
        (config_path / "security_config.json").write_text(json.dumps(security_config, indent=2))
        (config_path / "hotkey_config.json").write_text(json.dumps(hotkey_config, indent=2))

        yield config_path


@pytest.fixture(scope="session")
def mock_clipboard() -> Generator[Mock, None, None]:
    """Mock clipboard functionality with session scope for performance."""
    with patch("string_multitool.io.manager.CLIPBOARD_AVAILABLE", True):
        with patch("string_multitool.io.manager.pyperclip") as mock_pyperclip:
            mock_pyperclip.paste.return_value = "test content"
            mock_pyperclip.copy.return_value = None
            yield mock_pyperclip


@pytest.fixture(scope="session")
def config_manager(temp_config_dir: Path) -> ConfigurationManager:
    """Provide ConfigurationManager with test configuration."""
    return ConfigurationManager(config_dir=temp_config_dir)


@pytest.fixture(scope="session")
def transformation_engine(config_manager: ConfigurationManager) -> TextTransformationEngine:
    """Provide TextTransformationEngine instance for testing."""
    return TextTransformationEngine(config_manager)


@pytest.fixture
def io_manager(mock_clipboard: Mock) -> InputOutputManager:
    """Provide InputOutputManager with mocked clipboard."""
    return InputOutputManager()


@pytest.fixture(
    params=[
        ("Hello World", "/t", "Hello World"),
        ("  Hello World  ", "/t", "Hello World"),
        ("Hello World", "/l", "hello world"),
        ("hello world", "/u", "HELLO WORLD"),
        ("hello_world", "/p", "HelloWorld"),
        ("Hello World", "/c", "helloWorld"),
        ("Hello World", "/s", "hello_world"),
    ]
)
def transformation_test_case(request: pytest.FixtureRequest) -> tuple[str, str, str]:
    """Parametrized fixture providing test cases for transformations."""
    return request.param


@pytest.fixture(
    params=[
        "simple text",
        "text with spaces",
        "TEXT WITH CAPS",
        "123 numbers 456",
        "special!@#$%chars",
        "unicode: こんにちは",
        "multiline\ntext\nhere",
    ]
)
def sample_texts(request: pytest.FixtureRequest) -> str:
    """Parametrized fixture providing various text samples."""
    return request.param


@pytest.fixture
def crypto_manager(config_manager: ConfigurationManager):
    """Mock crypto manager for testing."""
    try:
        from string_multitool.models.crypto import CryptographyManager

        return CryptographyManager(config_manager)
    except (ImportError, TypeError):
        return None


# Modern pytest markers for organizing tests
pytest_markers = [
    "unit: Unit tests for individual components",
    "integration: Integration tests for component interaction",
    "performance: Performance and benchmark tests",
    "security: Security-related tests",
    "edge_cases: Edge case and boundary condition tests",
    "slow: Tests that take significant time to run",
]


def pytest_configure(config):
    """Configure pytest with custom markers."""
    for marker in pytest_markers:
        config.addinivalue_line("markers", marker)


# Exception testing helpers following modern pytest patterns
class ExceptionTestHelper:
    """Helper class for testing exceptions with proper context."""

    @staticmethod
    def assert_validation_error(func, *args, expected_message: str = None, **kwargs):
        """Assert that function raises ValidationError with optional message check."""
        from string_multitool.exceptions import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            func(*args, **kwargs)

        if expected_message:
            assert expected_message in str(exc_info.value)

    @staticmethod
    def assert_transformation_error(func, *args, expected_message: str = None, **kwargs):
        """Assert that function raises TransformationError with optional message check."""
        from string_multitool.exceptions import TransformationError

        with pytest.raises(TransformationError) as exc_info:
            func(*args, **kwargs)

        if expected_message:
            assert expected_message in str(exc_info.value)


@pytest.fixture
def exception_helper() -> ExceptionTestHelper:
    """Provide exception testing helper."""
    return ExceptionTestHelper()


# Performance testing fixture using pytest-benchmark if available
@pytest.fixture
def performance_threshold():
    """Define performance thresholds for benchmark tests."""
    return {
        "transformation_time": 0.01,  # 10ms max for single transformation
        "bulk_transformation_time": 1.0,  # 1s max for 1000 transformations
        "config_load_time": 0.1,  # 100ms max for config loading
    }


@pytest.fixture
def interactive_session(
    io_manager: InputOutputManager, transformation_engine: TextTransformationEngine
):
    """Provide InteractiveSession instance for testing."""
    from string_multitool.models.interactive import InteractiveSession

    return InteractiveSession(io_manager, transformation_engine)
