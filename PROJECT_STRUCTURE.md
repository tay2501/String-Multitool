# Project Structure

This document describes the organization and purpose of files in the String_Multitool project with modular enterprise architecture.

## 📁 Root Directory

```
String_Multitool/
├── 📄 String_Multitool.py              # 🔄 Legacy entry point (backward compatible)
├── 📄 README.md                        # 📚 Comprehensive documentation
├── 📄 pyproject.toml                   # 🔧 Modern Python project configuration
├── 📄 pyrightconfig.json               # 🔍 Pylance/Pyright type checker configuration
├── 📄 requirements.txt                 # 📦 Python dependencies
├── 📄 test_transform.py                # 🧪 Main test suite
├── 📄 build.ps1                        # 🔨 PowerShell build script
├── 📄 setup.py                         # 📦 Python package setup (legacy support)
├── 📄 LICENSE                          # 📜 MIT License
├── 📄 .gitignore                       # 🚫 Git ignore rules (comprehensive)
├── 📄 PROJECT_STRUCTURE.md             # 📋 This file
├── 📄 ARCHITECTURE.md                  # 🏗️ System architecture documentation
├── 📄 CONTRIBUTING.md                  # 🤝 Contribution guidelines
├── 📄 DELIVERABLES_SUMMARY.md          # 📊 Project deliverables summary
└── 📄 CLAUDE.md                        # 🤖 Claude Code integration instructions
```

## 📁 Core Package Structure

### `/string_multitool/` - Main Package
```
string_multitool/
├── 📄 __init__.py                      # Package initialization
├── 📄 main.py                          # 🎯 Main application interface
├── 📄 cli.py                           # 🖥️ Modern Typer CLI interface
├── 📄 application_factory.py          # 🏭 Application factory and DI container
├── 📄 exceptions.py                    # 🚨 Custom exception definitions
├── 📁 core/                           # Core business logic
│   ├── 📄 __init__.py
│   ├── 📄 config.py                   # 🔧 Configuration management
│   ├── 📄 crypto.py                   # 🔒 RSA encryption/decryption
│   ├── 📄 transformations.py          # 🔄 Text transformation engine
│   ├── 📄 types.py                    # 📋 Type definitions and protocols
│   └── 📄 dependency_injection.py     # 🔗 Dependency injection framework
├── 📁 io/                             # Input/Output operations
│   ├── 📄 __init__.py
│   ├── 📄 clipboard.py                # 📋 Clipboard operations
│   └── 📄 manager.py                  # 📊 I/O management
├── 📁 modes/                          # Application execution modes
│   ├── 📄 __init__.py
│   ├── 📄 daemon.py                   # 🔄 Daemon mode (continuous monitoring)
│   ├── 📄 daemon_config_manager.py    # 🔧 Daemon configuration management
│   ├── 📄 clipboard_monitor.py        # 📋 Clipboard monitoring functionality
│   ├── 📄 hotkey.py                   # ⌨️ Hotkey mode (global keyboard shortcuts)
│   ├── 📄 hotkey_sequence_manager.py  # ⌨️ Hotkey sequence management
│   └── 📄 interactive.py              # 💬 Interactive mode
└── 📁 utils/                          # Utility modules
    ├── 📄 __init__.py
    └── 📄 logger.py                   # 📝 Logging utilities
```

## 📁 Configuration Directory

### `/config/` - Configuration Files
```
config/
├── 📄 transformation_rules.json       # 🔄 Transformation rule definitions
├── 📄 security_config.json           # 🔒 Security and encryption settings
├── 📄 daemon_config.json             # 🤖 Daemon mode configuration
├── 📄 hotkey_config.json             # ⌨️ Hotkey configuration
├── 📄 logging_config.json            # 📝 Logging configuration
└── 📄 logging_config_local.json      # 📝 Local logging overrides
```

**Purpose**: Externalized configuration for rules, security, and daemon settings.
- `transformation_rules.json`: Defines all transformation rules with metadata, categories, and examples
- `security_config.json`: RSA encryption parameters, key sizes, and security settings
- `daemon_config.json`: Daemon mode presets and monitoring configuration

## 📁 Development Configuration

### `/.vscode/` - VSCode Settings
```
.vscode/
└── 📄 settings.json                   # 🔧 Python interpreter and Pylance configuration
```

**Purpose**: IDE configuration for optimal development experience with Python type checking.

