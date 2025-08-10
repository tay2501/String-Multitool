#!/usr/bin/env python3
"""
Test suite for String_Multitool transformation rules and functionality.
"""

from __future__ import annotations

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Any, Generator

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from String_Multitool import (
    ConfigurationManager, 
    TextTransformationEngine, 
    InputOutputManager,
    InteractiveSession,
    CommandProcessor,
    ClipboardMonitor,
    CryptographyManager,
    ApplicationInterface,
    CRYPTO_AVAILABLE
)


class TestConfigurationManager:
    """Test configuration management functionality."""
    
    def test_load_transformation_rules(self) -> None:
        """Test loading transformation rules from config."""
        config_manager: ConfigurationManager = ConfigurationManager()
        rules: dict[str, Any] = config_manager.load_transformation_rules()
        
        assert isinstance(rules, dict)
        assert 'basic_transformations' in rules
        assert 'case_transformations' in rules
        assert 'string_operations' in rules
        assert 'advanced_rules' in rules
    
    def test_load_security_config(self) -> None:
        """Test loading security configuration."""
        config_manager: ConfigurationManager = ConfigurationManager()
        config: dict[str, Any] = config_manager.load_security_config()
        
        assert isinstance(config, dict)
        assert 'rsa_encryption' in config
        assert config['rsa_encryption']['key_size'] == 4096


class TestTextTransformationEngine:
    """Test text transformation functionality."""
    
    @pytest.fixture
    def engine(self) -> TextTransformationEngine:
        """Create a TextTransformationEngine instance for testing."""
        config_manager: ConfigurationManager = ConfigurationManager()
        return TextTransformationEngine(config_manager)
    
    def test_basic_transformations(self, engine: TextTransformationEngine) -> None:
        """Test basic transformation rules."""
        test_cases: list[tuple[str, str, str]] = [
            ('/uh', 'TBL_CHA1', 'TBL-CHA1'),
            ('/hu', 'TBL-CHA1', 'TBL_CHA1'),
            ('/fh', 'ＴＢＬ－ＣＨＡ１', 'TBL-CHA1'),
            ('/hf', 'TBL-CHA1', 'ＴＢＬ－ＣＨＡ１'),
        ]
        
        for rule, input_text, expected in test_cases:
            result: str = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_case_transformations(self, engine: TextTransformationEngine) -> None:
        """Test case transformation rules."""
        test_cases: list[tuple[str, str, str]] = [
            ('/l', 'SAY HELLO TO MY LITTLE FRIEND!', 'say hello to my little friend!'),
            ('/u', 'Can you hear me, Major Tom?', 'CAN YOU HEAR ME, MAJOR TOM?'),
            ('/p', 'The quick brown fox jumps over the lazy dog', 'TheQuickBrownFoxJumpsOverTheLazyDog'),
            ('/c', 'is error state!', 'isErrorState'),
            ('/s', 'is error state!', 'is_error_state'),
            ('/a', 'the quick brown fox jumps over the lazy dog', 'The Quick Brown Fox Jumps Over The Lazy Dog'),
        ]
        
        for rule, input_text, expected in test_cases:
            result: str = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_string_operations(self, engine: TextTransformationEngine) -> None:
        """Test string operation rules."""
        test_cases: list[tuple[str, str, str]] = [
            ('/t', '  Well, something is happening  ', 'Well, something is happening'),
            ('/R', 'hello', 'olleh'),
            ('/si', 'A0001\r\nA0002\r\nA0003', "'A0001',\r\n'A0002',\r\n'A0003'"),
            ('/dlb', 'A0001\r\nA0002\r\nA0003', 'A0001A0002A0003'),
        ]
        
        for rule, input_text, expected in test_cases:
            result: str = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_sequential_processing(self, engine: TextTransformationEngine) -> None:
        """Test sequential rule processing."""
        test_cases: list[tuple[str, str, str]] = [
            ('/t/l', '  HELLO WORLD  ', 'hello world'),
            ('/s/u', 'The Quick Brown Fox', 'THE_QUICK_BROWN_FOX'),
        ]
        
        for rule, input_text, expected in test_cases:
            result: str = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_argument_based_rules(self, engine: TextTransformationEngine) -> None:
        """Test rules with arguments."""
        test_cases: list[tuple[str, str, str]] = [
            ("/S '+'", 'http://foo.bar/baz/brrr', 'http+foo+bar+baz+brrr'),
            ("/r 'Will' 'Bill'", "I'm Will, Will's son", "I'm Bill, Bill's son"),
            ("/S", 'hello world test', 'hello-world-test'),  # Default replacement
            ("/r 'this'", 'remove this text', 'remove  text'),  # Default replacement (empty)
        ]
        
        for rule, input_text, expected in test_cases:
            result: str = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_invalid_rule(self, engine: TextTransformationEngine) -> None:
        """Test handling of invalid rules."""
        with pytest.raises(ValueError, match="Unknown rule"):
            engine.apply_transformations("test", "/invalid")
    
    def test_empty_rule_string(self, engine: TextTransformationEngine) -> None:
        """Test handling of empty rule string."""
        with pytest.raises(ValueError, match="Rules must start with"):
            engine.apply_transformations("test", "")
    
    def test_rule_without_slash(self, engine: TextTransformationEngine) -> None:
        """Test handling of rule without leading slash."""
        with pytest.raises(ValueError, match="Rules must start with"):
            engine.apply_transformations("test", "invalid")
    
    def test_parse_rule_string_edge_cases(self, engine: TextTransformationEngine) -> None:
        """Test edge cases in rule string parsing."""
        # Test rule with no arguments when arguments expected
        parsed: list[tuple[str, list[str]]] = engine.parse_rule_string("/S")
        assert len(parsed) == 1
        assert parsed[0][0] == "S"
        assert parsed[0][1] == ["-"]  # Default argument
    
    def test_get_available_rules(self, engine: TextTransformationEngine) -> None:
        """Test getting available rules."""
        rules: dict[str, Any] = engine.get_available_rules()
        assert isinstance(rules, dict)
        assert len(rules) > 0
        assert 'u' in rules  # Basic rule
        assert 'S' in rules  # Advanced rule


