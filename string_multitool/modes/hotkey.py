"""
Hotkey mode implementation for String_Multitool using keyboard library.

This module provides global hotkey monitoring with sequential key input
support and automatic transformation execution using the keyboard library.
"""

from __future__ import annotations

import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

try:
    import keyboard
    import pyperclip
    KEYBOARD_AVAILABLE = True
except ImportError as e:
    KEYBOARD_AVAILABLE = False
    raise ImportError(
        "keyboard and pyperclip are required for hotkey mode. "
        "Install with: pip install keyboard pyperclip"
    ) from e

from ..exceptions import ValidationError, ConfigurationError
from ..core.types import (
    IOManagerProtocol, TransformationEngineProtocol, ConfigManagerProtocol
)
from ..utils.logger import get_logger


class SequenceState:
    """Manages the state of hotkey sequences using keyboard library."""
    
    def __init__(self, timeout_seconds: float = 2.0) -> None:
        """Initialize sequence state manager.
        
        Args:
            timeout_seconds: Timeout for key sequences in seconds
        """
        self.is_waiting: bool = False
        self.timeout_seconds: float = timeout_seconds
        self.start_time: Optional[datetime] = None
        self.first_key: Optional[str] = None
        self._lock = threading.Lock()
    
    def start_sequence(self, first_key: str) -> None:
        """Start a new key sequence."""
        with self._lock:
            self.is_waiting = True
            self.start_time = datetime.now()
            self.first_key = first_key
    
    def end_sequence(self) -> None:
        """End the current key sequence."""
        with self._lock:
            self.is_waiting = False
            self.start_time = None
            self.first_key = None
    
    def is_sequence_active(self) -> bool:
        """Check if a sequence is currently active and not timed out."""
        with self._lock:
            if not self.is_waiting or self.start_time is None:
                return False
            
            elapsed = datetime.now() - self.start_time
            if elapsed.total_seconds() > self.timeout_seconds:
                self.end_sequence()
                return False
                
            return True
    
    def get_first_key(self) -> Optional[str]:
        """Get the first key of the current sequence."""
        with self._lock:
            return self.first_key


