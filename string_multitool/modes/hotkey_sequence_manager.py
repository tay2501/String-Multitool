"""
Hotkey sequence management for daemon mode.

This module provides specialized hotkey sequence detection and management
following the Single Responsibility Principle.
"""

from __future__ import annotations

import threading
from collections.abc import Mapping, Sequence, Callable
from datetime import datetime
from typing import Any, Final, Protocol
from typing_extensions import TypeAlias

from ..core.types import TransformationEngineProtocol
from ..exceptions import ValidationError, TransformationError
from ..io.manager import InputOutputManager

try:
    import keyboard
    KEYBOARD_AVAILABLE: Final[bool] = True
except ImportError:
    try:
        from pynput import keyboard as pynput_keyboard
        PYNPUT_AVAILABLE: Final[bool] = True
        KEYBOARD_AVAILABLE: Final[bool] = False
    except ImportError:
        PYNPUT_AVAILABLE: Final[bool] = False
        KEYBOARD_AVAILABLE: Final[bool] = False

# Type aliases
HotkeyCallback: TypeAlias = Callable[[], None]
SequenceConfig: TypeAlias = Mapping[str, Any]


class HotkeySequenceCallback(Protocol):
    """Protocol for hotkey sequence callbacks."""
    
    def __call__(self, rule: str, original_content: str, transformed_content: str) -> None:
        """Called when a hotkey sequence triggers a transformation."""
        ...


