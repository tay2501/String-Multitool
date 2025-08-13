"""
Main application interface for String_Multitool.

This module provides the primary application interface and coordinates
all components to deliver the complete functionality.
"""

from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Any

# Import logging utilities
from .utils.logger import get_logger, log_info, log_error, log_warning, log_debug

from .exceptions import (
    StringMultitoolError, ConfigurationError, TransformationError,
    CryptographyError, ClipboardError, ValidationError
)
from .core.dependency_injection import ServiceRegistry, inject, injectable
from .core.types import (
    TextSource, CommandResult, TransformationRuleType,
    ConfigManagerProtocol, TransformationEngineProtocol, CryptoManagerProtocol
)
from .io.manager import InputOutputManager
from .modes.interactive import InteractiveSession, CommandProcessor
from .modes.daemon_refactored import DaemonModeRefactored
from .modes.hotkey import HotkeyMode


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
        io_manager: InputOutputManager | None = None
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
            self.transformation_engine = transformation_engine or inject(TransformationEngineProtocol)
            self.io_manager = io_manager or inject(InputOutputManager)
            
            # Get optional crypto manager
            try:
                self.crypto_manager = inject(CryptoManagerProtocol)
                if self.crypto_manager:
                    self.transformation_engine.set_crypto_manager(self.crypto_manager)
            except Exception as e:
                logger = get_logger(__name__)
                log_warning(logger, f"Cryptography not available: {e}")
                self.crypto_manager = None
            
            # Initialize daemon mode (injected)
            self.daemon_mode = inject(DaemonModeRefactored)
            
            # Initialize hotkey mode (optional, injected)
            try:
                self.hotkey_mode = inject(HotkeyMode)
            except Exception:
                self.hotkey_mode = None
                
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize application: {e}",
                {"error_type": type(e).__name__}
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
                    # Check for clipboard changes if auto-detection is enabled
                    if session.auto_detection_enabled:
                        new_content: str | None = session.check_clipboard_changes()
                        if new_content is not None and new_content != session.current_text:
                            # Display clipboard content preview
                            display_content: str = new_content[:100] + "..." if len(new_content) > 100 else new_content
                            # Replace newlines with visible characters for better display
                            display_content = display_content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                            
                            logger = get_logger(__name__)
                            log_info(logger, f"\n🔔 Clipboard changed! New content available ({len(new_content)} chars)")
                            log_info(logger, f"   Content: '{display_content}'")
                            log_info(logger, "   Type 'refresh' to load new content or continue with current text.")
                    
                    # Get user input
                    try:
                        user_input: str = input("Rules: ").strip()
                    except EOFError:
                        logger = get_logger(__name__)
                        log_info(logger, "\nGoodbye!")
                        break
                    
                    if not user_input:
                        logger = get_logger(__name__)
                        log_info(logger, "Please enter a rule, command, or 'help'")
                        continue
                    
                    # Process command or transformation rule
                    if command_processor.is_command(user_input):
                        result: CommandResult = command_processor.process_command(user_input)
                        
                        if result.message == "SHOW_HELP":
                            self.display_help()
                            continue
                        
                        if result.message == "SWITCH_TO_DAEMON":
                            logger = get_logger(__name__)
                            log_info(logger, "🔄 Switching to daemon mode...")
                            log_info(logger, "   Interactive mode will exit and daemon mode will start.")
                            log_info(logger, "")
                            # Clean up interactive session
                            session.cleanup()
                            # Start daemon mode
                            self.run_daemon_mode()
                            return
                        
                        logger = get_logger(__name__)
                        log_info(logger, result.message)
                        
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
                                    fresh_content: str = self.io_manager.get_clipboard_text()
                                    # Show if clipboard content changed
                                    if fresh_content != session.current_text:
                                        display_old: str = session.current_text[:30] + "..." if len(session.current_text) > 30 else session.current_text
                                        display_new: str = fresh_content[:30] + "..." if len(fresh_content) > 30 else fresh_content
                                        logger = get_logger(__name__)
                                        log_info(logger, f"[CLIPBOARD] Using fresh content: '{display_old}' -> '{display_new}'")
                                        session.update_working_text(fresh_content, "clipboard")
                                except Exception:
                                    # If clipboard access fails, use current text
                                    pass
                            
                            # Apply transformation
                            transformation_result: str = self.transformation_engine.apply_transformations(
                                session.current_text, user_input
                            )
                            
                            # Copy result to clipboard
                            self.io_manager.set_output_text(transformation_result)
                            
                            # Display result
                            display_result: str = transformation_result[:100] + "..." if len(transformation_result) > 100 else transformation_result
                            logger = get_logger(__name__)
                            log_info(logger, f"Result: '{display_result}'")
                            log_info(logger, "✅ Transformation completed successfully!")
                            
                        except (ValidationError, TransformationError) as e:
                            logger = get_logger(__name__)
                            log_error(logger, f"❌ Transformation error: {e}")
                        except Exception as e:
                            logger = get_logger(__name__)
                            log_error(logger, f"❌ Unexpected error: {e}")
                
                except KeyboardInterrupt:
                    logger = get_logger(__name__)
                    log_info(logger, "\nGoodbye!")
                    break
                except Exception as e:
                    logger = get_logger(__name__)
                    log_error(logger, f"❌ Error: {e}")
            
            # Cleanup
            session.cleanup()
            
        except Exception as e:
            raise StringMultitoolError(
                f"Interactive mode failed: {e}",
                {"error_type": type(e).__name__}
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
            result: str = self.transformation_engine.apply_transformations(input_text, rule_string)
            
            # Output result
            self.io_manager.set_output_text(result)
            
            # Display applied rules and result for user feedback
            display_result: str = result[:100] + "..." if len(result) > 100 else result
            logger = get_logger(__name__)
            log_info(logger, f"Applied: {rule_string}")
            log_info(logger, f"Result: '{display_result}'")
            log_info(logger, "✅ Transformation completed successfully!")
            
        except (ValidationError, TransformationError, ClipboardError) as e:
            logger = get_logger(__name__)
            log_error(logger, f"❌ Error: {e}")
            sys.exit(1)
        except Exception as e:
            logger = get_logger(__name__)
            log_error(logger, f"❌ Unexpected error: {e}")
            sys.exit(1)
    
    def run_hotkey_mode(self) -> None:
        """Run application in hotkey mode.
        
        Raises:
            StringMultitoolError: If hotkey mode fails
        """
        try:
            logger = get_logger(__name__)
            log_info(logger, "Starting hotkey mode...")
            
            # Initialize hotkey mode if not already done
            if self.hotkey_mode is None:
                self.hotkey_mode = HotkeyMode(
                    self.io_manager, 
                    self.transformation_engine, 
                    self.config_manager
                )
            
            # Run hotkey mode (blocking)
            self.hotkey_mode.run()
            
        except KeyboardInterrupt:
            logger = get_logger(__name__)
            log_info(logger, "Hotkey mode stopped by user")
        except ConfigurationError as e:
            logger = get_logger(__name__)
            log_error(logger, f"Hotkey configuration error: {e}")
            raise
        except Exception as e:
            logger = get_logger(__name__)
            log_error(logger, f"Hotkey mode error: {e}")
            raise StringMultitoolError(
                f"Hotkey mode failed: {e}",
                {"error_type": type(e).__name__}
            ) from e

    def run_daemon_mode(self) -> None:
        """Run application in daemon mode.
        
        Raises:
            StringMultitoolError: If daemon mode fails
        """
        try:
            logger = get_logger(__name__)
            log_info(logger, "String_Multitool - Daemon Mode")
            log_info(logger, "=" * 40)
            log_info(logger, "Continuous clipboard monitoring and transformation")
            log_info(logger, "")
            
            # Show available presets
            daemon_config_path: Path = Path("config/daemon_config.json")
            if daemon_config_path.exists():
                try:
                    with open(daemon_config_path, 'r', encoding='utf-8') as f:
                        config: dict[str, Any] = json.load(f)
                        presets: dict[str, Any] = config.get("auto_transformation", {}).get("rule_presets", {})
                        
                        if presets:
                            logger = get_logger(__name__)
                            log_info(logger, "Available presets:")
                            for name, rules in presets.items():
                                if isinstance(rules, str):
                                    log_info(logger, f"  {name}: {rules}")
                                else:
                                    log_info(logger, f"  {name}: {' -> '.join(rules)}")
                            log_info(logger, "")
                except Exception:
                    pass
            
            logger = get_logger(__name__)
            log_info(logger, "Commands:")
            log_info(logger, "  preset <n>     - Set transformation preset")
            log_info(logger, "  rules <rules>     - Set custom transformation rules")
            log_info(logger, "  /rule             - Set transformation rule directly (e.g., '/t/l')")
            log_info(logger, "  start             - Start daemon monitoring")
            log_info(logger, "  stop              - Stop daemon monitoring")
            log_info(logger, "  status            - Show daemon status")
            log_info(logger, "  interactive       - Switch to interactive mode")
            log_info(logger, "  quit              - Exit daemon mode")
            log_info(logger, "")
            
            while True:
                try:
                    try:
                        user_input: str = input("Daemon> ").strip()
                    except EOFError:
                        logger = get_logger(__name__)
                        log_info(logger, "\nGoodbye!")
                        break
                    
                    if not user_input:
                        continue
                    
                    # Check if input is a transformation rule (starts with /)
                    if user_input.startswith('/'):
                        try:
                            # Validate rules by parsing them
                            # parsed_rules: list[tuple[str, list[str]]] = self.transformation_engine.parse_rule_string(user_input)
                            rule_list: list[str] = [user_input]  # Store as single rule string for sequential application
                            # Use the proper method to set rules
                            self.daemon_mode.set_transformation_rules(rule_list)
                        except Exception as e:
                            logger = get_logger(__name__)
                            log_error(logger, f"Error: Invalid rule string: {e}")
                        continue
                    
                    parts: list[str] = user_input.split()
                    command: str = parts[0].lower()
                    
                    if command in ['quit', 'q', 'exit']:
                        if self.daemon_mode.is_running:
                            self.daemon_mode.stop()
                        logger = get_logger(__name__)
                        log_info(logger, "Goodbye!")
                        break
                    
                    elif command == 'preset':
                        if len(parts) < 2:
                            logger = get_logger(__name__)
                            log_info(logger, "Usage: preset <n>")
                            continue
                        
                        preset_name: str = parts[1]
                        try:
                            self.daemon_mode.set_preset(preset_name)
                        except (ValidationError, ConfigurationError) as e:
                            logger = get_logger(__name__)
                            log_error(logger, f"Error: {e}")
                    
                    elif command == 'rules':
                        if len(parts) < 2:
                            logger = get_logger(__name__)
                            log_info(logger, "Usage: rules <rule_string>")
                            log_info(logger, "Example: rules /t/l")
                            continue
                        
                        rule_string: str = ' '.join(parts[1:])
                        try:
                            # Validate rules by parsing them
                            # parsed_daemon_rules: list[tuple[str, list[str]]] = self.transformation_engine.parse_rule_string(rule_string)
                            daemon_rule_list: list[str] = [rule_string]  # Store as single rule string for sequential application
                            self.daemon_mode.set_transformation_rules(daemon_rule_list)
                        except Exception as e:
                            logger = get_logger(__name__)
                            log_error(logger, f"Error: Invalid rule string: {e}")
                    
                    elif command == 'start':
                        try:
                            if self.daemon_mode.is_running:
                                logger = get_logger(__name__)
                                log_info(logger, "[DAEMON] Already running")
                            else:
                                # Start daemon monitoring without blocking command input
                                self.daemon_mode.start_monitoring()
                                logger = get_logger(__name__)
                                log_info(logger, "[DAEMON] Check interval: 1.0s")
                                log_info(logger, f"[DAEMON] Active transformation: {' -> '.join(self.daemon_mode.active_rules)}")
                                log_info(logger, "[DAEMON] Monitoring started in background")
                        except (ValidationError, TransformationError) as e:
                            logger = get_logger(__name__)
                            log_error(logger, f"Error: {e}")
                    
                    elif command == 'stop':
                        try:
                            self.daemon_mode.stop()
                        except TransformationError as e:
                            logger = get_logger(__name__)
                            log_error(logger, f"Error: {e}")
                    
                    elif command == 'status':
                        status: dict[str, Any] = self.daemon_mode.get_status()
                        logger = get_logger(__name__)
                        log_info(logger, f"Status: {'Running' if status['running'] else 'Stopped'}")
                        log_info(logger, f"Active rules: {' -> '.join(status['active_rules']) if status['active_rules'] else 'None'}")
                        log_info(logger, f"Active preset: {status['active_preset'] or 'None'}")
                        log_info(logger, f"Transformations applied: {status['stats']['transformations_applied']}")
                        if status.get('runtime'):
                            log_info(logger, f"Runtime: {status['runtime']}")
                    
                    elif command == 'interactive':
                        logger = get_logger(__name__)
                        log_info(logger, "🔄 Switching to interactive mode...")
                        log_info(logger, "   Daemon mode will exit and interactive mode will start.")
                        log_info(logger, "")
                        # Stop daemon if running
                        if self.daemon_mode.is_running:
                            self.daemon_mode.stop()
                        # Start interactive mode
                        try:
                            input_text: str = self.io_manager.get_input_text()
                            self.run_interactive_mode(input_text)
                        except Exception as e:
                            logger = get_logger(__name__)
                            log_error(logger, f"❌ Error starting interactive mode: {e}")
                        return
                    
                    elif command == 'help':
                        logger = get_logger(__name__)
                        log_info(logger, "Daemon Mode Commands:")
                        log_info(logger, "  preset <n>     - Set transformation preset")
                        log_info(logger, "  rules <rules>     - Set custom transformation rules")
                        log_info(logger, "  /rule             - Set transformation rule directly (e.g., '/t/l')")
                        log_info(logger, "  start             - Start daemon monitoring")
                        log_info(logger, "  stop              - Stop daemon monitoring")
                        log_info(logger, "  status            - Show daemon status")
                        log_info(logger, "  interactive       - Switch to interactive mode")
                        log_info(logger, "  quit              - Exit daemon mode")
                    
                    else:
                        logger = get_logger(__name__)
                        log_info(logger, f"Unknown command: {command}. Type 'help' for available commands.")
                    
                except KeyboardInterrupt:
                    if self.daemon_mode.is_running:
                        self.daemon_mode.stop()
                    logger = get_logger(__name__)
                    log_info(logger, "\nGoodbye!")
                    break
                except Exception as e:
                    logger = get_logger(__name__)
                    log_error(logger, f"Error: {e}")
                    
        except Exception as e:
            raise StringMultitoolError(
                f"Daemon mode failed: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def display_help(self) -> None:
        """Display comprehensive help information."""
        try:
            available_rules: dict[str, Any] = self.transformation_engine.get_available_rules()
            # rules_config: dict[str, Any] = self.config_manager.load_transformation_rules()
            
            logger = get_logger(__name__)
            log_info(logger, "String_Multitool - Advanced Text Transformation Tool")
            log_info(logger, "=" * 55)
            log_info(logger, "")
            log_info(logger, "Usage:")
            log_info(logger, "  String_Multitool.py                    # Interactive mode (clipboard input)")
            log_info(logger, "  String_Multitool.py /t/l               # Apply trim + lowercase to clipboard")
            log_info(logger, "  String_Multitool.py --daemon           # Daemon mode (continuous monitoring)")
            log_info(logger, "  String_Multitool.py --hotkey           # Hotkey mode (global keyboard shortcuts)")
            log_info(logger, "  echo 'text' | String_Multitool.py      # Interactive mode (pipe input)")
            log_info(logger, "  echo 'text' | String_Multitool.py /t/l # Apply trim + lowercase to piped text")
            log_info(logger, "")
            log_info(logger, "Available Transformation Rules:")
            log_info(logger, "-" * 35)
            
            # Display rules by category
            category_display_names: dict[TransformationRuleType, str] = {
                TransformationRuleType.BASIC: "Basic Transformations",
                TransformationRuleType.CASE: "Case Transformations", 
                TransformationRuleType.STRING_OPS: "String Operations",
                TransformationRuleType.ENCRYPTION: "Encryption/Decryption",
                TransformationRuleType.ADVANCED: "Advanced Rules (with arguments)"
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
                log_info(logger, f"\n{category_name}:")
                
                for rule_key, rule in rules:
                    if rule.requires_args:
                        log_info(logger, f"  /{rule_key} '<args>' - {rule.name}")
                    else:
                        log_info(logger, f"  /{rule_key} - {rule.name}")
                    log_info(logger, f"    Example: {rule.example}")
            
            log_info(logger, "")
            log_info(logger, "Usage Examples:")
            log_info(logger, "  /t                        # Trim whitespace")
            log_info(logger, "  /t/l                      # Trim then lowercase")
            log_info(logger, "  /enc                      # Encrypt with RSA")
            log_info(logger, "  /dec                      # Decrypt with RSA")
            log_info(logger, "  /S '-'                    # Slugify with hyphen")
            log_info(logger, "  /r 'old' 'new'            # Replace 'old' with 'new'")
            
            if self.crypto_manager:
                log_info(logger, "")
                log_info(logger, "RSA Encryption Information:")
                log_info(logger, "  • Key Size: RSA-4096")
                log_info(logger, "  • AES Encryption: AES-256-CBC")
                log_info(logger, "  • Hash Algorithm: SHA256")
                log_info(logger, "  • Keys Location: rsa/")
                log_info(logger, "  • Auto-generated on first use")
                log_info(logger, "  • Supports unlimited text size")
            
            log_info(logger, "")
            log_info(logger, "Daemon Mode:")
            log_info(logger, "  String_Multitool.py --daemon")
            log_info(logger, "  • Continuous clipboard monitoring")
            log_info(logger, "  • Automatic transformation application")
            log_info(logger, "  • Configurable transformation presets")
            log_info(logger, "  • Background operation")
            log_info(logger, "  • Real-time clipboard processing")
            
        except Exception as e:
            logger = get_logger(__name__)
            log_error(logger, f"Error displaying help: {e}")
    
    def _display_interactive_header(self, session: InteractiveSession) -> None:
        """Display interactive mode header with current status."""
        try:
            status: Any = session.get_status_info()
            display_text: str = session.get_display_text()
            
            logger = get_logger(__name__)
            log_info(logger, "String_Multitool - Interactive Mode")
            log_info(logger, "=" * 45)
            log_info(logger, f"Input text: '{display_text}' ({status.character_count} chars, from {status.text_source.value})")
            log_info(logger, f"Auto-detection: {'ON' if status.auto_detection_enabled else 'OFF'}")
            
            # Show full clipboard content if available at startup
            if status.text_source == TextSource.CLIPBOARD and session.current_text.strip():
                log_info(logger, "")
                log_info(logger, "📋 Current clipboard content:")
                # Display full content with proper formatting
                full_content: str = session.current_text
                if len(full_content) <= 200:
                    # Show full content for shorter text
                    formatted_content: str = full_content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    log_info(logger, f"   '{formatted_content}'")
                else:
                    # Show first 200 characters for longer text
                    preview: str = full_content[:200] + "..."
                    formatted_preview: str = preview.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    log_info(logger, f"   '{formatted_preview}'")
            
            log_info(logger, "")
            log_info(logger, "Available commands: help, refresh, auto, status, clear, copy, commands, quit")
            log_info(logger, "Enter transformation rules (e.g., /t/l) or command:")
            if status.text_source == TextSource.CLIPBOARD:
                log_info(logger, "Note: Transformation rules will use the latest clipboard content")
            log_info(logger, "")
            
        except Exception as e:
            logger = get_logger(__name__)
            log_warning(logger, f"Could not display header: {e}")
    
    def run(self) -> None:
        """Main application entry point.
        
        Raises:
            StringMultitoolError: If application execution fails
        """
        try:
            # Parse command line arguments
            if len(sys.argv) > 1:
                arg = sys.argv[1].lower()
                
                if arg in ['-h', '--help', 'help']:
                    self.display_help()
                    return
                
                # Support partial matching for --daemon option
                if arg in ['-d', '--daemon', 'daemon'] or arg.startswith('--daemon'):
                    self.run_daemon_mode()
                    return
                
                if arg in ['-k', '--hotkey', 'hotkey'] or arg.startswith('--hotkey'):
                    self.run_hotkey_mode()
                    return
                
                # Check for invalid options starting with --
                if arg.startswith('--') and not arg.startswith('--daemon') and not arg.startswith('--hotkey') and arg != '--help':
                    logger = get_logger(__name__)
                    log_error(logger, f"❌ Unknown option: {sys.argv[1]}")
                    log_info(logger, "Available options: --daemon, --hotkey, --help")
                    log_info(logger, "Or use transformation rules starting with '/' (e.g., /t/l)")
                    sys.exit(1)
                
                # Command mode - join all arguments to handle quoted strings
                rule_string: str = ' '.join(sys.argv[1:])
                self.run_command_mode(rule_string)
            else:
                # Interactive mode
                input_text: str = self.io_manager.get_input_text()
                self.run_interactive_mode(input_text)
                
        except (ConfigurationError, ValidationError, TransformationError, 
                CryptographyError, ClipboardError) as e:
            logger = get_logger(__name__)
            log_error(logger, str(e), exc_info=False)
            sys.exit(1)
        except KeyboardInterrupt:
            logger = get_logger(__name__)
            log_info(logger, "\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            logger = get_logger(__name__)
            log_error(logger, f"Unexpected error: {e}")
            sys.exit(1)


def main() -> None:
    """Application entry point with Typer integration."""
    try:
        # Check for modern CLI usage (subcommands)
        if len(sys.argv) > 1 and sys.argv[1] in ['interactive', 'transform', 'encrypt', 'decrypt', 'daemon', 'hotkey', 'rules', 'version']:
            # Use new Typer CLI
            from .cli import run_cli
            run_cli()
        else:
            # Use legacy CLI for backward compatibility
            # Explicitly typed app variable to avoid Pylance warnings
            app: 'ApplicationInterface' = ApplicationInterface()
            app.run()
    except Exception as e:
        logger = get_logger(__name__)
        log_error(logger, f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()