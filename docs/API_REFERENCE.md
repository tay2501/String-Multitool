# String-Multitool API Reference

This document provides comprehensive API reference for String-Multitool components following PEP 257 docstring standards and modern documentation practices.

## Table of Contents

- [Core Architecture](#core-architecture)
- [Application Interface](#application-interface)
- [Transformation Engine](#transformation-engine)
- [I/O Management](#io-management)
- [Configuration System](#configuration-system)
- [Security Components](#security-components)
- [Interactive Components](#interactive-components)
- [Exception Handling](#exception-handling)

## Core Architecture

String-Multitool follows an MVC (Model-View-Controller) architecture pattern optimized for command-line applications.

### Architecture Overview

```
string_multitool/
├── models/          # Business Logic Layer (Model)
│   ├── config.py            # Configuration management
│   ├── transformations.py   # Core transformation engine
│   ├── crypto.py           # Cryptography operations
│   ├── interactive.py      # Interactive session management
│   └── types.py            # Type definitions and protocols
├── io/             # View/Controller Layer
│   ├── manager.py          # I/O operations and clipboard handling
│   └── clipboard.py        # Clipboard monitoring
├── transformations/ # Transformation Implementations
│   ├── basic_transformations.py      # Basic text operations
│   ├── case_transformations.py       # Case conversion operations
│   ├── encryption_transformations.py # Security operations
│   └── ...                          # Other transformation modules
├── utils/          # Utility Components
│   ├── unified_logger.py   # Logging infrastructure
│   └── lifecycle_manager.py # Application lifecycle
└── main.py         # Application Entry Point
```

## Application Interface

### ApplicationInterface Class

The main application interface coordinating all String-Multitool components.

**Location**: `string_multitool.main.ApplicationInterface`

#### Constructor

```python
def __init__(
    self,
    config_manager: ConfigurationManager,
    transformation_engine: TextTransformationEngine,
    io_manager: InputOutputManager,
    crypto_manager: CryptographyManager | None = None,
) -> None:
    """Initialize application interface with dependency injection.
    
    Args:
        config_manager: Configuration manager instance
        transformation_engine: Text transformation engine instance  
        io_manager: Input/output manager instance
        crypto_manager: Optional cryptography manager for encryption features
        
    Raises:
        ValidationError: If any required dependency is invalid
    """
```

#### Key Methods

##### `run() -> None`

Main application entry point that handles command-line parsing and execution modes.

```python
def run(self) -> None:
    """Main application entry point.
    
    Parses command line arguments and routes to appropriate execution mode:
    - Interactive mode for real-time clipboard monitoring
    - Rule mode for single transformation execution  
    - Help mode for documentation display
    """
```

##### `display_help() -> None`

Display comprehensive help information including available transformation rules.

```python
def display_help(self) -> None:
    """Display help information.
    
    Shows:
    - Available transformation rules with descriptions and examples
    - Usage patterns for different execution modes
    - Interactive command reference
    """
```

## Transformation Engine

### TextTransformationEngine Class

Advanced text transformation engine with configurable rules and comprehensive error handling.

**Location**: `string_multitool.models.transformations.TextTransformationEngine`

#### Key Features

- **Rule-Based Processing**: Configurable transformation rules via JSON
- **Sequential Application**: Chain multiple transformations (`/t/l/u`)
- **Argument Support**: Advanced rules with parameters (`/r 'old' 'new'`)
- **Error Context**: Detailed error information for debugging
- **Extensibility**: Easy addition of new transformation rules

#### Constructor

```python
def __init__(self, config_manager: ConfigManagerProtocol) -> None:
    """Initialize transformation engine with EAFP pattern.
    
    Args:
        config_manager: Configuration manager protocol instance
        
    Raises:
        TransformationError: If initialization fails
        ValidationError: If config_manager is invalid
    """
```

#### Core Methods

##### `apply_transformations(text: str, rule_chain: str) -> str`

Apply a sequence of transformation rules to input text.

```python
def apply_transformations(self, text: str, rule_chain: str) -> str:
    """Apply transformation rules to text.
    
    Args:
        text: Input text to transform
        rule_chain: Transformation rules (e.g., '/t/l/u' for trim+lowercase+uppercase)
        
    Returns:
        Transformed text
        
    Raises:
        TransformationError: If transformation fails
        ValidationError: If input parameters are invalid
        
    Examples:
        >>> engine.apply_transformations("  Hello World  ", "/t/l")
        "hello world"
        
        >>> engine.apply_transformations("Hello World", "/r 'World' 'Python'")
        "Hello Python"
    """
```

##### `get_available_rules() -> dict[str, TransformationRule]`

Get all available transformation rules with their metadata.

```python
def get_available_rules(self) -> dict[str, TransformationRule]:
    """Get all available transformation rules.
    
    Returns:
        Dictionary mapping rule names to TransformationRule objects
        containing description, examples, and metadata
        
    Examples:
        >>> rules = engine.get_available_rules()
        >>> print(rules['t'].description)
        "Trim whitespace from both ends"
    """
```

### Transformation Rules Reference

#### Basic Transformations

| Rule | Description | Example | Result |
|------|-------------|---------|--------|
| `/t` | Trim whitespace | `"  hello  " -> "/t"` | `"hello"` |
| `/l` | Convert to lowercase | `"HELLO" -> "/l"` | `"hello"` |
| `/u` | Convert to uppercase | `"hello" -> "/u"` | `"HELLO"` |

#### Case Transformations

| Rule | Description | Example | Result |
|------|-------------|---------|--------|
| `/p` | Convert to PascalCase | `"hello world" -> "/p"` | `"HelloWorld"` |
| `/c` | Convert to camelCase | `"hello world" -> "/c"` | `"helloWorld"` |
| `/s` | Convert to snake_case | `"hello world" -> "/s"` | `"hello_world"` |

#### String Operations

| Rule | Description | Example | Result |
|------|-------------|---------|--------|
| `/r 'old' 'new'` | Replace text | `"hello world" -> "/r 'world' 'python'"` | `"hello python"` |
| `/S '+'` | Split and join with separator | `"a,b,c" -> "/S '+'"` | `"a+b+c"` |

#### Advanced Operations

| Rule | Description | Example | Result |
|------|-------------|---------|--------|
| `/e` | Encrypt text (requires crypto) | `"secret" -> "/e"` | `"encrypted_base64"` |
| `/d` | Decrypt text (requires crypto) | `"encrypted_base64" -> "/d"` | `"secret"` |

## I/O Management

### InputOutputManager Class

Manages input and output operations for the application with proper error handling.

**Location**: `string_multitool.io.manager.InputOutputManager`

#### Key Features

- **Multi-Source Input**: Clipboard, stdin, or manual input
- **Cross-Platform Clipboard**: Works on Windows, macOS, Linux
- **Pipe Detection**: Automatic stdin/clipboard switching
- **Error Resilience**: Graceful fallback mechanisms

#### Constructor

```python
def __init__(self) -> None:
    """Initialize the I/O manager.
    
    Automatically detects clipboard availability and configures
    appropriate input/output mechanisms.
    """
```

#### Core Methods

##### `get_input_text() -> str`

Get input text from the most appropriate source.

```python
def get_input_text(self) -> str:
    """Get input text from the most appropriate source.
    
    Determines whether to read from stdin (pipe) or clipboard
    based on the execution context.
    
    Returns:
        Input text from pipe or clipboard
        
    Raises:
        ClipboardError: If clipboard operations fail
        IOError: If stdin reading fails
    """
```

##### `set_output_text(text: str) -> None`

Set output text to clipboard or stdout.

```python
def set_output_text(self, text: str) -> None:
    """Set output text to clipboard.
    
    Args:
        text: Text to copy to clipboard
        
    Raises:
        ClipboardError: If clipboard operations fail
    """
```

## Configuration System

### ConfigurationManager Class

Manages application configuration from JSON files with caching and validation.

**Location**: `string_multitool.models.config.ConfigurationManager`

#### Key Features

- **JSON-Based Configuration**: External configuration files
- **Caching**: Performance-optimized configuration loading
- **Validation**: Type-safe configuration access
- **Hot-Reloading**: Dynamic configuration updates

#### Constructor

```python
def __init__(self, config_dir: str | Path = "config") -> None:
    """Initialize configuration manager.
    
    Args:
        config_dir: Directory containing configuration files
        
    Raises:
        ConfigurationError: If config directory is not accessible
    """
```

#### Configuration Files

- **`transformation_rules.json`**: Rule definitions and metadata
- **`security_config.json`**: Cryptography and security settings  
- **`hotkey_config.json`**: Keyboard shortcut configurations

## Security Components

### CryptographyManager Class

Military-grade RSA-4096 + AES-256 hybrid encryption system.

**Location**: `string_multitool.models.crypto.CryptographyManager`

#### Security Features

- **RSA-4096 Encryption**: Public-key cryptography for key exchange
- **AES-256-CBC**: Symmetric encryption for data payload
- **Hybrid Architecture**: Combines RSA + AES for optimal security/performance
- **Secure Key Management**: Auto-generation with proper file permissions
- **Base64 Encoding**: Safe text representation of encrypted data

#### Constructor

```python
def __init__(self, config_manager: ConfigManagerProtocol) -> None:
    """Initialize cryptography manager.
    
    Args:
        config_manager: Configuration manager for security settings
        
    Raises:
        ConfigurationError: If security configuration is invalid
        CryptographyError: If cryptographic initialization fails
    """
```

## Interactive Components

### InteractiveSession Class

Manages interactive mode sessions with real-time clipboard monitoring.

**Location**: `string_multitool.models.interactive.InteractiveSession`

#### Key Features

- **Real-Time Monitoring**: Automatic clipboard change detection
- **Session State**: Persistent state management
- **Auto-Detection**: Smart content type recognition
- **Performance Optimized**: Efficient polling mechanisms

### CommandProcessor Class

Processes interactive commands and manages session control.

**Location**: `string_multitool.models.interactive.CommandProcessor`

#### Available Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `help` | Show transformation rules | `> help` |
| `commands` | List interactive commands | `> commands` |
| `refresh` | Reload clipboard content | `> refresh` |
| `quit` / `exit` | Exit interactive mode | `> quit` |

## Exception Handling

String-Multitool uses a comprehensive exception hierarchy for precise error handling.

### Exception Hierarchy

```python
StringMultitoolError                    # Base exception
├── ValidationError                     # Input validation failures  
├── TransformationError                 # Transformation processing errors
├── ConfigurationError                  # Configuration file issues
├── ClipboardError                      # Clipboard operation failures
└── CryptographyError                   # Encryption/decryption errors
```

### Error Context

All exceptions include contextual information for debugging:

```python
try:
    result = engine.apply_transformations(text, rule)
except TransformationError as e:
    print(f"Error: {e}")
    print(f"Context: {e.context}")  # Additional debugging information
```

## Type System

String-Multitool uses comprehensive type hints following PEP 484 standards.

### Key Protocols

```python
# Configuration management protocol
class ConfigManagerProtocol(Protocol):
    def get_config(self, key: str, default: Any = None) -> Any: ...

# Transformation engine protocol
class TransformationEngineProtocol(Protocol):
    def apply_transformations(self, text: str, rules: str) -> str: ...
    def get_available_rules(self) -> dict[str, TransformationRule]: ...

# I/O manager protocol  
class IOManagerProtocol(Protocol):
    def get_input_text(self) -> str: ...
    def set_output_text(self, text: str) -> None: ...
```

## Best Practices

### Extension Development

When adding new transformation rules:

1. **Define Rule Metadata**: Add rule definition to `transformation_rules.json`
2. **Implement Method**: Create transformation method in appropriate module
3. **Register Rule**: Add to `TextTransformationEngine._initialize_rules()`
4. **Add Tests**: Comprehensive test coverage in `test_transform.py`
5. **Update Documentation**: Add to help system and this API reference

### Error Handling

Always use the provided exception hierarchy and include context information:

```python
try:
    # Transformation logic
    result = process_text(text)
except Exception as e:
    raise TransformationError(
        f"Processing failed: {e}",
        {"input_length": len(text), "rule": rule_name}
    ) from e
```

### Performance Considerations

- Configuration caching is automatic but can be invalidated if needed
- Clipboard monitoring uses efficient polling with configurable intervals
- Cryptographic operations are optimized but inherently expensive
- Large text processing is memory-efficient with streaming where possible

---

*This API reference follows PEP 257 docstring conventions and modern Python documentation standards. For usage examples and tutorials, see the main README.md.*