"""
Refactored daemon mode following SOLID principles.

This module provides the main daemon mode coordinator that orchestrates
specialized components following the Single Responsibility Principle.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any, Final

from ..core.types import TransformationEngineProtocol, ConfigManagerProtocol
from ..exceptions import ValidationError, TransformationError, ConfigurationError

from .clipboard_monitor import ClipboardMonitor, ClipboardChangeCallback
from .hotkey_sequence_manager import HotkeySequenceManager, HotkeySequenceCallback
from .daemon_config_manager import DaemonConfigManager


class DaemonModeRefactored:
    """
    Refactored daemon mode coordinator.
    
    This class orchestrates specialized components (clipboard monitor,
    hotkey sequence manager, configuration manager) following SOLID principles.
    It focuses solely on coordination and delegation, not implementation details.
    """
    
    def __init__(
        self,
        transformation_engine: TransformationEngineProtocol,
        config_manager: ConfigManagerProtocol
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
            clipboard_config = self._daemon_config_manager.get_clipboard_monitoring_config()
            check_interval = self._daemon_config_manager.get_check_interval()
            
            self._clipboard_monitor = ClipboardMonitor(
                transformation_engine,
                clipboard_config,
                check_interval=check_interval
            )
            
            # Initialize hotkey sequence manager
            sequence_config = self._daemon_config_manager.get_sequence_hotkeys_config()
            sequence_timeout = self._daemon_config_manager.get_sequence_timeout()
            
            self._hotkey_manager = HotkeySequenceManager(
                transformation_engine,
                sequence_config,
                timeout=sequence_timeout
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
            
            # Start clipboard monitoring if enabled
            if self._daemon_config_manager.is_clipboard_monitoring_enabled():
                self._clipboard_monitor.start_monitoring()
                print("[DAEMON] Clipboard monitoring started")
            
            # Start hotkey sequence monitoring if enabled and available
            if (self._daemon_config_manager.is_sequence_hotkeys_enabled() and\n                self._hotkey_manager.keyboard_available):\n                self._hotkey_manager.start_sequence_monitoring()\n                print(\"[DAEMON] Hotkey sequence monitoring started\")\n            \n        except Exception as e:\n            # Clean up on failure\n            self._stop_all_monitoring()\n            raise TransformationError(\n                f\"Failed to start daemon monitoring: {e}\"\n            ) from e\n    \n    def stop(self) -> None:\n        \"\"\"Stop daemon monitoring and display statistics.\"\"\"\n        try:\n            self._stop_all_monitoring()\n            self._display_stop_statistics()\n        except Exception as e:\n            raise TransformationError(\n                f\"Failed to stop daemon monitoring: {e}\"\n            ) from e\n    \n    def set_transformation_rules(self, rules: list[str]) -> None:\n        \"\"\"Set active transformation rules for clipboard monitoring.\"\"\"\n        self._clipboard_monitor.set_active_rules(rules)\n        self._active_preset = None  # Clear preset when setting custom rules\n        print(f\"[DAEMON] Active rules set: {' -> '.join(rules)}\")\n    \n    def set_preset(self, preset_name: str) -> bool:\n        \"\"\"Set transformation preset and configure rules.\"\"\"\n        if not isinstance(preset_name, str) or not preset_name.strip():\n            raise ValidationError(\"Preset name must be a non-empty string\")\n        \n        try:\n            preset_rules = self._daemon_config_manager.get_preset_rules(preset_name)\n            self._clipboard_monitor.set_active_rules(preset_rules)\n            self._active_preset = preset_name\n            \n            print(f\"[DAEMON] Preset '{preset_name}' activated: {' -> '.join(preset_rules)}\")\n            return True\n            \n        except ValidationError:\n            # Re-raise validation errors as-is\n            raise\n        except Exception as e:\n            raise ConfigurationError(\n                f\"Failed to set preset '{preset_name}': {e}\"\n            ) from e\n    \n    def get_status(self) -> dict[str, Any]:\n        \"\"\"Get comprehensive daemon status information.\"\"\"\n        clipboard_stats = self._clipboard_monitor.stats\n        hotkey_stats = self._hotkey_manager.stats\n        \n        # Combine statistics\n        total_transformations = (\n            clipboard_stats.get(\"transformations_applied\", 0) +\n            hotkey_stats.get(\"transformations_applied\", 0)\n        )\n        \n        status = {\n            \"running\": self.is_running,\n            \"active_preset\": self._active_preset,\n            \"clipboard_monitoring\": {\n                \"enabled\": self._daemon_config_manager.is_clipboard_monitoring_enabled(),\n                \"running\": self._clipboard_monitor.is_running,\n                \"stats\": clipboard_stats\n            },\n            \"hotkey_sequences\": {\n                \"enabled\": self._daemon_config_manager.is_sequence_hotkeys_enabled(),\n                \"available\": self._hotkey_manager.keyboard_available,\n                \"active\": self._hotkey_manager.is_active,\n                \"stats\": hotkey_stats\n            },\n            \"total_transformations\": total_transformations\n        }\n        \n        if self._start_time and self.is_running:\n            runtime = datetime.now() - self._start_time\n            status[\"runtime\"] = str(runtime).split('.')[0]  # Remove microseconds\n        \n        return status\n    \n    def reload_config(self) -> None:\n        \"\"\"Reload daemon configuration from file.\"\"\"\n        try:\n            # Reload configuration\n            self._daemon_config_manager.load_config(force_reload=True)\n            \n            # Update component configurations\n            # Note: This would require stopping and restarting components\n            # in a full implementation\n            print(\"[DAEMON] Configuration reloaded\")\n            \n        except Exception as e:\n            raise ConfigurationError(\n                f\"Failed to reload daemon configuration: {e}\"\n            ) from e\n    \n    def _setup_callbacks(self) -> None:\n        \"\"\"Set up callbacks between components.\"\"\"\n        # Clipboard change callback\n        def on_clipboard_change(content: str, result: str) -> None:\n            self._display_transformation(\"CLIPBOARD\", content, result)\n        \n        self._clipboard_monitor.add_change_callback(on_clipboard_change)\n        \n        # Hotkey sequence callback\n        def on_hotkey_sequence(rule: str, content: str, result: str) -> None:\n            self._display_transformation(f\"HOTKEY({rule})\", content, result)\n        \n        self._hotkey_manager.add_sequence_callback(on_hotkey_sequence)\n    \n    def _stop_all_monitoring(self) -> None:\n        \"\"\"Stop all monitoring components.\"\"\"\n        try:\n            self._clipboard_monitor.stop_monitoring()\n        except Exception as e:\n            print(f\"[DAEMON] Error stopping clipboard monitor: {e}\")\n        \n        try:\n            self._hotkey_manager.stop_sequence_monitoring()\n        except Exception as e:\n            print(f\"[DAEMON] Error stopping hotkey manager: {e}\")\n    \n    def _display_transformation(self, source: str, content: str, result: str) -> None:\n        \"\"\"Display transformation result with source information.\"\"\"\n        MAX_DISPLAY_LENGTH: Final[int] = 50\n        \n        display_input = (\n            content[:MAX_DISPLAY_LENGTH] + \"...\"\n            if len(content) > MAX_DISPLAY_LENGTH\n            else content\n        )\n        display_output = (\n            result[:MAX_DISPLAY_LENGTH] + \"...\"\n            if len(result) > MAX_DISPLAY_LENGTH\n            else result\n        )\n        \n        print(\n            f\"\\r[DAEMON:{source}] Transformed: '{display_input}' -> '{display_output}'\",\n            flush=True\n        )\n    \n    def _display_stop_statistics(self) -> None:\n        \"\"\"Display daemon stop statistics.\"\"\"\n        if self._start_time:\n            runtime = datetime.now() - self._start_time\n            print(f\"[DAEMON] Stopped after {runtime}\")\n        \n        status = self.get_status()\n        total_transformations = status[\"total_transformations\"]\n        print(f\"[DAEMON] Total transformations applied: {total_transformations}\")\n        \n        clipboard_stats = status[\"clipboard_monitoring\"][\"stats\"]\n        hotkey_stats = status[\"hotkey_sequences\"][\"stats\"]\n        \n        print(f\"[DAEMON] Clipboard transformations: {clipboard_stats.get('transformations_applied', 0)}\")\n        print(f\"[DAEMON] Hotkey transformations: {hotkey_stats.get('transformations_applied', 0)}\")\n        print(f\"[DAEMON] Sequences detected: {hotkey_stats.get('sequences_detected', 0)}\")"}, {"old_string": "            # Start hotkey sequence monitoring if enabled and available\n            if (self._daemon_config_manager.is_sequence_hotkeys_enabled() and\n                self._hotkey_manager.keyboard_available):\n                self._hotkey_manager.start_sequence_monitoring()\n                print(\"[DAEMON] Hotkey sequence monitoring started\")", "new_string": "            # Start hotkey sequence monitoring if enabled and available\n            if (self._daemon_config_manager.is_sequence_hotkeys_enabled() and\n                self._hotkey_manager.keyboard_available):\n                self._hotkey_manager.start_sequence_monitoring()\n                print(\"[DAEMON] Hotkey sequence monitoring started\")"}]