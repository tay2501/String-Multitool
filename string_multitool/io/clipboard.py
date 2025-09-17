"""
Clipboard monitoring for String_Multitool.

This module provides clipboard change detection and monitoring
capabilities for auto-detection functionality.
"""

from __future__ import annotations

import threading
import time
from typing import Final

from ..exceptions import ClipboardError, ValidationError
from ..models.types import IOManagerProtocol, ThreadCallback
from ..utils.unified_logger import get_logger

logger = get_logger(__name__)


class ClipboardMonitor:
    """Monitors clipboard changes for auto-detection functionality.

    This class provides background clipboard monitoring with
    configurable intervals and content size limits.
    """

    def __init__(self, io_manager: IOManagerProtocol) -> None:
        """Initialize clipboard monitor.

        Args:
            io_manager: I/O manager for clipboard access

        Raises:
            ValidationError: If io_manager is invalid
        """
        if io_manager is None:
            raise ValidationError("IO manager cannot be None")

        # Constants
        DEFAULT_CHECK_INTERVAL: Final[float] = 1.0  # seconds
        MAX_CONTENT_SIZE: Final[int] = 1024 * 1024  # 1MB limit

        # Instance variable annotations following PEP 526
        self.io_manager: IOManagerProtocol = io_manager
        self.is_monitoring: bool = False
        self.last_content: str = ""
        self.check_interval: float = DEFAULT_CHECK_INTERVAL
        self.max_content_size: int = MAX_CONTENT_SIZE
        self._monitor_thread: threading.Thread | None = None
        self._stop_event: threading.Event = threading.Event()
        self._change_callback: ThreadCallback = None

    def start_monitoring(self, change_callback: ThreadCallback = None) -> None:
        """Start clipboard monitoring in background.

        Args:
            change_callback: Optional callback function called when clipboard changes

        Raises:
            ClipboardError: If monitoring cannot be started
        """
        if self.is_monitoring:
            return

        try:
            self._change_callback = change_callback
            self._stop_event.clear()

            # Initialize with current clipboard content
            try:
                self.last_content = self.io_manager.get_clipboard_text()
            except Exception:
                self.last_content = ""

            # Start monitoring thread
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop, daemon=True, name="ClipboardMonitor"
            )
            self._monitor_thread.start()
            self.is_monitoring = True

        except Exception as e:
            raise ClipboardError(
                f"Failed to start clipboard monitoring: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def stop_monitoring(self) -> None:
        """Stop clipboard monitoring.

        Raises:
            ClipboardError: If monitoring cannot be stopped
        """
        if not self.is_monitoring:
            return

        try:
            self._stop_event.set()
            self.is_monitoring = False

            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=2.0)

            self._monitor_thread = None
            self._change_callback = None

        except Exception as e:
            raise ClipboardError(
                f"Failed to stop clipboard monitoring: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def check_for_changes(self) -> bool:
        """Check for clipboard changes manually.

        Returns:
            True if clipboard content has changed

        Raises:
            ClipboardError: If clipboard check fails
        """
        try:
            current_content = self.io_manager.get_clipboard_text()

            if current_content != self.last_content:
                # Check content size limit
                if len(current_content) > self.max_content_size:
                    raise ClipboardError(
                        f"Clipboard content too large: {len(current_content)} bytes (max: {self.max_content_size})",
                        {
                            "content_size": len(current_content),
                            "max_size": self.max_content_size,
                        },
                    )

                self.last_content = current_content
                return True

            return False

        except ClipboardError:
            raise
        except Exception as e:
            raise ClipboardError(
                f"Failed to check clipboard changes: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def set_check_interval(self, interval: float) -> None:
        """Set clipboard check interval.

        Args:
            interval: Check interval in seconds (minimum 0.1)

        Raises:
            ValidationError: If interval is invalid
        """
        if not isinstance(interval, (int, float)):
            raise ValidationError(
                f"Check interval must be a number, got {type(interval).__name__}",
                {"interval_type": type(interval).__name__},
            )

        if interval < 0.1:
            raise ValidationError(
                f"Check interval too small: {interval} (minimum: 0.1)",
                {"interval": interval, "minimum": 0.1},
            )

        self.check_interval = max(0.1, float(interval))

    def set_max_content_size(self, size: int) -> None:
        """Set maximum clipboard content size.

        Args:
            size: Maximum size in bytes (minimum 1024)

        Raises:
            ValidationError: If size is invalid
        """
        if not isinstance(size, int):
            raise ValidationError(
                f"Content size must be an integer, got {type(size).__name__}",
                {"size_type": type(size).__name__},
            )

        if size < 1024:
            raise ValidationError(
                f"Content size too small: {size} (minimum: 1024)",
                {"size": size, "minimum": 1024},
            )

        self.max_content_size = size

    def _monitor_loop(self) -> None:
        """Main monitoring loop running in background thread."""
        while not self._stop_event.is_set():
            try:
                if self.check_for_changes() and self._change_callback:
                    self._change_callback(self.last_content)

                # Use shorter sleep intervals for better responsiveness
                for _ in range(int(self.check_interval * 10)):
                    if self._stop_event.is_set():
                        break
                    time.sleep(0.1)

            except Exception as e:
                # Log error but continue monitoring
                logger.error(f"Error during clipboard check: {e}")
                time.sleep(self.check_interval)
