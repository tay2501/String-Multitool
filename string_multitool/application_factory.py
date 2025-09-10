"""
Application factory using dependency injection.

This module provides factory functions for creating application instances
with proper dependency injection configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .main import ApplicationInterface

from .exceptions import CryptographyError
from .io.manager import InputOutputManager
from .models.config import ConfigurationManager
from .models.crypto import CryptographyManager

# ApplicationInterface will be imported locally to avoid circular imports
from .models.transformations import TextTransformationEngine
from .utils.unified_logger import get_logger, log_with_context

# DIContainer削除 - 直接的なファクトリパターンに変更


def create_services() -> tuple[
    ConfigurationManager,
    TextTransformationEngine,
    InputOutputManager,
    CryptographyManager | None,
]:
    """サービス群を直接作成するファクトリ関数

    EAFP (Easier to Ask for Forgiveness than Permission) アプローチを使用し、
    堅牢なサービス作成とエラーハンドリングを提供します。

    Returns:
        作成されたサービスのタプル (config_manager, transformation_engine, io_manager, crypto_manager)

    Raises:
        ConfigurationError: サービス作成に失敗した場合
    """
    from .exceptions import ConfigurationError

    logger = get_logger(__name__)

    try:
        # ConfigurationManager を作成 (EAFP style)
        try:
            config_manager = ConfigurationManager()
            logger.debug("ConfigurationManager created successfully")
        except Exception as e:
            logger.error(f"Failed to create ConfigurationManager: {e}")
            raise ConfigurationError(f"Configuration manager creation failed: {e}") from e

        # TextTransformationEngine を作成 (config_manager に依存)
        try:
            transformation_engine = TextTransformationEngine(config_manager)
            logger.debug("TextTransformationEngine created successfully")
        except Exception as e:
            logger.error(f"Failed to create TextTransformationEngine: {e}")
            raise ConfigurationError(f"Transformation engine creation failed: {e}") from e

        # InputOutputManager を作成
        try:
            io_manager = InputOutputManager()
            logger.debug("InputOutputManager created successfully")
        except Exception as e:
            logger.error(f"Failed to create InputOutputManager: {e}")
            raise ConfigurationError(f"I/O manager creation failed: {e}") from e

        # CryptographyManager を作成 (オプション - 失敗しても続行)
        crypto_manager = None
        try:
            crypto_manager = CryptographyManager(config_manager)
            logger.debug("CryptographyManager created successfully")
        except CryptographyError as e:
            # 暗号化依存関係が利用できない場合は期待される動作
            logger.warning(f"CryptographyManager not available: {e}")
            logger.info("Encryption/decryption features will be disabled")
        except Exception as e:
            logger.error(f"Unexpected error creating CryptographyManager: {e}")
            # 暗号化はオプションなので例外を発生させない
            logger.info("Continuing without cryptography support")

        return config_manager, transformation_engine, io_manager, crypto_manager

    except Exception as e:
        logger.error(f"Service creation failed: {e}")
        raise ConfigurationError(f"Failed to create application services: {e}") from e


class ApplicationFactory:
    """Factory for creating application instances with dependency injection."""

    @staticmethod
    def create_application() -> ApplicationInterface:
        """Create application instance with all dependencies configured.

        Uses EAFP (Easier to Ask for Forgiveness than Permission) approach
        for robust dependency injection and error handling.

        Returns:
            ApplicationInterface: Fully configured application instance

        Raises:
            ConfigurationError: If application creation fails
        """
        from .exceptions import ConfigurationError
        from .utils.unified_logger import get_logger

        logger = get_logger(__name__)
        log_with_context(
            logger, "debug", "Starting application creation with dependency injection"
        )

        try:
            # Import ApplicationInterface at runtime to avoid circular imports
            from .main import ApplicationInterface

            # Create services directly - EAFP style
            config_manager, transformation_engine, io_manager, crypto_manager = create_services()
            log_with_context(logger, "debug", "Services created successfully")

            # Create application interface with core dependencies
            app_interface = ApplicationInterface(
                config_manager=config_manager,
                transformation_engine=transformation_engine,
                io_manager=io_manager,
                crypto_manager=crypto_manager,
            )
            log_with_context(logger, "debug", "Application interface created successfully")
            return app_interface

        except Exception as e:
            raise ConfigurationError(
                f"Failed to create application: {e}",
                {"error_type": type(e).__name__},
            ) from e

    @staticmethod
    def create_for_testing(
        config_override: dict[str, Any] | None = None,
    ) -> ApplicationInterface:
        """Create application instance for testing with optional config override.

        Args:
            config_override: Optional configuration overrides for testing

        Returns:
            ApplicationInterface: Test-configured application instance

        Raises:
            ConfigurationError: If test application creation fails
        """
        from .exceptions import ConfigurationError
        from .utils.unified_logger import get_logger

        logger = get_logger(__name__)

        try:
            # Import ApplicationInterface at runtime to avoid circular imports
            from .main import ApplicationInterface

            # Create services directly for testing
            config_manager, transformation_engine, io_manager, _ = create_services()

            # Apply test-specific overrides if needed
            if config_override:
                logger.debug(f"Applying test config overrides: {config_override}")

            # Create minimal application for testing (skip crypto)
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
