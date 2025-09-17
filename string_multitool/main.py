"""
Main application interface for String_Multitool.

This module provides the primary ApplicationInterface class that coordinates
all application components and handles command-line execution.
"""

from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.crypto import CryptographyManager

from .exceptions import ValidationError
from .io.manager import InputOutputManager
from .models.config import ConfigurationManager
from .models.transformations import TextTransformationEngine
from .utils.unified_logger import get_logger

logger = get_logger(__name__)


class ApplicationInterface:
    """Main application interface coordinating all String_Multitool components."""

    def __init__(
        self,
        config_manager: ConfigurationManager,
        transformation_engine: TextTransformationEngine,
        io_manager: InputOutputManager,
        crypto_manager: CryptographyManager | None = None,
    ) -> None:
        """Initialize application interface with dependency injection."""
        try:
            self.config_manager = config_manager
            self.transformation_engine = transformation_engine
            self.io_manager = io_manager
            self.crypto_manager = crypto_manager
            self.silent_mode = False

            self.logger = get_logger(__name__)

            # Validate dependencies using EAFP - avoid calling methods that may block
            self.config_manager.load_transformation_rules()
            self.transformation_engine.get_available_rules()
            # Skip io_manager validation to avoid stdin blocking in tests
        except (AttributeError, TypeError) as e:
            raise ValidationError(f"Invalid dependency injection: {e}") from e

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
        # Parse command line arguments using argparse best practices
        parser = self._create_argument_parser()
        args = parser.parse_args()

        # Set silent mode
        self.silent_mode = args.silent

        # Handle different modes based on arguments
        if args.help_cmd:
            self.display_help()
        elif args.rule:
            self._run_rule_mode(args.rule, args.args)
        else:
            self._run_interactive_mode()

    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser following best practices."""
        parser = argparse.ArgumentParser(
            prog="String_Multitool.py",
            description="Advanced text transformation tool with pipe support and RSA encryption",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  String_Multitool.py                     # Interactive mode
  String_Multitool.py /t/l                # Apply trim + lowercase to clipboard
  String_Multitool.py -s /u               # Silent mode, uppercase only
  echo "text" | String_Multitool.py /t/l  # Apply to piped text
  String_Multitool.py help                # Show detailed help
            """,
            add_help=False,  # Custom help handling
        )

        # Add silent mode option following best practices
        parser.add_argument(
            "-s",
            "--silent",
            action="store_true",
            help="Silent mode - show only transformation result",
        )

        # Add help option
        parser.add_argument(
            "--help",
            "-h",
            action="store_true",
            dest="help_cmd",
            help="Show this help message and exit",
        )

        # Positional arguments for transformation rule and parameters
        parser.add_argument(
            "rule", nargs="?", default=None, help="Transformation rule (e.g., /t/l, /u, help)"
        )
        parser.add_argument(
            "args",
            nargs="*",
            help="Additional arguments for the transformation rule (e.g., /S '+' where '+' is the separator)",
        )

        return parser

    def _run_interactive_mode(self) -> None:
        """Run interactive mode."""
        from .models.interactive import CommandProcessor, InteractiveSession

        # Only show messages in non-silent mode
        if not self.silent_mode:
            logger.info("Interactive mode")
            logger.info(
                "Type 'help' for available transformation rules or 'commands' for interactive commands."
            )
            logger.info(
                "Enter transformation rules (e.g. '/t/l' for trim + lowercase) or commands."
            )
            logger.info("Type 'quit' or 'exit' to leave.\n")

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
                        logger.info(result.message)

                        if not result.should_continue:
                            break
                        elif result.message == "SHOW_HELP":
                            self.display_help()
                    else:
                        # It's a transformation rule
                        try:
                            # Get current clipboard text
                            input_text = self.io_manager.get_input_text()
                            if not input_text:
                                logger.warning(
                                    "No input text available. Try 'refresh' to load from clipboard."
                                )
                                continue

                            # Apply transformation
                            result_text = self.transformation_engine.apply_transformations(
                                input_text, user_input
                            )

                            # Handle output based on mode
                            if self.silent_mode:
                                # Silent mode: only show the result, no clipboard copy
                                logger.info(result_text)
                            else:
                                # Normal mode: copy to clipboard and show success message
                                self.io_manager.set_output_text(result_text)
                                display_text = (
                                    result_text[:100] + "..."
                                    if len(result_text) > 100
                                    else result_text
                                )
                                logger.info(f"Result copied to clipboard: '{display_text}'")

                        except (ValidationError, Exception) as e:
                            error_type = (
                                "Transformation"
                                if isinstance(e, ValidationError)
                                else "Unexpected"
                            )
                            logger.error(f"{error_type} error: {e}")
                        except Exception as e:
                            logger.error(f"Transformation error: {e}")

                except KeyboardInterrupt:
                    logger.info("\nUse 'quit' or 'exit' to leave interactive mode.")
                except EOFError:
                    logger.info("\nGoodbye!")
                    break

        finally:
            # Cleanup
            session.cleanup()

    def _run_rule_mode(self, rule: str, rule_args: list[str] | None = None) -> None:
        """Run rule-based transformation mode."""
        # Handle help command
        if rule == "help":
            self.display_help()
            return

        # Windows CMD compatibility: normalize double slashes to single slashes
        # This handles cases where Windows converts /t to T: in command line
        if rule and "//" in rule:
            rule = rule.replace("//", "/")

        # Combine rule with arguments if provided (e.g., "/S '+'" becomes "/S '+'")
        combined_rule = f"{rule} {' '.join(repr(arg) for arg in rule_args)}" if rule_args else rule

        input_text = self.io_manager.get_input_text()
        result = self.transformation_engine.apply_transformations(input_text, combined_rule)

        if self.silent_mode:
            # Silent mode: only output the transformation result, no clipboard copying
            logger.info(result)
        else:
            # Normal mode: output to stdout for pipe chaining AND copy to clipboard
            logger.info(result)
            self.io_manager.set_output_text(result)

    def display_help(self) -> None:
        """Display help information."""
        logger.info("String_Multitool Help")
        logger.info("=" * 50)

        # Get available transformation rules
        try:
            rules = self.transformation_engine.get_available_rules()
            if rules:
                logger.info("\nAvailable transformation rules:")
                for rule_name, rule in rules.items():
                    logger.info(f"  /{rule_name:<8} - {rule.description}")
                    if rule.example:
                        logger.info(f"            Example: {rule.example}")
            else:
                logger.info("\nNo transformation rules available.")
        except Exception as e:
            logger.error(f"\nError loading rules: {e}")

        logger.info("\nUsage:")
        logger.info("  python String_Multitool.py                 - Interactive mode")
        logger.info("  python String_Multitool.py /rule           - Apply rule to clipboard")
        logger.info("  python String_Multitool.py help            - Show this help")
        logger.info("\nIn interactive mode, type 'commands' for available commands.")


def main() -> None:
    """Main entry point function."""
    from .application_factory import ApplicationFactory

    app = ApplicationFactory.create_application()
    app.run()
