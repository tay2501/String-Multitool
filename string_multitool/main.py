"""
Main application interface for String_Multitool.

This module provides the primary application interface and coordinates
all components to deliver the complete functionality.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from .core.dependency_injection import ServiceRegistry, inject, injectable
from .core.types import (
    CommandResult,
    ConfigManagerProtocol,
    CryptoManagerProtocol,
    TextSource,
    TransformationEngineProtocol,
    TransformationRuleType,
)
from .exceptions import (
    ClipboardError,
    ConfigurationError,
    CryptographyError,
    StringMultitoolError,
    TransformationError,
    ValidationError,
)
from .io.manager import InputOutputManager
from .modes.daemon import DaemonMode
from .modes.hotkey import HotkeyMode
from .modes.interactive import CommandProcessor, InteractiveSession

# Import logging utilities
from .utils.logger import get_logger, log_debug, log_error, log_info, log_warning


@injectable
class ApplicationInterface:
    """Main application interface and user interaction handler.

    This class coordinates all components and provides the main entry
    points for different application modes. Uses dependency injection
    for loose coupling and testability.
    """

    def __init__(
        self,
        config_manager: ConfigManagerProtocol | None = None,
        transformation_engine: TransformationEngineProtocol | None = None,
        io_manager: InputOutputManager | None = None,
    ) -> None:
        """Initialize application interface with dependency injection.

        Args:
            config_manager: Configuration manager (injected if None)
            transformation_engine: Transformation engine (injected if None)
            io_manager: I/O manager (injected if None)

        Raises:
            ConfigurationError: If initialization fails
        """
        try:
            # Use dependency injection to get services
            self.config_manager = config_manager or inject(ConfigManagerProtocol)
            self.transformation_engine = transformation_engine or inject(
                TransformationEngineProtocol
            )
            self.io_manager = io_manager or inject(InputOutputManager)
            self._logger = get_logger(__name__)

            # Get optional crypto manager
            try:
                self.crypto_manager = inject(CryptoManagerProtocol)
                if self.crypto_manager:
                    self.transformation_engine.set_crypto_manager(self.crypto_manager)
            except Exception as e:
                self._logger.error(f"[ERROR] Cryptography not available: {e}")
                self.crypto_manager = None

            # Initialize daemon mode (injected) - skip if all dependencies provided
            if config_manager and transformation_engine and io_manager:
                # Manual initialization for testing - create minimal daemon mode
                try:
                    self.daemon_mode = DaemonMode(
                        transformation_engine=transformation_engine,
                        config_manager=config_manager,
                    )
                except Exception:
                    self.daemon_mode = None
                self.hotkey_mode = None  # Skip hotkey mode in testing
            else:
                # Use DI for production
                self.daemon_mode = inject(DaemonMode)

                # Initialize hotkey mode (optional, injected)
                try:
                    self.hotkey_mode = inject(HotkeyMode)
                except Exception:
                    self.hotkey_mode = None

        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize application: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def run_interactive_mode(self, input_text: str) -> None:
        """Run application in interactive mode.

        Args:
            input_text: Initial input text

        Raises:
            StringMultitoolError: If interactive mode fails
        """
        try:
            # Create interactive session (injected)
            session: InteractiveSession = inject(InteractiveSession)
            command_processor: CommandProcessor = inject(CommandProcessor)

            # Initialize session with input text
            text_source: str = "pipe" if not sys.stdin.isatty() else "clipboard"
            session.initialize_with_text(input_text, text_source)

            # Display initial status
            self._display_interactive_header(session)

            # Main interactive loop
            while True:
                try:
                    # Check for clipboard changes (auto-detection is always enabled)
                    new_content: str | None = session.check_clipboard_changes()
                    if new_content is not None and new_content != session.current_text:
                        # Display clipboard content preview
                        display_content: str = (
                            new_content[:100] + "..."
                            if len(new_content) > 100
                            else new_content
                        )
                        # Replace newlines with visible characters for better display
                        display_content = (
                            display_content.replace("\n", "\\n")
                            .replace("\r", "\\r")
                            .replace("\t", "\\t")
                        )

                    # Get user input
                    try:
                        # Check if this is pipe input and no more data available
                        if text_source == "pipe" and not sys.stdin.isatty():
                            # For pipe input, try to read from stdin, but if EOF immediately,
                            # switch to terminal input for interactive mode
                            try:
                                user_input: str = input("Rules: ").strip()
                            except EOFError:
                                self._logger.info(
                                    "\n[INFO] Pipe input received. Switching to interactive mode..."
                                )
                                self._logger.info(
                                    "You can now enter transformation rules (e.g., /u for uppercase) or commands."
                                )
                                self._logger.info(
                                    "Type 'help' for available rules, 'status' to see current text, or 'quit' to exit."
                                )

                                # Switch to terminal input by reopening stdin
                                import os

                                if os.name == "nt":  # Windows
                                    try:
                                        sys.stdin.close()
                                        sys.stdin = open("CON", "r")
                                    except:
                                        # Fallback: continue with current stdin
                                        pass
                                else:  # Unix-like systems
                                    try:
                                        sys.stdin.close()
                                        sys.stdin = open("/dev/tty", "r")
                                    except:
                                        # Fallback: continue with current stdin
                                        pass

                                # Update text_source to indicate we're now interactive
                                text_source = "clipboard"

                                # Try to get input from terminal
                                try:
                                    user_input: str = input("Rules: ").strip()
                                except EOFError:
                                    self._logger.error(
                                        "Unable to switch to interactive input. Exiting..."
                                    )
                                    break
                        else:
                            user_input: str = input("Rules: ").strip()
                    except EOFError:
                        self._logger.info("\nGoodbye!")
                        break

                    if not user_input:
                        self._logger.info("Please enter a rule, command, or 'help'")
                        continue

                    # Process command or transformation rule
                    if command_processor.is_command(user_input):
                        result: CommandResult = command_processor.process_command(
                            user_input
                        )

                        if result.message == "SHOW_HELP":
                            self.display_help()
                            continue

                        if result.message == "SWITCH_TO_DAEMON":
                            self._logger.info("[MODE] Switching to daemon mode...")
                            # Clean up interactive session
                            session.cleanup()
                            # Start daemon mode
                            self.run_daemon_mode()
                            return

                        self._logger.info(result.message)

                        if result.updated_text is not None:
                            # Text was updated by command
                            pass

                        if not result.should_continue:
                            break

                    else:
                        # Handle transformation rules
                        try:
                            # Always get fresh clipboard content for transformation rules
                            # unless the input came from pipe initially
                            if session.text_source != TextSource.PIPE:
                                try:
                                    fresh_content: str = (
                                        self.io_manager.get_clipboard_text()
                                    )
                                    # Show if clipboard content changed
                                    if fresh_content != session.current_text:
                                        display_old: str = (
                                            session.current_text[:30] + "..."
                                            if len(session.current_text) > 30
                                            else session.current_text
                                        )
                                        display_new: str = (
                                            fresh_content[:30] + "..."
                                            if len(fresh_content) > 30
                                            else fresh_content
                                        )
                                        self._logger.debug(
                                            f"'{display_old}' -> '{display_new}'",
                                        )
                                        session.update_working_text(
                                            fresh_content, "clipboard"
                                        )
                                except Exception:
                                    # If clipboard access fails, use current text
                                    pass

                            # Apply transformation
                            transformation_result: str = (
                                self.transformation_engine.apply_transformations(
                                    session.current_text, user_input
                                )
                            )

                            # Copy result to clipboard
                            self.io_manager.set_output_text(transformation_result)

                            # Display result
                            display_result: str = (
                                transformation_result[:100] + "..."
                                if len(transformation_result) > 100
                                else transformation_result
                            )
                            self._logger.info(f"'{display_result}'")

                        except (ValidationError, TransformationError) as e:
                            self._logger.error(f"[ERROR] Transformation error: {e}")
                        except Exception as e:
                            raise StringMultitoolError(
                                f"Unexpected interactive transformation error: {e}",
                                {"error_type": type(e).__name__},
                            ) from e

                except KeyboardInterrupt:
                    self._logger.info("\nGoodbye!")
                    break
                except Exception as e:
                    raise StringMultitoolError(
                        f"Interactive session error: {e}",
                        {"error_type": type(e).__name__},
                    ) from e

            # Cleanup
            session.cleanup()

        except Exception as e:
            raise StringMultitoolError(
                f"Interactive mode failed: {e}", {"error_type": type(e).__name__}
            ) from e

    def run_command_mode(self, rule_string: str) -> None:
        """Run application in command mode with specified rules.

        Args:
            rule_string: Rule string to apply

        Raises:
            StringMultitoolError: If command mode fails
        """
        try:
            # Get input text
            input_text: str = self.io_manager.get_input_text()

            # Apply transformations
            result: str = self.transformation_engine.apply_transformations(
                input_text, rule_string
            )

            # Output result
            self.io_manager.set_output_text(result)

            # Display applied rules and result for user feedback
            display_result: str = result[:100] + "..." if len(result) > 100 else result
            self._logger.info(f"Applied: {rule_string}")
            self._logger.info(f"Result: '{display_result}'")

        except (ValidationError, TransformationError, ClipboardError) as e:
            self._logger.error(f"[ERROR] Error: {e}")
            sys.exit(1)
        except Exception as e:
            raise StringMultitoolError(
                f"Command mode execution failed: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def run_hotkey_mode(self) -> None:
        """Run application in hotkey mode.

        Raises:
            StringMultitoolError: If hotkey mode fails
        """
        try:
            self._logger.info("Starting hotkey mode...")

            # Initialize hotkey mode if not already done
            if self.hotkey_mode is None:
                self.hotkey_mode = HotkeyMode(
                    self.io_manager, self.transformation_engine, self.config_manager
                )

            # Run hotkey mode (blocking)
            self.hotkey_mode.run()

        except KeyboardInterrupt:
            self._logger.info("Hotkey mode stopped by user")
        except ConfigurationError as e:
            self._logger.error(f"Hotkey configuration error: {e}")
            raise
        except Exception as e:
            self._logger.error(f"Hotkey mode error: {e}")
            raise StringMultitoolError(
                f"Hotkey mode failed: {e}", {"error_type": type(e).__name__}
            ) from e

    def run_daemon_mode(self) -> None:
        """Run application in daemon mode.

        Raises:
            StringMultitoolError: If daemon mode fails
        """
        try:
            self._logger.info("String_Multitool - Daemon Mode")

            # Show available presets
            daemon_config_path: Path = Path("config/daemon_config.json")
            if daemon_config_path.exists():
                try:
                    with open(daemon_config_path, "r", encoding="utf-8") as f:
                        config: dict[str, Any] = json.load(f)
                        presets: dict[str, Any] = config.get(
                            "auto_transformation", {}
                        ).get("rule_presets", {})

                        if presets:
                            self._logger.info("Available presets:")
                            for name, rules in presets.items():
                                if isinstance(rules, str):
                                    self._logger.info(f"  {name}: {rules}")
                                else:
                                    self._logger.info(f"  {name}: {' -> '.join(rules)}")
                except Exception as e:
                    raise ConfigurationError(
                        f"Failed to load daemon config: {e}",
                        {"error_type": type(e).__name__},
                    ) from e

            self._logger.info("Commands:")
            self._logger.info("  preset <n>     - Set transformation preset")
            self._logger.info("  rules <rules>     - Set custom transformation rules")
            self._logger.info(
                "  /rule             - Set transformation rule directly (e.g., '/t/l')"
            )
            self._logger.info("  start             - Start daemon monitoring")
            self._logger.info("  stop              - Stop daemon monitoring")
            self._logger.info("  status            - Show daemon status")
            self._logger.info("  interactive       - Switch to interactive mode")
            self._logger.info("  quit              - Exit daemon mode")

            while True:
                try:
                    try:
                        user_input: str = input("Daemon> ").strip()
                    except EOFError:
                        self._logger.info("\nGoodbye!")
                        break

                    if not user_input:
                        continue

                    # Check if input is a transformation rule (starts with /)
                    if user_input.startswith("/"):
                        try:
                            # Validate rules by parsing them
                            # parsed_rules: list[tuple[str, list[str]]] = self.transformation_engine.parse_rule_string(user_input)
                            rule_list: list[str] = [
                                user_input
                            ]  # Store as single rule string for sequential application
                            # Use the proper method to set rules
                            if self.daemon_mode:
                                self.daemon_mode.set_transformation_rules(rule_list)
                        except Exception as e:
                            raise ValidationError(
                                f"Invalid daemon preset rule string: {e}",
                                {"error_type": type(e).__name__},
                            ) from e
                        continue

                    parts: list[str] = user_input.split()
                    command: str = parts[0].lower()

                    if command in ["quit", "q", "exit"]:
                        if self.daemon_mode and self.daemon_mode.is_running:
                            self.daemon_mode.stop()
                        self._logger.info("Goodbye!")
                        break

                    elif command == "preset":
                        if len(parts) < 2:
                            self._logger.info("Usage: preset <n>")
                            continue

                        preset_name: str = parts[1]
                        try:
                            if self.daemon_mode:
                                self.daemon_mode.set_preset(preset_name)
                            else:
                                self._logger.error(
                                    "[ERROR] Daemon mode not available"
                                )
                        except (ValidationError, ConfigurationError) as e:
                            self._logger.error(f"[ERROR] {e}")

                    elif command == "rules":
                        if len(parts) < 2:
                            self._logger.info("Usage: rules <rule_string>, Example: rules /t/l")
                            continue

                        rule_string: str = " ".join(parts[1:])
                        try:
                            # Validate rules by parsing them
                            # parsed_daemon_rules: list[tuple[str, list[str]]] = self.transformation_engine.parse_rule_string(rule_string)
                            daemon_rule_list: list[str] = [
                                rule_string
                            ]  # Store as single rule string for sequential application
                            if self.daemon_mode:
                                self.daemon_mode.set_transformation_rules(
                                    daemon_rule_list
                                )
                            else:
                                self._logger.warning("[WARNING] Daemon mode not available")
                        except Exception as e:
                            raise ValidationError(
                                f"Invalid daemon custom rule string: {e}",
                                {"error_type": type(e).__name__},
                            ) from e

                    elif command == "start":
                        try:
                            if not self.daemon_mode:
                                self._logger.warning("[WARNING] Daemon mode not available")
                            elif self.daemon_mode.is_running:
                                self._logger.info("[DAEMON] Already running")
                            else:
                                # Start daemon monitoring without blocking command input
                                self.daemon_mode.start_monitoring()
                                self._logger.debug("[DAEMON] Check interval: 1.0s")
                                self._logger.info(
                                    f"[DAEMON] Active transformation: {' -> '.join(self.daemon_mode.active_rules)}",
                                )
                                self._logger.debug(
                                    "[DAEMON] Monitoring started in background"
                                )
                        except (ValidationError, TransformationError) as e:
                            self._logger.warning(f"[WARNING] {e}")

                    elif command == "stop":
                        try:
                            if not self.daemon_mode:
                                self._logger.warning("[WARNING] Daemon mode not available")
                            else:
                                self.daemon_mode.stop()
                        except TransformationError as e:
                            self._logger.warning(f"[WARNING] {e}")

                    elif command == "status":
                        if not self.daemon_mode:
                            self._logger.warning("[WARNING] Daemon mode not available")
                        else:
                            status: dict[str, Any] = self.daemon_mode.get_status()
                            self._logger.info(
                                f"Status: {'Running' if status['running'] else 'Stopped'}",
                            )
                            self._logger.info(
                                f"Active rules: {' -> '.join(status['active_rules']) if status['active_rules'] else 'None'}",
                            )
                            self._logger.info(
                                f"Active preset: {status['active_preset'] or 'None'}",
                            )
                            self._logger.info(
                                f"Transformations applied: {status['stats']['transformations_applied']}",
                            )
                            if status.get("runtime"):
                                self._logger.info(f"Runtime: {status['runtime']}")

                    elif command == "interactive":
                        self._logger.info("[MODE] Switching to interactive mode...")
                        self._logger.info(
                            "[MODE] Daemon mode will exit and interactive mode will start."
                            "   Daemon mode will exit and interactive mode will start.",
                        )
                        # Stop daemon if running
                        if self.daemon_mode and self.daemon_mode.is_running:
                            self.daemon_mode.stop()
                        # Start interactive mode
                        try:
                            input_text: str = self.io_manager.get_input_text()
                            self.run_interactive_mode(input_text)
                        except Exception as e:
                            raise StringMultitoolError(
                                f"Failed to start interactive mode from daemon: {e}",
                                {"error_type": type(e).__name__},
                            ) from e
                        return

                    elif command == "help":
                        self._logger.info("Daemon Mode Commands:")
                        self._logger.info("  preset <n>     - Set transformation preset")
                        self._logger.info(
                            "  rules <rules>     - Set custom transformation rules",
                        )
                        self._logger.info(
                            "  /rule             - Set transformation rule directly (e.g., '/t/l')",
                        )
                        self._logger.info(
                            "  start             - Start daemon monitoring"
                        )
                        self._logger.info("  stop              - Stop daemon monitoring")
                        self._logger.info("  status            - Show daemon status")
                        self._logger.info(
                            "  interactive       - Switch to interactive mode"
                        )
                        self._logger.info("  quit              - Exit daemon mode")

                    else:
                        self._logger.warning(
                            f"Unknown command: {command}. Type 'help' for available commands.",
                        )

                except KeyboardInterrupt:
                    if self.daemon_mode and self.daemon_mode.is_running:
                        self.daemon_mode.stop()
                    self._logger.info("\nGoodbye!")
                    break
                except Exception as e:
                    raise StringMultitoolError(
                        f"Unexpected daemon error: {e}",
                        {"error_type": type(e).__name__},
                    ) from e

        except Exception as e:
            raise StringMultitoolError(
                f"Daemon mode failed: {e}", {"error_type": type(e).__name__}
            ) from e

    def display_help(self) -> None:
        """Display comprehensive help information."""
        try:
            available_rules: dict[str, Any] = (
                self.transformation_engine.get_available_rules()
            )
            # rules_config: dict[str, Any] = self.config_manager.load_transformation_rules()

            self._logger.info("String_Multitool - Advanced Text Transformation Tool")
            self._logger.info("=" * 55)
            self._logger.info("Usage:")
            self._logger.info(
                "  String_Multitool.py                    # Interactive mode (clipboard input)",
            )
            self._logger.info(
                "  String_Multitool.py /t/l               # Apply trim + lowercase to clipboard",
            )
            self._logger.info(
                "  String_Multitool.py --daemon           # Daemon mode (continuous monitoring)",
            )
            self._logger.info(
                "  String_Multitool.py --hotkey           # Hotkey mode (global keyboard shortcuts)",
            )
            self._logger.info(
                "  echo 'text' | String_Multitool.py      # Interactive mode (pipe input)",
            )
            self._logger.info(
                "  echo 'text' | String_Multitool.py /t/l # Apply trim + lowercase to piped text",
            )
            self._logger.info("Available Transformation Rules:")
            self._logger.info("-" * 35)

            # Display rules by category
            category_display_names: dict[TransformationRuleType, str] = {
                TransformationRuleType.BASIC: "Basic Transformations",
                TransformationRuleType.CASE: "Case Transformations",
                TransformationRuleType.STRING_OPS: "String Operations",
                TransformationRuleType.ENCRYPTION: "Encryption/Decryption",
                TransformationRuleType.ADVANCED: "Advanced Rules (with arguments)",
            }

            # Group rules by category
            rules_by_category: dict[Any, list[tuple[str, Any]]] = {}
            for rule_key, rule in available_rules.items():
                category: Any = rule.rule_type
                if category not in rules_by_category:
                    rules_by_category[category] = []
                rules_by_category[category].append((rule_key, rule))

            # Display each category
            for category, rules in rules_by_category.items():
                category_name: str = category_display_names.get(category, str(category))
                self._logger.info(f"\n{category_name}:")

                for rule_key, rule in rules:
                    if rule.requires_args:
                        self._logger.info(f"  /{rule_key} '<args>' - {rule.name}")
                    else:
                        self._logger.info(f"  /{rule_key} - {rule.name}")
                    self._logger.info(f"    Example: {rule.example}")

            self._logger.info("Usage Examples:")
            self._logger.info("  /t                        # Trim whitespace")
            self._logger.info("  /t/l                      # Trim then lowercase")
            self._logger.info("  /enc                      # Encrypt with RSA")
            self._logger.info("  /dec                      # Decrypt with RSA")
            self._logger.info("  /S '-'                    # Slugify with hyphen")
            self._logger.info("  /r 'old' 'new'            # Replace 'old' with 'new'")

            if self.crypto_manager:
                self._logger.info("RSA Encryption Information:")
                self._logger.info("Key Size: RSA-4096")
                self._logger.info("AES Encryption: AES-256-CBC")
                self._logger.info("Hash Algorithm: SHA256")
                self._logger.info("Keys Location: rsa/")
                self._logger.info("Auto-generated on first use")
                self._logger.info("Supports unlimited text size")

            self._logger.info("Daemon Mode:")
            self._logger.info("String_Multitool.py --daemon")
            self._logger.info("Continuous clipboard monitoring")
            self._logger.info("Automatic transformation application")
            self._logger.info("Background operation")
            self._logger.info("Real-time clipboard processing")

        except Exception as e:
            raise StringMultitoolError(
                f"Failed to display help: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def _display_interactive_header(self, session: InteractiveSession) -> None:
        """Display interactive mode header with current status."""
        try:
            status: Any = session.get_status_info()
            display_text: str = session.get_display_text()

            self._logger.debug("String_Multitool - Interactive Mode")
            self._logger.info(
                f"'{display_text}'",
            )
            self._logger.debug(
                f"Input text: '{display_text}' ({status.character_count} chars, from {status.text_source.value if hasattr(status.text_source, 'value') else status.text_source})",
            )
        except Exception as e:
            raise StringMultitoolError(
                f"Failed to display interactive header: {e}",
                {"error_type": type(e).__name__},
            ) from e

    def run(self) -> None:
        """Main application entry point.

        Raises:
            StringMultitoolError: If application execution fails
        """
        try:
            # Parse command line arguments
            if len(sys.argv) > 1:
                arg = sys.argv[1].lower()

                if arg in ["-h", "--help", "help"]:
                    self.display_help()
                    return

                # Support partial matching for --daemon option
                if arg in ["-d", "--daemon", "daemon"] or arg.startswith("--daemon"):
                    self.run_daemon_mode()
                    return

                if arg in ["-k", "--hotkey", "hotkey"] or arg.startswith("--hotkey"):
                    self.run_hotkey_mode()
                    return

                # Check for invalid options starting with --
                if (
                    arg.startswith("--")
                    and not arg.startswith("--daemon")
                    and not arg.startswith("--hotkey")
                    and arg != "--help"
                ):
                    self._logger.warning(f"[WARNING] Unknown option: {sys.argv[1]}")
                    self._logger.info("Available options: --daemon, --hotkey, --help")
                    self._logger.info(
                        "Or use transformation rules starting with '/' (e.g., /t/l)",
                    )
                    sys.exit(1)

                # Command mode - join all arguments to handle quoted strings
                rule_string: str = " ".join(sys.argv[1:])
                self.run_command_mode(rule_string)
            else:
                # Interactive mode
                input_text: str = self.io_manager.get_input_text()
                self.run_interactive_mode(input_text)

        except (
            ConfigurationError,
            ValidationError,
            TransformationError,
            CryptographyError,
            ClipboardError,
        ) as e:
            self._logger.error(str(e))
            sys.exit(1)
        except KeyboardInterrupt:
            self._logger.info("\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            raise StringMultitoolError(
                f"Application run failed: {e}",
                {"error_type": type(e).__name__},
            ) from e


def main() -> None:
    """Application entry point with Typer integration."""
    logger = get_logger(__name__)
    log_debug(logger, f"Starting Application entry point with Typer integration...")
    try:
        # Check for modern CLI usage (subcommands)
        if len(sys.argv) > 1 and sys.argv[1] in [
            "interactive",
            "transform",
            "encrypt",
            "decrypt",
            "daemon",
            "hotkey",
            "rules",
            "version",
        ]:
            # Use new Typer CLI
            from .cli import run_cli
            run_cli()
        else:
            # Use legacy CLI for backward compatibility
            # Explicitly typed app variable to avoid Pylance warnings
            app: "ApplicationInterface" = ApplicationInterface()
            app.run()
    except Exception as e:
        logger = get_logger(__name__)
        raise StringMultitoolError(
            f"Fatal main execution error: {e}",
            {"error_type": type(e).__name__},
        ) from e

if __name__ == "__main__":
    main()