### `/rsa/` - Encryption Keys (Auto-generated)
```
rsa/
├── 📄 rsa                             # 🔐 Private key (PEM format, git-ignored)
└── 📄 rsa.pub                         # 🔓 Public key (PEM format, git-ignored)
```

**Purpose**: RSA-4096 key storage for encryption/decryption operations. Auto-generated on first use.

### `/logs/` - Application Logs
```
logs/
├── 📄 string_multitool.log           # 📝 Application runtime logs
└── 📄 debug.log                      # 🐛 Debug-level logging
```

**Purpose**: Runtime logging for debugging and monitoring with multiple log levels.

## 📁 Build and Distribution

### Build Artifacts (Generated)
```
build/                                 # 🔨 Build intermediate files
dist/                                  # 📦 Distribution packages
String_Multitool.exe                   # 💻 Executable file (when built)
```

**Purpose**: Generated during build process, excluded from version control.

## 🏗️ Architecture Overview

### Core Components

1. **ApplicationInterface** (`main.py`)
   - Main application coordinator
   - Handles mode switching and user interaction
   - Manages component initialization and lifecycle

2. **ApplicationFactory** (`application_factory.py`)
   - Dependency injection container
   - Component creation and lifecycle management
   - Configuration-driven component assembly

3. **TextTransformationEngine** (`core/transformations.py`)
   - Core text transformation logic
   - Rule parsing and sequential processing
   - Configuration-driven rule registration

4. **CryptographyManager** (`core/crypto.py`)
   - RSA-4096 key management
   - Hybrid AES+RSA encryption
   - Secure key storage and permissions

5. **ConfigurationManager** (`core/config.py`)
   - JSON configuration loading and caching
   - Validation and error handling
   - Runtime configuration updates

6. **InputOutputManager** (`io/manager.py`)
   - Clipboard operations
   - Stdin/stdout handling
   - Cross-platform compatibility

7. **Modern CLI Interface** (`cli.py`)
   - Typer-based command-line interface
   - Rich terminal output
   - Subcommand organization

### Application Modes

1. **Interactive Mode** (`modes/interactive.py`)
   - Real-time clipboard monitoring
   - Dynamic text refresh
   - Command-driven interface

2. **Daemon Mode** (`modes/daemon.py`)
   - Background clipboard monitoring
   - Automatic transformations
   - Preset-based configuration

3. **Hotkey Mode** (`modes/hotkey.py`)
   - Global hotkey support
   - Sequence-based hotkey management
   - System tray integration

### Type Safety System

- **Protocol Definitions** (`types.py`): Structural typing for dependency injection
- **Dataclass Models**: Type-safe configuration and rule definitions
- **Generic Containers**: Reusable patterns for state and result management
- **TypeGuard Functions**: Runtime type validation

## 📊 Development Workflow

### Entry Points
- **Legacy CLI**: `String_Multitool.py` - Backward compatible entry point
- **Modern CLI**: `python -m string_multitool.main` or `string-multitool` command
- **Package Import**: `from string_multitool.main import ApplicationInterface`
- **Direct Execution**: `python string_multitool/main.py`

### Configuration Management
- JSON-based configuration files in `/config/`
- Runtime configuration loading with caching
- Type-safe configuration validation

### Testing Strategy
- Unit tests for transformation rules
- Integration tests for end-to-end workflows
- Security tests for cryptographic operations

### Build System
- PowerShell build script (`build.ps1`)
- PyInstaller for executable generation
- Modern pyproject.toml configuration

## 🔧 Development Environment

### Required Tools
- Python 3.10+
- VSCode with Pylance extension
- PowerShell (for Windows build)

### Configuration Files
- `pyproject.toml`: Project metadata, dependencies, build configuration
- `pyrightconfig.json`: Type checker configuration
- `.vscode/settings.json`: IDE Python interpreter settings
- `.gitignore`: Comprehensive ignore patterns

### Type Checking
- Full type hints throughout codebase
- Pylance integration with VSCode
- MyPy compatibility for CI/CD

## 📈 Scalability Features

### Modular Design
- Clean separation of concerns
- Dependency injection via protocols
- Extensible rule system

### Configuration-Driven
- Rules defined in JSON configuration
- Security parameters externalized
- Runtime behavior customization

### Professional Error Handling
- Custom exception hierarchy
- Contextual error messages
- Graceful degradation

This structure supports both current functionality and future enhancements while maintaining enterprise-grade code quality and type safety.