"""
Application lifecycle management module for String_Multitool.

This module provides comprehensive lifecycle tracking, debug information collection,
and structured logging for application startup, operation, and shutdown events.

Features:
- Start/end timestamp tracking with precise timing
- Exit reason classification and logging
- System environment and resource monitoring
- Performance metrics collection
- Structured JSON logging format
- Exception and error tracking
- International (English) messaging for global usage

Architecture:
- Singleton pattern for centralized lifecycle management
- Observer pattern for event notification
- Strategy pattern for different logging strategies
- Dependency injection compatible design

Reference:
- PEP 282: A Logging System
- Python Official Documentation: logging, threading, resource modules
- ISO 8601: Date and time format standard
"""

from __future__ import annotations

import json
import os
import platform
import sys
import threading
import time
import traceback
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Protocol, TypedDict
from uuid import uuid4

from .unified_logger import get_logger

# Optional dependencies with graceful fallbacks
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import resource

    RESOURCE_AVAILABLE = True
except ImportError:
    RESOURCE_AVAILABLE = False


class ExitReason(Enum):
    """Enumeration of application exit reasons for categorization."""

    # Normal exits
    NORMAL_COMPLETION = "normal_completion"
    USER_REQUESTED = "user_requested"
    COMMAND_COMPLETED = "command_completed"

    # Interactive exits
    USER_QUIT = "user_quit"
    USER_INTERRUPT = "user_interrupt"  # Ctrl+C
    EOF_INPUT = "eof_input"

    # Mode switches
    MODE_SWITCH = "mode_switch"
    DAEMON_STOP = "daemon_stop"

    # Error exits
    CONFIGURATION_ERROR = "configuration_error"
    VALIDATION_ERROR = "validation_error"
    TRANSFORMATION_ERROR = "transformation_error"
    CRYPTOGRAPHY_ERROR = "cryptography_error"
    CLIPBOARD_ERROR = "clipboard_error"
    IO_ERROR = "io_error"
    DEPENDENCY_ERROR = "dependency_error"

    # System exits
    SYSTEM_SIGNAL = "system_signal"
    OUT_OF_MEMORY = "out_of_memory"
    PERMISSION_ERROR = "permission_error"

    # Unknown/unexpected
    UNKNOWN_ERROR = "unknown_error"
    FATAL_ERROR = "fatal_error"


class SessionInfo(TypedDict):
    """Type definition for session information structure."""

    session_id: str
    start_timestamp: str
    start_timestamp_iso: str
    end_timestamp: str | None
    end_timestamp_iso: str | None
    duration_seconds: float | None
    exit_reason: str | None
    exit_code: int | None
    mode: str | None
    command_args: list[str]


class SystemInfo(TypedDict):
    """Type definition for system information structure."""

    platform: str
    platform_version: str
    python_version: str
    architecture: str
    hostname: str
    username: str
    process_id: int
    parent_process_id: int
    working_directory: str
    executable_path: str
    environment_variables: dict[str, str]


class ResourceMetrics(TypedDict):
    """Type definition for resource usage metrics."""

    memory_usage_mb: float
    memory_peak_mb: float
    cpu_percent: float
    open_file_descriptors: int
    thread_count: int
    user_time: float
    system_time: float


class DebugInfo(TypedDict):
    """Type definition for comprehensive debug information."""

    session: SessionInfo
    system: SystemInfo
    resources: ResourceMetrics
    components_status: dict[str, Any]
    error_details: dict[str, Any] | None
    performance_metrics: dict[str, Any]


class LifecycleObserver(Protocol):
    """Protocol for lifecycle event observers."""

    def on_application_start(self, session_info: SessionInfo) -> None:
        """Called when application starts."""
        ...

    def on_application_end(self, session_info: SessionInfo, debug_info: DebugInfo) -> None:
        """Called when application ends."""
        ...


