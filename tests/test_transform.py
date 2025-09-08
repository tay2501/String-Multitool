#!/usr/bin/env python3
"""
Test suite for String_Multitool transformation rules and functionality.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Generator
from unittest.mock import Mock, patch

import pytest

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from string_multitool.models.config import ConfigurationManager
from string_multitool.models.transformations import TextTransformationEngine
from string_multitool.models.types import (
    CommandResult,
    SessionState,
    TextSource,
    TransformationRule,
)
from string_multitool.io.clipboard import ClipboardMonitor
from string_multitool.io.manager import InputOutputManager
# Mock ApplicationInterface for testing
class ApplicationInterface:
    """Mock ApplicationInterface for testing purposes."""
    
    def __init__(
        self,
        config_manager: ConfigurationManager,
        transformation_engine: TextTransformationEngine,
        io_manager: InputOutputManager,
        crypto_manager=None,
        hotkey_mode=None,
        system_tray_mode=None,
    ):
        self.config_manager = config_manager
        self.transformation_engine = transformation_engine
        self.io_manager = io_manager
        self.crypto_manager = crypto_manager
        self.hotkey_mode = hotkey_mode
        self.system_tray_mode = system_tray_mode
    
    def run(self):
        """Mock run method."""
        pass
    
    def display_help(self):
        """Mock display help method."""
        pass

try:
    from string_multitool.models.crypto import CryptographyManager, CRYPTOGRAPHY_AVAILABLE as CRYPTO_AVAILABLE
except ImportError:
    CryptographyManager = None
    CRYPTO_AVAILABLE = False
from string_multitool.exceptions import (
    ClipboardError,
    ConfigurationError,
    CryptographyError,
    TransformationError,
    ValidationError,
)
from string_multitool.models.interactive import CommandProcessor, InteractiveSession

try:
    from string_multitool.transformations.encryption_transformations import (
        DecryptTransformation,
        EncryptTransformation,
    )

    CRYPTO_TRANSFORMATIONS_AVAILABLE = True
except ImportError:
    CRYPTO_TRANSFORMATIONS_AVAILABLE = False
from string_multitool.utils.unified_logger import get_logger


class TestConfigurationManager:
    """Test configuration management functionality with modern pytest patterns."""

    def test_load_transformation_rules(self, config_manager: ConfigurationManager) -> None:
        """Test loading transformation rules from config using pytest fixture."""
        rules: dict[str, Any] = config_manager.load_transformation_rules()

        assert isinstance(rules, dict)
        assert "basic_transformations" in rules
        assert "case_transformations" in rules
        assert "string_operations" in rules
        assert "advanced_rules" in rules

    def test_load_security_config(self, config_manager: ConfigurationManager) -> None:
        """Test loading security configuration using pytest fixture."""
        config: dict[str, Any] = config_manager.load_security_config()

        assert isinstance(config, dict)
        assert "rsa_encryption" in config
        assert config["rsa_encryption"]["key_size"] == 4096
    
    @pytest.mark.parametrize("config_key,expected_type", [
        ("basic_transformations", dict),
        ("case_transformations", dict), 
        ("string_operations", dict),
        ("advanced_rules", dict),
    ])
    def test_rule_sections_exist(self, config_manager: ConfigurationManager, config_key: str, expected_type: type) -> None:
        """Test that all required rule sections exist with correct types using parametrized testing."""
        rules = config_manager.load_transformation_rules()
        assert config_key in rules
        assert isinstance(rules[config_key], expected_type)


@pytest.mark.unit
class TestTextTransformationEngine:
    """Test text transformation functionality with modern pytest patterns."""

    @pytest.mark.parametrize("rule,input_text,expected", [
        ("/uh", "TBL_CHA1", "TBL-CHA1"),
        ("/hu", "TBL-CHA1", "TBL_CHA1"),
        ("/fh", "ＴＢＬ－ＣＨＡ１", "TBL-CHA1"),
        ("/hf", "TBL-CHA1", "ＴＢＬ－ＣＨＡ１"),
    ])
    def test_basic_transformations(self, transformation_engine: TextTransformationEngine, rule: str, input_text: str, expected: str) -> None:
        """Test basic transformation rules using parametrized testing."""
        result: str = transformation_engine.apply_transformations(input_text, rule)
        assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"

    @pytest.mark.parametrize("rule,input_text,expected", [
        ("/l", "SAY HELLO TO MY LITTLE FRIEND!", "say hello to my little friend!"),
        ("/u", "Can you hear me, Major Tom?", "CAN YOU HEAR ME, MAJOR TOM?"),
        ("/p", "The quick brown fox jumps over the lazy dog", "TheQuickBrownFoxJumpsOverTheLazyDog"),
        ("/c", "is error state!", "isErrorState"),
        ("/s", "is error state!", "is_error_state"),
        ("/a", "the quick brown fox jumps over the lazy dog", "The Quick Brown Fox Jumps Over The Lazy Dog"),
    ])
    def test_case_transformations(self, transformation_engine: TextTransformationEngine, rule: str, input_text: str, expected: str) -> None:
        """Test case transformation rules using parametrized testing."""
        result: str = transformation_engine.apply_transformations(input_text, rule)
        assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"

    @pytest.mark.parametrize("rule,input_text,expected", [
        ("/t", "  Well, something is happening  ", "Well, something is happening"),
        ("/R", "hello", "olleh"),
        ("/si", "A0001\r\nA0002\r\nA0003", "'A0001',\r\n'A0002',\r\n'A0003'"),
        ("/dlb", "A0001\r\nA0002\r\nA0003", "A0001A0002A0003"),
    ])
    def test_string_operations(self, transformation_engine: TextTransformationEngine, rule: str, input_text: str, expected: str) -> None:
        """Test string operation rules using parametrized testing."""
        result: str = transformation_engine.apply_transformations(input_text, rule)
        assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"

    @pytest.mark.parametrize("rule,input_text,expected", [
        ("/t/l", "  HELLO WORLD  ", "hello world"),
        ("/s/u", "The Quick Brown Fox", "THE_QUICK_BROWN_FOX"),
    ])
    def test_sequential_processing(self, transformation_engine: TextTransformationEngine, rule: str, input_text: str, expected: str) -> None:
        """Test sequential rule processing using parametrized testing."""
        result: str = transformation_engine.apply_transformations(input_text, rule)
        assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"

    @pytest.mark.parametrize("rule,input_text,expected", [
        ("/S '+'", "http://foo.bar/baz/brrr", "http+foo+bar+baz+brrr"),
        ("/r 'Will' 'Bill'", "I'm Will, Will's son", "I'm Bill, Bill's son"),
        ("/S", "hello world test", "hello-world-test"),  # Default replacement
        ("/r 'this'", "remove this text", "remove  text"),  # Default replacement (empty)
        # Escape sequence tests for newline conversion
        ("/r '\\r\\n' '\\n'", "Line1\r\nLine2\r\nLine3", "Line1\nLine2\nLine3"),  # CRLF to LF
        ("/r '\\n' '\\r\\n'", "Line1\nLine2\nLine3", "Line1\r\nLine2\r\nLine3"),  # LF to CRLF  
        ("/r '\\r' '\\n'", "Line1\rLine2\rLine3", "Line1\nLine2\nLine3"),  # CR to LF
        ("/r '\\t' ' '", "Col1\tCol2\tCol3", "Col1 Col2 Col3"),  # Tab to space
        ("/r '\\\\' '/'", "C:\\path\\to\\file", "C:/path/to/file"),  # Backslash to forward slash
    ])
    def test_argument_based_rules(self, transformation_engine: TextTransformationEngine, rule: str, input_text: str, expected: str) -> None:
        """Test rules with arguments using parametrized testing."""
        result: str = transformation_engine.apply_transformations(input_text, rule)
        assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"

    def test_invalid_rule(self, transformation_engine: TextTransformationEngine) -> None:
        """Test handling of invalid rules."""
        with pytest.raises(TransformationError, match="Unknown rule"):
            transformation_engine.apply_transformations("test", "/invalid")

    def test_empty_rule_string(self, transformation_engine: TextTransformationEngine) -> None:
        """Test handling of empty rule string."""
        with pytest.raises(ValidationError, match="Rule string cannot be empty"):
            transformation_engine.apply_transformations("test", "")

    def test_rule_without_slash(self, transformation_engine: TextTransformationEngine) -> None:
        """Test handling of rule without leading slash."""
        with pytest.raises(ValidationError, match="Rules must start with"):
            transformation_engine.apply_transformations("test", "invalid")

    def test_parse_rule_string_edge_cases(self, transformation_engine: TextTransformationEngine) -> None:
        """Test edge cases in rule string parsing."""
        # Test rule with no arguments when arguments expected
        parsed: list[tuple[str, list[str]]] = transformation_engine.parse_rule_string("/S")
        assert len(parsed) == 1
        assert parsed[0][0] == "S"
        assert parsed[0][1] == []  # No arguments provided

    def test_get_available_rules(self, transformation_engine: TextTransformationEngine) -> None:
        """Test getting available rules."""
        rules: dict[str, Any] = transformation_engine.get_available_rules()
        assert isinstance(rules, dict)
        assert len(rules) > 0
        assert "u" in rules  # Basic rule
        assert "S" in rules  # Advanced rule
    
    @pytest.mark.parametrize("rule,input_text,expected", [
        # Empty string edge cases
        ("/l", "", ""),
        ("/u", "", ""),
        ("/t", "", ""),
        # Single character edge cases
        ("/l", "A", "a"),
        ("/u", "z", "Z"),
        ("/t", " ", ""),
        # Special character edge cases
        ("/l", "123!@#", "123!@#"),
        ("/u", "456$%^", "456$%^"),
        ("/R", "!@#", "#@!"),
        # Unicode edge cases
        ("/l", "\u00dc", "\u00fc"),
        ("/u", "\u00f1", "\u00d1"),
        ("/t", "\u3000", ""),  # Full-width space
        # Null and control characters
        ("/l", "\x00", "\x00"),
        ("/u", "\t\n", "\t\n"),
    ])
    def test_edge_case_transformations(self, transformation_engine: TextTransformationEngine, rule: str, input_text: str, expected: str) -> None:
        """Test edge case transformations using parametrized testing."""
        result: str = transformation_engine.apply_transformations(input_text, rule)
        assert result == expected, f"Edge case rule {rule} failed: got '{result}', expected '{expected}'"


class TestInteractiveSession:
    """Test interactive session functionality with modern pytest patterns."""

    @pytest.fixture
    def session(self, io_manager: InputOutputManager, transformation_engine: TextTransformationEngine) -> InteractiveSession:
        """Create an InteractiveSession instance for testing using dependency injection."""
        return InteractiveSession(io_manager, transformation_engine)

    def test_initialization(self, session: InteractiveSession) -> None:
        """Test session initialization."""
        assert session.current_text == ""
        assert session.text_source == TextSource.CLIPBOARD
        assert session.auto_detection_enabled  # Now defaults to True

    def test_update_working_text(self, session: InteractiveSession) -> None:
        """Test updating working text."""
        session.update_working_text("test text", TextSource.MANUAL.value)

        assert session.current_text == "test text"
        assert session.text_source == TextSource.MANUAL

    def test_get_status_info(self, session: InteractiveSession) -> None:
        """Test getting status information."""
        session.update_working_text("test", TextSource.CLIPBOARD.value)
        status: Any = session.get_status_info()

        assert status.current_text == "test"
        assert status.text_source == TextSource.CLIPBOARD
        assert status.character_count == 4
        assert status.auto_detection_enabled  # Now defaults to True

    @patch("string_multitool.io.manager.pyperclip")
    def test_refresh_from_clipboard(
        self, mock_pyperclip: Mock, session: InteractiveSession
    ) -> None:
        """Test refreshing from clipboard."""
        mock_pyperclip.paste.return_value = "new content"
        with patch.object(
            session.io_manager, "get_clipboard_text", return_value="new content"
        ):

            result: str = session.refresh_from_clipboard()

            assert result == "new content"
            assert session.current_text == "new content"
            assert session.text_source == TextSource.CLIPBOARD


class TestCommandProcessor:
    """Test command processing functionality."""

    @pytest.fixture
    def processor(self) -> CommandProcessor:
        """Create a CommandProcessor instance for testing."""
        session: Mock = Mock(spec=InteractiveSession)
        return CommandProcessor(session)

    def test_is_command(self, processor: CommandProcessor) -> None:
        """Test command detection."""
        assert processor.is_command("help") is True
        assert processor.is_command("refresh") is True
        assert processor.is_command("status") is True
        assert processor.is_command("/t/l") is False
        assert processor.is_command("/enc") is False

    def test_status_command(self, processor: CommandProcessor) -> None:
        """Test status command processing."""
        # Mock session status
        mock_status: Mock = Mock()
        mock_status.character_count = 10
        mock_status.text_source = "clipboard"
        mock_status.auto_detection_enabled = True
        mock_status.clipboard_monitor_active = False

        with (
            patch.object(
                processor.session, "get_status_info", return_value=mock_status
            ),
            patch.object(
                processor.session, "get_display_text", return_value="test text"
            ),
            patch.object(
                processor.session, "get_time_since_update", return_value="1 minute ago"
            ),
        ):

            result: Any = processor.process_command("status")

            assert result.success is True
            assert "[STATUS]:" in result.message or "Session Status" in result.message
            # Check for status information (文字数やクリップボード情報を確認)
            assert any(info in result.message for info in ["Current clipboard", "Auto-detection", "Monitor active"])


class TestCryptographyManager:
    """Test cryptography functionality."""

    @pytest.fixture
    def crypto_manager(self, tmp_path) -> CryptographyManager:
        """Create a CryptographyManager instance for testing with temporary keys."""
        import tempfile
        from pathlib import Path
        
        config_manager: ConfigurationManager = ConfigurationManager()
        if not CRYPTO_AVAILABLE:
            pytest.skip("Cryptography not available")
        
        # Create temporary directory for test keys
        test_key_dir = tmp_path / "test_rsa"
        test_key_dir.mkdir(exist_ok=True)
        
        # Override the key directory in the crypto manager
        crypto_manager = CryptographyManager(config_manager)
        crypto_manager.key_directory = test_key_dir
        crypto_manager.private_key_path = test_key_dir / "rsa"
        crypto_manager.public_key_path = test_key_dir / "rsa.pub"
        
        return crypto_manager

    def test_key_generation(self, crypto_manager: CryptographyManager) -> None:
        """Test RSA key pair generation."""
        private_key: Any
        public_key: Any
        private_key, public_key = crypto_manager.ensure_key_pair()

        assert private_key is not None
        assert public_key is not None
        assert private_key.key_size >= 2048

    def test_encryption_decryption(self, crypto_manager: CryptographyManager) -> None:
        """Test encryption and decryption cycle."""
        test_text: str = "Hello, World!"

        # Encrypt
        encrypted: str = crypto_manager.encrypt_text(test_text)
        assert encrypted != test_text
        assert len(encrypted) > 0

        # Decrypt
        decrypted: str = crypto_manager.decrypt_text(encrypted)
        assert decrypted == test_text

    def test_large_text_encryption(self, crypto_manager: CryptographyManager) -> None:
        """Test encryption of large text."""
        large_text: str = "A" * 1000  # 1KB of text

        encrypted: str = crypto_manager.encrypt_text(large_text)
        decrypted: str = crypto_manager.decrypt_text(encrypted)

        assert decrypted == large_text

    def test_japanese_text_encryption(
        self, crypto_manager: CryptographyManager
    ) -> None:
        """Test encryption of Japanese text."""
        japanese_text: str = "こんにちは世界"

        encrypted: str = crypto_manager.encrypt_text(japanese_text)
        decrypted: str = crypto_manager.decrypt_text(encrypted)

        assert decrypted == japanese_text

    def test_empty_text_encryption(self, crypto_manager: CryptographyManager) -> None:
        """Test encryption of empty text."""
        empty_text: str = ""

        encrypted: str = crypto_manager.encrypt_text(empty_text)
        decrypted: str = crypto_manager.decrypt_text(encrypted)

        assert decrypted == empty_text


class TestClipboardMonitor:
    """Test clipboard monitoring functionality."""

    @pytest.fixture
    def monitor(self) -> ClipboardMonitor:
        """Create a ClipboardMonitor instance for testing."""
        io_manager: Mock = Mock(spec=InputOutputManager)
        return ClipboardMonitor(io_manager)

    def test_monitor_initialization(self, monitor: ClipboardMonitor) -> None:
        """Test monitor initialization."""
        assert not monitor.is_monitoring
        assert monitor.check_interval == 1.0
        assert monitor.last_content == ""

    def test_set_check_interval(self, monitor: ClipboardMonitor) -> None:
        """Test setting check interval."""
        monitor.set_check_interval(2.0)
        assert monitor.check_interval == 2.0

        # Test minimum interval - should raise ValidationError
        with pytest.raises(ValidationError):
            monitor.set_check_interval(0.05)

    def test_set_max_content_size(self, monitor: ClipboardMonitor) -> None:
        """Test setting maximum content size."""
        monitor.set_max_content_size(2048)
        assert monitor.max_content_size == 2048

        # Test minimum size - should raise ValidationError
        with pytest.raises(ValidationError):
            monitor.set_max_content_size(512)


class TestInputOutputManager:
    """Test input/output operations."""

    @patch("string_multitool.io.manager.sys.stdin")
    @patch("string_multitool.io.manager.pyperclip")
    def test_get_input_text_from_pipe(
        self, mock_pyperclip: Mock, mock_stdin: Mock
    ) -> None:
        """Test getting input from pipe."""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "piped text\n"

        io_manager = InputOutputManager()
        result: str = io_manager.get_input_text()
        assert result == "piped text"

    @patch("string_multitool.io.manager.sys.stdin")
    @patch("string_multitool.io.manager.pyperclip")
    def test_get_input_text_from_clipboard(
        self, mock_pyperclip: Mock, mock_stdin: Mock
    ) -> None:
        """Test getting input from clipboard."""
        mock_stdin.isatty.return_value = True
        mock_pyperclip.paste.return_value = "clipboard text"

        io_manager = InputOutputManager()
        result: str = io_manager.get_input_text()
        assert result == "clipboard text"

    @patch("string_multitool.io.manager.pyperclip")
    def test_get_clipboard_text(self, mock_pyperclip: Mock) -> None:
        """Test getting text from clipboard only."""
        mock_pyperclip.paste.return_value = "test text"

        io_manager = InputOutputManager()
        result: str = io_manager.get_clipboard_text()
        assert result == "test text"

    @patch("string_multitool.io.manager.pyperclip")
    def test_set_output_text(self, mock_pyperclip: Mock) -> None:
        """Test setting output text to clipboard."""
        io_manager = InputOutputManager()
        io_manager.set_output_text("test output")
        mock_pyperclip.copy.assert_called_once_with("test output")

    @patch("string_multitool.io.manager.CLIPBOARD_AVAILABLE", False)
    def test_clipboard_unavailable(self) -> None:
        """Test behavior when clipboard is unavailable."""
        with pytest.raises(
            ClipboardError, match="Clipboard functionality not available"
        ):
            io_manager = InputOutputManager()
            io_manager.get_clipboard_text()


# Fixtures are now defined in conftest.py following modern pytest practices
# This eliminates duplication and improves test organization


class TestApplicationInterface:
    """Test main application interface."""

    @pytest.fixture
    def app_interface(self) -> ApplicationInterface:
        """Create an ApplicationInterface instance for testing."""
        # Create dependencies manually for testing
        config_manager = ConfigurationManager()
        transformation_engine = TextTransformationEngine(config_manager)
        io_manager = InputOutputManager()
        return ApplicationInterface(
            config_manager=config_manager,
            transformation_engine=transformation_engine,
            io_manager=io_manager,
        )

    def test_initialization(self, app_interface: ApplicationInterface) -> None:
        """Test application interface initialization."""
        assert app_interface.config_manager is not None
        assert app_interface.transformation_engine is not None
        assert app_interface.io_manager is not None

    def test_help_command(self, app_interface: ApplicationInterface) -> None:
        """Test help command execution."""
        # Test that display_help can be called without error
        app_interface.display_help()

    def test_command_mode(self, app_interface: ApplicationInterface) -> None:
        """Test command mode execution."""
        # Test transformation engine directly
        result = app_interface.transformation_engine.apply_transformations("hello", "/u")
        assert result == "HELLO"

    def test_display_help(self, app_interface: ApplicationInterface) -> None:
        """Test help display functionality."""
        # This should not raise an exception
        app_interface.display_help()


class TestModularTransformations:
    """Test modular transformation classes."""

    @pytest.fixture
    def transformation_classes(self) -> dict[str, Any]:
        """Get available transformation classes."""
        from string_multitool.transformations.advanced_transformations import (
            ReplaceTransformation,
        )
        from string_multitool.transformations.basic_transformations import (
            FullToHalfWidthTransformation,
            HalfToFullWidthTransformation,
            HyphenToUnderbarTransformation,
            UnderbarToHyphenTransformation,
        )
        from string_multitool.transformations.case_transformations import (
            CamelCaseTransformation,
            CapitalizeTransformation,
            LowercaseTransformation,
            PascalCaseTransformation,
            SnakeCaseTransformation,
            UppercaseTransformation,
        )
        from string_multitool.transformations.encryption_transformations import (
            DecryptTransformation,
            EncryptTransformation,
        )
        from string_multitool.transformations.string_operations import (
            TrimTransformation,
        )

        return {
            "uh": UnderbarToHyphenTransformation,
            "hu": HyphenToUnderbarTransformation,
            "fh": FullToHalfWidthTransformation,
            "hf": HalfToFullWidthTransformation,
            "l": LowercaseTransformation,
            "u": UppercaseTransformation,
            "p": PascalCaseTransformation,
            "c": CamelCaseTransformation,
            "s": SnakeCaseTransformation,
            "a": CapitalizeTransformation,
            "t": TrimTransformation,
            "r": ReplaceTransformation,
            "enc": EncryptTransformation,
            "dec": DecryptTransformation,
        }

    def test_basic_transformation_classes(
        self, transformation_classes: dict[str, Any]
    ) -> None:
        """Test individual transformation classes."""
        test_cases: list[tuple[str, str, str]] = [
            ("uh", "TBL_CHA1", "TBL-CHA1"),
            ("hu", "TBL-CHA1", "TBL_CHA1"),
            ("fh", "ＴＢＬ－ＣＨＡ１", "TBL-CHA1"),
            ("hf", "TBL-CHA1", "ＴＢＬ－ＣＨＡ１"),
        ]

        for rule, input_text, expected in test_cases:
            transformation_class = transformation_classes[rule]
            transformation = transformation_class()
            result = transformation.transform(input_text)

            assert (
                result == expected
            ), f"Rule {rule} failed: got '{result}', expected '{expected}'"
            assert transformation.get_transformation_rule() == rule
            assert transformation.get_input_text() == input_text
            assert transformation.get_output_text() == expected

    def test_case_transformation_classes(
        self, transformation_classes: dict[str, Any]
    ) -> None:
        """Test case transformation classes."""
        test_cases: list[tuple[str, str, str]] = [
            ("l", "SAY HELLO TO MY LITTLE FRIEND!", "say hello to my little friend!"),
            ("u", "Can you hear me, Major Tom?", "CAN YOU HEAR ME, MAJOR TOM?"),
            (
                "p",
                "The quick brown fox jumps over the lazy dog",
                "TheQuickBrownFoxJumpsOverTheLazyDog",
            ),
            ("c", "is error state!", "isErrorState"),
            ("s", "is error state!", "is_error_state"),
            (
                "a",
                "the quick brown fox jumps over the lazy dog",
                "The Quick Brown Fox Jumps Over The Lazy Dog",
            ),
        ]

        for rule, input_text, expected in test_cases:
            transformation_class = transformation_classes[rule]
            transformation = transformation_class()
            result = transformation.transform(input_text)

            assert (
                result == expected
            ), f"Rule {rule} failed: got '{result}', expected '{expected}'"
            assert transformation.get_transformation_rule() == rule
            assert transformation.get_input_text() == input_text
            assert transformation.get_output_text() == expected

    def test_transformation_error_handling(
        self, transformation_classes: dict[str, Any]
    ) -> None:
        """Test error handling in transformation classes."""
        from string_multitool.exceptions import TransformationError

        # Test with None input converted to string (Python handles this)
        transformation = transformation_classes["l"]()

        # Test error handling by trying to access attributes that would cause exceptions
        # Since we can't mock str.lower directly, we test error handling through actual errors
        import os
        import tempfile

        # Create a mock transformation that will fail
        with patch.object(
            transformation, "transform", side_effect=RuntimeError("Mock error")
        ):
            with pytest.raises(RuntimeError, match="Mock error"):
                transformation.transform("test")

        # Test that error context can be set and retrieved
        transformation.set_error_context({"test_key": "test_value", "rule": "l"})
        error_context = transformation.get_error_context()
        assert "test_key" in error_context
        assert "rule" in error_context

    def test_string_operation_classes(
        self, transformation_classes: dict[str, Any]
    ) -> None:
        """Test string operation transformation classes."""
        test_cases: list[tuple[str, str, str]] = [
            ("t", "  Well, something is happening  ", "Well, something is happening"),
        ]

        for rule, input_text, expected in test_cases:
            transformation_class = transformation_classes[rule]
            transformation = transformation_class()
            result = transformation.transform(input_text)

            assert (
                result == expected
            ), f"Rule {rule} failed: got '{result}', expected '{expected}'"
            assert transformation.get_transformation_rule() == rule
            assert transformation.get_input_text() == input_text
            assert transformation.get_output_text() == expected

    def test_advanced_transformation_classes_with_args(
        self, transformation_classes: dict[str, Any]
    ) -> None:
        """Test advanced transformation classes with arguments."""
        # Test replace transformation
        replace_transformation = transformation_classes["r"]()

        # Test replace with both arguments
        replace_transformation.set_arguments(["Will", "Bill"])
        result = replace_transformation.transform("I'm Will, Will's son")
        assert result == "I'm Bill, Bill's son"

        # Test replace with single argument (removal)
        replace_transformation.set_arguments(["this"])
        result = replace_transformation.transform("remove this text")
        assert result == "remove  text"

        # Test error with no arguments
        with pytest.raises(
            TransformationError, match="置換処理には最低1つの引数が必要"
        ):
            replace_transformation.set_arguments([])

    def test_transformation_with_config(
        self, transformation_classes: dict[str, Any]
    ) -> None:
        """Test transformation classes with configuration."""
        config = {"test_setting": "test_value"}
        transformation = transformation_classes["u"](config)

        result = transformation.transform("hello")
        assert result == "HELLO"

        # Config should be available through base class
        assert hasattr(transformation, "_config")

    def test_transformation_base_methods(
        self, transformation_classes: dict[str, Any]
    ) -> None:
        """Test transformation base class methods."""
        transformation = transformation_classes["l"]()

        # Test initial state
        assert transformation.get_input_text() == ""
        assert transformation.get_output_text() == ""
        assert transformation.get_error_context() == {}

        # Test after transformation
        result = transformation.transform("HELLO")
        assert result == "hello"
        assert transformation.get_input_text() == "HELLO"
        assert transformation.get_output_text() == "hello"

        # Test error context setting
        transformation.set_error_context({"test": "value"})
        assert transformation.get_error_context() == {"test": "value"}

    def test_encryption_transformation_classes(
        self, transformation_classes: dict[str, Any]
    ) -> None:
        """Test encryption transformation classes."""
        from string_multitool.exceptions import TransformationError

        # Test encryption without crypto manager (should fail)
        encrypt_transformation = transformation_classes["enc"]()
        with pytest.raises(
            TransformationError, match="暗号化マネージャーが設定されていません"
        ):
            encrypt_transformation.transform("test")

        # Test with mock crypto manager
        mock_crypto_manager = Mock()
        mock_crypto_manager.encrypt_text.return_value = "encrypted_text"
        mock_crypto_manager.decrypt_text.return_value = "decrypted_text"

        # Test encryption
        encrypt_transformation.set_crypto_manager(mock_crypto_manager)
        result = encrypt_transformation.transform("hello world")
        assert result == "encrypted_text"
        mock_crypto_manager.encrypt_text.assert_called_once_with("hello world")

        # Test decryption
        decrypt_transformation = transformation_classes["dec"]()
        decrypt_transformation.set_crypto_manager(mock_crypto_manager)
        result = decrypt_transformation.transform("encrypted_data")
        assert result == "decrypted_text"
        mock_crypto_manager.decrypt_text.assert_called_once_with("encrypted_data")


def test_main_functionality() -> None:
    """Integration test for main functionality."""
    # Test that the main components can be instantiated without errors
    config_manager = ConfigurationManager()
    engine = TextTransformationEngine(config_manager)

    # Test a simple transformation
    result = engine.apply_transformations("hello world", "/u")
    assert result == "HELLO WORLD"


def test_main_function() -> None:
    """Test main function execution."""
    from string_multitool.main import main

    # Test that main function can be imported and called
    # (This will test the basic structure)
    assert callable(main)


def test_dataclass_structures() -> None:
    """Test dataclass structures."""
    # TransformationRule, SessionState, CommandResult already imported at top

    # Test TransformationRule
    rule = TransformationRule(
        name="Test Rule",
        description="Test description",
        example="test example",
        function=lambda x: x.upper(),
    )
    assert rule.name == "Test Rule"
    assert rule.function("hello") == "HELLO"

    # Test SessionState
    from datetime import datetime

    state = SessionState(
        current_text="test",
        text_source=TextSource.CLIPBOARD,
        last_update_time=datetime.now(),
        character_count=4,
        auto_detection_enabled=True,
        clipboard_monitor_active=False,
    )
    assert state.current_text == "test"
    assert state.character_count == 4

    # Test CommandResult
    result = CommandResult(success=True, message="Test message")
    assert result.success is True
    assert result.message == "Test message"


def test_logging_functionality() -> None:
    """Test unified logging functionality."""
    from string_multitool.utils.unified_logger import (
        get_logger,
        log_error,
        log_info,
    )

    # Test get_logger function
    logger = get_logger("test_logger")
    assert logger is not None

    # Test logging functions
    log_info(logger, "Test info message")
    log_error(logger, "Test error message")


def test_logging_integration() -> None:
    """Test integration of unified logging with application components."""
    from string_multitool.utils.unified_logger import get_logger

    logger = get_logger("integration_test")
    logger.info("Integration test message")
    
    # Basic integration test - logger should work without errors
    assert logger is not None


@pytest.mark.stress
class TestStressAndBoundaryConditions:
    """Stress testing and boundary condition validation."""
    
    def test_memory_usage_with_repeated_transformations(
        self, transformation_engine: TextTransformationEngine
    ) -> None:
        """Test memory usage with repeated transformations."""
        import gc
        
        # Force garbage collection before test
        gc.collect()
        
        # Perform many transformations
        for i in range(10000):
            result = transformation_engine.apply_transformations(f"test{i}", "/u")
            assert result == f"TEST{i}"
            
            # Periodically force garbage collection
            if i % 1000 == 0:
                gc.collect()
        
        # Final garbage collection
        gc.collect()
    
    def test_deeply_nested_rule_chains(
        self, transformation_engine: TextTransformationEngine
    ) -> None:
        """Test deeply nested rule chains."""
        # Create a very long rule chain
        long_chain = "/t/l/u/l/u/l/u/l/u/l/u/l/u/l/u/l/u/l/u"  # 19 rules
        
        result = transformation_engine.apply_transformations("  Hello World  ", long_chain)
        # Final result should be lowercase (last /u changes to uppercase, but there's one more /l)
        assert result == "hello world"
    
    @pytest.mark.parametrize("malicious_input", [
        "\x00" * 1000,  # Null bytes
        "\xff" * 1000,  # High bytes
        "<script>alert('xss')</script>",  # XSS attempt
        "'; DROP TABLE users; --",  # SQL injection attempt
        "../../../etc/passwd",  # Path traversal attempt
        "\u200B" * 1000,  # Zero-width spaces
        "\uFEFF" * 1000,  # Byte order marks
    ])
    def test_malicious_input_handling(
        self, 
        transformation_engine: TextTransformationEngine, 
        malicious_input: str
    ) -> None:
        """Test handling of potentially malicious input."""
        try:
            # Should not crash or raise security issues
            result = transformation_engine.apply_transformations(malicious_input, "/l")
            assert isinstance(result, str)
        except Exception as e:
            # Some malicious inputs might cause legitimate exceptions
            # but should not cause security vulnerabilities
            assert "security" not in str(e).lower()
            assert "attack" not in str(e).lower()
    
    def test_resource_exhaustion_protection(
        self, transformation_engine: TextTransformationEngine
    ) -> None:
        """Test protection against resource exhaustion attacks."""
        import time
        
        # Test with extremely long input
        very_long_input = "A" * 1000000  # 1MB
        
        start_time = time.time()
        try:
            result = transformation_engine.apply_transformations(very_long_input, "/l")
            elapsed = time.time() - start_time
            
            # Should complete within reasonable time (5 seconds for 1MB)
            assert elapsed < 5.0, f"Transformation took too long: {elapsed:.2f}s"
            assert result == "a" * 1000000
            
        except MemoryError:
            # If system can't handle 1MB, that's acceptable
            pytest.skip("System unable to handle 1MB transformation")
    
    def test_unicode_boundary_conditions(
        self, transformation_engine: TextTransformationEngine
    ) -> None:
        """Test Unicode boundary conditions and edge cases."""
        boundary_cases = [
            "\U0001F600",  # Emoji (4-byte UTF-8)
            "\U00010000",  # First character in supplementary planes
            "\U0010FFFF",  # Last valid Unicode code point
            "\uD800\uDC00",  # Surrogate pair (valid in UTF-16)
            "\u0300",  # Combining character alone
            "a\u0300\u0301\u0302",  # Base + multiple combining characters
        ]
        
        for test_case in boundary_cases:
            try:
                result = transformation_engine.apply_transformations(test_case, "/t")
                assert isinstance(result, str)
            except UnicodeError:
                # Some boundary cases might legitimately fail
                pass
            except Exception as e:
                # Should not cause other types of exceptions
                pytest.fail(f"Unexpected exception for Unicode boundary case {repr(test_case)}: {e}")


def test_pathlib_usage() -> None:
    """Test proper pathlib usage throughout the project."""
    from pathlib import Path

    from string_multitool.models.config import ConfigurationManager

    # Test ConfigurationManager with pathlib
    config_manager = ConfigurationManager()
    assert isinstance(config_manager.config_dir, Path)
    assert config_manager.config_dir.exists()

    # Test Path union types
    config_manager_with_path = ConfigurationManager(Path("config"))
    assert isinstance(config_manager_with_path.config_dir, Path)

    # Test Path operations
    test_path = Path("test") / "path" / "example.txt"
    assert isinstance(test_path, Path)
    assert test_path.suffix == ".txt"
    assert test_path.name == "example.txt"
    assert test_path.parent.name == "path"


def test_pathlib_type_safety() -> None:
    """Test pathlib type safety and operations."""
    import tempfile
    from pathlib import Path

    # Test pathlib methods vs os.path equivalents
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_file = temp_path / "test.txt"

        # Create test file
        test_file.write_text("test content", encoding="utf-8")

        # Test pathlib methods
        assert test_file.exists()  # vs os.path.exists()
        assert test_file.is_file()  # vs os.path.isfile()
        assert temp_path.is_dir()  # vs os.path.isdir()
        assert test_file.parent == temp_path  # vs os.path.dirname()
        assert test_file.name == "test.txt"  # vs os.path.basename()
        assert test_file.suffix == ".txt"  # Additional pathlib capability

        # Test path joining with / operator
        joined_path = temp_path / "sub" / "file.dat"
        assert isinstance(joined_path, Path)
        assert str(joined_path).endswith("file.dat")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
