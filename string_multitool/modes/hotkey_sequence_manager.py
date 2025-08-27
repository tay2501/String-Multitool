"""
Hotkey sequence management for daemon mode.

This module provides specialized hotkey sequence detection and management
following the Single Responsibility Principle.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime
from typing import Any, Final, Protocol

from typing_extensions import TypeAlias

from ..core.types import TransformationEngineProtocol
from ..exceptions import TransformationError, ValidationError
from ..io.manager import InputOutputManager

# Check library availability
_keyboard_available = False
_pynput_available = False

try:
    import keyboard

    _keyboard_available = True
except ImportError:
    try:
        from pynput import keyboard as pynput_keyboard

        _pynput_available = True
    except ImportError:
        pass

# Final constants based on availability
KEYBOARD_AVAILABLE: Final[bool] = _keyboard_available
PYNPUT_AVAILABLE: Final[bool] = _pynput_available

# Type aliases
HotkeyCallback: TypeAlias = Callable[[], None]
SequenceConfig: TypeAlias = Mapping[str, Any]


class HotkeySequenceCallback(Protocol):
    """Protocol for hotkey sequence callbacks."""

    def __call__(
        self, rule: str, original_content: str, transformed_content: str
    ) -> None:
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
        timeout: float = DEFAULT_SEQUENCE_TIMEOUT,
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

        # Load suppress setting from hotkey_settings
        hotkey_settings = sequence_config.get("hotkey_settings", {})
        self._suppress = hotkey_settings.get("suppress", True)

        # State management
        self._is_active = False
        self._hotkey_listener: Any | None = None
        self._registered_hotkeys: list[str] = []

        # Sequence detection state
        self._key_sequence: list[str] = []
        self._last_key_time: datetime | None = None

        # Statistics
        self._stats: dict[str, int | str | None] = {
            "sequences_detected": 0,
            "transformations_applied": 0,
            "last_sequence": None,
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
                first_key = sequence[0].replace("+", "+")
                second_key = sequence[1].replace("+", "+")

                keyboard.add_hotkey(first_key, first_callback, suppress=self._suppress)
                keyboard.add_hotkey(
                    second_key, second_callback, suppress=self._suppress
                )

                self._registered_hotkeys.extend([first_key, second_key])

            except Exception as e:
                print(f"[HOTKEY_SEQUENCE] Warning: Failed to register {rule}: {e}")

    def _start_pynput_monitoring(self) -> None:
        """Start sequence monitoring using pynput library (fallback)."""
        self._hotkey_listener = pynput_keyboard.Listener(
            on_press=self._on_key_press_pynput, on_release=None
        )
        if self._hotkey_listener is not None:
            self._hotkey_listener.start()

    def _stop_keyboard_monitoring(self) -> None:
        """Stop keyboard library monitoring."""
        for hotkey in self._registered_hotkeys:
            try:
                keyboard.remove_hotkey(hotkey)
            except Exception:
                pass  # Ignore removal errors
        self._registered_hotkeys.clear()

    def _create_sequence_callbacks(
        self, rule_name: str, sequence: Sequence[str]
    ) -> tuple[HotkeyCallback, HotkeyCallback]:
        """Create callback functions for a hotkey sequence."""
        sequence_state: dict[str, Any] = {
            "last_key_time": None,
            "expecting_second": False,
        }

        def first_key_callback() -> None:
            sequence_state["last_key_time"] = datetime.now()
            sequence_state["expecting_second"] = True
            # Set a timer to reset the sequence
            threading.Timer(
                self._timeout,
                lambda: sequence_state.update({"expecting_second": False}),
            ).start()

        def second_key_callback() -> None:
            if (
                sequence_state["expecting_second"]
                and sequence_state["last_key_time"]
                and (datetime.now() - sequence_state["last_key_time"]).total_seconds()
                <= self._timeout
            ):
                self._apply_sequence_rule(rule_name)
                sequence_state["expecting_second"] = False

        return first_key_callback, second_key_callback

    def _on_key_press_pynput(self, key: Any) -> None:
        """Handle keyboard key press events for sequence detection."""
        try:
            # Convert key to string format
            key_str = self._key_to_string(key)
            if not key_str:
                return

            # Check for sequence timeout
            current_time = datetime.now()
            if (
                self._last_key_time
                and (current_time - self._last_key_time).total_seconds() > self._timeout
            ):
                self._key_sequence.clear()

            # Add key to sequence
            self._key_sequence.append(key_str)
            self._last_key_time = current_time

            # Keep only last keys (maximum sequence length)
            if len(self._key_sequence) > self.SEQUENCE_MAX_LENGTH:
                self._key_sequence = self._key_sequence[-self.SEQUENCE_MAX_LENGTH :]

            # Check if current sequence matches any configured sequences
            self._check_sequence_match()

        except Exception as e:
            print(f"[HOTKEY_SEQUENCE] Error processing key press: {e}")

    def _key_to_string(self, key: Any) -> str | None:
        """Convert pynput key to string format."""
        try:
            # Handle special keys
            if hasattr(key, "char") and key.char is not None:
                return key.char.lower()

            # For modifier combinations, use simplified approach
            current_modifiers = self._get_current_modifiers()

            if hasattr(key, "char") and key.char:
                if current_modifiers:
                    return f"{'+'.join(current_modifiers)}+{key.char.lower()}"
                return key.char.lower()
            elif hasattr(key, "name"):
                if current_modifiers:
                    return f"{'+'.join(current_modifiers)}+{key.name.lower()}"
                return key.name.lower()
        except Exception:
            pass
        return None

    def _get_current_modifiers(self) -> list[str]:
        """Get currently pressed modifier keys (simplified implementation)."""
        modifiers: list[str] = []
        try:
            # Check if ctrl+shift combination is pressed
            if KEYBOARD_AVAILABLE:
                import keyboard as kb

                if kb.is_pressed("ctrl") and kb.is_pressed("shift"):
                    modifiers = ["ctrl", "shift"]
        except Exception:
            pass
        return modifiers

    def _check_sequence_match(self) -> None:
        """Check if current key sequence matches any configured sequences."""
        if len(self._key_sequence) < self.SEQUENCE_MAX_LENGTH:
            return

        sequences: Mapping[str, Any] = self._config.get("sequences", {})
        current_seq = self._key_sequence[-self.SEQUENCE_MAX_LENGTH :]

        for rule, seq_config in sequences.items():
            expected_sequence: Sequence[str] = seq_config.get("sequence", [])
            if len(expected_sequence) != self.SEQUENCE_MAX_LENGTH:
                continue

            if self._sequences_match(current_seq, expected_sequence):
                sequences_count = self._stats["sequences_detected"]
                if isinstance(sequences_count, int):
                    self._stats["sequences_detected"] = sequences_count + 1
                self._stats["last_sequence"] = rule
                self._apply_sequence_rule(rule)
                self._key_sequence.clear()
                break

    def _sequences_match(self, current: Sequence[str], expected: Sequence[str]) -> bool:
        """Check if current sequence matches expected sequence."""
        if len(current) != len(expected):
            return False

        try:
            for curr_key, exp_key in zip(current, expected):
                if "ctrl+shift+" in exp_key:
                    target_key = exp_key.split("+")[-1]
                    if target_key not in curr_key:
                        return False
                elif curr_key != exp_key:
                    return False
            return True
        except Exception:
            return False

    def _apply_sequence_rule(self, rule: str) -> None:
        """Apply transformation rule triggered by sequence hotkey."""
        try:
            # Get clipboard content
            io_manager = InputOutputManager()
            content = io_manager.get_clipboard_text()

            if not content.strip():
                return

            # Apply the transformation
            result = self._transformation_engine.apply_transformations(content, rule)

            if result != content:
                # Update clipboard with result
                io_manager.set_output_text(result)

                # Update statistics
                transformations_count = self._stats["transformations_applied"]
                if isinstance(transformations_count, int):
                    self._stats["transformations_applied"] = transformations_count + 1

                # Notify callbacks
                for callback in self._sequence_callbacks:
                    try:
                        callback(rule, content, result)
                    except Exception as e:
                        print(f"[HOTKEY_SEQUENCE] Callback error: {e}")

        except Exception as e:
            print(f"[HOTKEY_SEQUENCE] Error applying sequence rule {rule}: {e}")
