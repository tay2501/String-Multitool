"""
Configuration management for String_Multitool.

This module handles loading and validation of configuration files,
providing type-safe access to application settings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..exceptions import ConfigurationError
from .types import ConfigurableComponent


class ConfigurationManager(ConfigurableComponent[dict[str, Any]]):
    """Manages application configuration from JSON files.

    This class provides centralized configuration management with
    caching and validation capabilities.
    """

    def __init__(self, config_dir: str | Path = "config") -> None:
        """Initialize configuration manager.

        Args:
            config_dir: Directory containing configuration files (str or Path)

        Raises:
            ConfigurationError: If config directory doesn't exist
        """
        # Instance variable annotations following PEP 526
        self.config_dir: Path = (
            Path(config_dir) if not isinstance(config_dir, Path) else config_dir
        )
        self._transformation_rules: dict[str, Any] | None = None
        self._security_config: dict[str, Any] | None = None
        self._hotkey_config: dict[str, Any] | None = None

        try:
            # EAFP: Try to access the directory instead of checking existence first
            self.config_dir.stat()
        except (OSError, FileNotFoundError) as e:
            raise ConfigurationError(
                f"Configuration directory not accessible: {config_dir}",
                {"config_dir": str(self.config_dir), "error": str(e)},
            ) from e

        super().__init__({})

    def load_transformation_rules(self) -> dict[str, Any]:
        """Load transformation rules from configuration file.

        Returns:
            Dictionary containing transformation rules

        Raises:
            ConfigurationError: If rules file cannot be loaded or parsed
        """
        if self._transformation_rules is None:
            config_file = self.config_dir / "transformation_rules.json"
            self._transformation_rules = self._load_json_file(config_file, "transformation rules")

        return self._transformation_rules

    def load_security_config(self) -> dict[str, Any]:
        """Load security configuration from configuration file.

        Returns:
            Dictionary containing security configuration

        Raises:
            ConfigurationError: If security config file cannot be loaded or parsed
        """
        if self._security_config is None:
            config_file = self.config_dir / "security_config.json"
            self._security_config = self._load_json_file(config_file, "security configuration")

        return self._security_config

    def load_hotkey_config(self) -> dict[str, Any]:
        """Load hotkey configuration from configuration file.

        Returns:
            Dictionary containing hotkey configuration

        Raises:
            ConfigurationError: If hotkey config file cannot be loaded or parsed
        """
        if self._hotkey_config is None:
            config_file = self.config_dir / "hotkey_config.json"
            self._hotkey_config = self._load_json_file(config_file, "hotkey configuration")

        return self._hotkey_config

    def _load_json_file(self, file_path: Path, description: str) -> dict[str, Any]:
        """Load and parse a JSON configuration file.

        Args:
            file_path: Path to the JSON file
            description: Human-readable description for error messages

        Returns:
            Parsed JSON data as dictionary

        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        try:
            with open(file_path, encoding="utf-8") as file:
                data: Any = json.load(file)

            if not isinstance(data, dict):
                raise ConfigurationError(
                    f"Invalid {description}: expected object, got {type(data).__name__}",
                    {"file_path": str(file_path), "data_type": type(data).__name__},
                )

            return data

        except FileNotFoundError as e:
            raise ConfigurationError(
                f"Configuration file not found: {file_path}",
                {"file_path": str(file_path), "description": description},
            ) from e
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in {description} file: {e}",
                {"file_path": str(file_path), "json_error": str(e)},
            ) from e
        except Exception as e:
            raise ConfigurationError(
                f"Unexpected error loading {description}: {e}",
                {"file_path": str(file_path), "error_type": type(e).__name__},
            ) from e

    def validate_config(self) -> bool:
        """Validate all configuration files.

        Returns:
            True if all configurations are valid

        Raises:
            ConfigurationError: If any configuration is invalid
        """
        try:
            self.load_transformation_rules()
            self.load_security_config()
            self.load_hotkey_config()
            return True
        except ConfigurationError:
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Configuration validation failed: {e}",
                {"error_type": type(e).__name__},
            ) from e
