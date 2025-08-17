"""
Integration test for hotkey mode functionality.

This script tests the hotkey mode initialization and basic functionality
without actually registering global hotkeys.
"""

import sys

from string_multitool.core.config import ConfigurationManager
from string_multitool.core.transformations import TextTransformationEngine
from string_multitool.io.manager import InputOutputManager
from string_multitool.modes.hotkey import HotkeyMode, SequenceState


def test_hotkey_mode_initialization():
    """Test HotkeyMode initialization."""
    print("Testing HotkeyMode initialization...")

    try:
        # Initialize components
        config_manager = ConfigurationManager()
        io_manager = InputOutputManager()
        transformation_engine = TextTransformationEngine(config_manager)

        # Initialize hotkey mode
        hotkey_mode = HotkeyMode(io_manager, transformation_engine, config_manager)

        print(f"  OK: HotkeyMode initialized successfully")
        print(f"  OK: Direct hotkeys: {len(hotkey_mode._direct_hotkeys)}")
        print(f"  OK: Sequence hotkeys: {len(hotkey_mode._sequence_hotkeys)}")
        print(f"  OK: Timeout: {hotkey_mode.sequence_state.timeout_seconds}s")

        return True

    except Exception as e:
        print(f"  ERROR: Initialization failed: {e}")
        return False


def test_configuration_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")

    try:
        config_manager = ConfigurationManager()
        hotkey_config = config_manager.load_hotkey_config()

        required_keys = ["hotkey_settings", "direct_hotkeys"]
        for key in required_keys:
            if key not in hotkey_config:
                print(f"  ERROR: Missing configuration key: {key}")
                return False

        print(f"  OK: Configuration loaded successfully")
        print(
            f"  OK: Hotkey enabled: {hotkey_config['hotkey_settings'].get('enabled')}"
        )
        print(f"  OK: Direct hotkeys count: {len(hotkey_config['direct_hotkeys'])}")
        print(
            f"  OK: Sequence hotkeys count: {len(hotkey_config.get('sequence_hotkeys', {}))}"
        )

        return True

    except Exception as e:
        print(f"  ERROR: Configuration loading failed: {e}")
        return False


def test_state_management():
    """Test hotkey state management."""
    print("Testing state management...")

    try:
        state = SequenceState(timeout_seconds=1.0)

        # Test initial state
        if state.is_sequence_active():
            print("  ERROR: State should be inactive initially")
            return False

        # Test sequence start
        state.start_sequence("h")
        if not state.is_sequence_active():
            print("  ERROR: State should be active after start")
            return False

        # Test sequence end
        state.end_sequence()
        if state.is_sequence_active():
            print("  ERROR: State should be inactive after end")
            return False

        print("  OK: State management working correctly")
        return True

    except Exception as e:
        print(f"  ERROR: State management failed: {e}")
        return False


def test_command_execution():
    """Test command execution (mock)."""
    print("Testing command execution...")

    try:
        config_manager = ConfigurationManager()
        io_manager = InputOutputManager()
        transformation_engine = TextTransformationEngine(config_manager)
        hotkey_mode = HotkeyMode(io_manager, transformation_engine, config_manager)

        # Test command execution (will read from actual clipboard)
        # Note: This test assumes clipboard has some content
        hotkey_mode._execute_command("/l")

        print("  OK: Command execution completed without errors")
        return True

    except Exception as e:
        print(f"  ERROR: Command execution failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 50)
    print("HotkeyMode Integration Tests")
    print("=" * 50)

    tests = [
        test_hotkey_mode_initialization,
        test_configuration_loading,
        test_state_management,
        test_command_execution,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"  ERROR: Test failed with exception: {e}")
            print()

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("All tests passed! HotkeyMode is ready for use.")
        print("\nTo use hotkey mode:")
        print("  python String_Multitool.py --hotkey")
        print(
            "  Direct shortcuts: Ctrl+Shift+L (lowercase), Ctrl+Shift+U (uppercase), etc."
        )
        print("  Sequence shortcuts: Ctrl+Shift+H then U (hyphen to underscore), etc.")
        return 0
    else:
        print(f"{total - passed} test(s) failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
