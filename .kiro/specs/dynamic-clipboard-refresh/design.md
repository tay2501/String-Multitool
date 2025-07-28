# Dynamic Clipboard Refresh Feature - Design

## Overview

This design implements dynamic clipboard refresh functionality for String_Multitool's interactive mode, allowing users to seamlessly work with multiple text snippets without restarting the application. The solution extends the existing ApplicationInterface class with enhanced clipboard management capabilities.

## Architecture

### Core Components

1. **ClipboardMonitor**: New class for managing clipboard state and change detection
2. **InteractiveSession**: Enhanced session management with clipboard refresh capabilities  
3. **CommandProcessor**: Extended command processing for new clipboard commands
4. **ApplicationInterface**: Updated with new interactive commands and clipboard management

### Component Interactions

```
ApplicationInterface
├── InteractiveSession
│   ├── ClipboardMonitor (optional auto-detection)
│   ├── CommandProcessor (command parsing)
│   └── InputOutputManager (clipboard operations)
└── TextTransformationEngine (existing)
```

## Components and Interfaces

### ClipboardMonitor Class

```python
class ClipboardMonitor:
    """Monitors clipboard changes for auto-detection functionality."""
    
    def __init__(self, io_manager: InputOutputManager):
        self.io_manager = io_manager
        self.last_content = ""
        self.last_check_time = None
        self.is_monitoring = False
        self.check_interval = 1.0  # seconds
    
    def start_monitoring(self) -> None:
        """Start clipboard monitoring in background."""
        
    def stop_monitoring(self) -> None:
        """Stop clipboard monitoring."""
        
    def check_for_changes(self) -> Optional[str]:
        """Check if clipboard content has changed."""
        
    def get_current_content(self) -> str:
        """Get current clipboard content."""
```

### InteractiveSession Class

```python
class InteractiveSession:
    """Manages interactive session state and clipboard operations."""
    
    def __init__(self, io_manager: InputOutputManager, transformation_engine: TextTransformationEngine):
        self.io_manager = io_manager
        self.transformation_engine = transformation_engine
        self.current_text = ""
        self.text_source = "clipboard"  # clipboard, pipe, manual
        self.last_update_time = None
        self.clipboard_monitor = ClipboardMonitor(io_manager)
        self.auto_detection_enabled = False
    
    def refresh_from_clipboard(self) -> bool:
        """Refresh working text from clipboard."""
        
    def update_working_text(self, text: str, source: str) -> None:
        """Update current working text with source tracking."""
        
    def get_status_info(self) -> dict:
        """Get current session status information."""
        
    def toggle_auto_detection(self, enabled: bool) -> None:
        """Enable/disable automatic clipboard detection."""
```

### Enhanced Command Processing

```python
class CommandProcessor:
    """Processes interactive commands including clipboard operations."""
    
    CLIPBOARD_COMMANDS = {
        'refresh': 'Refresh input text from clipboard',
        'reload': 'Alias for refresh',
        'r': 'Short alias for refresh',
        'auto': 'Toggle automatic clipboard detection',
        'status': 'Show current session status',
        'clear': 'Clear current working text',
        'copy': 'Copy working text to clipboard',
        'commands': 'Show all available commands',
        'cmd': 'Short alias for commands'
    }
    
    def process_command(self, command: str, session: InteractiveSession) -> CommandResult:
        """Process interactive command and return result."""
```

## Data Models

### Session State

```python
@dataclass
class SessionState:
    """Represents current interactive session state."""
    current_text: str
    text_source: str  # "clipboard", "pipe", "manual"
    last_update_time: datetime
    character_count: int
    auto_detection_enabled: bool
    clipboard_monitor_active: bool
```

### Command Result

```python
@dataclass
class CommandResult:
    """Result of command processing."""
    success: bool
    message: str
    should_continue: bool = True
    updated_text: Optional[str] = None
```

## Error Handling

### Clipboard Access Errors
- Graceful handling of clipboard access failures
- Fallback to manual text input when clipboard unavailable
- Clear error messages with suggested solutions

### Auto-Detection Errors
- Automatic disabling of monitoring on repeated failures
- User notification of monitoring status changes
- Resource cleanup on error conditions

### Memory Management
- Size limits for clipboard content (configurable)
- Warning messages for large content
- Option to truncate or reject oversized content

## Testing Strategy

### Unit Tests
- ClipboardMonitor functionality
- Command processing logic
- Session state management
- Error condition handling

### Integration Tests
- End-to-end clipboard refresh workflow
- Auto-detection functionality
- Command interaction with transformation engine
- Cross-platform clipboard behavior

### Performance Tests
- Memory usage with large clipboard content
- Auto-detection polling efficiency
- Response time for clipboard operations

## Implementation Plan

### Phase 1: Core Clipboard Refresh
1. Implement basic refresh command ('refresh', 'r')
2. Add session state tracking
3. Update interactive mode with new commands
4. Basic error handling

### Phase 2: Auto-Detection
1. Implement ClipboardMonitor class
2. Add background monitoring capability
3. Integrate with interactive session
4. Performance optimization

### Phase 3: Enhanced Commands
1. Add status, clear, copy commands
2. Implement command help system
3. Improve user feedback and messaging
4. Cross-platform testing

### Phase 4: Polish and Optimization
1. Performance tuning
2. Memory management improvements
3. Enhanced error messages
4. Documentation updates

## Configuration Options

### New Configuration Settings
```json
{
  "interactive_mode": {
    "clipboard_refresh": {
      "auto_detection_interval": 1.0,
      "max_content_size": 1048576,
      "enable_auto_detection_by_default": false,
      "show_character_count": true,
      "show_timestamps": true
    }
  }
}
```

## User Interface Changes

### Enhanced Interactive Prompt
```
String_Multitool - Interactive Mode
========================================
Input text: 'Hello World' (15 chars, from clipboard, updated 14:30:25)
Auto-detection: OFF

Available commands: help, refresh, auto, status, clear, copy, quit
Enter transformation rules (e.g., /t/l) or command:
Rules: 
```

### Command Help Display
```
Interactive Commands:
  refresh, reload, r    - Refresh input text from clipboard
  auto [on|off]        - Toggle automatic clipboard detection
  status               - Show current session information
  clear                - Clear current working text
  copy                 - Copy working text to clipboard
  commands, cmd        - Show this command list
  help                 - Show transformation rules
  quit, q, exit        - Exit application

Transformation Rules:
  /t/l                 - Trim and lowercase
  /enc                 - Encrypt text
  [... existing rules ...]
```

## Backward Compatibility

### Preserved Behavior
- All existing transformation rules work unchanged
- Current command-line interface remains identical
- Existing interactive mode commands (help, quit) unchanged
- Pipe input and clipboard input behavior preserved

### Migration Strategy
- New commands are additive only
- No breaking changes to existing functionality
- Optional features can be disabled via configuration
- Graceful degradation when clipboard unavailable

## Security Considerations

### Clipboard Content Validation
- Size limits to prevent memory exhaustion
- Content sanitization for display purposes
- No automatic execution of clipboard content

### Auto-Detection Privacy
- User control over when monitoring is active
- Clear indication of monitoring status
- Option to disable auto-detection permanently

### Memory Security
- Secure cleanup of sensitive clipboard content
- No persistent storage of clipboard history
- Proper disposal of large text buffers