class ApplicationLifecycleManager:
    """
    Centralized application lifecycle management system.

    This class provides comprehensive tracking of application lifecycle events,
    system resources, performance metrics, and debug information collection.
    It follows best practices for enterprise-grade logging and monitoring.
    """

    _instance: ApplicationLifecycleManager | None = None
    _lock = threading.Lock()

    def __new__(cls) -> ApplicationLifecycleManager:
        """Ensure singleton pattern with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize lifecycle manager with default configuration."""
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self._logger = get_logger(__name__)
        self._session_id = str(uuid4())
        self._start_time = time.time()
        self._start_datetime = datetime.now(UTC)
        self._observers: list[LifecycleObserver] = []
        self._components_status: dict[str, Any] = {}
        self._performance_metrics: dict[str, Any] = {}
        self._error_details: dict[str, Any] | None = None
        self._mode: str | None = None
        self._command_args: list[str] = sys.argv[1:].copy()

        # Initialize resource monitoring with fallback
        if PSUTIL_AVAILABLE:
            try:
                self._process = psutil.Process()
                self._initial_memory = self._process.memory_info().rss / 1024 / 1024  # MB
            except Exception as e:
                self._logger.warning(f"Failed to initialize psutil process monitoring: {e}")
                self._process = None
                self._initial_memory = 0.0
        else:
            self._process = None
            self._initial_memory = 0.0

        # Log application startup
        self._log_application_start()

    def _log_application_start(self) -> None:
        """Log comprehensive application startup information."""
        try:
            session_info = self._build_session_info()
            system_info = self._collect_system_info()
            resource_metrics = self._collect_resource_metrics()

            startup_log = {
                "event": "APPLICATION_START",
                "timestamp": session_info["start_timestamp_iso"],
                "session_id": self._session_id,
                "system": system_info,
                "resources": resource_metrics,
                "command_args": self._command_args,
                "message": "String_Multitool application started successfully",
            }

            # Log structured data for machine processing
            self._logger.info(
                f"APPLICATION_LIFECYCLE: {json.dumps(startup_log, ensure_ascii=False)}"
            )

            # Log human-readable startup message
            self._logger.info(f"Application started - Session ID: {self._session_id}")
            self._logger.debug(f"Startup timestamp: {session_info['start_timestamp_iso']}")
            self._logger.debug(
                f"System: {system_info['platform']} {system_info['platform_version']}"
            )
            self._logger.debug(f"Python: {system_info['python_version']}")
            self._logger.debug(f"Memory usage: {resource_metrics['memory_usage_mb']:.1f} MB")
            self._logger.debug(f"Process ID: {system_info['process_id']}")

            # Notify observers
            for observer in self._observers:
                try:
                    observer.on_application_start(session_info)
                except Exception as e:
                    self._logger.error(f"Error notifying observer on start: {e}")

        except Exception as e:
            self._logger.error(f"Failed to log application start: {e}")
            self._logger.debug(f"Startup logging error: {traceback.format_exc()}")

    def set_mode(self, mode: str) -> None:
        """Set the current application mode for tracking."""
        self._mode = mode
        self._logger.debug(f"Application mode set to: {mode}")

    def set_component_status(self, component: str, status: Any) -> None:
        """Set status information for a specific component."""
        self._components_status[component] = status
        self._logger.debug(f"Component {component} status updated")

    def add_performance_metric(self, metric_name: str, value: Any) -> None:
        """Add a performance metric for tracking."""
        self._performance_metrics[metric_name] = value
        self._logger.debug(f"Performance metric {metric_name}: {value}")

    def register_observer(self, observer: LifecycleObserver) -> None:
        """Register an observer for lifecycle events."""
        self._observers.append(observer)
        self._logger.debug(f"Lifecycle observer registered: {type(observer).__name__}")

    def unregister_observer(self, observer: LifecycleObserver) -> None:
        """Unregister a lifecycle event observer."""
        try:
            self._observers.remove(observer)
            self._logger.debug(f"Lifecycle observer unregistered: {type(observer).__name__}")
        except ValueError:
            self._logger.warning(
                f"Observer not found for unregistration: {type(observer).__name__}"
            )

    def _build_session_info(self) -> SessionInfo:
        """Build comprehensive session information."""
        end_time = time.time()
        end_datetime = datetime.now(UTC)
        duration = end_time - self._start_time

        return {
            "session_id": self._session_id,
            "start_timestamp": self._start_datetime.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "start_timestamp_iso": self._start_datetime.isoformat(),
            "end_timestamp": end_datetime.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "end_timestamp_iso": end_datetime.isoformat(),
            "duration_seconds": round(duration, 3),
            "exit_reason": None,
            "exit_code": None,
            "mode": self._mode,
            "command_args": self._command_args,
        }

    def _collect_system_info(self) -> SystemInfo:
        """Collect comprehensive system information."""
        try:
            # Get filtered environment variables (exclude sensitive data)
            safe_env_vars = {}
            sensitive_keys = {
                "password",
                "token",
                "key",
                "secret",
                "auth",
                "credential",
            }
            for key, value in os.environ.items():
                if not any(sensitive in key.lower() for sensitive in sensitive_keys):
                    safe_env_vars[key] = value
                else:
                    safe_env_vars[key] = "[REDACTED]"

            return {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "python_version": platform.python_version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "username": os.getlogin() if hasattr(os, "getlogin") else "unknown",
                "process_id": os.getpid(),
                "parent_process_id": os.getppid(),
                "working_directory": str(Path.cwd()),
                "executable_path": sys.executable,
                "environment_variables": safe_env_vars,
            }
        except Exception as e:
            self._logger.error(f"Error collecting system info: {e}")
            return {
                "platform": "unknown",
                "platform_version": "unknown",
                "python_version": "unknown",
                "architecture": "unknown",
                "hostname": "unknown",
                "username": "unknown",
                "process_id": os.getpid(),
                "parent_process_id": 0,
                "working_directory": "unknown",
                "executable_path": "unknown",
                "environment_variables": {},
            }

    def _collect_resource_metrics(self) -> ResourceMetrics:
        """Collect current resource usage metrics with graceful fallbacks."""
        try:
            # Initialize default values
            memory_mb = 0.0
            peak_memory = 0.0
            cpu_percent = 0.0
            open_fds = 0
            thread_count = threading.active_count()
            user_time = 0.0
            system_time = 0.0

            # Try to get psutil metrics if available
            if PSUTIL_AVAILABLE and self._process is not None:
                try:
                    # Memory information
                    memory_info = self._process.memory_info()
                    memory_mb = memory_info.rss / 1024 / 1024

                    # CPU usage (may be 0.0 on first call)
                    cpu_percent = self._process.cpu_percent()

                    # File descriptors (Unix-like systems)
                    try:
                        open_fds = len(self._process.open_files())
                    except (AttributeError, psutil.AccessDenied):
                        open_fds = 0

                    # Thread count
                    try:
                        thread_count = self._process.num_threads()
                    except (AttributeError, psutil.AccessDenied):
                        thread_count = threading.active_count()

                except Exception as e:
                    self._logger.debug(f"Error collecting psutil metrics: {e}")

            # Try to get resource module metrics if available
            if RESOURCE_AVAILABLE:
                try:
                    if hasattr(resource, "getrusage") and hasattr(resource, "RUSAGE_SELF"):
                        # Type-safe access to resource constants
                        rusage_self = resource.RUSAGE_SELF
                        ru = resource.getrusage(rusage_self)
                        user_time = ru.ru_utime
                        system_time = ru.ru_stime
                        peak_memory = ru.ru_maxrss / 1024  # Convert to MB (Linux reports in KB)
                        if platform.system() == "Darwin":  # macOS reports in bytes
                            peak_memory = ru.ru_maxrss / 1024 / 1024
                except (AttributeError, OSError) as e:
                    self._logger.debug(f"Error collecting resource usage: {e}")
                    peak_memory = memory_mb
            else:
                peak_memory = memory_mb

            return {
                "memory_usage_mb": round(memory_mb, 2),
                "memory_peak_mb": round(peak_memory, 2),
                "cpu_percent": round(cpu_percent, 1),
                "open_file_descriptors": open_fds,
                "thread_count": thread_count,
                "user_time": round(user_time, 3),
                "system_time": round(system_time, 3),
            }

        except Exception as e:
            self._logger.error(f"Error collecting resource metrics: {e}")
            return self._get_fallback_metrics()

    def _get_fallback_metrics(self) -> ResourceMetrics:
        """Get fallback resource metrics when psutil is unavailable."""
        return {
            "memory_usage_mb": 0.0,
            "memory_peak_mb": 0.0,
            "cpu_percent": 0.0,
            "open_file_descriptors": 0,
            "thread_count": threading.active_count(),
            "user_time": 0.0,
            "system_time": 0.0,
        }

    def log_application_end(
        self,
        exit_reason: ExitReason,
        exit_code: int = 0,
        exception: Exception | None = None,
    ) -> None:
        """
        Log comprehensive application shutdown information.

        Args:
            exit_reason: Categorized reason for application exit
            exit_code: System exit code
            exception: Exception that caused the exit (if applicable)
        """
        try:
            # Build comprehensive debug information
            session_info = self._build_session_info()
            session_info["exit_reason"] = exit_reason.value
            session_info["exit_code"] = exit_code

            debug_info: DebugInfo = {
                "session": session_info,
                "system": self._collect_system_info(),
                "resources": self._collect_resource_metrics(),
                "components_status": self._components_status.copy(),
                "error_details": None,
                "performance_metrics": self._performance_metrics.copy(),
            }

            # Add exception details if provided
            if exception is not None:
                debug_info["error_details"] = {
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "traceback": traceback.format_exc(),
                    "module": getattr(exception, "__module__", "unknown"),
                    "line_number": (
                        traceback.extract_tb(exception.__traceback__)[-1].lineno
                        if exception.__traceback__
                        else 0
                    ),
                }

            # Create structured shutdown log
            shutdown_log = {
                "event": "APPLICATION_END",
                "timestamp": session_info["end_timestamp_iso"],
                "session_id": self._session_id,
                "duration_seconds": session_info["duration_seconds"],
                "exit_reason": exit_reason.value,
                "exit_code": exit_code,
                "mode": self._mode,
                "resources": debug_info["resources"],
                "performance_metrics": self._performance_metrics,
                "message": self._get_exit_message(exit_reason, exit_code),
            }

            if debug_info["error_details"]:
                shutdown_log["error"] = debug_info["error_details"]

            # Log structured data for machine processing
            self._logger.info(
                f"APPLICATION_LIFECYCLE: {json.dumps(shutdown_log, ensure_ascii=False)}"
            )

            # Log human-readable shutdown message
            duration = session_info["duration_seconds"] or 0
            self._logger.info(
                f"Application ended - Duration: {duration:.3f}s, Reason: {exit_reason.value}"
            )
            self._logger.debug(f"End timestamp: {session_info['end_timestamp_iso']}")
            self._logger.debug(f"Exit code: {exit_code}")
            self._logger.debug(
                f"Peak memory usage: {debug_info['resources']['memory_peak_mb']:.1f} MB"
            )

            if exception:
                self._logger.error(
                    f"Exception caused exit: {type(exception).__name__}: {str(exception)}"
                )

            # Notify observers
            for observer in self._observers:
                try:
                    observer.on_application_end(session_info, debug_info)
                except Exception as e:
                    self._logger.error(f"Error notifying observer on end: {e}")

        except Exception as e:
            self._logger.error(f"Failed to log application end: {e}")
            self._logger.debug(f"Shutdown logging error: {traceback.format_exc()}")

    def _get_exit_message(self, exit_reason: ExitReason, exit_code: int) -> str:
        """Generate human-readable exit message based on exit reason."""
        if exit_code == 0:
            return {
                ExitReason.NORMAL_COMPLETION: "Application completed successfully",
                ExitReason.USER_REQUESTED: "Application terminated by user request",
                ExitReason.COMMAND_COMPLETED: "Command executed successfully",
                ExitReason.USER_QUIT: "User quit application normally",
                ExitReason.USER_INTERRUPT: "Application interrupted by user (Ctrl+C)",
                ExitReason.EOF_INPUT: "End of input stream reached",
                ExitReason.MODE_SWITCH: "Application mode switched",
                ExitReason.DAEMON_STOP: "Daemon mode stopped",
            }.get(exit_reason, "Application ended normally")
        else:
            return {
                ExitReason.CONFIGURATION_ERROR: "Application failed due to configuration error",
                ExitReason.VALIDATION_ERROR: "Application failed due to validation error",
                ExitReason.TRANSFORMATION_ERROR: "Application failed due to transformation error",
                ExitReason.CRYPTOGRAPHY_ERROR: "Application failed due to cryptography error",
                ExitReason.CLIPBOARD_ERROR: "Application failed due to clipboard error",
                ExitReason.IO_ERROR: "Application failed due to I/O error",
                ExitReason.DEPENDENCY_ERROR: "Application failed due to dependency error",
                ExitReason.SYSTEM_SIGNAL: "Application terminated by system signal",
                ExitReason.OUT_OF_MEMORY: "Application terminated due to out of memory",
                ExitReason.PERMISSION_ERROR: "Application failed due to permission error",
                ExitReason.UNKNOWN_ERROR: "Application failed due to unknown error",
                ExitReason.FATAL_ERROR: "Application failed due to fatal error",
            }.get(exit_reason, f"Application failed with exit code {exit_code}")

    def get_session_id(self) -> str:
        """Get the current session ID."""
        return self._session_id

    def get_runtime_seconds(self) -> float:
        """Get the current runtime in seconds."""
        return time.time() - self._start_time

    def get_debug_summary(self) -> dict[str, Any]:
        """Get a summary of current debug information for troubleshooting."""
        try:
            return {
                "session_id": self._session_id,
                "runtime_seconds": round(self.get_runtime_seconds(), 3),
                "mode": self._mode,
                "components_status": self._components_status.copy(),
                "resource_metrics": self._collect_resource_metrics(),
                "performance_metrics": self._performance_metrics.copy(),
            }
        except Exception as e:
            self._logger.error(f"Error building debug summary: {e}")
            return {"error": str(e)}


