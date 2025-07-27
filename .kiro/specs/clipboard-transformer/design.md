# Design Document

## Overview

The Clipboard Transformer is a lightweight Windows application built in Python that provides real-time clipboard text transformations through configurable keyboard shortcuts. The application runs as a background service, monitoring for hotkey presses and applying predefined or custom transformation rules to clipboard content.

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
clipboard-transformer/
├── src/
│   ├── main.py              # Application entry point and orchestration
│   ├── clipboard_manager.py # Clipboard read/write operations
│   ├── hotkey_manager.py    # Keyboard shortcut handling
│   ├── transformer.py      # Text transformation engine
│   ├── config_manager.py    # Configuration file management
│   └── logger.py           # Logging functionality
├── config/
│   └── transformations.json # Default transformation rules
├── logs/                   # Log file directory
└── requirements.txt        # Python dependencies
```

### Core Components

1. **Main Application Controller**: Orchestrates all components and manages application lifecycle
2. **Clipboard Manager**: Handles Windows clipboard API interactions using `pyperclip`
3. **Hotkey Manager**: Manages global keyboard shortcuts using `pynput`
4. **Transformation Engine**: Applies regex-based text transformations
5. **Configuration Manager**: Loads and validates transformation rules from JSON
6. **Logger**: Provides structured logging with automatic rotation

## Components and Interfaces

### ClipboardManager Class
```python
class ClipboardManager:
    def get_text() -> str | None
    def set_text(text: str) -> bool
    def is_text_available() -> bool
```

### HotkeyManager Class
```python
class HotkeyManager:
    def register_hotkey(key_combination: str, callback: Callable) -> bool
    def unregister_all() -> None
    def start_listening() -> None
    def stop_listening() -> None
```

### TransformationEngine Class
```python
class TransformationEngine:
    def __init__(config_path: str)
    def apply_transformation(text: str, rule_name: str) -> str
    def get_available_transformations() -> List[str]
    def reload_rules() -> None
```

### ConfigManager Class
```python
class ConfigManager:
    def load_config(path: str) -> Dict
    def validate_config(config: Dict) -> bool
    def create_default_config(path: str) -> None
    def watch_config_changes(callback: Callable) -> None
```

## Data Models

### Transformation Rule Structure
```json
{
  "transformations": {
    "hyphen_to_underscore": {
      "name": "Hyphen to Underscore",
      "pattern": "-",
      "replacement": "_",
      "hotkey": "ctrl+alt+1",
      "description": "Convert hyphens to underscores"
    },
    "sql_in_clause": {
      "name": "SQL IN Clause",
      "pattern": "^(.+)$",
      "replacement": "'$1'",
      "separator": "\n",
      "join_with": ",",
      "hotkey": "ctrl+alt+3",
      "description": "Format lines for SQL IN clause"
    },
    "fullwidth_to_halfwidth": {
      "name": "Full-width to Half-width",
      "pattern": "[０-９Ａ-Ｚａ-ｚー]",
      "replacement": "unicode_normalize",
      "hotkey": "ctrl+alt+4",
      "description": "Convert full-width characters to half-width"
    }
  }
}
```

### Log Entry Structure
```json
{
  "timestamp": "2025-01-19T10:30:00Z",
  "transformation": "hyphen_to_underscore",
  "input_length": 15,
  "output_length": 15,
  "success": true,
  "error_message": null,
  "execution_time_ms": 2.5
}
```

## Error Handling

### Clipboard Access Errors
- Implement retry logic with exponential backoff for clipboard access failures
- Gracefully handle clipboard locks by other applications
- Provide user notification for persistent clipboard access issues

### Hotkey Registration Errors
- Detect and report hotkey conflicts with existing applications
- Provide alternative hotkey suggestions when conflicts occur
- Allow dynamic hotkey reassignment without application restart

### Configuration Errors
- Validate JSON syntax and structure on configuration load
- Provide detailed error messages for invalid transformation rules
- Fall back to default configuration when user config is corrupted

### Transformation Errors
- Catch and log regex compilation errors
- Handle Unicode encoding/decoding issues gracefully
- Provide rollback capability for failed transformations

## Testing Strategy

### Unit Testing
- Test each component in isolation using pytest
- Mock external dependencies (clipboard, keyboard) for reliable testing
- Achieve minimum 90% code coverage for core transformation logic

### Integration Testing
- Test end-to-end transformation workflows
- Verify hotkey registration and callback execution
- Test configuration loading and validation

### Manual Testing
- Test on different Windows 11 configurations
- Verify performance with large clipboard content
- Test hotkey conflicts with common applications (Office, browsers)

### Performance Testing
- Measure memory usage during extended operation
- Test transformation speed with various text sizes
- Verify log rotation and cleanup functionality

## Security Considerations

### Clipboard Data Handling
- Never log actual clipboard content to prevent data leakage
- Implement secure memory handling for sensitive text transformations
- Provide option to disable logging for privacy-sensitive environments

### Configuration Security
- Validate all user-provided regex patterns to prevent ReDoS attacks
- Sanitize file paths in configuration to prevent directory traversal
- Implement configuration file integrity checks

## Deployment Strategy

### Distribution
- Package as standalone executable using PyInstaller for easy deployment
- Provide Python source distribution for development environments
- Include comprehensive README with setup and configuration instructions

### Installation
- Create Windows installer with optional auto-start configuration
- Support portable mode for USB drive deployment
- Provide uninstaller with complete cleanup of logs and configuration