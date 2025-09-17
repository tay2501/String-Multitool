"""
Interactive mode components for String_Multitool.

This module provides interactive session management and command processing
with comprehensive error handling and type safety.
"""

from __future__ import annotations

from datetime import datetime

from ..exceptions import ClipboardError, ValidationError
from ..io.clipboard import ClipboardMonitor
from .types import (
    CommandResult,
    IOManagerProtocol,
    SessionState,
    TextSource,
    TransformationEngineProtocol,
)


class InteractiveSession:
    """Manages interactive session state and clipboard operations.

    This class provides centralized session management with auto-detection
    capabilities and comprehensive state tracking.
    """

    def __init__(
        self,
        io_manager: IOManagerProtocol,
        transformation_engine: TransformationEngineProtocol,
    ) -> None:
        """Initialize interactive session.

        Args:
            io_manager: InputOutputManager instance
            transformation_engine: TextTransformationEngine instance

        Raises:
            ValidationError: If required parameters are invalid
        """
        # EAFP: Try to use the dependencies, catch if they're invalid
        try:
            self.io_manager: IOManagerProtocol = io_manager
            self.transformation_engine: TransformationEngineProtocol = transformation_engine

            # Validate by checking essential methods exist
            if not hasattr(self.io_manager, "get_input_text"):
                raise AttributeError("IO manager missing get_input_text method")
            if not hasattr(self.transformation_engine, "get_available_rules"):
                raise AttributeError("Transformation engine missing get_available_rules method")
        except (AttributeError, TypeError) as e:
            raise ValidationError(f"Invalid dependency: {e}") from e
        self.current_text: str = ""
        self.text_source: TextSource = TextSource.CLIPBOARD
        self.last_update_time: datetime = datetime.now()
        self.clipboard_monitor: ClipboardMonitor = ClipboardMonitor(io_manager)
        self.auto_detection_enabled: bool = True
        self.session_start_time: datetime = datetime.now()

        # Auto-detection is always enabled
        self.auto_detection_enabled = True
        # Start monitoring immediately
        import contextlib

        with contextlib.suppress(Exception):
            # Continue with auto-detection enabled even if monitoring fails
            self.clipboard_monitor.start_monitoring(self._on_clipboard_change)

    def initialize_with_text(self, text: str, source: str = "clipboard") -> None:
        """Initialize session with initial text.

        Args:
            text: Initial text content
            source: Source of the text (clipboard, pipe, manual)

        Raises:
            ValidationError: If parameters are invalid
        """
        if not isinstance(text, str):
            raise ValidationError(
                f"Text must be a string, got {type(text).__name__}",
                {"text_type": type(text).__name__},
            )

        try:
            text_source: TextSource = TextSource(source)
        except ValueError as e:
            raise ValidationError(
                f"Invalid text source: {source}",
                {"source": source, "valid_sources": [s.value for s in TextSource]},
            ) from e

        self.current_text = text
        self.text_source = text_source
        self.last_update_time = datetime.now()

    def update_working_text(self, text: str, source: str) -> None:
        """Update the current working text.

        Args:
            text: New text content
            source: Source of the text

        Raises:
            ValidationError: If parameters are invalid
        """
        self.initialize_with_text(text, source)

    def get_status_info(self) -> SessionState:
        """Get current session status information.

        Returns:
            SessionState object with current session information
        """
        return SessionState(
            current_text=self.current_text,
            text_source=self.text_source,
            last_update_time=self.last_update_time,
            character_count=len(self.current_text),
            auto_detection_enabled=self.auto_detection_enabled,
            clipboard_monitor_active=self.clipboard_monitor.is_monitoring,
        )

    def refresh_from_clipboard(self) -> str:
        """Refresh working text from clipboard.

        Returns:
            New clipboard content

        Raises:
            ClipboardError: If clipboard access fails
        """
        try:
            new_content = self.io_manager.get_clipboard_text()
            self.update_working_text(new_content, "clipboard")
            return new_content

        except Exception as e:
            raise ClipboardError(
                f"Failed to refresh from clipboard: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def clear_working_text(self) -> None:
        """Clear the current working text."""
        self.update_working_text("", "manual")

    def check_clipboard_changes(self) -> str | None:
        """Check for clipboard changes (for manual polling).

        Returns:
            New clipboard content if changed, None otherwise

        Raises:
            ClipboardError: If clipboard check fails
        """
        try:
            if self.clipboard_monitor.check_for_changes():
                return self.clipboard_monitor.last_content
            return None

        except Exception as e:
            raise ClipboardError(
                f"Failed to check clipboard changes: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def get_display_text(self, max_length: int = 50) -> str:
        """Get text for display purposes with length limit.

        Args:
            max_length: Maximum length for display

        Returns:
            Truncated text for display
        """
        if len(self.current_text) <= max_length:
            return self.current_text
        return self.current_text[:max_length] + "..."

    def get_time_since_update(self) -> str:
        """Get human-readable time since last update.

        Returns:
            Formatted time string
        """
        delta = datetime.now() - self.last_update_time
        total_seconds: int = int(delta.total_seconds())

        if total_seconds < 60:
            return f"{total_seconds} seconds ago"
        elif total_seconds < 3600:
            minutes: int = total_seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            hours: int = total_seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"

    def cleanup(self) -> None:
        """Clean up session resources."""
        self.clipboard_monitor.stop_monitoring()

    def _on_clipboard_change(self, new_content: str) -> None:
        """Handle clipboard change notification.

        Args:
            new_content: New clipboard content
        """
        # This is called by the clipboard monitor when content changes
        # We'll just store the notification for the main thread to handle
        pass


class CommandProcessor:
    """Processes interactive commands including clipboard operations.

    This class provides comprehensive command processing with proper
    error handling and validation.
    """

    # Command definitions for help and validation
    CLIPBOARD_COMMANDS = {
        "refresh": "Refresh input text from clipboard",
        "reload": "Alias for refresh",
        "replace": "Short alias for refresh",
        "status": "Show current session status",
        "clear": "Clear current working text",
        "copy": "Copy working text to clipboard",
        "commands": "Show all available commands",
        "cmd": "Short alias for commands",
    }

    SYSTEM_COMMANDS = {
        "help": "Show transformation rules",
        "h": "Short alias for help",
        "?": "Short alias for help",
        "quit": "Exit application",
        "q": "Short alias for quit",
        "exit": "Exit application",
    }

    def __init__(self, session: InteractiveSession) -> None:
        """Initialize command processor.

        Args:
            session: InteractiveSession instance

        Raises:
            ValidationError: If session is invalid
        """
        if session is None:
            raise ValidationError("Session cannot be None")

        # Instance variable annotations following PEP 526
        self.session: InteractiveSession = session

    def is_command(self, input_text: str) -> bool:
        """Check if input text is a command (not a transformation rule).

        Args:
            input_text: User input text

        Returns:
            True if input is a command, False if it's a transformation rule
        """
        # Type annotation ensures input_text is always str
        input_text = input_text.strip().lower()

        # Check all known commands
        all_commands: dict[str, str] = {
            **self.CLIPBOARD_COMMANDS,
            **self.SYSTEM_COMMANDS,
        }
        if input_text in all_commands:
            return True

        # If it starts with '/', it's a transformation rule
        # Default to command for unrecognized input
        return not input_text.startswith("/")

    def process_command(self, command: str) -> CommandResult:
        """Process interactive command and return result.

        Args:
            command: Command string to process

        Returns:
            CommandResult with operation result

        Raises:
            ValidationError: If command is invalid
        """
        if not isinstance(command, str):
            raise ValidationError(
                f"Command must be a string, got {type(command).__name__}",
                {"command_type": type(command).__name__},
            )

        command = command.strip().lower()

        try:
            # Handle system commands
            if command in ["help", "h", "?"]:
                return self._handle_help_command()

            if command in ["quit", "q", "exit"]:
                return CommandResult(success=True, message="Goodbye!", should_continue=False)

            # Handle clipboard commands
            if command in ["refresh", "reload", "replace"]:
                return self._handle_refresh_command()

            if command == "status":
                return self._handle_status_command()

            if command == "clear":
                return self._handle_clear_command()

            if command == "copy":
                return self._handle_copy_command()

            if command in ["commands", "cmd"]:
                return self._handle_commands_command()

            # Unknown command
            return CommandResult(
                success=False,
                message=f"Unknown command: {command}. Type 'commands' for available commands.",
            )

        except Exception as e:
            return CommandResult(success=False, message=f"Command execution failed: {e}")

    def _handle_refresh_command(self) -> CommandResult:
        """Handle clipboard refresh command."""
        try:
            new_content: str = self.session.refresh_from_clipboard()
            char_count: int = len(new_content)
            display_text: str = new_content[:50] + "..." if len(new_content) > 50 else new_content

            return CommandResult(
                success=True,
                message=f"[SUCCESS] Refreshed from clipboard ({char_count} chars)\nNew text: '{display_text}'",
            )

        except Exception as e:
            return CommandResult(
                success=False, message=f"[ERROR] Failed to refresh from clipboard: {e}"
            )

    def _handle_status_command(self) -> CommandResult:
        """Handle status command."""
        try:
            # Get current clipboard content for real-time display
            try:
                current_clipboard: str = self.session.io_manager.get_clipboard_text()
                clipboard_display: str = (
                    current_clipboard[:100] + "..."
                    if len(current_clipboard) > 100
                    else current_clipboard
                )
                clipboard_length: int = len(current_clipboard)

                # Show if clipboard differs from session text
                session_different: bool = current_clipboard != self.session.current_text
                clipboard_info: str = (
                    f"   Current clipboard: '{clipboard_display}' ({clipboard_length} chars)"
                )
                # if session_different:
                #     clipboard_info += " [DIFFERENT FROM SESSION]"

            except Exception:
                clipboard_info = "   Current clipboard: [Unable to access clipboard]"

            status: SessionState = self.session.get_status_info()
            # display_text: str = self.session.get_display_text(100)
            # time_since: str = self.session.get_time_since_update()

            lines: list[str] = [
                "[STATUS]:",
                # f"   Text: '{display_text}'",
                # f"   Length: {status.character_count} characters",
                # f"   Source: {status.text_source.value if hasattr(status.text_source, 'value') else status.text_source}",
                # f"   Last updated: {time_since}",
                clipboard_info,
                f"   Auto-detection: {'ON' if status.auto_detection_enabled else 'OFF'}",
                f"   Monitor active: {'Yes' if status.clipboard_monitor_active else 'No'}",
            ]

            return CommandResult(success=True, message="\n".join(lines))

        except Exception as e:
            return CommandResult(success=False, message=f"[ERROR] Failed to get status: {e}")

    def _handle_clear_command(self) -> CommandResult:
        """Handle clear command."""
        try:
            self.session.clear_working_text()
            return CommandResult(success=True, message="[SUCCESS] Working text cleared.")

        except Exception as e:
            return CommandResult(success=False, message=f"[ERROR] Failed to clear text: {e}")

    def _handle_copy_command(self) -> CommandResult:
        """Handle copy command."""
        try:
            if not self.session.current_text:
                return CommandResult(
                    success=False,
                    message="[ERROR] No text to copy. Use 'refresh' to load text from clipboard.",
                )

            self.session.io_manager.set_output_text(self.session.current_text)
            char_count: int = len(self.session.current_text)

            return CommandResult(
                success=True,
                message=f"[SUCCESS] Copied {char_count} characters to clipboard.",
            )

        except Exception as e:
            return CommandResult(
                success=False, message=f"[ERROR] Failed to copy to clipboard: {e}"
            )

    def _handle_commands_command(self) -> CommandResult:
        """Handle commands list command."""
        lines: list[str] = [
            "[HELP] Available Interactive Commands:",
            "",
            "Clipboard Operations:",
        ]

        for cmd, desc in self.CLIPBOARD_COMMANDS.items():
            lines.append(f"  {cmd:<12} - {desc}")

        lines.extend(
            [
                "",
                "System Commands:",
            ]
        )

        for cmd, desc in self.SYSTEM_COMMANDS.items():
            lines.append(f"  {cmd:<12} - {desc}")

        lines.extend(
            [
                "",
                "[TIP] Type '/rule' to apply transformation rules (e.g., '/t/l' for trim + lowercase)",
            ]
        )

        return CommandResult(success=True, message="\n".join(lines))

    def _handle_help_command(self) -> CommandResult:
        """Handle help command - this will be handled by ApplicationInterface."""
        return CommandResult(
            success=True,
            message="SHOW_HELP",  # Special message to trigger help display
            should_continue=True,
        )