class TestInteractiveSession:
    """Test interactive session functionality."""
    
    @pytest.fixture
    def session(self) -> InteractiveSession:
        """Create an InteractiveSession instance for testing."""
        io_manager: Mock = Mock(spec=InputOutputManager)
        engine: Mock = Mock(spec=TextTransformationEngine)
        return InteractiveSession(io_manager, engine)
    
    def test_initialization(self, session: InteractiveSession) -> None:
        """Test session initialization."""
        assert session.current_text == ""
        assert session.text_source == "clipboard"
        assert session.auto_detection_enabled  # Now defaults to True
    
    def test_update_working_text(self, session: InteractiveSession) -> None:
        """Test updating working text."""
        session.update_working_text("test text", "manual")
        
        assert session.current_text == "test text"
        assert session.text_source == "manual"
    
    def test_get_status_info(self, session: InteractiveSession) -> None:
        """Test getting status information."""
        session.update_working_text("test", "clipboard")
        status: Any = session.get_status_info()
        
        assert status.current_text == "test"
        assert status.text_source == "clipboard"
        assert status.character_count == 4
        assert status.auto_detection_enabled  # Now defaults to True
    
    @patch('String_Multitool.pyperclip')
    def test_refresh_from_clipboard(self, mock_pyperclip: Mock, session: InteractiveSession) -> None:
        """Test refreshing from clipboard."""
        mock_pyperclip.paste.return_value = "new content"
        session.io_manager.get_clipboard_text.return_value = "new content"
        
        result: bool = session.refresh_from_clipboard()
        
        assert result is True
        assert session.current_text == "new content"
        assert session.text_source == "clipboard"


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
        
        processor.session.get_status_info.return_value = mock_status
        processor.session.get_display_text.return_value = "test text"
        processor.session.get_time_since_update.return_value = "1 minute ago"
        
        result: Any = processor.process_command("status")
        
        assert result.success is True
        assert "Session Status" in result.message
        assert "10 characters" in result.message


