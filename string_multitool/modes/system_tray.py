"""
System tray functionality for String_Multitool.

This module provides system tray icon support with context menu
and background operation capabilities.
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    import pystray

try:
    import pystray
    from PIL import Image

    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

from ..core.dependency_injection import inject
from ..core.types import ConfigManagerProtocol, TransformationEngineProtocol
from ..exceptions import ConfigurationError, StringMultitoolError
from ..io.manager import InputOutputManager
from ..utils.logger import get_logger
from .daemon import DaemonMode


class SystemTrayMode:
    """System tray mode for background operation with UI controls."""

    def __init__(
        self,
        transformation_engine: Optional[TransformationEngineProtocol] = None,
        config_manager: Optional[ConfigManagerProtocol] = None,
        io_manager: Optional[InputOutputManager] = None,
    ) -> None:
        """Initialize system tray mode.

        Args:
            transformation_engine: Transformation engine (injected if None)
            config_manager: Configuration manager (injected if None)
            io_manager: I/O manager (injected if None)

        Raises:
            ConfigurationError: If pystray is not available
        """
        if not PYSTRAY_AVAILABLE:
            raise ConfigurationError(
                "pystray library not available. Install with: pip install pystray pillow",
                {"missing_dependency": "pystray"},
            )

        self._logger = get_logger(__name__)

        # Use dependency injection - cast to correct types
        from ..core.transformations import TextTransformationEngine
        from ..core.config import ConfigurationManager

        self.transformation_engine = transformation_engine or inject(
            TextTransformationEngine
        )
        self.config_manager = config_manager or inject(ConfigurationManager)
        self.io_manager = io_manager or inject(InputOutputManager)

        # Initialize daemon mode for background processing
        self.daemon_mode = DaemonMode(
            transformation_engine=self.transformation_engine,
            config_manager=self.config_manager,
        )

        # Tray icon state
        self.icon: Optional[Any] = None
        self.is_running = False
        self._stop_event = threading.Event()

        # Create tray icon
        self._create_icon()

    def _create_icon(self) -> None:
        """Create system tray icon with menu."""
        try:
            # Try to load custom icon, fallback to default
            icon_path = Path("resources/icon.png")
            if icon_path.exists():
                image: Any = Image.open(icon_path)
            else:
                # Create default icon (16x16 blue square)
                image = Image.new("RGB", (16, 16), color="blue")

            # Create menu
            menu = pystray.Menu(
                pystray.MenuItem("String Multitool", None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(
                    "Start Monitoring",
                    self._start_monitoring,
                    checked=lambda _: (
                        self.daemon_mode.is_running if self.daemon_mode else False
                    ),
                ),
                pystray.MenuItem(
                    "Stop Monitoring",
                    self._stop_monitoring,
                    enabled=self.daemon_mode.is_running if self.daemon_mode else False,
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Preset 1: Trim (/t)", lambda: self._set_preset("1")),
                pystray.MenuItem(
                    "Preset 2: Full→Half (/fh)", lambda: self._set_preset("2")
                ),
                pystray.MenuItem(
                    "Preset 3: Half→Full (/hf)", lambda: self._set_preset("3")
                ),
                pystray.MenuItem(
                    "Preset 4: Hyphen→Underscore (/hu)", lambda: self._set_preset("4")
                ),
                pystray.MenuItem(
                    "Preset 5: Underscore→Hyphen (/uh)", lambda: self._set_preset("5")
                ),
                pystray.MenuItem(
                    "Preset 6: Sort Items (/si)", lambda: self._set_preset("6")
                ),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Status", self._show_status),
                pystray.MenuItem("Help", self._show_help),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit", self._exit_application),
            )

            # Create icon
            self.icon = pystray.Icon(
                "String_Multitool",
                image,
                "String Multitool - Text Transformation Tool",
                menu,
            )

        except Exception as e:
            raise ConfigurationError(
                f"Failed to create system tray icon: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def _start_monitoring(self, icon: Any, item: Any) -> None:
        """Start daemon monitoring."""
        try:
            if self.daemon_mode and not self.daemon_mode.is_running:
                # Set default preset if no rules are active
                if not self.daemon_mode.active_rules:
                    self.daemon_mode.set_preset("1")

                self.daemon_mode.start_monitoring()
                self._logger.info("[TRAY] Monitoring started")

                # Update icon tooltip
                if self.icon:
                    self.icon.title = "String Multitool - Monitoring Active"
            else:
                self._logger.warning("[TRAY] Monitoring already running")
        except Exception as e:
            raise StringMultitoolError(
                f"Failed to start monitoring from system tray: {e}",
                {
                    "error_type": type(e).__name__,
                    "operation": "start_monitoring",
                    "daemon_running": (
                        self.daemon_mode.is_running if self.daemon_mode else False
                    ),
                },
            ) from e

    def _stop_monitoring(self, icon: Any, item: Any) -> None:
        """Stop daemon monitoring."""
        try:
            if self.daemon_mode and self.daemon_mode.is_running:
                self.daemon_mode.stop()
                self._logger.info("[TRAY] Monitoring stopped")

                # Update icon tooltip
                if self.icon:
                    self.icon.title = "String Multitool - Monitoring Stopped"
            else:
                self._logger.warning("[TRAY] Monitoring not running")
        except Exception as e:
            raise StringMultitoolError(
                f"Failed to stop monitoring from system tray: {e}",
                {
                    "error_type": type(e).__name__,
                    "operation": "stop_monitoring",
                    "daemon_running": (
                        self.daemon_mode.is_running if self.daemon_mode else False
                    ),
                },
            ) from e

    def _set_preset(self, preset_name: str) -> None:
        """Set transformation preset."""
        try:
            if self.daemon_mode:
                self.daemon_mode.set_preset(preset_name)
                self._logger.info(f"[TRAY] Preset {preset_name} activated")

                # Update icon tooltip
                if self.icon:
                    self.icon.title = f"String Multitool - Preset {preset_name}"
        except Exception as e:
            raise StringMultitoolError(
                f"Failed to set preset '{preset_name}' from system tray: {e}",
                {
                    "error_type": type(e).__name__,
                    "operation": "set_preset",
                    "preset_name": preset_name,
                    "daemon_available": self.daemon_mode is not None,
                },
            ) from e

    def _show_status(self, icon: Any, item: Any) -> None:
        """Show current status."""
        try:
            if self.daemon_mode:
                status = self.daemon_mode.get_status()
                self._logger.info(
                    f"[TRAY] Status: {'Running' if status['running'] else 'Stopped'}"
                )
                self._logger.info(
                    f"[TRAY] Active rules: {' -> '.join(status['active_rules']) if status['active_rules'] else 'None'}"
                )
                self._logger.info(
                    f"[TRAY] Active preset: {status['active_preset'] or 'None'}"
                )
        except Exception as e:
            raise StringMultitoolError(
                f"Failed to get status from system tray: {e}",
                {
                    "error_type": type(e).__name__,
                    "operation": "show_status",
                    "daemon_available": self.daemon_mode is not None,
                },
            ) from e

    def _show_help(self, icon: Any, item: Any) -> None:
        """Show help information."""
        self._logger.info("[TRAY] String Multitool - System Tray Mode")
        self._logger.info("[TRAY] Right-click the tray icon for options:")
        self._logger.info(
            "[TRAY] - Start/Stop Monitoring: Control clipboard monitoring"
        )
        self._logger.info("[TRAY] - Set Preset: Choose transformation preset")
        self._logger.info("[TRAY] - Status: View current configuration")
        self._logger.info("[TRAY] - Exit: Close application")

    def _exit_application(self, icon: Any, item: Any) -> None:
        """Exit the application."""
        try:
            self._logger.info("[TRAY] Exiting application...")

            # Stop daemon monitoring if running
            if self.daemon_mode and self.daemon_mode.is_running:
                self.daemon_mode.stop()

            # Signal stop
            self._stop_event.set()
            self.is_running = False

            # Stop icon
            if self.icon:
                self.icon.stop()

        except Exception as e:
            raise StringMultitoolError(
                f"Error during system tray exit: {e}",
                {
                    "error_type": type(e).__name__,
                    "operation": "exit_application",
                    "daemon_running": (
                        self.daemon_mode.is_running if self.daemon_mode else False
                    ),
                    "icon_available": self.icon is not None,
                },
            ) from e

    def run(self) -> None:
        """Run system tray mode.

        Raises:
            StringMultitoolError: If tray mode fails to start
        """
        try:
            if not self.icon:
                raise StringMultitoolError(
                    "System tray icon not initialized", {"component": "system_tray"}
                )

            self._logger.info("[TRAY] Starting system tray mode...")
            self._logger.info("[TRAY] Right-click the tray icon for options")

            self.is_running = True

            # Run icon (this blocks until icon.stop() is called)
            self.icon.run()

        except KeyboardInterrupt:
            self._logger.info("[TRAY] Interrupted by user")
            self.stop()
        except Exception as e:
            raise StringMultitoolError(
                f"System tray mode failed: {e}", {"error_type": type(e).__name__}
            ) from e
        finally:
            self.cleanup()

    def stop(self) -> None:
        """Stop system tray mode."""
        try:
            self._logger.info("[TRAY] Stopping system tray mode...")

            # Stop daemon if running
            if self.daemon_mode and self.daemon_mode.is_running:
                self.daemon_mode.stop()

            # Signal stop
            self._stop_event.set()
            self.is_running = False

            # Stop icon
            if self.icon:
                self.icon.stop()

        except Exception as e:
            raise StringMultitoolError(
                f"Error stopping system tray: {e}",
                {
                    "error_type": type(e).__name__,
                    "operation": "stop",
                    "daemon_running": (
                        self.daemon_mode.is_running if self.daemon_mode else False
                    ),
                    "is_running": self.is_running,
                },
            ) from e

    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Stop daemon
            if self.daemon_mode:
                if self.daemon_mode.is_running:
                    self.daemon_mode.stop()

            # Clean up icon
            if self.icon:
                self.icon = None

            self._logger.debug("[TRAY] Cleanup completed")

        except Exception as e:
            raise StringMultitoolError(
                f"Error during system tray cleanup: {e}",
                {
                    "error_type": type(e).__name__,
                    "operation": "cleanup",
                    "daemon_available": self.daemon_mode is not None,
                    "icon_available": self.icon is not None,
                },
            ) from e