class HotkeyMode:
    """Global hotkey mode for String_Multitool using keyboard library.
    
    This class provides reliable sequential hotkey functionality with
    configurable key mappings and automatic transformation execution.
    """
    
    def __init__(
        self,
        io_manager: IOManagerProtocol,
        transformation_engine: TransformationEngineProtocol, 
        config_manager: ConfigManagerProtocol
    ) -> None:
        """Initialize hotkey mode.
        
        Args:
            io_manager: InputOutputManager instance
            transformation_engine: TextTransformationEngine instance
            config_manager: ConfigurationManager instance
            
        Raises:
            ValidationError: If required parameters are invalid
            ConfigurationError: If hotkey configuration is invalid
        """
        if io_manager is None:
            raise ValidationError("IO manager cannot be None")
        if transformation_engine is None:
            raise ValidationError("Transformation engine cannot be None")
        if config_manager is None:
            raise ValidationError("Configuration manager cannot be None")
        
        self.io_manager = io_manager
        self.transformation_engine = transformation_engine
        self.config_manager = config_manager
        self.logger = get_logger(__name__)
        
        # Load hotkey configuration
        self._config = self._load_hotkey_config()
        
        # Initialize sequence state manager
        timeout = self._config.get("hotkey_settings", {}).get("sequence_timeout_seconds", 2.0)
        self.sequence_state = SequenceState(timeout)
        
        # Track active state
        self._is_running = False
        self._registered_hotkeys: list[str] = []
        
        # Parse hotkey mappings
        self._direct_hotkeys = self._parse_direct_hotkeys()
        self._sequence_hotkeys = self._parse_sequence_hotkeys()
    
    def _load_hotkey_config(self) -> dict[str, Any]:
        """Load hotkey configuration.
        
        Returns:
            Dictionary containing hotkey configuration
            
        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        try:
            self.logger.info("Loading hotkey configuration")
            return self.config_manager.load_hotkey_config()
        except AttributeError:
            raise ConfigurationError(
                "ConfigurationManager does not support hotkey configuration yet",
                {"config_manager_type": type(self.config_manager).__name__}
            )
    
    def _parse_direct_hotkeys(self) -> dict[str, str]:
        """Parse direct hotkey mappings from configuration.
        
        Returns:
            Dictionary mapping hotkey strings to commands
        """
        direct_mappings = {}
        direct_hotkeys = self._config.get("direct_hotkeys", {})
        
        for hotkey, config in direct_hotkeys.items():
            command = config.get("command", "")
            if command:
                direct_mappings[hotkey] = command
        
        return direct_mappings
    
    def _parse_sequence_hotkeys(self) -> dict[str, dict[str, str]]:
        """Parse sequence hotkey mappings from configuration.
        
        Returns:
            Dictionary mapping first keys to their sequence mappings
        """
        sequence_mappings = {}
        sequence_hotkeys = self._config.get("sequence_hotkeys", {})
        
        for first_key, config in sequence_hotkeys.items():
            sequences = config.get("sequences", {})
            sequence_commands = {}
            
            for second_key, seq_config in sequences.items():
                command = seq_config.get("command", "")
                if command:
                    sequence_commands[second_key] = command
            
            if sequence_commands:
                sequence_mappings[first_key] = sequence_commands
        
        return sequence_mappings
    
    def _execute_command(self, command: str) -> None:
        """Execute a transformation command.
        
        Args:
            command: Transformation command string (e.g., "/l", "/t/u")
        """
        try:
            self.logger.info(f"Executing hotkey command: {command}")
            
            # Get current clipboard content using pyperclip
            current_text = pyperclip.paste()
            if not current_text:
                self.logger.warning("Clipboard is empty, nothing to transform")
                return
            
            # Apply transformation
            result = self.transformation_engine.apply_transformations(current_text, command)
            
            # Copy result to clipboard using pyperclip
            pyperclip.copy(result)
            self.logger.info("Result copied to clipboard")
            self.logger.info("Hotkey transformation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error executing hotkey command {command}: {e}")
    
    def _on_direct_hotkey(self, command: str) -> None:
        """Handle direct hotkey press.
        
        Args:
            command: The command to execute
        """
        self._execute_command(command)
    
    def _on_sequence_start(self, first_key: str) -> None:
        """Handle sequence hotkey start.
        
        Args:
            first_key: The first key in the sequence (e.g., 'h' for h→u sequence)
        """
        try:
            if first_key not in self._sequence_hotkeys:
                self.logger.warning(f"Unknown sequence key: {first_key}")
                return
            
            self.logger.debug(f"Sequence started: {first_key}")
            self.sequence_state.start_sequence(first_key)
            
        except Exception as e:
            self.logger.error(f"Error handling sequence start {first_key}: {e}")
    
    def _on_sequence_key(self, key: str) -> None:
        """Handle unified sequence key press.
        
        Args:
            key: The key pressed
        """
        try:
            if self.sequence_state.is_sequence_active():
                # This is a second key in sequence
                first_key = self.sequence_state.get_first_key()
                if not first_key:
                    return
                
                sequences = self._sequence_hotkeys.get(first_key, {})
                if key not in sequences:
                    self.logger.warning(f"Unknown sequence: {first_key}→{key}")
                    self.sequence_state.end_sequence()
                    return
                
                command = sequences[key]
                self.logger.info(f"Executing sequence command: {first_key}→{key} = {command}")
                self._execute_command(command)
                self.sequence_state.end_sequence()
            else:
                # This could be a first key in sequence
                if key in self._sequence_hotkeys:
                    self.logger.debug(f"Sequence started: {key}")
                    self.sequence_state.start_sequence(key)
                else:
                    self.logger.warning(f"Unknown sequence key: {key}")
            
        except Exception as e:
            self.logger.error(f"Error handling sequence key {key}: {e}")
            self.sequence_state.end_sequence()
    
    def _on_sequence_second_key(self, second_key: str) -> None:
        """Handle second key in sequence (deprecated - use _on_sequence_key).
        
        Args:
            second_key: The second key pressed
        """
        # This method is kept for compatibility but should not be used
        self._on_sequence_key(second_key)
    
    def start(self) -> None:
        """Start hotkey monitoring."""
        if self._is_running:
            self.logger.warning("Hotkey mode is already running")
            return
        
        if not self._config.get("hotkey_settings", {}).get("enabled", False):
            raise ConfigurationError("Hotkey mode is disabled in configuration")
        
        try:
            self.logger.info("Starting keyboard hotkey mode...")
            
            # Register direct hotkeys
            for hotkey_str, command in self._direct_hotkeys.items():
                try:
                    keyboard.add_hotkey(
                        hotkey_str, 
                        lambda cmd=command: self._on_direct_hotkey(cmd)
                    )
                    self._registered_hotkeys.append(hotkey_str)
                except Exception as e:
                    self.logger.warning(f"Failed to register direct hotkey {hotkey_str}: {e}")
            
            # Register sequence hotkeys with unified handler
            modifier = self._config.get("hotkey_settings", {}).get("modifier_key", "ctrl+shift")
            
            # Collect all unique keys (first keys and second keys)
            all_sequence_keys = set()
            for first_key, sequences in self._sequence_hotkeys.items():
                all_sequence_keys.add(first_key)
                all_sequence_keys.update(sequences.keys())
            
            # Register unified sequence handler for each unique key
            for key in all_sequence_keys:
                sequence_hotkey = f"{modifier}+{key}"
                try:
                    keyboard.add_hotkey(
                        sequence_hotkey,
                        lambda k=key: self._on_sequence_key(k)
                    )
                    self._registered_hotkeys.append(sequence_hotkey)
                except Exception as e:
                    self.logger.warning(f"Failed to register sequence hotkey {sequence_hotkey}: {e}")
            
            self._is_running = True
            
            self.logger.info("Keyboard hotkey mode started successfully")
            self.logger.info(f"Direct hotkeys: {len(self._direct_hotkeys)} registered")
            self.logger.info(f"Sequence hotkeys: {len(self._sequence_hotkeys)} registered")
            
        except Exception as e:
            self.logger.error(f"Failed to start hotkey mode: {e}")
            raise
    
    def stop(self) -> None:
        """Stop hotkey monitoring."""
        if not self._is_running:
            return
        
        try:
            self.logger.info("Stopping hotkey mode...")
            
            # Remove all registered hotkeys
            for hotkey in self._registered_hotkeys:
                try:
                    keyboard.remove_hotkey(hotkey)
                except Exception as e:
                    self.logger.warning(f"Failed to remove hotkey {hotkey}: {e}")
            
            self._registered_hotkeys.clear()
            self.sequence_state.end_sequence()
            self._is_running = False
            
            self.logger.info("Hotkey mode stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping hotkey mode: {e}")
    
    def is_running(self) -> bool:
        """Check if hotkey mode is currently running.
        
        Returns:
            True if hotkey mode is active
        """
        return self._is_running
    
    def run(self) -> None:
        """Run hotkey mode (blocking).
        
        This method starts hotkey monitoring and blocks until stopped.
        """
        self.start()
        
        try:
            self.logger.info("Hotkey mode is now active. Press Ctrl+C to exit.")
            
            # Keep the main thread alive
            while self._is_running:
                time.sleep(0.1)
                
                # Clean up timed out sequences
                if self.sequence_state.is_sequence_active():
                    # The is_sequence_active method handles timeout cleanup
                    pass
        
        except KeyboardInterrupt:
            self.logger.info("Hotkey mode interrupted by user")
        
        finally:
            self.stop()