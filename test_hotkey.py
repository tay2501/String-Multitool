"""
Test cases for hotkey mode functionality.

This module provides comprehensive tests for the HotkeyMode class
and related hotkey functionality.
"""

import threading
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import pytest

from string_multitool.core.config import ConfigurationManager
from string_multitool.core.transformations import TextTransformationEngine
from string_multitool.exceptions import ConfigurationError, ValidationError
from string_multitool.io.manager import InputOutputManager
from string_multitool.modes.hotkey import HotkeyMode, SequenceState


class TestSequenceState:
    """Test cases for SequenceState class."""

    def test_initialization(self):
        """Test SequenceState initialization."""
        state = SequenceState(timeout_seconds=3.0)
        assert state.timeout_seconds == 3.0
        assert not state.is_waiting
        assert state.start_time is None
        assert state.first_key is None

    def test_start_sequence(self):
        """Test starting a key sequence."""
        state = SequenceState()
        state.start_sequence("h")

        assert state.is_waiting
        assert state.start_time is not None
        assert isinstance(state.start_time, datetime)
        assert state.first_key == "h"

    def test_end_sequence(self):
        """Test ending a key sequence."""
        state = SequenceState()
        state.start_sequence("h")
        state.end_sequence()

        assert not state.is_waiting
        assert state.start_time is None
        assert state.first_key is None

    def test_is_sequence_active(self):
        """Test sequence active detection."""
        state = SequenceState(timeout_seconds=0.1)

        # Initially not active
        assert not state.is_sequence_active()

        # Active after starting
        state.start_sequence("h")
        assert state.is_sequence_active()

        # Still active within timeout
        time.sleep(0.05)
        assert state.is_sequence_active()

        # Not active after timeout
        time.sleep(0.1)
        assert not state.is_sequence_active()

    def test_timeout_cleanup(self):
        """Test that timeout automatically cleans up state."""
        state = SequenceState(timeout_seconds=0.1)
        state.start_sequence("h")

        # Wait for timeout
        time.sleep(0.2)

        # Check that is_sequence_active cleans up expired state
        assert not state.is_sequence_active()
        assert not state.is_waiting
        assert state.start_time is None
        assert state.first_key is None


