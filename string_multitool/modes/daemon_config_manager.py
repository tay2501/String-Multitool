"""
Daemon configuration management.

This module provides specialized daemon configuration loading and management
following the Single Responsibility Principle.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Final

from ..exceptions import ConfigurationError, ValidationError


class DaemonConfigManager:
    """
    Specialized daemon configuration manager.
    
    Handles loading, validation, and access to daemon-specific configuration
    settings. Follows SRP by focusing solely on configuration management.
    """
    
    # Class constants
    DEFAULT_CONFIG_PATH: Final[Path] = Path("config/daemon_config.json")
    
    def __init__(self, config_path: Path | None = None) -> None:
        """
        Initialize daemon configuration manager.
        
        Args:
            config_path: Path to daemon configuration file
        """
        self._config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config_cache: dict[str, Any] | None = None
        self._last_modified: float | None = None
    
    @property
    def config_path(self) -> Path:
        """Get the configuration file path."""
        return self._config_path
    
    def load_config(self, *, force_reload: bool = False) -> dict[str, Any]:
        """
        Load daemon configuration from file with caching.
        
        Args:
            force_reload: Force reload even if cached
            
        Returns:
            Daemon configuration dictionary
            
        Raises:
            ConfigurationError: If configuration cannot be loaded
        """
        try:
            # Check if we need to reload
            if not force_reload and self._config_cache is not None:
                if self._config_path.exists():
                    current_modified = self._config_path.stat().st_mtime
                    if self._last_modified == current_modified:
                        return self._config_cache
                else:
                    # File was deleted, use cached default
                    return self._config_cache
            
            # Load configuration
            if self._config_path.exists():
                config_data = self._load_from_file()
                self._last_modified = self._config_path.stat().st_mtime
            else:
                config_data = self._get_default_config()
                self._last_modified = None
            
            # Validate configuration
            self._validate_config(config_data)
            
            # Cache and return
            self._config_cache = config_data
            return config_data
            
        except (ConfigurationError, ValidationError):
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load daemon configuration: {e}"
            ) from e
    
    def get_daemon_mode_config(self) -> Mapping[str, Any]:
        """Get daemon mode specific configuration."""
        config = self.load_config()
        return config.get("daemon_mode", {})
    
    def get_clipboard_monitoring_config(self) -> Mapping[str, Any]:
        """Get clipboard monitoring configuration."""
        config = self.load_config()
        return config.get("clipboard_monitoring", {})
    
    def get_auto_transformation_config(self) -> Mapping[str, Any]:
        """Get auto transformation configuration."""
        config = self.load_config()
        return config.get("auto_transformation", {})
    
    def get_sequence_hotkeys_config(self) -> Mapping[str, Any]:
        """Get sequence hotkeys configuration."""
        config = self.load_config()
        return config.get("sequence_hotkeys", {})
    
    def get_rule_presets(self) -> Mapping[str, Any]:
        """Get available rule presets."""
        auto_config = self.get_auto_transformation_config()
        return auto_config.get("rule_presets", {})
    
    def get_preset_rules(self, preset_name: str) -> list[str]:
        """
        Get rules for a specific preset.
        
        Args:
            preset_name: Name of the preset
            
        Returns:
            List of transformation rules
            
        Raises:
            ValidationError: If preset does not exist
        """
        presets = self.get_rule_presets()
        
        if preset_name not in presets:
            available_presets = list(presets.keys())
            raise ValidationError(
                f"Unknown preset: {preset_name}",
                {
                    "preset_name": preset_name,
                    "available_presets": available_presets
                }
            )
        
        preset_rules = presets[preset_name]
        if isinstance(preset_rules, str):
            return [preset_rules]
        elif isinstance(preset_rules, list):
            return preset_rules.copy()
        else:
            raise ValidationError(
                f"Invalid preset format for '{preset_name}': {type(preset_rules)}"
            )
    
    def get_check_interval(self) -> float:
        """Get clipboard monitoring check interval."""
        daemon_config = self.get_daemon_mode_config()
        return daemon_config.get("check_interval", 1.0)
    
    def get_sequence_timeout(self) -> float:
        """Get sequence hotkey timeout."""
        sequence_config = self.get_sequence_hotkeys_config()
        return sequence_config.get("timeout", 2.0)
    
    def is_clipboard_monitoring_enabled(self) -> bool:
        """Check if clipboard monitoring is enabled."""
        clipboard_config = self.get_clipboard_monitoring_config()
        return clipboard_config.get("enabled", True)
    
    def is_sequence_hotkeys_enabled(self) -> bool:
        """Check if sequence hotkeys are enabled."""
        sequence_config = self.get_sequence_hotkeys_config()
        return sequence_config.get("enabled", False)
    
    def _load_from_file(self) -> dict[str, Any]:
        """Load configuration from file."""
        try:
            with self._config_path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise ConfigurationError(
                f"Failed to read daemon config file '{self._config_path}': {e}"
            ) from e
    
    def _get_default_config(self) -> dict[str, Any]:
        """Get default daemon configuration."""
        return {\n            \"daemon_mode\": {\n                \"check_interval\": 1.0,\n                \"max_retries\": 3,\n                \"retry_delay\": 0.5\n            },\n            \"clipboard_monitoring\": {\n                \"enabled\": True,\n                \"ignore_duplicates\": True,\n                \"ignore_empty\": True,\n                \"min_length\": 1,\n                \"max_length\": 10000,\n                \"ignore_patterns\": []\n            },\n            \"auto_transformation\": {\n                \"rule_presets\": {\n                    \"uppercase\": \"/u\",\n                    \"lowercase\": \"/l\",\n                    \"snake_case\": \"/s\",\n                    \"pascal_case\": \"/p\",\n                    \"camel_case\": \"/c\",\n                    \"trim_lowercase\": \"/t/l\",\n                    \"hyphen_to_underscore\": \"/hu\"\n                }\n            },\n            \"sequence_hotkeys\": {\n                \"enabled\": False,\n                \"timeout\": 2.0,\n                \"sequences\": {}\n            }\n        }\n    \n    def _validate_config(self, config: dict[str, Any]) -> None:\n        \"\"\"Validate daemon configuration structure.\"\"\"\n        if not isinstance(config, dict):\n            raise ValidationError(\"Configuration must be a dictionary\")\n        \n        # Validate daemon_mode section\n        daemon_mode = config.get(\"daemon_mode\", {})\n        if not isinstance(daemon_mode, dict):\n            raise ValidationError(\"daemon_mode must be a dictionary\")\n        \n        check_interval = daemon_mode.get(\"check_interval\", 1.0)\n        if not isinstance(check_interval, (int, float)) or check_interval <= 0:\n            raise ValidationError(\"check_interval must be a positive number\")\n        \n        # Validate clipboard_monitoring section\n        clipboard_monitoring = config.get(\"clipboard_monitoring\", {})\n        if not isinstance(clipboard_monitoring, dict):\n            raise ValidationError(\"clipboard_monitoring must be a dictionary\")\n        \n        min_length = clipboard_monitoring.get(\"min_length\", 1)\n        max_length = clipboard_monitoring.get(\"max_length\", 10000)\n        \n        if not isinstance(min_length, int) or min_length < 0:\n            raise ValidationError(\"min_length must be a non-negative integer\")\n        \n        if not isinstance(max_length, int) or max_length <= 0:\n            raise ValidationError(\"max_length must be a positive integer\")\n        \n        if min_length > max_length:\n            raise ValidationError(\"min_length cannot be greater than max_length\")\n        \n        # Validate auto_transformation section\n        auto_transformation = config.get(\"auto_transformation\", {})\n        if not isinstance(auto_transformation, dict):\n            raise ValidationError(\"auto_transformation must be a dictionary\")\n        \n        rule_presets = auto_transformation.get(\"rule_presets\", {})\n        if not isinstance(rule_presets, dict):\n            raise ValidationError(\"rule_presets must be a dictionary\")\n        \n        for preset_name, preset_rules in rule_presets.items():\n            if not isinstance(preset_name, str):\n                raise ValidationError(f\"Preset name must be string: {preset_name}\")\n            \n            if isinstance(preset_rules, str):\n                continue\n            elif isinstance(preset_rules, list):\n                if not all(isinstance(rule, str) for rule in preset_rules):\n                    raise ValidationError(\n                        f\"All preset rules must be strings in '{preset_name}'\"\n                    )\n            else:\n                raise ValidationError(\n                    f\"Preset rules must be string or list in '{preset_name}'\"\n                )\n        \n        # Validate sequence_hotkeys section\n        sequence_hotkeys = config.get(\"sequence_hotkeys\", {})\n        if not isinstance(sequence_hotkeys, dict):\n            raise ValidationError(\"sequence_hotkeys must be a dictionary\")\n        \n        timeout = sequence_hotkeys.get(\"timeout\", 2.0)\n        if not isinstance(timeout, (int, float)) or timeout <= 0:\n            raise ValidationError(\"sequence timeout must be a positive number\")"}, {"old_string": "        return {\n            \"daemon_mode\": {\n                \"check_interval\": 1.0,\n                \"max_retries\": 3,\n                \"retry_delay\": 0.5\n            },\n            \"clipboard_monitoring\": {\n                \"enabled\": True,\n                \"ignore_duplicates\": True,\n                \"ignore_empty\": True,\n                \"min_length\": 1,\n                \"max_length\": 10000,\n                \"ignore_patterns\": []\n            },\n            \"auto_transformation\": {\n                \"rule_presets\": {\n                    \"uppercase\": \"/u\",\n                    \"lowercase\": \"/l\",\n                    \"snake_case\": \"/s\",\n                    \"pascal_case\": \"/p\",\n                    \"camel_case\": \"/c\",\n                    \"trim_lowercase\": \"/t/l\",\n                    \"hyphen_to_underscore\": \"/hu\"\n                }\n            },\n            \"sequence_hotkeys\": {\n                \"enabled\": False,\n                \"timeout\": 2.0,\n                \"sequences\": {}\n            }\n        }", "new_string": "        return {\n            \"daemon_mode\": {\n                \"check_interval\": 1.0,\n                \"max_retries\": 3,\n                \"retry_delay\": 0.5\n            },\n            \"clipboard_monitoring\": {\n                \"enabled\": True,\n                \"ignore_duplicates\": True,\n                \"ignore_empty\": True,\n                \"min_length\": 1,\n                \"max_length\": 10000,\n                \"ignore_patterns\": []\n            },\n            \"auto_transformation\": {\n                \"rule_presets\": {\n                    \"uppercase\": \"/u\",\n                    \"lowercase\": \"/l\",\n                    \"snake_case\": \"/s\",\n                    \"pascal_case\": \"/p\",\n                    \"camel_case\": \"/c\",\n                    \"trim_lowercase\": \"/t/l\",\n                    \"hyphen_to_underscore\": \"/hu\"\n                }\n            },\n            \"sequence_hotkeys\": {\n                \"enabled\": False,\n                \"timeout\": 2.0,\n                \"sequences\": {}\n            }\n        }"}]