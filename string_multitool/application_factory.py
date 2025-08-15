"""
Application factory using dependency injection.

This module provides factory functions for creating application instances
with proper dependency injection configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .core.config import ConfigurationManager
from .core.crypto import CryptographyManager
from .core.dependency_injection import DIContainer, ServiceRegistry
from .core.transformations import TextTransformationEngine
from .core.types import (
    ConfigManagerProtocol,
    CryptoManagerProtocol,
    TransformationEngineProtocol,
)
from .exceptions import ConfigurationError, CryptographyError
from .io.manager import InputOutputManager
from .modes.daemon import DaemonMode
from .modes.hotkey import HotkeyMode
from .modes.interactive import CommandProcessor, InteractiveSession
from .utils.logger import get_logger, log_warning


def configure_services(container: DIContainer) -> None:
    """Configure all application services in the DI container."""
    # Configuration manager (singleton)
    config_manager = ConfigurationManager()
    container.register_singleton(ConfigManagerProtocol, config_manager)
    container.register_singleton(ConfigurationManager, config_manager)

    # Text transformation engine (singleton)
    def create_transformation_engine(
        config_mgr: ConfigManagerProtocol,
    ) -> TextTransformationEngine:
        return TextTransformationEngine(config_mgr)

    container.register_factory(
        TransformationEngineProtocol, create_transformation_engine
    )
    container.register_factory(TextTransformationEngine, create_transformation_engine)

    # Cryptography manager (singleton with error handling)
    def create_crypto_manager(
        config_mgr: ConfigManagerProtocol,
    ) -> CryptographyManager | None:
        try:
            return CryptographyManager(config_mgr)
        except CryptographyError as e:
            logger = get_logger(__name__)
            log_warning(logger, f"Cryptography not available: {e}")
            return None

    container.register_factory(CryptoManagerProtocol, create_crypto_manager)
    container.register_factory(CryptographyManager, create_crypto_manager)

    # I/O manager (transient)
    container.register_transient(InputOutputManager, InputOutputManager)

    # Daemon mode (transient with dependencies)
    def create_daemon_mode(
        transformation_engine: TransformationEngineProtocol,
        config_manager: ConfigManagerProtocol,
    ) -> DaemonMode:
        return DaemonMode(transformation_engine, config_manager)

    container.register_factory(DaemonMode, create_daemon_mode)

    # Interactive session (transient with dependencies)
    def create_interactive_session(
        io_manager: InputOutputManager,
        transformation_engine: TransformationEngineProtocol,
    ) -> InteractiveSession:
        return InteractiveSession(io_manager, transformation_engine)

    container.register_factory(InteractiveSession, create_interactive_session)

    # Command processor (transient with dependencies)
    def create_command_processor(session: InteractiveSession) -> CommandProcessor:
        return CommandProcessor(session)

    container.register_factory(CommandProcessor, create_command_processor)

    # Hotkey mode (transient with dependencies)
    def create_hotkey_mode(
        io_manager: InputOutputManager,
        transformation_engine: TransformationEngineProtocol,
        config_manager: ConfigManagerProtocol,
    ) -> HotkeyMode | None:
        try:
            return HotkeyMode(io_manager, transformation_engine, config_manager)
        except Exception as e:
            logger = get_logger(__name__)
            log_warning(logger, f"Hotkey mode not available: {e}")
            return None

    container.register_factory(HotkeyMode, create_hotkey_mode)


class ApplicationFactory:
    """Factory for creating application instances with dependency injection."""

    @staticmethod
    def create_application() -> "ApplicationInterface":
        """Create application instance with all dependencies configured."""
        # Configure services
        ServiceRegistry.configure(configure_services)

        # Create application interface
        return ApplicationInterface()

    @staticmethod
    def create_for_testing(
        config_override: dict[str, Any] | None = None,
    ) -> "ApplicationInterface":
        """Create application instance for testing with optional config override."""
        # Reset service registry for clean test state
        ServiceRegistry.reset()

        # Configure services with test overrides
        def configure_test_services(container: DIContainer) -> None:
            configure_services(container)

            # Apply test-specific overrides
            if config_override:
                # This would require test-specific configuration manager
                pass

        ServiceRegistry.configure(configure_test_services)

        return ApplicationInterface()


from .main import ApplicationInterface  # Import here to avoid circular imports"
