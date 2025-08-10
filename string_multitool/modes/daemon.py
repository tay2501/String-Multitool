"""
Daemon mode for String_Multitool.

This module provides continuous clipboard monitoring and automatic
transformation capabilities with comprehensive configuration support.
"""

from __future__ import annotations

import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from ..exceptions import ConfigurationError, ValidationError, TransformationError
from ..core.types import TransformationEngineProtocol, ConfigManagerProtocol
from ..io.manager import InputOutputManager


class DaemonMode:
    """Daemon mode for continuous clipboard monitoring and transformation.
    
    This class provides background clipboard processing with configurable
    transformation rules and comprehensive status tracking.
    """
    
    def __init__(
        self, 
        transformation_engine: TransformationEngineProtocol,
        config_manager: ConfigManagerProtocol
    ) -> None:
        """Initialize daemon mode.
        
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
        
        # Instance variable annotations following PEP 526
        self.transformation_engine: TransformationEngineProtocol = transformation_engine
        self.config_manager: ConfigManagerProtocol = config_manager
        self.is_running: bool = False
        self.last_clipboard_content: str = ""
        self.active_rules: list[str] = []
        self.clipboard_monitor: threading.Thread | None = None
        self.active_preset: str | None = None
        self.daemon_config: dict[str, Any] = {}
        self.stats: dict[str, Any] = {
            'transformations_applied': 0,
            'start_time': None,
            'last_transformation': None
        }
        
        # Load daemon configuration
        try:
            self.daemon_config = self._load_daemon_config()
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load daemon configuration: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def start_monitoring(self) -> None:
        """Start daemon monitoring in a separate thread.
        
        Raises:
            ValidationError: If no transformation rules are set
            TransformationError: If monitoring cannot be started
        """
        if self.is_running:
            return
        
        if not self.active_rules:
            raise ValidationError("No transformation rules set. Use 'rules' or 'preset' command first.")
        
        try:
            self.is_running = True
            self.stats['start_time'] = datetime.now()
            
            # Start monitoring thread
            self.clipboard_monitor = threading.Thread(
                target=self._monitor_clipboard,
                daemon=True,
                name="DaemonClipboardMonitor"
            )
            self.clipboard_monitor.start()
            
        except Exception as e:
            self.is_running = False
            raise TransformationError(
                f"Failed to start daemon monitoring: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def stop(self) -> None:
        """Stop daemon monitoring.
        
        Raises:
            TransformationError: If monitoring cannot be stopped
        """
        if not self.is_running:
            return
        
        try:
            self.is_running = False
            
            if self.clipboard_monitor and self.clipboard_monitor.is_alive():
                self.clipboard_monitor.join(timeout=2.0)
            
            # Calculate runtime
            if self.stats['start_time']:
                runtime = datetime.now() - self.stats['start_time']
                print(f"[DAEMON] Stopped after {runtime}")
                print(f"[DAEMON] Transformations applied: {self.stats['transformations_applied']}")
            
            print("[DAEMON] Clipboard monitoring stopped")
            
        except Exception as e:
            raise TransformationError(
                f"Failed to stop daemon monitoring: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def set_transformation_rules(self, rules: list[str]) -> None:
        """Set active transformation rules.
        
        Args:
            rules: List of transformation rule strings
            
        Raises:
            ValidationError: If rules are invalid
        """
        if not isinstance(rules, list):
            raise ValidationError(
                f"Rules must be a list, got {type(rules).__name__}",
                {"rules_type": type(rules).__name__}
            )
        
        if not rules:
            raise ValidationError("Rules list cannot be empty")
        
        # Validate rules
        for rule in rules:
            if not isinstance(rule, str):
                raise ValidationError(
                    f"Each rule must be a string, got {type(rule).__name__}",
                    {"rule_type": type(rule).__name__, "rule": str(rule)}
                )
        
        self.active_rules = rules
        self.active_preset = None  # Clear preset when setting custom rules
        print(f"[DAEMON] Active rules set: {' -> '.join(rules) if rules else 'None'}")
    
    def set_preset(self, preset_name: str) -> bool:
        """Set transformation preset.
        
        Args:
            preset_name: Name of the preset to activate
            
        Returns:
            True if preset was set successfully
            
        Raises:
            ValidationError: If preset name is invalid
            ConfigurationError: If preset is not found
        """
        if not isinstance(preset_name, str):
            raise ValidationError(
                f"Preset name must be a string, got {type(preset_name).__name__}",
                {"preset_type": type(preset_name).__name__}
            )
        
        if not preset_name.strip():
            raise ValidationError("Preset name cannot be empty")
        
        try:
            presets: dict[str, Any] = self.daemon_config.get("auto_transformation", {}).get("rule_presets", {})
            
            if preset_name not in presets:
                available_presets: list[str] = list(presets.keys())
                raise ConfigurationError(
                    f"Unknown preset: {preset_name}",
                    {"preset_name": preset_name, "available_presets": available_presets}
                )
            
            preset_rules: str | list[str] = presets[preset_name]
            if isinstance(preset_rules, str):
                self.active_rules = [preset_rules]
            else:
                self.active_rules = preset_rules
            
            self.active_preset = preset_name
            print(f"[DAEMON] Preset '{preset_name}' activated: {' -> '.join(self.active_rules)}")
            return True
            
        except (ConfigurationError, ValidationError):
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Failed to set preset '{preset_name}': {e}",
                {"preset_name": preset_name, "error_type": type(e).__name__}
            ) from e
    
    def get_status(self) -> dict[str, Any]:
        """Get daemon status information.
        
        Returns:
            Dictionary containing status information
        """
        status: dict[str, Any] = {
            'running': self.is_running,
            'active_rules': self.active_rules.copy(),
            'active_preset': self.active_preset,
            'stats': self.stats.copy()
        }
        
        if self.stats['start_time'] and self.is_running:
            runtime = datetime.now() - self.stats['start_time']
            status['runtime'] = str(runtime).split('.')[0]  # Remove microseconds
        
        return status
    
    def _load_daemon_config(self) -> dict[str, Any]:
        """Load daemon configuration from file or use defaults.
        
        Returns:
            Daemon configuration dictionary
        """
        daemon_config_path: Path = Path("config/daemon_config.json")
        
        if daemon_config_path.exists():
            try:
                with open(daemon_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load daemon config, using defaults: {e}")
        
        return self._get_default_daemon_config()
    
    def _get_default_daemon_config(self) -> dict[str, Any]:
        """Get default daemon configuration."""
        return {
            "daemon_mode": {
                "check_interval": 1.0,
                "max_retries": 3,
                "retry_delay": 0.5
            },
            "clipboard_monitoring": {
                "enabled": True,
                "ignore_duplicates": True,
                "ignore_empty": True,
                "min_length": 1,
                "max_length": 10000,
                "ignore_patterns": []
            },
            "auto_transformation": {
                "rule_presets": {
                    "uppercase": "/u",
                    "lowercase": "/l",
                    "snake_case": "/s",
                    "pascal_case": "/p",
                    "camel_case": "/c",
                    "trim_lowercase": "/t/l",
                    "hyphen_to_underscore": "/hu"
                }
            }
        }
    
    def _monitor_clipboard(self) -> None:
        """Main clipboard monitoring loop."""
        check_interval: float = self.daemon_config["daemon_mode"]["check_interval"]
        
        while self.is_running:
            try:
                io_manager: InputOutputManager = InputOutputManager()
                current_content: str = io_manager.get_clipboard_text()
                
                if self._should_process_content(current_content):
                    self._process_clipboard_content(current_content)
                
                # Use shorter sleep intervals for better responsiveness
                sleep_iterations: int = int(check_interval * 10)
                for _ in range(sleep_iterations):
                    if not self.is_running:
                        break
                    time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\r[DAEMON] Error monitoring clipboard: {e}", flush=True)
                time.sleep(check_interval)
    
    def _should_process_content(self, content: str) -> bool:
        """Check if clipboard content should be processed.
        
        Args:
            content: Clipboard content to check
            
        Returns:
            True if content should be processed, False otherwise
        """
        config: dict[str, Any] = self.daemon_config["clipboard_monitoring"]
        
        # Check if monitoring is enabled
        if not config.get("enabled", True):
            return False
        
        # Check if we have active rules
        if not self.active_rules:
            return False
        
        # Check if content is different from last processed
        if config.get("ignore_duplicates", True):
            if content == self.last_clipboard_content:
                return False
        
        # Check if content is empty
        if config.get("ignore_empty", True) and not content.strip():
            return False
        
        # Check content length
        min_length: int = config.get("min_length", 1)
        max_length: int = config.get("max_length", 10000)
        
        if len(content) < min_length or len(content) > max_length:
            return False
        
        return True
    
    def _process_clipboard_content(self, content: str) -> None:
        """Process clipboard content with active transformation rules.
        
        Args:
            content: Clipboard content to process
        """
        try:
            # Apply transformation rules sequentially
            result: str = content
            for rule in self.active_rules:
                result = self.transformation_engine.apply_transformations(result, rule)
            
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
            self.stats['transformations_applied'] += 1
            self.stats['last_transformation'] = datetime.now()
            self.last_clipboard_content = result
            
            # Show transformation result (only when content actually changed)
            display_input: str = content[:50] + "..." if len(content) > 50 else content
            display_output: str = result[:50] + "..." if len(result) > 50 else result
            
            # Use \r to overwrite current line and avoid interfering with command input
            print(f"\r[DAEMON] Transformed: '{display_input}' -> '{display_output}'", end='', flush=True)
            print()  # Add newline after transformation message
            
        except Exception as e:
            print(f"\r[DAEMON] Error processing content: {e}", flush=True)