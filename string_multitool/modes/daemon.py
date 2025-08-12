"""
Daemon mode for String_Multitool.

This module provides continuous clipboard monitoring and automatic
transformation capabilities with comprehensive configuration support.
"""

from __future__ import annotations

import json
import time
import threading
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final, TypeAlias, ClassVar
from typing_extensions import override, Self

try:
    import keyboard
    KEYBOARD_AVAILABLE: Final[bool] = True
except ImportError:
    try:
        from pynput import keyboard as pynput_keyboard
        PYNPUT_AVAILABLE: Final[bool] = True
        KEYBOARD_AVAILABLE: Final[bool] = False
    except ImportError:
        PYNPUT_AVAILABLE: Final[bool] = False
        KEYBOARD_AVAILABLE: Final[bool] = False
        print("Warning: Neither keyboard nor pynput available, sequence hotkeys disabled")

from ..exceptions import ConfigurationError, ValidationError, TransformationError
from ..core.types import TransformationEngineProtocol, ConfigManagerProtocol
from ..io.manager import InputOutputManager

# Type aliases for better readability and maintainability
DaemonConfig: TypeAlias = dict[str, Any]
StatsDict: TypeAlias = dict[str, Any]
RulesList: TypeAlias = list[str]
HotkeyCallback: TypeAlias = Callable[[], None]