# Global lifecycle manager instance
_lifecycle_manager: ApplicationLifecycleManager | None = None
_manager_lock = threading.Lock()


def get_lifecycle_manager() -> ApplicationLifecycleManager:
    """Get the global lifecycle manager instance with thread safety."""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        with _manager_lock:
            if _lifecycle_manager is None:
                _lifecycle_manager = ApplicationLifecycleManager()
    return _lifecycle_manager


def log_application_start() -> str:
    """
    Log application startup and return session ID.

    Returns:
        Session ID for this application run
    """
    manager = get_lifecycle_manager()
    return manager.get_session_id()


def log_application_end(
    exit_reason: ExitReason, exit_code: int = 0, exception: Exception | None = None
) -> None:
    """
    Log application shutdown with comprehensive debug information.

    Args:
        exit_reason: Categorized reason for application exit
        exit_code: System exit code
        exception: Exception that caused the exit (if applicable)
    """
    manager = get_lifecycle_manager()
    manager.log_application_end(exit_reason, exit_code, exception)


def set_application_mode(mode: str) -> None:
    """Set the current application mode for tracking."""
    manager = get_lifecycle_manager()
    manager.set_mode(mode)


def set_component_status(component: str, status: Any) -> None:
    """Set status information for a specific component."""
    manager = get_lifecycle_manager()
    manager.set_component_status(component, status)


def add_performance_metric(metric_name: str, value: Any) -> None:
    """Add a performance metric for tracking."""
    manager = get_lifecycle_manager()
    manager.add_performance_metric(metric_name, value)


def get_debug_summary() -> dict[str, Any]:
    """Get a summary of current debug information for troubleshooting."""
    manager = get_lifecycle_manager()
    return manager.get_debug_summary()
