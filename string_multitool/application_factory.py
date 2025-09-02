"""
Application factory using dependency injection.

This module provides factory functions for creating application instances
with proper dependency injection configuration.
"""

from __future__ import annotations

from typing import Any

from .core.config import ConfigurationManager
from .core.crypto import CryptographyManager
from .core.dependency_injection import DIContainer, ServiceRegistry, inject
from .core.transformations import TextTransformationEngine
from .core.types import (
    ConfigManagerProtocol,
    CryptoManagerProtocol,
    TransformationEngineProtocol,
)
from .exceptions import CryptographyError
from .io.manager import InputOutputManager

# ApplicationInterface will be imported locally to avoid circular imports
from .modes.interactive import CommandProcessor, InteractiveSession
from .utils.unified_logger import get_logger, log_with_context


def configure_services(container: DIContainer) -> None:
    """Configure all application services in the DI container.

    Uses EAFP (Easier to Ask for Forgiveness than Permission) approach
    for robust service configuration with proper error handling.

    Args:
        container: Dependency injection container instance

    Raises:
        ConfigurationError: If service configuration fails
    """
    from .exceptions import ConfigurationError

    # Configuration manager (singleton) - EAFP style initialization
    try:
        config_manager = ConfigurationManager()
        container.register_singleton(type(config_manager), config_manager)
        container.register_singleton(ConfigurationManager, config_manager)
    except Exception as e:
        raise ConfigurationError(
            f"Failed to configure configuration manager: {e}",
            {"error_type": type(e).__name__},
        ) from e

    # Text transformation engine (singleton)
    def create_transformation_engine(
        config_mgr: ConfigurationManager,
    ) -> TextTransformationEngine:
        return TextTransformationEngine(config_mgr)

    # Skip protocol registration to avoid type-abstract error
    container.register_factory(TextTransformationEngine, create_transformation_engine)

    # Cryptography manager (singleton) - EAFP style with proper error handling
    def create_crypto_manager(
        config_mgr: ConfigurationManager,
    ) -> CryptographyManager | None:
        """Create cryptography manager using EAFP pattern.

        Args:
            config_mgr: Configuration manager protocol instance

        Returns:
            CryptographyManager instance or None if unavailable
        """
        try:
            return CryptographyManager(config_mgr)
        except CryptographyError as e:
            logger = get_logger(__name__)
            logger.warning("Cryptography manager not available", error=str(e))
            return None
        except Exception as e:
            logger = get_logger(__name__)
            log_with_context(
                logger,
                "warning",
                "Unexpected error creating crypto manager",
                error=str(e),
            )
            return None

    def create_crypto_manager_concrete(
        config_mgr: ConfigurationManager,
    ) -> CryptographyManager:
        """Create concrete cryptography manager with validation.

        Args:
            config_mgr: Configuration manager protocol instance

        Returns:
            CryptographyManager instance

        Raises:
            CryptographyError: If manager creation fails
        """
        result = create_crypto_manager(config_mgr)
        if result is None:
            raise CryptographyError(
                "Cryptography manager creation failed - dependencies unavailable",
                {"config_available": config_mgr is not None},
            )
        return result

    # Skip protocol registration to avoid type-abstract error
    container.register_factory(CryptographyManager, create_crypto_manager_concrete)

    # I/O manager (transient)
    container.register_transient(InputOutputManager, InputOutputManager)

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


class ApplicationFactory:
    """Factory for creating application instances with dependency injection."""

    @staticmethod
    def create_application() -> Any:  # Use Any to avoid forward reference issues
        """Create application instance with all dependencies configured.

        Uses EAFP (Easier to Ask for Forgiveness than Permission) approach
        for robust dependency injection and error handling.

        Returns:
            ApplicationInterface: Fully configured application instance

        Raises:
            ConfigurationError: If application creation fails
        """
        from .core.config import ConfigurationManager
        from .core.crypto import CryptographyManager
        from .core.transformations import TextTransformationEngine
        from .exceptions import ConfigurationError
        from .utils.unified_logger import get_logger, log_with_context

        logger = get_logger(__name__)
        log_with_context(
            logger, "debug", "Starting application creation with dependency injection"
        )

        try:
            # Import ApplicationInterface locally to avoid circular imports
            from .main import ApplicationInterface

            # Configure services - EAFP style
            ServiceRegistry.configure(configure_services)
            log_with_context(
                logger, "debug", "Service registry configured successfully"
            )

            # Get core dependencies via DI - these are required
            config_manager = inject(ConfigurationManager)
            transformation_engine = inject(TextTransformationEngine)
            io_manager = inject(InputOutputManager)
            log_with_context(logger, "debug", "Core dependencies injected successfully")

            # Get optional crypto manager - EAFP style
            crypto_manager = None
            try:
                crypto_manager = inject(CryptographyManager)
                log_with_context(logger, "debug", "Cryptography manager available")
            except (CryptographyError, ImportError, OSError) as e:
                log_with_context(
                    logger, "warning", "Cryptography manager unavailable", error=str(e)
                )
            except Exception as e:
                logger.warning("Unexpected error with crypto manager", error=str(e))

            # Create application interface with core dependencies
            app_interface = ApplicationInterface(
                config_manager=config_manager,
                transformation_engine=transformation_engine,
                io_manager=io_manager,
                crypto_manager=crypto_manager,
            )
            log_with_context(
                logger, "debug", "Application interface created successfully"
            )
            return app_interface

        except Exception as e:
            raise ConfigurationError(
                f"Failed to create application: {e}",
                {"error_type": type(e).__name__},
            ) from e

    @staticmethod
    def create_for_testing(
        config_override: dict[str, Any] | None = None,
    ) -> Any:  # Use Any to avoid forward reference issues
        """Create application instance for testing with optional config override.

        Args:
            config_override: Optional configuration overrides for testing

        Returns:
            ApplicationInterface: Test-configured application instance

        Raises:
            ConfigurationError: If test application creation fails
        """
        from .core.config import ConfigurationManager
        from .core.transformations import TextTransformationEngine
        from .exceptions import ConfigurationError
        from .utils.unified_logger import get_logger

        logger = get_logger(__name__)

        try:
            # Import ApplicationInterface locally to avoid circular imports
            from .main import ApplicationInterface

            # Reset service registry for clean test state
            ServiceRegistry.reset()

            # Configure services with test overrides
            def configure_test_services(container: DIContainer) -> None:
                configure_services(container)
                # Apply test-specific overrides if needed
                if config_override:
                    logger.debug(f"Applying test config overrides: {config_override}")

            ServiceRegistry.configure(configure_test_services)

            # Get core dependencies via DI
            config_manager = inject(ConfigurationManager)
            transformation_engine = inject(TextTransformationEngine)
            io_manager = inject(InputOutputManager)

            # Create minimal application for testing
            return ApplicationInterface(
                config_manager=config_manager,
                transformation_engine=transformation_engine,
                io_manager=io_manager,
                crypto_manager=None,  # Skip crypto for testing
            )

        except Exception as e:
            raise ConfigurationError(
                f"Failed to create test application: {e}",
                {"error_type": type(e).__name__},
            ) from e
