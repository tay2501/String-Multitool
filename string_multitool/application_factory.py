"""
Application factory using dependency injection.

This module provides factory functions for creating application instances
with proper dependency injection configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .core.dependency_injection import DIContainer, ServiceRegistry
from .core.config import ConfigurationManager
from .core.crypto import CryptographyManager
from .core.transformations import TextTransformationEngine
from .core.types import (
    ConfigManagerProtocol,
    TransformationEngineProtocol,
    CryptoManagerProtocol
)
from .io.manager import InputOutputManager
from .modes.daemon_refactored import DaemonModeRefactored
from .modes.interactive import InteractiveSession, CommandProcessor
from .modes.hotkey import HotkeyMode
from .exceptions import ConfigurationError, CryptographyError
from .utils.logger import get_logger, log_warning


def configure_services(container: DIContainer) -> None:
    \"\"\"Configure all application services in the DI container.\"\"\"\n    # Configuration manager (singleton)\n    config_manager = ConfigurationManager()\n    container.register_singleton(ConfigManagerProtocol, config_manager)\n    container.register_singleton(ConfigurationManager, config_manager)\n    \n    # Text transformation engine (singleton)\n    def create_transformation_engine(config_mgr: ConfigManagerProtocol) -> TextTransformationEngine:\n        return TextTransformationEngine(config_mgr)\n    \n    container.register_factory(TransformationEngineProtocol, create_transformation_engine)\n    container.register_factory(TextTransformationEngine, create_transformation_engine)\n    \n    # Cryptography manager (singleton with error handling)\n    def create_crypto_manager(config_mgr: ConfigManagerProtocol) -> CryptographyManager | None:\n        try:\n            return CryptographyManager(config_mgr)\n        except CryptographyError as e:\n            logger = get_logger(__name__)\n            log_warning(logger, f\"Cryptography not available: {e}\")\n            return None\n    \n    container.register_factory(CryptoManagerProtocol, create_crypto_manager)\n    container.register_factory(CryptographyManager, create_crypto_manager)\n    \n    # I/O manager (transient)\n    container.register_transient(InputOutputManager, InputOutputManager)\n    \n    # Daemon mode (transient with dependencies)\n    def create_daemon_mode(\n        transformation_engine: TransformationEngineProtocol,\n        config_manager: ConfigManagerProtocol\n    ) -> DaemonModeRefactored:\n        return DaemonModeRefactored(transformation_engine, config_manager)\n    \n    container.register_factory(DaemonModeRefactored, create_daemon_mode)\n    \n    # Interactive session (transient with dependencies)\n    def create_interactive_session(\n        io_manager: InputOutputManager,\n        transformation_engine: TransformationEngineProtocol\n    ) -> InteractiveSession:\n        return InteractiveSession(io_manager, transformation_engine)\n    \n    container.register_factory(InteractiveSession, create_interactive_session)\n    \n    # Command processor (transient with dependencies)\n    def create_command_processor(\n        session: InteractiveSession\n    ) -> CommandProcessor:\n        return CommandProcessor(session)\n    \n    container.register_factory(CommandProcessor, create_command_processor)\n    \n    # Hotkey mode (transient with dependencies)\n    def create_hotkey_mode(\n        transformation_engine: TransformationEngineProtocol,\n        config_manager: ConfigManagerProtocol\n    ) -> HotkeyMode | None:\n        try:\n            return HotkeyMode(transformation_engine, config_manager)\n        except Exception as e:\n            logger = get_logger(__name__)\n            log_warning(logger, f\"Hotkey mode not available: {e}\")\n            return None\n    \n    container.register_factory(HotkeyMode, create_hotkey_mode)\n\n\nclass ApplicationFactory:\n    \"\"\"Factory for creating application instances with dependency injection.\"\"\"\n    \n    @staticmethod\n    def create_application() -> 'ApplicationInterface':\n        \"\"\"Create application instance with all dependencies configured.\"\"\"\n        # Configure services\n        ServiceRegistry.configure(configure_services)\n        \n        # Create application interface\n        return ApplicationInterface()\n    \n    @staticmethod\n    def create_for_testing(\n        config_override: dict[str, Any] | None = None\n    ) -> 'ApplicationInterface':\n        \"\"\"Create application instance for testing with optional config override.\"\"\"\n        # Reset service registry for clean test state\n        ServiceRegistry.reset()\n        \n        # Configure services with test overrides\n        def configure_test_services(container: DIContainer) -> None:\n            configure_services(container)\n            \n            # Apply test-specific overrides\n            if config_override:\n                # This would require test-specific configuration manager\n                pass\n        \n        ServiceRegistry.configure(configure_test_services)\n        \n        return ApplicationInterface()\n\n\nfrom .main import ApplicationInterface  # Import here to avoid circular imports"