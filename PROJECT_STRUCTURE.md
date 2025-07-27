# Project Structure

This document describes the organization and purpose of files in the Clipboard Transformer project.

## 📁 Root Directory

```
clipboard-transformer/
├── 📄 manual_transform.py              # ⭐ Main application (recommended)
├── 📄 clipboard-transformer-portable.py # Optional hotkey mode
├── 📄 README.md                        # Comprehensive documentation
├── 📄 requirements.txt                 # Python dependencies
├── 📄 LICENSE                          # MIT License
├── 📄 .gitignore                       # Git ignore rules
├── 📄 PROJECT_STRUCTURE.md             # This file
└── 📄 CONTRIBUTING.md                  # Contribution guidelines
```

## 📁 Core Directories

### `/config/` - Configuration Files
```
config/
└── 📄 transformations.json            # Main configuration file
```

**Purpose**: Contains all configuration files for the application.
- `transformations.json`: Defines all 26 transformations (a-z) with metadata

### `/src/` - Source Code
```
src/
├── 📄 __init__.py                      # Package initialization
├── 📄 __version__.py                   # Version information
├── 📄 main.py                          # Main application entry point
├── 📄 clipboard_manager.py             # Clipboard operations
├── 📄 config_manager.py                # Configuration handling
├── 📄 hotkey_manager.py                # Global hotkey management
├── 📄 transformer.py                   # Text transformation engine
└── 📄 logger.py                        # Logging system
```

**Purpose**: Core application source code organized by functionality.

### `/tests/` - Test Suite
```
tests/
├── 📄 __init__.py                      # Test package initialization
├── 📄 test_main.py                     # Main application tests
├── 📄 test_clipboard_manager.py        # Clipboard operation tests
├── 📄 test_config_manager.py           # Configuration tests
├── 📄 test_hotkey_manager.py           # Hotkey management tests
├── 📄 test_transformer.py              # Transformation engine tests
├── 📄 test_logger.py                   # Logging system tests
└── 📄 test_error_handling_integration.py # Integration tests
```

**Purpose**: Comprehensive test suite covering all functionality.

### `/logs/` - Application Logs
```
logs/
├── 📄 .gitkeep                         # Keep directory in git
└── 📄 *.log                           # Application log files (auto-generated)
```

**Purpose**: Runtime logs for debugging and monitoring.
- Automatically cleaned up (keeps 3 most recent files)
- JSON format for structured logging

### `/.github/` - GitHub Integration
```
.github/
├── workflows/
│   └── 📄 build.yml                    # CI/CD pipeline
└── ISSUE_TEMPLATE/
    ├── 📄 bug_report.md                # Bug report template
    └── 📄 feature_request.md           # Feature request template
```

**Purpose**: GitHub-specific files for automation and issue management.

## 📁 Build and Distribution

### Build Scripts
```
├── 📄 build.bat                        # Windows batch build script
├── 📄 build.ps1                        # PowerShell build script
├── 📄 install.ps1                      # Installation script
├── 📄 clipboard_transformer.spec       # PyInstaller specification
└── 📄 version_info.txt                 # Windows executable version info
```

**Purpose**: Scripts for building and distributing the application.

## 📄 Key Files Explained

### `manual_transform.py` ⭐
**Primary application file** - Recommended for all users.
- **Purpose**: User-friendly manual transformation interface
- **Features**: 26 transformations, sequential processing, smart UI
- **Compatibility**: Works on all Windows systems, Japanese IME, HHKB
- **Usage**: `python manual_transform.py`

### `clipboard-transformer-portable.py`
**Alternative hotkey-based application**.
- **Purpose**: Global hotkey support for compatible systems
- **Features**: Background operation, system tray integration
- **Compatibility**: Best on English Windows with standard keyboards
- **Usage**: `python clipboard-transformer-portable.py`

### `config/transformations.json`
**Main configuration file** defining all transformations.
- **Structure**: JSON with transformations, categories, settings
- **Features**: 26 transformations (a-z), metadata, examples
- **Auto-reload**: Changes take effect immediately
- **Validation**: Automatic syntax and structure checking

### `src/transformer.py`
**Core transformation engine**.
- **Purpose**: Implements all text transformation logic
- **Features**: Regex processing, Unicode handling, error management
- **Extensibility**: Easy to add new transformation types

### `src/config_manager.py`
**Configuration management system**.
- **Purpose**: Load, validate, and monitor configuration files
- **Features**: JSON validation, file watching, error recovery
- **Auto-reload**: Detects changes and reloads automatically

### `src/hotkey_manager.py`
**Global hotkey management** (for hotkey mode).
- **Purpose**: Register and handle global keyboard shortcuts
- **Features**: Conflict detection, error recovery, cross-platform support
- **Compatibility**: Works with various keyboard layouts

### `src/clipboard_manager.py`
**Clipboard operations handler**.
- **Purpose**: Safe clipboard read/write operations
- **Features**: Error handling, retry logic, format detection
- **Reliability**: Handles clipboard conflicts gracefully

### `src/logger.py`
**Structured logging system**.
- **Purpose**: Comprehensive application logging
- **Features**: JSON format, automatic rotation, performance metrics
- **Storage**: Logs stored in `/logs/` directory

## 🔄 Application Flow

### Manual Mode Flow
```
User runs manual_transform.py
    ↓
Display clipboard content and all transformations
    ↓
User selects transformation(s) (e.g., "ad")
    ↓
Preview what will be applied
    ↓
Apply transformations sequentially
    ↓
Copy result to clipboard
    ↓
Option to continue with result
```

### Hotkey Mode Flow
```
User runs clipboard-transformer-portable.py
    ↓
Load configuration and register hotkeys
    ↓
Run in background (system tray)
    ↓
User presses registered hotkey
    ↓
Apply corresponding transformation
    ↓
Copy result to clipboard
```

## 🏗️ Architecture

### Modular Design
- **Separation of Concerns**: Each module has a specific responsibility
- **Loose Coupling**: Modules interact through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together

### Error Handling Strategy
- **Graceful Degradation**: Application continues working even if some features fail
- **User-Friendly Messages**: Clear error messages for users
- **Comprehensive Logging**: Detailed logs for debugging

### Configuration Management
- **Centralized**: All configuration in one JSON file
- **Validated**: Automatic syntax and structure validation
- **Extensible**: Easy to add new transformations and settings

## 🧪 Testing Strategy

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Error Handling Tests**: Edge case and error condition testing

### Test Organization
- **Mirror Source Structure**: Test files mirror source file organization
- **Descriptive Names**: Test names clearly describe what is being tested
- **Comprehensive Coverage**: All critical paths are tested

## 📦 Distribution Strategy

### Multiple Distribution Methods
1. **Python Script**: Direct execution with Python interpreter
2. **Portable Executable**: Self-contained Windows executable
3. **Installer**: System-wide installation with shortcuts

### Build Process
1. **Dependency Installation**: Install all required packages
2. **Testing**: Run full test suite
3. **Building**: Create executable with PyInstaller
4. **Packaging**: Create distribution packages
5. **Validation**: Test built packages

## 🔧 Development Workflow

### Adding New Features
1. **Design**: Plan the feature and its integration
2. **Implementation**: Write code following project patterns
3. **Testing**: Add comprehensive tests
4. **Documentation**: Update relevant documentation
5. **Integration**: Ensure compatibility with existing features

### Code Quality Standards
- **Type Hints**: Use type annotations for better code clarity
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Proper exception handling throughout
- **Consistency**: Follow established patterns and conventions

This structure ensures maintainability, extensibility, and ease of use for both developers and end users.