class DaemonMode:
    """Daemon mode for continuous clipboard monitoring and transformation.
    
    This class provides background clipboard processing with configurable
    transformation rules and comprehensive status tracking.
    """
    
    # Class constants
    DEFAULT_SEQUENCE_TIMEOUT: ClassVar[float] = 2.0
    DEFAULT_CHECK_INTERVAL: ClassVar[float] = 1.0
    MONITOR_THREAD_NAME: ClassVar[str] = "DaemonClipboardMonitor"
    SEQUENCE_MAX_LENGTH: ClassVar[int] = 2
    
    def __init__(
        self, 
        transformation_engine: TransformationEngineProtocol,
        config_manager: ConfigManagerProtocol
    ) -> None:
        """Initialize daemon mode.
        
        Args:
            transformation_engine: Text transformation engine
            config_manager: Configuration manager
            
        Raises:
            ValidationError: If required parameters are invalid
            ConfigurationError: If daemon configuration is invalid
        """
        if transformation_engine is None:
            raise ValidationError("Transformation engine cannot be None")
        if config_manager is None:
            raise ValidationError("Config manager cannot be None")
        
        # Instance variable annotations following PEP 526
        self.transformation_engine: TransformationEngineProtocol = transformation_engine
        self.config_manager: ConfigManagerProtocol = config_manager
        self.is_running: bool = False
        self.last_clipboard_content: str = ""
        self.active_rules: RulesList = []
        self.clipboard_monitor: threading.Thread | None = None
        self.active_preset: str | None = None
        self.daemon_config: DaemonConfig = {}
        self.stats: StatsDict = {
            'transformations_applied': 0,
            'start_time': None,
            'last_transformation': None
        }
        
        # Sequence hotkeys support
        self.hotkey_listener: Any | None = None
        self.key_sequence: list[str] = []
        self.last_key_time: datetime | None = None
        self.sequence_timeout: float = self.DEFAULT_SEQUENCE_TIMEOUT
        self.registered_hotkeys: list[str] = []
        
        # Load daemon configuration
        try:
            self.daemon_config = self._load_daemon_config()
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load daemon configuration: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def start_monitoring(self) -> None:
        """Start daemon monitoring in a separate thread.
        
        Raises:
            ValidationError: If no transformation rules are set
            TransformationError: If monitoring cannot be started
        """
        if self.is_running:
            return
        
        if not self.active_rules:
            raise ValidationError("No transformation rules set. Use 'rules' or 'preset' command first.")
        
        try:
            self.is_running = True
            self.stats['start_time'] = datetime.now()
            
            # Start monitoring thread
            self.clipboard_monitor = threading.Thread(
                target=self._monitor_clipboard,
                daemon=True,
                name="DaemonClipboardMonitor"
            )
            self.clipboard_monitor.start()
            
            # Start sequence hotkey monitoring if enabled
            self._start_sequence_hotkeys()
            
        except Exception as e:
            self.is_running = False
            raise TransformationError(
                f"Failed to start daemon monitoring: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def stop(self) -> None:
        """Stop daemon monitoring.
        
        Raises:
            TransformationError: If monitoring cannot be stopped
        """
        if not self.is_running:
            return
        
        try:
            self.is_running = False
            
            # Stop sequence hotkeys
            self._stop_sequence_hotkeys()
            
            if self.clipboard_monitor and self.clipboard_monitor.is_alive():
                self.clipboard_monitor.join(timeout=2.0)
            
            # Calculate runtime
            if self.stats['start_time']:
                runtime = datetime.now() - self.stats['start_time']
                print(f"[DAEMON] Stopped after {runtime}")
                print(f"[DAEMON] Transformations applied: {self.stats['transformations_applied']}")
            
            print("[DAEMON] Clipboard monitoring stopped")
            
        except Exception as e:
            raise TransformationError(
                f"Failed to stop daemon monitoring: {e}",
                {"error_type": type(e).__name__}
            ) from e
    
    def set_transformation_rules(self, rules: RulesList) -> None:
        """Set active transformation rules.
        
        Args:
            rules: List of transformation rule strings
            
        Raises:
            ValidationError: If rules are invalid
        """
        if not isinstance(rules, list):
            raise ValidationError(
                f"Rules must be a list, got {type(rules).__name__}",
                {"rules_type": type(rules).__name__}
            )
        
        if not rules:
            raise ValidationError("Rules list cannot be empty")
        
        # Validate rules
        for rule in rules:
            if not isinstance(rule, str):
                raise ValidationError(
                    f"Each rule must be a string, got {type(rule).__name__}",
                    {"rule_type": type(rule).__name__, "rule": str(rule)}
                )
        
        self.active_rules = rules
        self.active_preset = None  # Clear preset when setting custom rules
        print(f"[DAEMON] Active rules set: {' -> '.join(rules) if rules else 'None'}")
    
    def set_preset(self, preset_name: str) -> bool:
        """Set transformation preset.
        
        Args:
            preset_name: Name of the preset to activate
            
        Returns:
            True if preset was set successfully
            
        Raises:
            ValidationError: If preset name is invalid
            ConfigurationError: If preset is not found
        """
        if not isinstance(preset_name, str):
            raise ValidationError(
                f"Preset name must be a string, got {type(preset_name).__name__}",
                {"preset_type": type(preset_name).__name__}
            )
        
        if not preset_name.strip():
            raise ValidationError("Preset name cannot be empty")
        
        try:
            presets: Mapping[str, Any] = self.daemon_config.get("auto_transformation", {}).get("rule_presets", {})
            
            if preset_name not in presets:
                available_presets: Sequence[str] = list(presets.keys())
                raise ConfigurationError(
                    f"Unknown preset: {preset_name}",
                    {"preset_name": preset_name, "available_presets": available_presets}
                )
            
            preset_rules: str | RulesList = presets[preset_name]
            if isinstance(preset_rules, str):
                self.active_rules = [preset_rules]
            else:
                self.active_rules = preset_rules
            
            self.active_preset = preset_name
            print(f"[DAEMON] Preset '{preset_name}' activated: {' -> '.join(self.active_rules)}")
            return True
            
        except (ConfigurationError, ValidationError):
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Failed to set preset '{preset_name}': {e}",
                {"preset_name": preset_name, "error_type": type(e).__name__}
            ) from e
    
    def get_status(self) -> StatsDict:
        """Get daemon status information.
        
        Returns:
            Dictionary containing status information
        """
        status: StatsDict = {
            'running': self.is_running,
            'active_rules': self.active_rules.copy(),
            'active_preset': self.active_preset,
            'stats': self.stats.copy()
        }
        
        if self.stats['start_time'] and self.is_running:
            runtime = datetime.now() - self.stats['start_time']
            status['runtime'] = str(runtime).split('.')[0]  # Remove microseconds
        
        return status
    
    def _load_daemon_config(self) -> DaemonConfig:
        """Load daemon configuration from file or use defaults.
        
        Returns:
            Daemon configuration dictionary
        """
        daemon_config_path: Final[Path] = Path("config/daemon_config.json")
        
        if daemon_config_path.exists():
            try:
                with daemon_config_path.open('r', encoding='utf-8') as f:
                    config_data: Any = json.load(f)
                    return config_data
            except (OSError, json.JSONDecodeError) as e:
                print(f"Warning: Failed to load daemon config, using defaults: {e}")
        
        return self._get_default_daemon_config()
    
    def _get_default_daemon_config(self) -> DaemonConfig:
        """Get default daemon configuration."""
        return {
            "daemon_mode": {
                "check_interval": 1.0,
                "max_retries": 3,
                "retry_delay": 0.5
            },
            "clipboard_monitoring": {
                "enabled": True,
                "ignore_duplicates": True,
                "ignore_empty": True,
                "min_length": 1,
                "max_length": 10000,
                "ignore_patterns": []
            },
            "auto_transformation": {
                "rule_presets": {
                    "uppercase": "/u",
                    "lowercase": "/l",
                    "snake_case": "/s",
                    "pascal_case": "/p",
                    "camel_case": "/c",
                    "trim_lowercase": "/t/l",
                    "hyphen_to_underscore": "/hu"
                }
            }
        }
    
    def _monitor_clipboard(self) -> None:
        """Main clipboard monitoring loop."""
        check_interval: Final[float] = self.daemon_config["daemon_mode"]["check_interval"]
        
        while self.is_running:
            try:
                io_manager: InputOutputManager = InputOutputManager()
                current_content: str = io_manager.get_clipboard_text()
                
                if self._should_process_content(current_content):
                    self._process_clipboard_content(current_content)
                
                # Use shorter sleep intervals for better responsiveness
                sleep_iterations: Final[int] = int(check_interval * 10)
                for _ in range(sleep_iterations):
                    if not self.is_running:
                        break
                    time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\r[DAEMON] Error monitoring clipboard: {e}", flush=True)
                time.sleep(check_interval)
    
    def _should_process_content(self, content: str) -> bool:
        """Check if clipboard content should be processed.
        
        Args:
            content: Clipboard content to check
            
        Returns:
            True if content should be processed, False otherwise
        """
        config: Mapping[str, Any] = self.daemon_config["clipboard_monitoring"]
        
        # Check if monitoring is enabled
        if not config.get("enabled", True):
            return False
        
        # Check if we have active rules
        if not self.active_rules:
            return False
        
        # Check if content is different from last processed
        if config.get("ignore_duplicates", True):
            if content == self.last_clipboard_content:
                return False
        
        # Check if content is empty
        if config.get("ignore_empty", True) and not content.strip():
            return False
        
        # Check content length
        min_length: Final[int] = config.get("min_length", 1)
        max_length: Final[int] = config.get("max_length", 10000)
        
        if len(content) < min_length or len(content) > max_length:
            return False
        
        return True
    
    def _process_clipboard_content(self, content: str) -> None:
        """Process clipboard content with active transformation rules.
        
        Args:
            content: Clipboard content to process
        """
        try:
            # Apply transformation rules sequentially
            result: str = content
            for rule in self.active_rules:
                result = self.transformation_engine.apply_transformations(result, rule)
            
            # Skip if transformation didn't change the content
            if result == content:
                return
            
            # Update clipboard with transformed content (silently)
            try:
                import pyperclip
                pyperclip.copy(result)
            except Exception:
                pass  # Silently fail if clipboard update fails
            
            # Update statistics and state
            self.stats['transformations_applied'] += 1
            self.stats['last_transformation'] = datetime.now()
            self.last_clipboard_content = result
            
            # Show transformation result (only when content actually changed)
            MAX_DISPLAY_LENGTH: Final[int] = 50
            display_input: str = content[:MAX_DISPLAY_LENGTH] + "..." if len(content) > MAX_DISPLAY_LENGTH else content
            display_output: str = result[:MAX_DISPLAY_LENGTH] + "..." if len(result) > MAX_DISPLAY_LENGTH else result
            
            # Use \r to overwrite current line and avoid interfering with command input
            print(f"\r[DAEMON] Transformed: '{display_input}' -> '{display_output}'", end='', flush=True)
            print()  # Add newline after transformation message
            
        except Exception as e:
            print(f"\r[DAEMON] Error processing content: {e}", flush=True)
    
    def _start_sequence_hotkeys(self) -> None:
        """Start sequence hotkey monitoring if enabled and available."""
        if not (KEYBOARD_AVAILABLE or PYNPUT_AVAILABLE):
            return
        
        config = self.daemon_config.get("sequence_hotkeys", {})
        if not config.get("enabled", False):
            return
        
        self.sequence_timeout = config.get("timeout", 2.0)
        
        try:
            if KEYBOARD_AVAILABLE:
                self._start_keyboard_hotkeys(config)
            elif PYNPUT_AVAILABLE:
                self._start_pynput_hotkeys(config)
                
            print("[DAEMON] Sequence hotkeys monitoring started")
        except Exception as e:
            print(f"[DAEMON] Warning: Failed to start sequence hotkeys: {e}")
    
    def _start_keyboard_hotkeys(self, config: Mapping[str, Any]) -> None:
        """Start sequence hotkeys using keyboard library."""
        sequences = config.get("sequences", {})
        
        for rule, seq_info in sequences.items():
            sequence = seq_info.get("sequence", [])
            if len(sequence) == 2:
                # Register sequence as: first_hotkey -> second_hotkey -> action
                first_key = sequence[0].replace('+', '+')
                second_key = sequence[1].replace('+', '+')
                
                try:
                    # Create a callback for this specific sequence
                    def create_sequence_callback(rule_name: str, seq: Sequence[str]) -> tuple[HotkeyCallback, HotkeyCallback]:
                        sequence_state: dict[str, Any] = {"last_key_time": None, "expecting_second": False}
                        
                        def first_key_callback() -> None:
                            sequence_state["last_key_time"] = datetime.now()
                            sequence_state["expecting_second"] = True
                            # Set a timer to reset the sequence
                            threading.Timer(
                                self.sequence_timeout, 
                                lambda: sequence_state.update({"expecting_second": False})
                            ).start()
                        
                        def second_key_callback() -> None:
                            if (sequence_state["expecting_second"] and 
                                sequence_state["last_key_time"] and
                                (datetime.now() - sequence_state["last_key_time"]).total_seconds() <= self.sequence_timeout):
                                self._apply_sequence_rule(rule_name)
                                sequence_state["expecting_second"] = False
                        
                        return first_key_callback, second_key_callback
                    
                    first_callback: HotkeyCallback
                    second_callback: HotkeyCallback
                    first_callback, second_callback = create_sequence_callback(rule, sequence)
                    
                    # Register both hotkeys
                    keyboard.add_hotkey(first_key, first_callback)
                    keyboard.add_hotkey(second_key, second_callback)
                    
                    self.registered_hotkeys.extend([first_key, second_key])
                    
                except Exception as e:
                    print(f"[DAEMON] Warning: Failed to register hotkey sequence {rule}: {e}")
    
    def _start_pynput_hotkeys(self, config: Mapping[str, Any]) -> None:
        """Start sequence hotkeys using pynput library (fallback)."""
        self.hotkey_listener = pynput_keyboard.Listener(
            on_press=self._on_key_press_pynput,
            on_release=None
        )
        self.hotkey_listener.start()
    
    def _stop_sequence_hotkeys(self) -> None:
        """Stop sequence hotkey monitoring."""
        try:
            if KEYBOARD_AVAILABLE:
                # Remove registered hotkeys
                for hotkey in self.registered_hotkeys:
                    try:
                        keyboard.remove_hotkey(hotkey)
                    except:
                        pass
                self.registered_hotkeys.clear()
            
            if self.hotkey_listener:
                self.hotkey_listener.stop()
                self.hotkey_listener = None
            
            print("[DAEMON] Sequence hotkeys monitoring stopped")
        except Exception as e:
            print(f"[DAEMON] Warning: Error stopping sequence hotkeys: {e}")
    
    def _on_key_press_pynput(self, key) -> None:
        """Handle keyboard key press events for sequence detection."""
        try:
            # Convert key to string format
            key_str = self._key_to_string(key)
            if not key_str:
                return
            
            # Check for sequence timeout
            current_time = datetime.now()
            if (self.last_key_time and 
                (current_time - self.last_key_time).total_seconds() > self.sequence_timeout):
                self.key_sequence.clear()
            
            # Add key to sequence
            self.key_sequence.append(key_str)
            self.last_key_time = current_time
            
            # Keep only last 2 keys (maximum sequence length)
            if len(self.key_sequence) > self.SEQUENCE_MAX_LENGTH:
                self.key_sequence = self.key_sequence[-self.SEQUENCE_MAX_LENGTH:]
            
            # Check if current sequence matches any configured sequences
            self._check_sequence_match()
            
        except Exception as e:
            print(f"[DAEMON] Error processing key press: {e}")
    
    def _key_to_string(self, key) -> str | None:
        """Convert pynput key to string format."""
        try:
            # Handle special keys
            if hasattr(key, 'char') and key.char is not None:
                # Regular character key with modifiers
                return key.char.lower()
            
            # Handle modifier + key combinations
            modifiers = []
            if hasattr(key, 'ctrl') and key.ctrl:
                modifiers.append('ctrl')
            if hasattr(key, 'shift') and key.shift:
                modifiers.append('shift')
            if hasattr(key, 'alt') and key.alt:
                modifiers.append('alt')
            
            # For this implementation, we need to track modifier combinations
            # This is a simplified approach - in practice, you might need more sophisticated tracking
            current_modifiers = self._get_current_modifiers()
            
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                return None  # Don't track modifier keys alone
            elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                return None
            elif hasattr(key, 'char') and key.char:
                if current_modifiers:
                    return f"{'+'.join(current_modifiers)}+{key.char.lower()}"
                return key.char.lower()
            elif hasattr(key, 'name'):
                if current_modifiers:
                    return f"{'+'.join(current_modifiers)}+{key.name.lower()}"
                return key.name.lower()
                
        except Exception:
            pass
        return None
    
    def _get_current_modifiers(self) -> list[str]:
        """Get currently pressed modifier keys."""
        # This is a simplified implementation
        # In practice, you would track modifier state
        modifiers: list[str] = []
        try:
            # Check if ctrl+shift combination is pressed
            # This is a placeholder - actual implementation would need proper modifier tracking
            import keyboard as kb
            if kb.is_pressed('ctrl') and kb.is_pressed('shift'):
                modifiers = ['ctrl', 'shift']
        except:
            pass
        return modifiers
    
    def _check_sequence_match(self) -> None:
        """Check if current key sequence matches any configured sequences."""
        if len(self.key_sequence) < self.SEQUENCE_MAX_LENGTH:
            return
        
        config: Mapping[str, Any] = self.daemon_config.get("sequence_hotkeys", {})
        sequences: Mapping[str, Any] = config.get("sequences", {})
        
        # Create current sequence string for comparison
        current_seq: list[str] = self.key_sequence[-self.SEQUENCE_MAX_LENGTH:]  # Last 2 keys
        
        for rule, seq_config in sequences.items():
            expected_sequence: Sequence[str] = seq_config.get("sequence", [])
            if len(expected_sequence) != self.SEQUENCE_MAX_LENGTH:
                continue
                
            # Simple string matching for ctrl+shift combinations
            if self._sequences_match(current_seq, expected_sequence):
                print(f"[DAEMON] Sequence hotkey detected: {rule}")
                self._apply_sequence_rule(rule)
                self.key_sequence.clear()
                break
    
    def _sequences_match(self, current: Sequence[str], expected: Sequence[str]) -> bool:
        """Check if current sequence matches expected sequence."""
        if len(current) != len(expected):
            return False
        
        # For ctrl+shift+h -> ctrl+shift+u pattern
        # This is a simplified matching - you might need more sophisticated logic
        try:
            for i, (curr_key, exp_key) in enumerate(zip(current, expected)):
                if "ctrl+shift+" in exp_key:
                    target_key = exp_key.split('+')[-1]
                    if target_key not in curr_key:
                        return False
                elif curr_key != exp_key:
                    return False
            return True
        except Exception:
            return False
    
    def _apply_sequence_rule(self, rule: str) -> None:
        """Apply transformation rule triggered by sequence hotkey."""
        try:
            # Get clipboard content
            io_manager: InputOutputManager = InputOutputManager()
            content: str = io_manager.get_clipboard_text()
            
            if not content.strip():
                return
            
            # Apply the transformation
            result: str = self.transformation_engine.apply_transformations(content, rule)
            
            if result != content:
                # Update clipboard with result
                io_manager.set_output_text(result)
                
                # Update statistics
                self.stats['transformations_applied'] += 1
                self.stats['last_transformation'] = datetime.now()
                
                print(f"[DAEMON] Sequence hotkey transformation applied: {rule}")
                print(f"[DAEMON] '{content[:30]}...' -> '{result[:30]}...'")
            
        except Exception as e:
            print(f"[DAEMON] Error applying sequence rule {rule}: {e}")