"""
Clipboard monitoring component for daemon mode.

This module provides specialized clipboard monitoring functionality
following the Single Responsibility Principle.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Mapping
from datetime import datetime
from typing import Any, Final, Protocol

from ..core.types import TransformationEngineProtocol
from ..exceptions import TransformationError, ValidationError
from ..io.manager import InputOutputManager


class ClipboardChangeCallback(Protocol):
    """Protocol for clipboard change callbacks."""

    def __call__(self, content: str, transformed_result: str) -> None:
        """Called when clipboard content is successfully transformed."""
        ...


class ClipboardMonitor:
    """
    Specialized clipboard monitoring component.

    Handles continuous clipboard monitoring with configurable filtering
    and transformation application. Follows SRP by focusing solely on
    clipboard-related operations.
    """

    # Class constants
    DEFAULT_CHECK_INTERVAL: Final[float] = 1.0
    SLEEP_RESOLUTION: Final[float] = 0.1
    MAX_DISPLAY_LENGTH: Final[int] = 50

    def __init__(
        self,
        transformation_engine: TransformationEngineProtocol,
        monitor_config: Mapping[str, Any],
        *,
        check_interval: float = DEFAULT_CHECK_INTERVAL,
    ) -> None:
        """
        Initialize clipboard monitor.

        Args:
            transformation_engine: Engine for text transformations
            monitor_config: Monitoring configuration
            check_interval: Monitoring check interval in seconds

        Raises:
            ValidationError: If configuration is invalid
        """
        if transformation_engine is None:
            raise ValidationError("Transformation engine cannot be None")

        if not isinstance(monitor_config, Mapping):
            raise ValidationError("Monitor config must be a mapping")

        if check_interval <= 0:
            raise ValidationError("Check interval must be positive")

        self._transformation_engine = transformation_engine
        self._config = monitor_config
        self._check_interval = check_interval

        # State management
        self._is_running: bool = False
        self._monitor_thread: threading.Thread | None = None
        self._last_clipboard_content = ""
        self._active_rules: list[str] = []

        # Statistics
        self._stats: dict[str, int | datetime | None] = {
            "transformations_applied": 0,
            "start_time": None,
            "last_transformation": None,
        }

        # Callbacks
        self._change_callbacks: list[ClipboardChangeCallback] = []

    @property
    def is_running(self) -> bool:
        """Check if monitor is currently running."""
        return self._is_running

    @property
    def stats(self) -> dict[str, Any]:
        """Get monitoring statistics."""
        return self._stats.copy()

    def set_active_rules(self, rules: list[str]) -> None:
        """
        Set active transformation rules.

        Args:
            rules: List of transformation rules to apply

        Raises:
            ValidationError: If rules are invalid
        """
        if not isinstance(rules, list):
            raise ValidationError(f"Rules must be a list, got {type(rules).__name__}")

        if not rules:
            raise ValidationError("Rules list cannot be empty")

        for rule in rules:
            if not isinstance(rule, str):
                raise ValidationError(
                    f"Each rule must be a string, got {type(rule).__name__}"
                )

        self._active_rules = rules.copy()

    def add_change_callback(self, callback: ClipboardChangeCallback) -> None:
        """Add a callback to be called when clipboard changes."""
        self._change_callbacks.append(callback)

    def remove_change_callback(self, callback: ClipboardChangeCallback) -> None:
        """Remove a clipboard change callback."""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    def start_monitoring(self) -> None:
        """
        Start clipboard monitoring in a background thread.

        Raises:
            ValidationError: If no transformation rules are set
            TransformationError: If monitoring cannot be started
        """
        if self._is_running:
            return

        if not self._active_rules:
            raise ValidationError(
                "No transformation rules set. Use set_active_rules() first."
            )

        try:
            self._is_running = True
            self._stats["start_time"] = datetime.now()

            self._monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True, name="ClipboardMonitor"
            )
            self._monitor_thread.start()

        except Exception as e:
            self._is_running = False
            raise TransformationError(
                f"Failed to start clipboard monitoring: {e}"
            ) from e

    def stop_monitoring(self) -> None:
        """
        Stop clipboard monitoring.

        Raises:
            TransformationError: If monitoring cannot be stopped
        """
        if not self._is_running:
            return

        try:
            self._is_running = False

            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=2.0)

        except Exception as e:
            raise TransformationError(
                f"Failed to stop clipboard monitoring: {e}"
            ) from e

    def _monitor_loop(self) -> None:
        """Main clipboard monitoring loop."""
        sleep_iterations: Final[int] = max(1, int(self._check_interval / self.SLEEP_RESOLUTION))

        while self._is_running:
            try:
                io_manager = InputOutputManager()
                current_content = io_manager.get_clipboard_text()

                if self._should_process_content(current_content):
                    self._process_clipboard_content(current_content)

                # Use shorter sleep intervals for better responsiveness
                for _ in range(sleep_iterations):
                    if not self._is_running:
                        break  # type: ignore[unreachable]
                    time.sleep(self.SLEEP_RESOLUTION)

            except KeyboardInterrupt:
                print("\r[CLIPBOARD_MONITOR] Keyboard interrupt received, stopping...")
                self._is_running = False
                break
            except Exception as e:
                print(f"\\r[CLIPBOARD_MONITOR] Error: {e}", flush=True)
                time.sleep(self._check_interval)

    def _should_process_content(self, content: str) -> bool:
        """
        Check if clipboard content should be processed.

        Args:
            content: Clipboard content to check

        Returns:
            True if content should be processed
        """
        # Check if monitoring is enabled
        if not self._config.get("enabled", True):
            return False

        # Check if we have active rules
        if not self._active_rules:
            return False

        # Check if content is different from last processed
        if self._config.get("ignore_duplicates", True):
            if content == self._last_clipboard_content:
                return False

        # Check if content is empty
        if self._config.get("ignore_empty", True) and not content.strip():
            return False

        # Check content length
        min_length: Final[int] = self._config.get("min_length", 1)
        max_length: Final[int] = self._config.get("max_length", 10000)

        if len(content) < min_length or len(content) > max_length:
            return False

        return True

    def _process_clipboard_content(self, content: str) -> None:
        """
        Process clipboard content with active transformation rules.

        Args:
            content: Clipboard content to process
        """
        try:
            # Apply transformation rules sequentially
            result = content
            for rule in self._active_rules:
                result = self._transformation_engine.apply_transformations(result, rule)

            # Skip if transformation didn't change the content
            if result == content:
                return

            # Update clipboard with transformed content (silently)
            try:
                import pyperclip

                pyperclip.copy(result)
            except Exception:
                pass  # Silently fail if clipboard update fails

            # Update statistics and state
            transformations_count = self._stats["transformations_applied"]
            if isinstance(transformations_count, int):
                self._stats["transformations_applied"] = transformations_count + 1
            self._stats["last_transformation"] = datetime.now()
            self._last_clipboard_content = result

            # Notify callbacks
            for callback in self._change_callbacks:
                try:
                    callback(content, result)
                except Exception as e:
                    print(f"[CLIPBOARD_MONITOR] Callback error: {e}")

        except Exception as e:
            print(f"\\r[CLIPBOARD_MONITOR] Error processing content: {e}", flush=True)