class TestCryptographyManager:
    """Test cryptography functionality."""
    
    @pytest.fixture
    def crypto_manager(self) -> CryptographyManager:
        """Create a CryptographyManager instance for testing."""
        config_manager: ConfigurationManager = ConfigurationManager()
        if not CRYPTO_AVAILABLE:
            pytest.skip("Cryptography not available")
        return CryptographyManager(config_manager)
    
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
    
    def test_japanese_text_encryption(self, crypto_manager: CryptographyManager) -> None:
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
        
        # Test minimum interval
        monitor.set_check_interval(0.05)
        assert monitor.check_interval == 0.1
    
    def test_set_max_content_size(self, monitor: ClipboardMonitor) -> None:
        """Test setting maximum content size."""
        monitor.set_max_content_size(2048)
        assert monitor.max_content_size == 2048
        
        # Test minimum size
        monitor.set_max_content_size(512)
        assert monitor.max_content_size == 1024


class TestInputOutputManager:
    """Test input/output operations."""
    
    @patch('String_Multitool.sys.stdin')
    @patch('String_Multitool.pyperclip')
    def test_get_input_text_from_pipe(self, mock_pyperclip: Mock, mock_stdin: Mock) -> None:
        """Test getting input from pipe."""
        mock_stdin.isatty.return_value = False
        mock_stdin.read.return_value = "piped text\n"
        
        result: str = InputOutputManager.get_input_text()
        assert result == "piped text"
    
    @patch('String_Multitool.sys.stdin')
    @patch('String_Multitool.pyperclip')
    def test_get_input_text_from_clipboard(self, mock_pyperclip: Mock, mock_stdin: Mock) -> None:
        """Test getting input from clipboard."""
        mock_stdin.isatty.return_value = True
        mock_pyperclip.paste.return_value = "clipboard text"
        
        result: str = InputOutputManager.get_input_text()
        assert result == "clipboard text"
    
    @patch('String_Multitool.pyperclip')
    def test_get_clipboard_text(self, mock_pyperclip: Mock) -> None:
        """Test getting text from clipboard only."""
        mock_pyperclip.paste.return_value = "test text"
        
        result: str = InputOutputManager.get_clipboard_text()
        assert result == "test text"
    
    @patch('String_Multitool.pyperclip')
    def test_set_output_text(self, mock_pyperclip: Mock) -> None:
        """Test setting output text to clipboard."""
        InputOutputManager.set_output_text("test output")
        mock_pyperclip.copy.assert_called_once_with("test output")
    
    @patch('String_Multitool.CLIPBOARD_AVAILABLE', False)
    def test_clipboard_unavailable(self) -> None:
        """Test behavior when clipboard is unavailable."""
        with pytest.raises(RuntimeError, match="Clipboard functionality not available"):
            InputOutputManager.get_clipboard_text()


@pytest.fixture(autouse=True)
def mock_clipboard() -> Generator[Mock, None, None]:
    """Mock clipboard functionality for all tests."""
    with patch('String_Multitool.CLIPBOARD_AVAILABLE', True):
        with patch('String_Multitool.pyperclip') as mock_pyperclip:
            mock_pyperclip.paste.return_value = ""
            mock_pyperclip.copy.return_value = None
            yield mock_pyperclip


