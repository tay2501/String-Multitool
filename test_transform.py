#!/usr/bin/env python3
"""
Test suite for String_Multitool transformation rules and functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from String_Multitool import (
    ConfigurationManager, 
    TextTransformationEngine, 
    InputOutputManager,
    InteractiveSession,
    CommandProcessor,
    ClipboardMonitor
)


class TestConfigurationManager:
    """Test configuration management functionality."""
    
    def test_load_transformation_rules(self):
        """Test loading transformation rules from config."""
        config_manager = ConfigurationManager()
        rules = config_manager.load_transformation_rules()
        
        assert isinstance(rules, dict)
        assert 'basic_transformations' in rules
        assert 'case_transformations' in rules
        assert 'string_operations' in rules
        assert 'advanced_rules' in rules
    
    def test_load_security_config(self):
        """Test loading security configuration."""
        config_manager = ConfigurationManager()
        config = config_manager.load_security_config()
        
        assert isinstance(config, dict)
        assert 'rsa_encryption' in config
        assert config['rsa_encryption']['key_size'] == 4096


class TestTextTransformationEngine:
    """Test text transformation functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create a TextTransformationEngine instance for testing."""
        config_manager = ConfigurationManager()
        return TextTransformationEngine(config_manager)
    
    def test_basic_transformations(self, engine):
        """Test basic transformation rules."""
        test_cases = [
            ('/uh', 'TBL_CHA1', 'TBL-CHA1'),
            ('/hu', 'TBL-CHA1', 'TBL_CHA1'),
            ('/fh', 'ＴＢＬ－ＣＨＡ１', 'TBL-CHA1'),
            ('/hf', 'TBL-CHA1', 'ＴＢＬ－ＣＨＡ１'),
        ]
        
        for rule, input_text, expected in test_cases:
            result = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_case_transformations(self, engine):
        """Test case transformation rules."""
        test_cases = [
            ('/l', 'SAY HELLO TO MY LITTLE FRIEND!', 'say hello to my little friend!'),
            ('/u', 'Can you hear me, Major Tom?', 'CAN YOU HEAR ME, MAJOR TOM?'),
            ('/p', 'The quick brown fox jumps over the lazy dog', 'TheQuickBrownFoxJumpsOverTheLazyDog'),
            ('/c', 'is error state!', 'isErrorState'),
            ('/s', 'is error state!', 'is_error_state'),
            ('/a', 'the quick brown fox jumps over the lazy dog', 'The Quick Brown Fox Jumps Over The Lazy Dog'),
        ]
        
        for rule, input_text, expected in test_cases:
            result = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_string_operations(self, engine):
        """Test string operation rules."""
        test_cases = [
            ('/t', '  Well, something is happening  ', 'Well, something is happening'),
            ('/R', 'hello', 'olleh'),
            ('/si', 'A0001\r\nA0002\r\nA0003', "'A0001',\r\n'A0002',\r\n'A0003'"),
            ('/dlb', 'A0001\r\nA0002\r\nA0003', 'A0001A0002A0003'),
        ]
        
        for rule, input_text, expected in test_cases:
            result = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_sequential_processing(self, engine):
        """Test sequential rule processing."""
        test_cases = [
            ('/t/l', '  HELLO WORLD  ', 'hello world'),
            ('/s/u', 'The Quick Brown Fox', 'THE_QUICK_BROWN_FOX'),
        ]
        
        for rule, input_text, expected in test_cases:
            result = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_argument_based_rules(self, engine):
        """Test rules with arguments."""
        test_cases = [
            ("/S '+'", 'http://foo.bar/baz/brrr', 'http+foo+bar+baz+brrr'),
            ("/r 'Will' 'Bill'", "I'm Will, Will's son", "I'm Bill, Bill's son"),
            ("/S", 'hello world test', 'hello-world-test'),  # Default replacement
            ("/r 'this'", 'remove this text', 'remove  text'),  # Default replacement (empty)
        ]
        
        for rule, input_text, expected in test_cases:
            result = engine.apply_transformations(input_text, rule)
            assert result == expected, f"Rule {rule} failed: got '{result}', expected '{expected}'"
    
    def test_invalid_rule(self, engine):
        """Test handling of invalid rules."""
        with pytest.raises(ValueError, match="Unknown rule"):
            engine.apply_transformations("test", "/invalid")


class TestInteractiveSession:
    """Test interactive session functionality."""
    
    @pytest.fixture
    def session(self):
        """Create an InteractiveSession instance for testing."""
        io_manager = Mock(spec=InputOutputManager)
        engine = Mock(spec=TextTransformationEngine)
        return InteractiveSession(io_manager, engine)
    
    def test_initialization(self, session):
        """Test session initialization."""
        assert session.current_text == ""
        assert session.text_source == "clipboard"
        assert not session.auto_detection_enabled
    
    def test_update_working_text(self, session):
        """Test updating working text."""
        session.update_working_text("test text", "manual")
        
        assert session.current_text == "test text"
        assert session.text_source == "manual"
    
    def test_get_status_info(self, session):
        """Test getting status information."""
        session.update_working_text("test", "clipboard")
        status = session.get_status_info()
        
        assert status.current_text == "test"
        assert status.text_source == "clipboard"
        assert status.character_count == 4
        assert not status.auto_detection_enabled
    
    @patch('String_Multitool.pyperclip')
    def test_refresh_from_clipboard(self, mock_pyperclip, session):
        """Test refreshing from clipboard."""
        mock_pyperclip.paste.return_value = "new content"
        session.io_manager.get_clipboard_text.return_value = "new content"
        
        result = session.refresh_from_clipboard()
        
        assert result is True
        assert session.current_text == "new content"
        assert session.text_source == "clipboard"


class TestCommandProcessor:
    """Test command processing functionality."""
    
    @pytest.fixture
    def processor(self):
        """Create a CommandProcessor instance for testing."""
        session = Mock(spec=InteractiveSession)
        return CommandProcessor(session)
    
    def test_is_command(self, processor):
        """Test command detection."""
        assert processor.is_command("help") is True
        assert processor.is_command("refresh") is True
        assert processor.is_command("status") is True
        assert processor.is_command("/t/l") is False
        assert processor.is_command("/enc") is False
    
    def test_status_command(self, processor):
        """Test status command processing."""
        # Mock session status
        mock_status = Mock()
        mock_status.character_count = 10
        mock_status.text_source = "clipboard"
        mock_status.auto_detection_enabled = False
        mock_status.clipboard_monitor_active = False
        
        processor.session.get_status_info.return_value = mock_status
        processor.session.get_display_text.return_value = "test text"
        processor.session.get_time_since_update.return_value = "1 minute ago"
        
        result = processor.process_command("status")
        
        assert result.success is True
        assert "Session Status" in result.message
        assert "10 characters" in result.message


@pytest.fixture(autouse=True)
def mock_clipboard():
    """Mock clipboard functionality for all tests."""
    with patch('String_Multitool.CLIPBOARD_AVAILABLE', True):
        with patch('String_Multitool.pyperclip') as mock_pyperclip:
            mock_pyperclip.paste.return_value = ""
            mock_pyperclip.copy.return_value = None
            yield mock_pyperclip


def test_main_functionality():
    """Integration test for main functionality."""
    # Test that the main components can be instantiated without errors
    config_manager = ConfigurationManager()
    engine = TextTransformationEngine(config_manager)
    
    # Test a simple transformation
    result = engine.apply_transformations("hello world", "/u")
    assert result == "HELLO WORLD"


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])