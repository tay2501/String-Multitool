"""
Main application interface for String_Multitool.

This module provides the primary ApplicationInterface class that coordinates
all application components and handles command-line execution.
"""

from __future__ import annotations

import sys
from typing import Any, Optional

from .core.config import ConfigurationManager
from .core.transformations import TextTransformationEngine
from .exceptions import ValidationError
from .io.manager import InputOutputManager
from .utils.logger import get_logger


class ApplicationInterface:
    """Main application interface coordinating all String_Multitool components."""

    def __init__(
        self,
        config_manager: ConfigurationManager,
        transformation_engine: TextTransformationEngine,
        io_manager: InputOutputManager,
        crypto_manager: Optional[Any] = None,
        daemon_mode: Optional[Any] = None,
        hotkey_mode: Optional[Any] = None,
        system_tray_mode: Optional[Any] = None,
    ) -> None:
        """Initialize application interface with dependency injection."""
        if config_manager is None:
            raise ValidationError("Configuration manager cannot be None")
        if transformation_engine is None:
            raise ValidationError("Transformation engine cannot be None")
        if io_manager is None:
            raise ValidationError("IO manager cannot be None")

        self.config_manager = config_manager
        self.transformation_engine = transformation_engine
        self.io_manager = io_manager
        self.crypto_manager = crypto_manager
        self.daemon_mode = daemon_mode
        self.hotkey_mode = hotkey_mode
        self.system_tray_mode = system_tray_mode

        self.logger = get_logger(__name__)

        # Set crypto manager in transformation engine if available
        if self.crypto_manager is not None:
            self.transformation_engine.set_crypto_manager(self.crypto_manager)
            self.logger.debug("Cryptography manager set in transformation engine")
        else:
            self.logger.debug(
                "No cryptography manager available - encryption/decryption will be disabled"
            )

    def run(self) -> None:
        """Main application entry point."""
        args = sys.argv[1:] if len(sys.argv) > 1 else []

        if not args:
            self._run_interactive_mode()
        elif args[0] == "help":
            self.display_help()
        else:
            self._run_rule_mode(args[0])

    def _run_interactive_mode(self) -> None:
        """Run interactive mode."""
        from .modes.interactive import InteractiveSession, CommandProcessor

        print("Interactive mode")
        print(
            "Type 'help' for available transformation rules or 'commands' for interactive commands."
        )
        print(
            "Enter transformation rules (e.g. '/t/l' for trim + lowercase) or commands."
        )
        print("Type 'quit' or 'exit' to leave.\n")

        # Initialize interactive session
        session = InteractiveSession(self.io_manager, self.transformation_engine)
        processor = CommandProcessor(session)

        try:
            while True:
                try:
                    user_input = input("> ").strip()
                    if not user_input:
                        continue

                    # Check if it's a command or transformation rule
                    if processor.is_command(user_input):
                        result = processor.process_command(user_input)
                        print(result.message)

                        if not result.should_continue:
                            if result.message == "SWITCH_TO_DAEMON":
                                print("Switching to daemon mode...")
                                if self.daemon_mode:
                                    self.daemon_mode.start_monitoring()
                                else:
                                    print("Daemon mode not available.")
                            break
                        elif result.message == "SHOW_HELP":
                            self.display_help()
                    else:
                        # It's a transformation rule
                        try:
                            # Get current clipboard text
                            input_text = self.io_manager.get_input_text()
                            if not input_text:
                                print(
                                    "[WARNING] No input text available. Try 'refresh' to load from clipboard."
                                )
                                continue

                            # Apply transformation
                            result_text = (
                                self.transformation_engine.apply_transformations(
                                    input_text, user_input
                                )
                            )

                            # Copy result to clipboard
                            self.io_manager.set_output_text(result_text)

                            # Show result
                            display_text = (
                                result_text[:100] + "..."
                                if len(result_text) > 100
                                else result_text
                            )
                            print(
                                f"[SUCCESS] Result copied to clipboard: '{display_text}'"
                            )

                        except ValidationError as e:
                            print(f"[ERROR] Transformation failed: {e}")
                        except Exception as e:
                            print(f"[ERROR] Unexpected error: {e}")

                except KeyboardInterrupt:
                    print("\n[INFO] Use 'quit' or 'exit' to leave interactive mode.")
                except EOFError:
                    print("\nGoodbye!")
                    break

        finally:
            # Cleanup
            session.cleanup()

    def _run_rule_mode(self, rule: str) -> None:
        """Run rule-based transformation mode."""
        input_text = self.io_manager.get_input_text()
        result = self.transformation_engine.apply_transformations(input_text, rule)
        self.io_manager.set_output_text(result)

    def display_help(self) -> None:
        """Display help information."""
        print("String_Multitool Help")
        print("=" * 50)

        # Get available transformation rules
        try:
            rules = self.transformation_engine.get_available_rules()
            if rules:
                print("\nAvailable transformation rules:")
                for rule_name, rule in rules.items():
                    print(f"  /{rule_name:<8} - {rule.description}")
                    if rule.example:
                        print(f"            Example: {rule.example}")
            else:
                print("\nNo transformation rules available.")
        except Exception as e:
            print(f"\nError loading rules: {e}")

        print("\nUsage:")
        print("  python String_Multitool.py                 - Interactive mode")
        print("  python String_Multitool.py /rule           - Apply rule to clipboard")
        print("  python String_Multitool.py help            - Show this help")
        print("\nIn interactive mode, type 'commands' for available commands.")


def main() -> None:
    """Main entry point function."""
    from .application_factory import ApplicationFactory

    app = ApplicationFactory.create_application()
    app.run()