class HotkeySequenceManager:
    """
    Specialized hotkey sequence detection and management component.
    
    Handles global hotkey sequence detection, registration, and execution
    of transformation rules. Follows SRP by focusing solely on hotkey
    sequence functionality.
    """
    
    # Class constants
    DEFAULT_SEQUENCE_TIMEOUT: Final[float] = 2.0
    SEQUENCE_MAX_LENGTH: Final[int] = 2
    
    def __init__(
        self,
        transformation_engine: TransformationEngineProtocol,
        sequence_config: SequenceConfig,
        *,
        timeout: float = DEFAULT_SEQUENCE_TIMEOUT
    ) -> None:
        """
        Initialize hotkey sequence manager.
        
        Args:
            transformation_engine: Engine for text transformations
            sequence_config: Sequence configuration mapping
            timeout: Sequence timeout in seconds
            
        Raises:
            ValidationError: If configuration is invalid
        """
        if transformation_engine is None:
            raise ValidationError("Transformation engine cannot be None")
        
        if not isinstance(sequence_config, Mapping):
            raise ValidationError("Sequence config must be a mapping")
        
        if timeout <= 0:
            raise ValidationError("Timeout must be positive")
        
        self._transformation_engine = transformation_engine
        self._config = sequence_config
        self._timeout = timeout
        
        # State management
        self._is_active = False
        self._hotkey_listener: Any | None = None
        self._registered_hotkeys: list[str] = []
        
        # Sequence detection state
        self._key_sequence: list[str] = []
        self._last_key_time: datetime | None = None
        
        # Statistics
        self._stats = {
            "sequences_detected": 0,
            "transformations_applied": 0,
            "last_sequence": None
        }
        
        # Callbacks
        self._sequence_callbacks: list[HotkeySequenceCallback] = []
    
    @property
    def is_active(self) -> bool:
        """Check if hotkey sequence detection is active."""
        return self._is_active
    
    @property
    def stats(self) -> dict[str, Any]:
        """Get hotkey sequence statistics.""" 
        return self._stats.copy()
    
    @property
    def keyboard_available(self) -> bool:
        """Check if keyboard monitoring is available."""
        return KEYBOARD_AVAILABLE or PYNPUT_AVAILABLE
    
    def add_sequence_callback(self, callback: HotkeySequenceCallback) -> None:
        """Add a callback to be called when sequences are detected."""
        self._sequence_callbacks.append(callback)
    
    def remove_sequence_callback(self, callback: HotkeySequenceCallback) -> None:
        """Remove a sequence callback."""
        if callback in self._sequence_callbacks:
            self._sequence_callbacks.remove(callback)
    
    def start_sequence_monitoring(self) -> None:
        """
        Start hotkey sequence monitoring.
        
        Raises:
            ValidationError: If keyboard monitoring is not available
            TransformationError: If monitoring cannot be started
        """
        if self._is_active:
            return
        
        if not self.keyboard_available:
            raise ValidationError(
                "Keyboard monitoring not available (no keyboard/pynput library)"
            )
        
        if not self._config.get("enabled", False):
            return  # Silently skip if not enabled
        
        try:
            if KEYBOARD_AVAILABLE:
                self._start_keyboard_monitoring()
            elif PYNPUT_AVAILABLE:
                self._start_pynput_monitoring()
            
            self._is_active = True
            
        except Exception as e:
            raise TransformationError(
                f"Failed to start hotkey sequence monitoring: {e}"
            ) from e
    
    def stop_sequence_monitoring(self) -> None:
        """
        Stop hotkey sequence monitoring.
        
        Raises:
            TransformationError: If monitoring cannot be stopped
        """
        if not self._is_active:
            return
        
        try:
            self._is_active = False
            
            if KEYBOARD_AVAILABLE:
                self._stop_keyboard_monitoring()
            
            if self._hotkey_listener:
                self._hotkey_listener.stop()
                self._hotkey_listener = None
            
            # Clear sequence state
            self._key_sequence.clear()
            self._last_key_time = None
            
        except Exception as e:
            raise TransformationError(
                f"Failed to stop hotkey sequence monitoring: {e}"
            ) from e
    
    def _start_keyboard_monitoring(self) -> None:
        """Start sequence monitoring using keyboard library."""
        sequences: Mapping[str, Any] = self._config.get("sequences", {})
        
        for rule, seq_info in sequences.items():
            sequence: Sequence[str] = seq_info.get("sequence", [])
            if len(sequence) != self.SEQUENCE_MAX_LENGTH:
                continue
            
            try:
                # Create callbacks for this specific sequence
                first_callback, second_callback = self._create_sequence_callbacks(
                    rule, sequence
                )
                
                # Register both hotkeys
                first_key = sequence[0].replace('+', '+')
                second_key = sequence[1].replace('+', '+')\n                \n                keyboard.add_hotkey(first_key, first_callback)\n                keyboard.add_hotkey(second_key, second_callback)\n                \n                self._registered_hotkeys.extend([first_key, second_key])\n                \n            except Exception as e:\n                print(f\"[HOTKEY_SEQUENCE] Warning: Failed to register {rule}: {e}\")\n    \n    def _start_pynput_monitoring(self) -> None:\n        \"\"\"Start sequence monitoring using pynput library (fallback).\"\"\"\n        self._hotkey_listener = pynput_keyboard.Listener(\n            on_press=self._on_key_press_pynput,\n            on_release=None\n        )\n        self._hotkey_listener.start()\n    \n    def _stop_keyboard_monitoring(self) -> None:\n        \"\"\"Stop keyboard library monitoring.\"\"\"\n        for hotkey in self._registered_hotkeys:\n            try:\n                keyboard.remove_hotkey(hotkey)\n            except Exception:\n                pass  # Ignore removal errors\n        self._registered_hotkeys.clear()\n    \n    def _create_sequence_callbacks(\n        self, \n        rule_name: str, \n        sequence: Sequence[str]\n    ) -> tuple[HotkeyCallback, HotkeyCallback]:\n        \"\"\"Create callback functions for a hotkey sequence.\"\"\"\n        sequence_state: dict[str, Any] = {\n            \"last_key_time\": None, \n            \"expecting_second\": False\n        }\n        \n        def first_key_callback() -> None:\n            sequence_state[\"last_key_time\"] = datetime.now()\n            sequence_state[\"expecting_second\"] = True\n            # Set a timer to reset the sequence\n            threading.Timer(\n                self._timeout,\n                lambda: sequence_state.update({\"expecting_second\": False})\n            ).start()\n        \n        def second_key_callback() -> None:\n            if (\n                sequence_state[\"expecting_second\"]\n                and sequence_state[\"last_key_time\"]\n                and (datetime.now() - sequence_state[\"last_key_time\"]).total_seconds() <= self._timeout\n            ):\n                self._apply_sequence_rule(rule_name)\n                sequence_state[\"expecting_second\"] = False\n        \n        return first_key_callback, second_key_callback\n    \n    def _on_key_press_pynput(self, key: Any) -> None:\n        \"\"\"Handle keyboard key press events for sequence detection.\"\"\"\n        try:\n            # Convert key to string format\n            key_str = self._key_to_string(key)\n            if not key_str:\n                return\n            \n            # Check for sequence timeout\n            current_time = datetime.now()\n            if (\n                self._last_key_time\n                and (current_time - self._last_key_time).total_seconds() > self._timeout\n            ):\n                self._key_sequence.clear()\n            \n            # Add key to sequence\n            self._key_sequence.append(key_str)\n            self._last_key_time = current_time\n            \n            # Keep only last keys (maximum sequence length)\n            if len(self._key_sequence) > self.SEQUENCE_MAX_LENGTH:\n                self._key_sequence = self._key_sequence[-self.SEQUENCE_MAX_LENGTH:]\n            \n            # Check if current sequence matches any configured sequences\n            self._check_sequence_match()\n            \n        except Exception as e:\n            print(f\"[HOTKEY_SEQUENCE] Error processing key press: {e}\")\n    \n    def _key_to_string(self, key: Any) -> str | None:\n        \"\"\"Convert pynput key to string format.\"\"\"\n        try:\n            # Handle special keys\n            if hasattr(key, 'char') and key.char is not None:\n                return key.char.lower()\n            \n            # For modifier combinations, use simplified approach\n            current_modifiers = self._get_current_modifiers()\n            \n            if hasattr(key, 'char') and key.char:\n                if current_modifiers:\n                    return f\"{'+'.join(current_modifiers)}+{key.char.lower()}\"\n                return key.char.lower()\n            elif hasattr(key, 'name'):\n                if current_modifiers:\n                    return f\"{'+'.join(current_modifiers)}+{key.name.lower()}\"\n                return key.name.lower()\n        except Exception:\n            pass\n        return None\n    \n    def _get_current_modifiers(self) -> list[str]:\n        \"\"\"Get currently pressed modifier keys (simplified implementation).\"\"\"\n        modifiers: list[str] = []\n        try:\n            # Check if ctrl+shift combination is pressed\n            if KEYBOARD_AVAILABLE:\n                import keyboard as kb\n                if kb.is_pressed('ctrl') and kb.is_pressed('shift'):\n                    modifiers = ['ctrl', 'shift']\n        except Exception:\n            pass\n        return modifiers\n    \n    def _check_sequence_match(self) -> None:\n        \"\"\"Check if current key sequence matches any configured sequences.\"\"\"\n        if len(self._key_sequence) < self.SEQUENCE_MAX_LENGTH:\n            return\n        \n        sequences: Mapping[str, Any] = self._config.get(\"sequences\", {})\n        current_seq = self._key_sequence[-self.SEQUENCE_MAX_LENGTH:]\n        \n        for rule, seq_config in sequences.items():\n            expected_sequence: Sequence[str] = seq_config.get(\"sequence\", [])\n            if len(expected_sequence) != self.SEQUENCE_MAX_LENGTH:\n                continue\n            \n            if self._sequences_match(current_seq, expected_sequence):\n                self._stats[\"sequences_detected\"] += 1\n                self._stats[\"last_sequence\"] = rule\n                self._apply_sequence_rule(rule)\n                self._key_sequence.clear()\n                break\n    \n    def _sequences_match(\n        self, \n        current: Sequence[str], \n        expected: Sequence[str]\n    ) -> bool:\n        \"\"\"Check if current sequence matches expected sequence.\"\"\"\n        if len(current) != len(expected):\n            return False\n        \n        try:\n            for curr_key, exp_key in zip(current, expected):\n                if \"ctrl+shift+\" in exp_key:\n                    target_key = exp_key.split('+')[-1]\n                    if target_key not in curr_key:\n                        return False\n                elif curr_key != exp_key:\n                    return False\n            return True\n        except Exception:\n            return False\n    \n    def _apply_sequence_rule(self, rule: str) -> None:\n        \"\"\"Apply transformation rule triggered by sequence hotkey.\"\"\"\n        try:\n            # Get clipboard content\n            io_manager = InputOutputManager()\n            content = io_manager.get_clipboard_text()\n            \n            if not content.strip():\n                return\n            \n            # Apply the transformation\n            result = self._transformation_engine.apply_transformations(content, rule)\n            \n            if result != content:\n                # Update clipboard with result\n                io_manager.set_output_text(result)\n                \n                # Update statistics\n                self._stats[\"transformations_applied\"] += 1\n                \n                # Notify callbacks\n                for callback in self._sequence_callbacks:\n                    try:\n                        callback(rule, content, result)\n                    except Exception as e:\n                        print(f\"[HOTKEY_SEQUENCE] Callback error: {e}\")\n        \n        except Exception as e:\n            print(f\"[HOTKEY_SEQUENCE] Error applying sequence rule {rule}: {e}\")"}, {"old_string": "                keyboard.add_hotkey(first_key, first_callback)\n                keyboard.add_hotkey(second_key, second_callback)\n                \n                self._registered_hotkeys.extend([first_key, second_key])", "new_string": "                keyboard.add_hotkey(first_key, first_callback)\n                keyboard.add_hotkey(second_key, second_callback)\n                \n                self._registered_hotkeys.extend([first_key, second_key])"}]