class TestHotkeyMode:
    """Test cases for HotkeyMode class."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for HotkeyMode."""
        io_manager = Mock(spec=InputOutputManager)
        transformation_engine = Mock(spec=TextTransformationEngine)
        config_manager = Mock(spec=ConfigurationManager)

        # Mock hotkey configuration
        config_manager.load_hotkey_config.return_value = {
            "hotkey_settings": {
                "enabled": True,
                "prefix_key": "ctrl+shift+s",
                "timeout_seconds": 2.0,
            },
            "key_mappings": {
                "l": {"command": "/l", "description": "lowercase"},
                "u": {"command": "/u", "description": "uppercase"},
            },
            "advanced_mappings": {
                "tl": {"command": "/t/l", "description": "trim and lowercase"}
            },
        }

        return io_manager, transformation_engine, config_manager

    def test_initialization_valid(self, mock_dependencies):
        """Test valid HotkeyMode initialization."""
        io_manager, transformation_engine, config_manager = mock_dependencies

        hotkey_mode = HotkeyMode(io_manager, transformation_engine, config_manager)

        assert hotkey_mode.io_manager is io_manager
        assert hotkey_mode.transformation_engine is transformation_engine
        assert hotkey_mode.config_manager is config_manager
        assert isinstance(hotkey_mode.sequence_state, SequenceState)
        assert hotkey_mode.sequence_state.timeout_seconds == 2.0
        assert not hotkey_mode.is_running()

    def test_initialization_invalid_io_manager(self, mock_dependencies):
        """Test initialization with invalid io_manager."""
        _, transformation_engine, config_manager = mock_dependencies

        with pytest.raises(ValidationError, match="IO manager cannot be None"):
            HotkeyMode(None, transformation_engine, config_manager)  # type: ignore

    def test_initialization_invalid_transformation_engine(self, mock_dependencies):
        """Test initialization with invalid transformation_engine."""
        io_manager, _, config_manager = mock_dependencies

        with pytest.raises(
            ValidationError, match="Transformation engine cannot be None"
        ):
            HotkeyMode(io_manager, None, config_manager)  # type: ignore

    def test_initialization_invalid_config_manager(self, mock_dependencies):
        """Test initialization with invalid config_manager."""
        io_manager, transformation_engine, _ = mock_dependencies

        with pytest.raises(
            ValidationError, match="Configuration manager cannot be None"
        ):
            HotkeyMode(io_manager, transformation_engine, None)  # type: ignore

    def test_execute_command(self, mock_dependencies):
        """Test command execution."""
        io_manager, transformation_engine, config_manager = mock_dependencies

        # Mock clipboard content
        io_manager.read_clipboard.return_value = "test text"
        transformation_engine.process_text.return_value = "TEST TEXT"

        hotkey_mode = HotkeyMode(io_manager, transformation_engine, config_manager)
        hotkey_mode._execute_command("/u")

        # Verify the transformation was called
        io_manager.read_clipboard.assert_called_once()
        transformation_engine.process_text.assert_called_once_with(
            "test text", "/u", apply_to_clipboard=True
        )

    def test_execute_command_empty_clipboard(self, mock_dependencies):
        """Test command execution with empty clipboard."""
        io_manager, transformation_engine, config_manager = mock_dependencies

        # Mock empty clipboard
        io_manager.read_clipboard.return_value = ""

        hotkey_mode = HotkeyMode(io_manager, transformation_engine, config_manager)

        # Should not raise exception but log warning
        hotkey_mode._execute_command("/u")

        # Verify transformation was not called
        transformation_engine.process_text.assert_not_called()

    @patch("string_multitool.modes.hotkey.keyboard")
    def test_start_stop(self, mock_keyboard, mock_dependencies):
        """Test starting and stopping hotkey mode."""
        io_manager, transformation_engine, config_manager = mock_dependencies

        # Mock keyboard listener
        mock_listener = Mock()
        mock_keyboard.Listener.return_value = mock_listener

        hotkey_mode = HotkeyMode(io_manager, transformation_engine, config_manager)

        # Test start
        hotkey_mode.start()
        assert hotkey_mode.is_running()
        mock_listener.start.assert_called_once()

        # Test stop
        hotkey_mode.stop()
        assert not hotkey_mode.is_running()
        mock_listener.stop.assert_called_once()

    def test_start_disabled_config(self, mock_dependencies):
        """Test starting with disabled configuration."""
        io_manager, transformation_engine, config_manager = mock_dependencies

        # Mock disabled configuration
        config_manager.load_hotkey_config.return_value = {
            "hotkey_settings": {"enabled": False}
        }

        hotkey_mode = HotkeyMode(io_manager, transformation_engine, config_manager)

        with pytest.raises(ConfigurationError, match="Hotkey mode is disabled"):
            hotkey_mode.start()


class TestHotkeyIntegration:
    """Integration tests for hotkey functionality."""

    @pytest.fixture
    def real_config_manager(self):
        """Create a real ConfigurationManager for integration tests."""
        return ConfigurationManager()

    @pytest.fixture
    def mock_other_dependencies(self):
        """Create mock dependencies except ConfigurationManager."""
        io_manager = Mock(spec=InputOutputManager)
        transformation_engine = Mock(spec=TextTransformationEngine)
        return io_manager, transformation_engine

    def test_load_real_hotkey_config(
        self, real_config_manager, mock_other_dependencies
    ):
        """Test loading real hotkey configuration."""
        io_manager, transformation_engine = mock_other_dependencies

        try:
            hotkey_mode = HotkeyMode(
                io_manager, transformation_engine, real_config_manager
            )

            # Should load configuration without errors
            config = hotkey_mode._config
            assert "hotkey_settings" in config
            assert "key_mappings" in config

        except ConfigurationError:
            # This is expected if config file doesn't exist in test environment
            pytest.skip("Hotkey config file not available in test environment")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
