"""
Refactored daemon mode following SOLID principles.

This module provides the main daemon mode coordinator that orchestrates
specialized components following the Single Responsibility Principle.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Final

from ..core.types import ConfigManagerProtocol, TransformationEngineProtocol
from ..exceptions import ConfigurationError, TransformationError, ValidationError
from .clipboard_monitor import ClipboardChangeCallback, ClipboardMonitor
from .daemon_config_manager import DaemonConfigManager
from .hotkey_sequence_manager import HotkeySequenceCallback, HotkeySequenceManager


class DaemonMode:
    """
    Refactored daemon mode coordinator.

    This class orchestrates specialized components (clipboard monitor,
    hotkey sequence manager, configuration manager) following SOLID principles.
    It focuses solely on coordination and delegation, not implementation details.
    """

    def __init__(
        self,
        transformation_engine: TransformationEngineProtocol,
        config_manager: ConfigManagerProtocol,
    ) -> None:
        """
        Initialize daemon mode coordinator.

        Args:
            transformation_engine: Text transformation engine
            config_manager: Configuration manager

        Raises:
            ValidationError: If required parameters are invalid
            ConfigurationError: If daemon configuration is invalid
        """
        if transformation_engine is None:
            raise ValidationError("Transformation engine cannot be None")
        if config_manager is None:
            raise ValidationError("Config manager cannot be None")

        # Store core dependencies
        self._transformation_engine = transformation_engine
        self._config_manager = config_manager

        # Initialize specialized components
        try:
            self._daemon_config_manager = DaemonConfigManager()
            daemon_config = self._daemon_config_manager.load_config()

            # Initialize clipboard monitor
            clipboard_config = (
                self._daemon_config_manager.get_clipboard_monitoring_config()
            )
            check_interval = self._daemon_config_manager.get_check_interval()

            self._clipboard_monitor = ClipboardMonitor(
                transformation_engine, clipboard_config, check_interval=check_interval
            )

            # Initialize hotkey sequence manager
            sequence_config = self._daemon_config_manager.get_sequence_hotkeys_config()
            sequence_timeout = self._daemon_config_manager.get_sequence_timeout()

            self._hotkey_manager = HotkeySequenceManager(
                transformation_engine, sequence_config, timeout=sequence_timeout
            )

            # Set up callbacks
            self._setup_callbacks()

        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize daemon components: {e}"
            ) from e

        # State tracking
        self._active_preset: str | None = None
        self._start_time: datetime | None = None

    @property
    def is_running(self) -> bool:
        """Check if daemon is currently running."""
        return self._clipboard_monitor.is_running or self._hotkey_manager.is_active

    @property
    def active_rules(self) -> list[str]:
        """Get the currently active transformation rules."""
        if hasattr(self._clipboard_monitor, "_active_rules"):
            return self._clipboard_monitor._active_rules or []
        return []

    @property
    def active_preset(self) -> str | None:
        """Get currently active preset name."""
        return self._active_preset

    def start_monitoring(self) -> None:
        """
        Start daemon monitoring (clipboard and hotkey sequences).

        Raises:
            ValidationError: If no transformation rules are set
            TransformationError: If monitoring cannot be started
        """
        try:
            self._start_time = datetime.now()

            # Set default rules if none are set
            if (
                not hasattr(self._clipboard_monitor, "_active_rules")
                or not self._clipboard_monitor._active_rules
            ):
                # Try to set a default preset, fallback to basic trim+lowercase
                try:
                    self.set_preset("trim_lowercase")
                except (ValidationError, ConfigurationError):
                    # Fallback to basic rules if preset fails
                    self.set_transformation_rules(["/t", "/l"])

            # Start clipboard monitoring if enabled
            if self._daemon_config_manager.is_clipboard_monitoring_enabled():
                self._clipboard_monitor.start_monitoring()
                print("[DAEMON] Clipboard monitoring started")

            # Start hotkey sequence monitoring if enabled and available
            if (
                self._daemon_config_manager.is_sequence_hotkeys_enabled()
                and self._hotkey_manager.keyboard_available
            ):
                self._hotkey_manager.start_sequence_monitoring()
                print("[DAEMON] Hotkey sequence monitoring started")

        except Exception as e:
            # Clean up on failure
            self._stop_all_monitoring()
            raise TransformationError(f"Failed to start daemon monitoring: {e}") from e

    def stop(self) -> None:
        """Stop daemon monitoring and display statistics."""
        try:
            self._stop_all_monitoring()
            self._display_stop_statistics()
        except Exception as e:
            raise TransformationError(f"Failed to stop daemon monitoring: {e}") from e

    def set_transformation_rules(self, rules: list[str]) -> None:
        """Set active transformation rules for clipboard monitoring."""
        self._clipboard_monitor.set_active_rules(rules)
        self._active_preset = None  # Clear preset when setting custom rules
        print(f"[DAEMON] Active rules set: {' -> '.join(rules)}")

    def set_preset(self, preset_name: str) -> bool:
        """Set transformation preset and configure rules."""
        if not isinstance(preset_name, str) or not preset_name.strip():
            raise ValidationError("Preset name must be a non-empty string")

        try:
            preset_rules = self._daemon_config_manager.get_preset_rules(preset_name)
            self._clipboard_monitor.set_active_rules(preset_rules)
            self._active_preset = preset_name

            print(
                f"[DAEMON] Preset '{preset_name}' activated: {' -> '.join(preset_rules)}"
            )
            return True

        except ValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Failed to set preset '{preset_name}': {e}"
            ) from e

    def get_status(self) -> dict[str, Any]:
        """Get comprehensive daemon status information."""
        clipboard_stats = self._clipboard_monitor.stats
        hotkey_stats = self._hotkey_manager.stats

        # Combine statistics
        total_transformations = clipboard_stats.get(
            "transformations_applied", 0
        ) + hotkey_stats.get("transformations_applied", 0)

        status = {
            "running": self.is_running,
            "active_preset": self._active_preset,
            "clipboard_monitoring": {
                "enabled": self._daemon_config_manager.is_clipboard_monitoring_enabled(),
                "running": self._clipboard_monitor.is_running,
                "stats": clipboard_stats,
            },
            "hotkey_sequences": {
                "enabled": self._daemon_config_manager.is_sequence_hotkeys_enabled(),
                "available": self._hotkey_manager.keyboard_available,
                "active": self._hotkey_manager.is_active,
                "stats": hotkey_stats,
            },
            "total_transformations": total_transformations,
        }

        if self._start_time and self.is_running:
            runtime = datetime.now() - self._start_time
            status["runtime"] = str(runtime).split(".")[0]  # Remove microseconds

        return status

    def reload_config(self) -> None:
        """Reload daemon configuration from file."""
        try:
            # Reload configuration
            self._daemon_config_manager.load_config(force_reload=True)

            # Update component configurations
            # Note: This would require stopping and restarting components
            # in a full implementation
            print("[DAEMON] Configuration reloaded")

        except Exception as e:
            raise ConfigurationError(
                f"Failed to reload daemon configuration: {e}"
            ) from e

    def _setup_callbacks(self) -> None:
        """Set up callbacks between components."""

        # Clipboard change callback
        def on_clipboard_change(content: str, transformed_result: str) -> None:
            self._display_transformation("CLIPBOARD", content, transformed_result)

        self._clipboard_monitor.add_change_callback(on_clipboard_change)

        # Hotkey sequence callback
        def on_hotkey_sequence(
            rule: str, original_content: str, transformed_content: str
        ) -> None:
            self._display_transformation(
                f"HOTKEY({rule})", original_content, transformed_content
            )

        self._hotkey_manager.add_sequence_callback(on_hotkey_sequence)

    def _stop_all_monitoring(self) -> None:
        """Stop all monitoring components."""
        try:
            self._clipboard_monitor.stop_monitoring()
        except Exception as e:
            print(f"[DAEMON] Error stopping clipboard monitor: {e}")

        try:
            self._hotkey_manager.stop_sequence_monitoring()
        except Exception as e:
            print(f"[DAEMON] Error stopping hotkey manager: {e}")

    def _display_transformation(self, source: str, content: str, result: str) -> None:
        """Display transformation result with source information."""
        MAX_DISPLAY_LENGTH: Final[int] = 50

        display_input = (
            content[:MAX_DISPLAY_LENGTH] + "..."
            if len(content) > MAX_DISPLAY_LENGTH
            else content
        )
        display_output = (
            result[:MAX_DISPLAY_LENGTH] + "..."
            if len(result) > MAX_DISPLAY_LENGTH
            else result
        )

        print(
            f"\r[DAEMON:{source}] Transformed: '{display_input}' -> '{display_output}'",
            flush=True,
        )

    def _display_stop_statistics(self) -> None:
        """Display daemon stop statistics."""
        if self._start_time:
            runtime = datetime.now() - self._start_time
            print(f"[DAEMON] Stopped after {runtime}")

        status = self.get_status()
        total_transformations = status["total_transformations"]
        print(f"[DAEMON] Total transformations applied: {total_transformations}")

        clipboard_stats = status["clipboard_monitoring"]["stats"]
        hotkey_stats = status["hotkey_sequences"]["stats"]

        print(
            f"[DAEMON] Clipboard transformations: {clipboard_stats.get('transformations_applied', 0)}"
        )
        print(
            f"[DAEMON] Hotkey transformations: {hotkey_stats.get('transformations_applied', 0)}"
        )
        print(
            f"[DAEMON] Sequences detected: {hotkey_stats.get('sequences_detected', 0)}"
        )