class TestApplicationInterface:
    """Test main application interface."""
    
    @pytest.fixture
    def app_interface(self):
        """Create an ApplicationInterface instance for testing."""
        return ApplicationInterface()
    
    def test_initialization(self, app_interface):
        """Test application interface initialization."""
        assert app_interface.config_manager is not None
        assert app_interface.transformation_engine is not None
        assert app_interface.io_manager is not None
    
    @patch('String_Multitool.sys.argv', ['String_Multitool.py', 'help'])
    @patch('builtins.print')
    def test_help_command(self, mock_print, app_interface):
        """Test help command execution."""
        app_interface.run()
        # Verify that help was displayed (print was called)
        assert mock_print.called
    
    @patch('String_Multitool.sys.argv', ['String_Multitool.py', '/u'])
    @patch.object(InputOutputManager, 'get_input_text', return_value='hello')
    @patch.object(InputOutputManager, 'set_output_text')
    @patch('builtins.print')
    def test_command_mode(self, mock_print, mock_set_output, mock_get_input, app_interface):
        """Test command mode execution."""
        app_interface.run()
        mock_set_output.assert_called_once_with('HELLO')
    
    def test_display_help(self, app_interface):
        """Test help display functionality."""
        # This should not raise an exception
        app_interface.display_help()


def test_main_functionality():
    """Integration test for main functionality."""
    # Test that the main components can be instantiated without errors
    config_manager = ConfigurationManager()
    engine = TextTransformationEngine(config_manager)
    
    # Test a simple transformation
    result = engine.apply_transformations("hello world", "/u")
    assert result == "HELLO WORLD"


def test_main_function():
    """Test main function execution."""
    from String_Multitool import main
    
    # Test that main function can be imported and called
    # (This will test the basic structure)
    assert callable(main)


def test_dataclass_structures():
    """Test dataclass structures."""
    from String_Multitool import TransformationRule, SessionState, CommandResult
    
    # Test TransformationRule
    rule = TransformationRule(
        name="Test Rule",
        description="Test description",
        example="test example",
        function=lambda x: x.upper()
    )
    assert rule.name == "Test Rule"
    assert rule.function("hello") == "HELLO"
    
    # Test SessionState
    from datetime import datetime
    state = SessionState(
        current_text="test",
        text_source="clipboard",
        last_update_time=datetime.now(),
        character_count=4,
        auto_detection_enabled=True,
        clipboard_monitor_active=False
    )
    assert state.current_text == "test"
    assert state.character_count == 4
    
    # Test CommandResult
    result = CommandResult(
        success=True,
        message="Test message"
    )
    assert result.success is True
    assert result.message == "Test message"


def test_logging_functionality():
    """Test logging functionality."""
    import logging
    from unittest.mock import patch, MagicMock
    from string_multitool.utils.logger import LoggerManager, get_logger, log_info, log_error
    
    # Test LoggerManager singleton
    manager1 = LoggerManager()
    manager2 = LoggerManager()
    assert manager1 is manager2
    
    # Test get_logger function
    logger = get_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"
    
    # Test logging functions with mock
    with patch('logging.Logger.info') as mock_info:
        log_info(logger, "Test info message")
        mock_info.assert_called_once_with("Test info message")
    
    with patch('logging.Logger.error') as mock_error:
        log_error(logger, "Test error message")
        mock_error.assert_called_once_with("Test error message", exc_info=True)
    
    # Test log level setting
    LoggerManager.set_log_level(logging.DEBUG)
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG


def test_logging_integration():
    """Test integration of logging with application components."""
    import tempfile
    from pathlib import Path
    from string_multitool.utils.logger import LoggerManager
    
    # Test with temporary log file
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = Path(temp_dir) / "test.log"
        LoggerManager.add_file_handler(str(log_file))
        
        logger = get_logger("integration_test")
        logger.info("Integration test message")
        
        # Check if log file was created and has content
        assert log_file.exists()
        content = log_file.read_text(encoding='utf-8')
        assert "Integration test message" in content


def test_pathlib_usage():
    """Test proper pathlib usage throughout the project."""
    from pathlib import Path
    from string_multitool.core.config import ConfigurationManager
    
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


def test_pathlib_type_safety():
    """Test pathlib type safety and operations."""
    from pathlib import Path
    import tempfile
    
    # Test pathlib methods vs os.path equivalents
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_file = temp_path / "test.txt"
        
        # Create test file
        test_file.write_text("test content", encoding='utf-8')
        
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