"""
Main application interface for String_Multitool.

This module provides the primary application interface and coordinates
all components to deliver the complete functionality.
"""

import sys
import json
from pathlib import Path
from typing import Any

from .exceptions import (
    StringMultitoolError, ConfigurationError, TransformationError,
    CryptographyError, ClipboardError, ValidationError
)
from .core.config import ConfigurationManager
from .core.crypto import CryptographyManager
from .core.transformations import TextTransformationEngine
from .core.types import TextSource
from .io.manager import InputOutputManager
from .modes.interactive import InteractiveSession, CommandProcessor
from .modes.daemon import DaemonMode


class ApplicationInterface:
    """Main application interface and user interaction handler.
    
    This class coordinates all components and provides the main entry
    points for different application modes.
    """
    
    def __init__(self) -> None:
        """Initialize application interface.
        
        Raises:
            ConfigurationError: If initialization fails
        """
        try:
            # Initialize core components
            self.config_manager = ConfigurationManager()
            self.io_manager = InputOutputManager()
            self.transformation_engine = TextTransformationEngine(self.config_manager)
            
            # Initialize cryptography manager (optional)
            try:
                self.crypto_manager = CryptographyManager(self.config_manager)
                self.transformation_engine.set_crypto_manager(self.crypto_manager)
            except CryptographyError as e:
                print(f"Warning: Cryptography not available: {e}")
                self.crypto_manager = None
            
            # Initialize daemon mode
            self.daemon_mode = DaemonMode(self.transformation_engine, self.config_manager)
            
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
            # Create interactive session
            session = InteractiveSession(self.io_manager, self.transformation_engine)
            command_processor = CommandProcessor(session)
            
            # Initialize session with input text
            text_source = "pipe" if not sys.stdin.isatty() else "clipboard"
            session.initialize_with_text(input_text, text_source)
            
            # Display initial status
            self._display_interactive_header(session)
            
            # Main interactive loop
            while True:
                try:
                    # Check for clipboard changes if auto-detection is enabled
                    if session.auto_detection_enabled:
                        new_content = session.check_clipboard_changes()
                        if new_content is not None and new_content != session.current_text:
                            # Display clipboard content preview
                            display_content = new_content[:100] + "..." if len(new_content) > 100 else new_content
                            # Replace newlines with visible characters for better display
                            display_content = display_content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                            
                            print(f"\n🔔 Clipboard changed! New content available ({len(new_content)} chars)")
                            print(f"   Content: '{display_content}'")
                            print("   Type 'refresh' to load new content or continue with current text.")
                    
                    # Get user input
                    try:
                        user_input = input("Rules: ").strip()
                    except EOFError:
                        print("\nGoodbye!")
                        break
                    
                    if not user_input:
                        print("Please enter a rule, command, or 'help'")
                        continue
                    
                    # Process command or transformation rule
                    if command_processor.is_command(user_input):
                        result = command_processor.process_command(user_input)
                        
                        if result.message == "SHOW_HELP":
                            self.display_help()
                            continue
                        
                        if result.message == "SWITCH_TO_DAEMON":
                            print("🔄 Switching to daemon mode...")
                            print("   Interactive mode will exit and daemon mode will start.")
                            print()
                            # Clean up interactive session
                            session.cleanup()
                            # Start daemon mode
                            self.run_daemon_mode()
                            return
                        
                        print(result.message)
                        
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
                            if session.text_source != "pipe":
                                try:
                                    fresh_content = self.io_manager.get_clipboard_text()
                                    # Show if clipboard content changed
                                    if fresh_content != session.current_text:
                                        display_old = session.current_text[:30] + "..." if len(session.current_text) > 30 else session.current_text
                                        display_new = fresh_content[:30] + "..." if len(fresh_content) > 30 else fresh_content
                                        print(f"[CLIPBOARD] Using fresh content: '{display_old}' -> '{display_new}'")
                                        session.update_working_text(fresh_content, "clipboard")
                                except Exception:
                                    # If clipboard access fails, use current text
                                    pass
                            
                            # Apply transformation
                            result = self.transformation_engine.apply_transformations(
                                session.current_text, user_input
                            )
                            
                            # Copy result to clipboard
                            self.io_manager.set_output_text(result)
                            
                            # Display result
                            display_result = result[:100] + "..." if len(result) > 100 else result
                            print(f"Result: '{display_result}'")
                            print("✅ Transformation completed successfully!")
                            
                        except (ValidationError, TransformationError) as e:
                            print(f"❌ Transformation error: {e}")
                        except Exception as e:
                            print(f"❌ Unexpected error: {e}")
                
                except KeyboardInterrupt:
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
            
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
            input_text = self.io_manager.get_input_text()
            
            # Apply transformations
            result = self.transformation_engine.apply_transformations(input_text, rule_string)
            
            # Output result
            self.io_manager.set_output_text(result)
            
            # Display applied rules and result for user feedback
            display_result = result[:100] + "..." if len(result) > 100 else result
            print(f"Applied: {rule_string}")
            print(f"Result: '{display_result}'")
            print("✅ Transformation completed successfully!")
            
        except (ValidationError, TransformationError, ClipboardError) as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)
    
    def run_daemon_mode(self) -> None:
        """Run application in daemon mode.
        
        Raises:
            StringMultitoolError: If daemon mode fails
        """
        try:
            print("String_Multitool - Daemon Mode")
            print("=" * 40)
            print("Continuous clipboard monitoring and transformation")
            print()
            
            # Show available presets
            daemon_config_path = Path("config/daemon_config.json")
            if daemon_config_path.exists():
                try:
                    with open(daemon_config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        presets = config.get("auto_transformation", {}).get("rule_presets", {})
                        
                        if presets:
                            print("Available presets:")
                            for name, rules in presets.items():
                                if isinstance(rules, str):
                                    print(f"  {name}: {rules}")
                                else:
                                    print(f"  {name}: {' -> '.join(rules)}")
                            print()
                except Exception:
                    pass
            
            print("Commands:")
            print("  preset <n>     - Set transformation preset")
            print("  rules <rules>     - Set custom transformation rules")
            print("  /rule             - Set transformation rule directly (e.g., '/t/l')")
            print("  start             - Start daemon monitoring")
            print("  stop              - Stop daemon monitoring")
            print("  status            - Show daemon status")
            print("  interactive       - Switch to interactive mode")
            print("  quit              - Exit daemon mode")
            print()
            
            while True:
                try:
                    try:
                        user_input = input("Daemon> ").strip()
                    except EOFError:
                        print("\nGoodbye!")
                        break
                    
                    if not user_input:
                        continue
                    
                    # Check if input is a transformation rule (starts with /)
                    if user_input.startswith('/'):
                        try:
                            # Validate rules by parsing them
                            parsed_rules = self.transformation_engine.parse_rule_string(user_input)
                            rule_list = [user_input]  # Store as single rule string for sequential application
                            # Set rules directly without duplicate logging
                            self.daemon_mode.active_rules = rule_list
                            print(f"[DAEMON] Active rules set: {user_input}")
                        except Exception as e:
                            print(f"Error: Invalid rule string: {e}")
                        continue
                    
                    parts = user_input.split()
                    command = parts[0].lower()
                    
                    if command in ['quit', 'q', 'exit']:
                        if self.daemon_mode.is_running:
                            self.daemon_mode.stop()
                        print("Goodbye!")
                        break
                    
                    elif command == 'preset':
                        if len(parts) < 2:
                            print("Usage: preset <n>")
                            continue
                        
                        preset_name = parts[1]
                        try:
                            self.daemon_mode.set_preset(preset_name)
                        except (ValidationError, ConfigurationError) as e:
                            print(f"Error: {e}")
                    
                    elif command == 'rules':
                        if len(parts) < 2:
                            print("Usage: rules <rule_string>")
                            print("Example: rules /t/l")
                            continue
                        
                        rule_string = ' '.join(parts[1:])
                        try:
                            # Validate rules by parsing them
                            parsed_rules = self.transformation_engine.parse_rule_string(rule_string)
                            rule_list = [rule_string]  # Store as single rule string for sequential application
                            self.daemon_mode.set_transformation_rules(rule_list)
                        except Exception as e:
                            print(f"Error: Invalid rule string: {e}")
                    
                    elif command == 'start':
                        try:
                            if self.daemon_mode.is_running:
                                print("[DAEMON] Already running")
                            else:
                                # Start daemon monitoring without blocking command input
                                self.daemon_mode.start_monitoring()
                                print("[DAEMON] Check interval: 1.0s")
                                print(f"[DAEMON] Active transformation: {' -> '.join(self.daemon_mode.active_rules)}")
                                print("[DAEMON] Monitoring started in background")
                        except (ValidationError, TransformationError) as e:
                            print(f"Error: {e}")
                    
                    elif command == 'stop':
                        try:
                            self.daemon_mode.stop()
                        except TransformationError as e:
                            print(f"Error: {e}")
                    
                    elif command == 'status':
                        status = self.daemon_mode.get_status()
                        print(f"Status: {'Running' if status['running'] else 'Stopped'}")
                        print(f"Active rules: {' -> '.join(status['active_rules']) if status['active_rules'] else 'None'}")
                        print(f"Active preset: {status['active_preset'] or 'None'}")
                        print(f"Transformations applied: {status['stats']['transformations_applied']}")
                        if status.get('runtime'):
                            print(f"Runtime: {status['runtime']}")
                    
                    elif command == 'interactive':
                        print("🔄 Switching to interactive mode...")
                        print("   Daemon mode will exit and interactive mode will start.")
                        print()
                        # Stop daemon if running
                        if self.daemon_mode.is_running:
                            self.daemon_mode.stop()
                        # Start interactive mode
                        try:
                            input_text = self.io_manager.get_input_text()
                            self.run_interactive_mode(input_text)
                        except Exception as e:
                            print(f"❌ Error starting interactive mode: {e}")
                        return
                    
                    elif command == 'help':
                        print("Daemon Mode Commands:")
                        print("  preset <n>     - Set transformation preset")
                        print("  rules <rules>     - Set custom transformation rules")
                        print("  /rule             - Set transformation rule directly (e.g., '/t/l')")
                        print("  start             - Start daemon monitoring")
                        print("  stop              - Stop daemon monitoring")
                        print("  status            - Show daemon status")
                        print("  interactive       - Switch to interactive mode")
                        print("  quit              - Exit daemon mode")
                    
                    else:
                        print(f"Unknown command: {command}. Type 'help' for available commands.")
                    
                except KeyboardInterrupt:
                    if self.daemon_mode.is_running:
                        self.daemon_mode.stop()
                    print("\nGoodbye!")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    
        except Exception as e:
            raise StringMultitoolError(
                f"Daemon mode failed: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def display_help(self) -> None:
        """Display comprehensive help information."""
        try:
            available_rules = self.transformation_engine.get_available_rules()
            rules_config = self.config_manager.load_transformation_rules()
            
            print("String_Multitool - Advanced Text Transformation Tool")
            print("=" * 55)
            print()
            print("Usage:")
            print("  String_Multitool.py                    # Interactive mode (clipboard input)")
            print("  String_Multitool.py /t/l               # Apply trim + lowercase to clipboard")
            print("  String_Multitool.py --daemon           # Daemon mode (continuous monitoring)")
            print("  echo 'text' | String_Multitool.py      # Interactive mode (pipe input)")
            print("  echo 'text' | String_Multitool.py /t/l # Apply trim + lowercase to piped text")
            print()
            print("Available Transformation Rules:")
            print("-" * 35)
            
            # Display rules by category
            from .core.types import TransformationRuleType
            
            category_display_names = {
                TransformationRuleType.BASIC: "Basic Transformations",
                TransformationRuleType.CASE: "Case Transformations", 
                TransformationRuleType.STRING_OPS: "String Operations",
                TransformationRuleType.ENCRYPTION: "Encryption/Decryption",
                TransformationRuleType.ADVANCED: "Advanced Rules (with arguments)"
            }
            
            # Group rules by category
            rules_by_category = {}
            for rule_key, rule in available_rules.items():
                category = rule.rule_type
                if category not in rules_by_category:
                    rules_by_category[category] = []
                rules_by_category[category].append((rule_key, rule))
            
            # Display each category
            for category, rules in rules_by_category.items():
                category_name = category_display_names.get(category, str(category))
                print(f"\n{category_name}:")
                
                for rule_key, rule in rules:
                    if rule.requires_args:
                        print(f"  /{rule_key} '<args>' - {rule.name}")
                    else:
                        print(f"  /{rule_key} - {rule.name}")
                    print(f"    Example: {rule.example}")
            
            print()
            print("Usage Examples:")
            print("  /t                        # Trim whitespace")
            print("  /t/l                      # Trim then lowercase")
            print("  /enc                      # Encrypt with RSA")
            print("  /dec                      # Decrypt with RSA")
            print("  /S '-'                    # Slugify with hyphen")
            print("  /r 'old' 'new'            # Replace 'old' with 'new'")
            
            if self.crypto_manager:
                print()
                print("RSA Encryption Information:")
                print("  • Key Size: RSA-4096")
                print("  • AES Encryption: AES-256-CBC")
                print("  • Hash Algorithm: SHA256")
                print("  • Keys Location: rsa/")
                print("  • Auto-generated on first use")
                print("  • Supports unlimited text size")
            
            print()
            print("Daemon Mode:")
            print("  String_Multitool.py --daemon")
            print("  • Continuous clipboard monitoring")
            print("  • Automatic transformation application")
            print("  • Configurable transformation presets")
            print("  • Background operation")
            print("  • Real-time clipboard processing")
            
        except Exception as e:
            print(f"❌ Error displaying help: {e}", file=sys.stderr)
    
    def _display_interactive_header(self, session: InteractiveSession) -> None:
        """Display interactive mode header with current status."""
        try:
            status = session.get_status_info()
            display_text = session.get_display_text()
            
            print("String_Multitool - Interactive Mode")
            print("=" * 45)
            print(f"Input text: '{display_text}' ({status.character_count} chars, from {status.text_source.value})")
            print(f"Auto-detection: {'ON' if status.auto_detection_enabled else 'OFF'}")
            
            # Show full clipboard content if available at startup
            if status.text_source == TextSource.CLIPBOARD and session.current_text.strip():
                print()
                print("📋 Current clipboard content:")
                # Display full content with proper formatting
                full_content = session.current_text
                if len(full_content) <= 200:
                    # Show full content for shorter text
                    formatted_content = full_content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    print(f"   '{formatted_content}'")
                else:
                    # Show first 200 characters for longer text
                    preview = full_content[:200] + "..."
                    formatted_preview = preview.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                    print(f"   '{formatted_preview}'")
            
            print()
            print("Available commands: help, refresh, auto, status, clear, copy, commands, quit")
            print("Enter transformation rules (e.g., /t/l) or command:")
            if status.text_source == TextSource.CLIPBOARD:
                print("Note: Transformation rules will use the latest clipboard content")
            print()
            
        except Exception as e:
            print(f"Warning: Could not display header: {e}")
    
    def run(self) -> None:
        """Main application entry point.
        
        Raises:
            StringMultitoolError: If application execution fails
        """
        try:
            # Parse command line arguments
            if len(sys.argv) > 1:
                if sys.argv[1] in ['-h', '--help', 'help']:
                    self.display_help()
                    return
                
                if sys.argv[1] in ['-d', '--daemon', 'daemon']:
                    self.run_daemon_mode()
                    return
                
                # Command mode - join all arguments to handle quoted strings
                rule_string = ' '.join(sys.argv[1:])
                self.run_command_mode(rule_string)
            else:
                # Interactive mode
                input_text = self.io_manager.get_input_text()
                self.run_interactive_mode(input_text)
                
        except (ConfigurationError, ValidationError, TransformationError, 
                CryptographyError, ClipboardError) as e:
            print(f"❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """Application entry point."""
    try:
        app = ApplicationInterface()
        app.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()