# Developer Guide

This guide provides comprehensive information for developers working on String-Multitool, including setup instructions, development workflows, and contribution guidelines. The project follows **2025 Python packaging best practices** with PEP 621 compliance and modern toolchain integration.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Adding New Features](#adding-new-features)
- [Tab Completion System](#tab-completion-system)
- [MCP Integration (Context7 & Serena)](#mcp-integration-context7--serena)
- [Security Considerations](#security-considerations)
- [Performance Guidelines](#performance-guidelines)
- [Debugging and Troubleshooting](#debugging-and-troubleshooting)

## Development Environment Setup

### Prerequisites (2025 Standards)

- **Python 3.12+**: String-Multitool uses modern Python features and 2025 language standards
- **[UV 0.5.9+](https://docs.astral.sh/uv/)**: Modern Python package manager (strongly recommended) - 10-100x faster than pip
- **Git**: Version control
- **VS Code** or **PyCharm**: Recommended IDEs with Python support
- **Hatchling**: Modern build backend (automatically managed by pyproject.toml)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/[your-username]/String-Multitool.git
cd String-Multitool

# Setup virtual environment with uv (2025 standard - fastest and most comprehensive)
uv sync --group dev --all-extras

# Alternative with traditional pip (slower but compatible)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev,build]"

# Verify installation
uv run python String_Multitool.py help

# Run tests to verify setup
uv run pytest tests/ -v
```

### Development Tools Configuration

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.sortImports.args": ["--profile", "black"]
}
```

#### Pre-commit Hooks

String-Multitool uses pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Project Structure

### Architectural Decision: Simple, Focused Design

**Project Split for Simplicity (2025 Update)**

In adherence to the principle of **simplicity as the highest priority**, the String-Multitool project has been strategically divided into two focused components:

1. **Core String-Multitool**: The main application focused on text transformations, clipboard operations, and cryptographic functions
2. **Extensions Module**: Specialized Japanese encoding transformations and future extensibility modules

**Benefits of this separation:**

- **Single Responsibility**: Each component has a clear, focused purpose
- **Reduced Complexity**: Simpler codebase structure and dependency management
- **Enhanced Maintainability**: Easier to understand, debug, and extend individual components
- **Loose Coupling**: Independent development and testing of core vs. specialized features
- **Deployment Flexibility**: Core functionality remains lightweight while extensions can be loaded optionally

This architectural decision aligns with our core principles:
- **Simplicity First**: Avoid unnecessary complexity in the main application flow
- **Loose Coupling**: Components interact through well-defined interfaces
- **High Cohesion**: Related functionality grouped together appropriately
- **Extensibility**: New features can be added as separate modules without affecting core stability

Understanding the project organization is crucial for effective development:

```
String-Multitool/                           # Main project directory
├── smt_ui_cli/                            # 🖥️ Command Line Interface (改修: UI・コマンド変更)
│   ├── interactive_shell.py              # Interactive command shell
│   ├── argument_parser.py                # Command line argument handling
│   ├── output_formatter.py               # Result display formatting
│   └── main.py                           # CLI entry point
│
├── smt_ui_api/                            # 🌐 Web API Interface (改修: API・REST変更)
│   ├── endpoints/                         # REST API endpoints
│   ├── middleware/                        # Request/response middleware
│   └── server.py                         # Web server configuration
│
├── smt_engine_core/                       # ⚙️ Core Business Logic (改修: ビジネスルール変更)
│   ├── use_cases/                         # Application use cases
│   │   ├── text_transformation_use_case.py
│   │   ├── batch_processing_use_case.py
│   │   └── session_management_use_case.py
│   ├── entities/                          # Business entities
│   │   ├── text_entity.py
│   │   └── rule_entity.py
│   ├── protocols/                         # Interface definitions
│   │   ├── transformation_protocol.py
│   │   └── storage_protocol.py
│   └── exceptions/                        # Business exceptions
│       └── domain_exceptions.py
│
├── smt_transform_basic/                   # 📝 Basic Text Operations (改修: 基本的な文字列操作追加)
│   ├── case_transforms/                   # Case conversion operations
│   │   ├── lowercase.py
│   │   ├── uppercase.py
│   │   └── capitalize.py
│   ├── whitespace_transforms/             # Whitespace operations
│   │   ├── trim.py
│   │   ├── normalize_spaces.py
│   │   └── line_operations.py
│   └── string_operations/                 # Basic string manipulations
│       ├── reverse.py
│       ├── replace.py
│       └── substring.py
│
├── smt_transform_advanced/                # 🚀 Advanced Transformations (改修: 高度な変換機能追加)
│   ├── crypto_transforms/                 # Cryptographic operations
│   │   ├── encryption.py
│   │   ├── hashing.py
│   │   └── digital_signatures.py
│   ├── encoding_transforms/               # Text encoding operations
│   │   ├── base64_operations.py
│   │   ├── url_encoding.py
│   │   └── unicode_normalization.py
│   ├── japanese_transforms/               # Japanese-specific operations
│   │   ├── encoding_conversion.py
│   │   ├── kana_conversion.py
│   │   └── character_width.py
│   └── ai_transforms/                     # AI-powered transformations
│       ├── text_summarization.py
│       ├── language_detection.py
│       └── sentiment_analysis.py
│
├── smt_infrastructure/                    # 🔧 Technical Infrastructure (改修: システム・IO変更)
│   ├── io_adapters/                       # Input/Output adapters
│   │   ├── clipboard_adapter.py
│   │   ├── file_adapter.py
│   │   └── network_adapter.py
│   ├── config_repositories/               # Configuration storage
│   │   ├── json_config_repo.py
│   │   ├── yaml_config_repo.py
│   │   └── database_config_repo.py
│   ├── crypto_services/                   # Cryptographic services
│   │   ├── rsa_crypto_service.py
│   │   └── aes_crypto_service.py
│   ├── logging_services/                  # Logging infrastructure
│   │   ├── structured_logger.py
│   │   └── file_logger.py
│   └── storage_services/                  # Data persistence
│       ├── session_storage.py
│       └── cache_service.py
│
├── smt_data_converters/                   # 📊 Data Format Converters (改修: データ変換追加)
│   ├── tsv_converters/                    # TSV/CSV operations
│   │   ├── tsv_transformer.py
│   │   ├── rule_based_converter.py
│   │   └── database_importer.py
│   ├── json_converters/                   # JSON operations
│   │   ├── json_formatter.py
│   │   └── json_validator.py
│   └── xml_converters/                    # XML operations
│       ├── xml_transformer.py
│       └── xml_validator.py
│
├── smt_extensions_loader/                 # 🔌 Extension System (改修: プラグイン・拡張追加)
│   ├── plugin_discovery.py               # Dynamic plugin loading
│   ├── extension_registry.py             # Extension registration
│   └── dependency_resolver.py            # Plugin dependency management
│
├── tests/                                 # 🧪 Test Suite (改修: テスト追加・修正)
│   ├── unit/                             # Unit tests by component
│   │   ├── test_smt_engine_core/
│   │   ├── test_smt_transform_basic/
│   │   └── test_smt_transform_advanced/
│   ├── integration/                       # Integration tests
│   │   ├── test_ui_integration.py
│   │   └── test_transformation_pipeline.py
│   ├── performance/                       # Performance tests
│   │   └── test_large_text_processing.py
│   └── conftest.py                       # Shared test configuration
│
├── config/                                # ⚙️ Configuration Files (改修: 設定変更)
│   ├── transformation_rules.json         # Core transformation rules
│   ├── security_config.json              # Security settings
│   ├── ui_config.json                    # UI configuration
│   └── extension_config.json             # Extension settings
│
├── docs/                                  # 📚 Documentation (改修: ドキュメント更新)
│   ├── architecture/                      # Architecture documentation
│   │   ├── CLEAN_ARCHITECTURE.md
│   │   ├── PROJECT_STRUCTURE.md
│   │   └── DEPENDENCY_FLOW.md
│   ├── development/                       # Development guides
│   │   ├── ADDING_TRANSFORMATIONS.md
│   │   ├── CREATING_EXTENSIONS.md
│   │   └── TESTING_GUIDE.md
│   └── user/                             # User documentation
│       ├── CLI_GUIDE.md
│       ├── API_REFERENCE.md
│       └── EXAMPLES.md
│
└── deployment/                            # 🚀 Deployment Configuration (改修: デプロイ設定変更)
    ├── docker/                           # Container configuration
    ├── scripts/                          # Build and deployment scripts
    └── configs/                          # Environment-specific configs
```

## Development Workflow

### Feature Development Process

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement Changes**:
   - Follow the MVC architecture pattern
   - Write comprehensive tests
   - Update documentation
   - Add type hints

3. **Code Quality Checks**:
   ```bash
   # Type checking
   uv run python -m mypy string_multitool/
   
   # Code formatting
   uv run black string_multitool/
   
   # Import sorting
   uv run isort string_multitool/
   
   # Run tests
   uv run python -m pytest tests/ -v --cov=string_multitool
   ```

4. **Create Pull Request**:
   - Use the provided PR template
   - Include comprehensive description
   - Link related issues

### Commit Message Guidelines

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(transform): add new text reversal transformation
fix(crypto): resolve key generation issue on Windows
docs(api): update transformation engine documentation
test(integration): add end-to-end workflow tests
```

## Code Standards

### Python Code Style (2025 Standards)

String-Multitool follows **PEP 8** and **2025 Python best practices** with these guidelines:

- **Line Length**: 99 characters (project-specific, optimized for modern displays)
- **Type Hints**: Mandatory for all interfaces (Python 3.12+ modern syntax)
- **Docstrings**: Google-style docstrings following PEP 257
- **Imports**: Sorted with isort using Black profile
- **Build System**: Hatchling backend with PEP 621 metadata structure
- **Package Manager**: UV 0.5.9+ recommended for all development workflows
- **Linting**: Ruff 0.12.10+ for fast Python linting and code formatting

### Docstring Standards

Follow Google-style docstrings:

```python
def apply_transformations(self, text: str, rule_chain: str) -> str:
    """Apply transformation rules to input text.
    
    This method processes the input text through a sequence of transformation
    rules specified in the rule_chain parameter.
    
    Args:
        text: The input text to transform
        rule_chain: Transformation rules (e.g., '/t/l/u')
        
    Returns:
        The transformed text
        
    Raises:
        TransformationError: If transformation processing fails
        ValidationError: If input parameters are invalid
        
    Examples:
        >>> engine.apply_transformations("  Hello  ", "/t/l")
        "hello"
        
        >>> engine.apply_transformations("Hello", "/r 'H' 'h'")
        "hello"
    """
```

### Type Hints

Use modern Python type hints (Python 3.10+ union syntax):

```python
# Use new union syntax
def process_text(text: str, options: dict[str, Any] | None = None) -> str:
    pass

# Use generics for collections
def get_rules(self) -> dict[str, TransformationRule]:
    pass

# Use protocols for interfaces
def __init__(self, config_manager: ConfigManagerProtocol) -> None:
    pass
```

### Error Handling

Use EAFP (Easier to Ask for Forgiveness than Permission) pattern:

```python
def load_config_file(self, file_path: Path) -> dict[str, Any]:
    """Load configuration file using EAFP pattern."""
    try:
        with file_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigurationError(f"Configuration file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in {file_path}: {e}")
```

## Testing Guidelines

### Test Organization

String-Multitool uses modern pytest patterns:

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def transformation_engine(config_manager):
    """Provide TextTransformationEngine for testing."""
    return TextTransformationEngine(config_manager)

@pytest.mark.unit
class TestTextTransformationEngine:
    """Test text transformation functionality."""
    
    @pytest.mark.parametrize("input_text,rule,expected", [
        ("  hello  ", "/t", "hello"),
        ("HELLO", "/l", "hello"),
        ("hello", "/u", "HELLO"),
    ])
    def test_basic_transformations(self, transformation_engine, input_text, rule, expected):
        """Test basic transformation rules."""
        result = transformation_engine.apply_transformations(input_text, rule)
        assert result == expected
```

### Test Categories

Use pytest markers to organize tests:

- `@pytest.mark.unit`: Unit tests for individual components
- `@pytest.mark.integration`: Integration tests for component interaction
- `@pytest.mark.performance`: Performance and benchmark tests
- `@pytest.mark.security`: Security-related tests
- `@pytest.mark.slow`: Tests that take significant time

### Testing Commands

```bash
# Run all tests with latest pytest 8.4.2
uv run pytest tests/ -v

# Run with coverage analysis
uv run pytest tests/ -v --cov=string_multitool --cov-report=html

# Run specific test categories
uv run pytest tests/ -m "unit and not slow"
uv run pytest tests/ -m "integration"

# Parallel testing for faster execution
uv run pytest tests/ -n auto

# Run with modern mypy 1.18.1 type checking
uv run mypy string_multitool/

# Run with ruff 0.12.10 linting
uv run ruff check string_multitool/

# Format code with black
uv run black string_multitool/
```

### Mock Usage

Use mocks for external dependencies:

```python
@pytest.fixture
def mock_clipboard():
    """Mock clipboard functionality."""
    with patch("string_multitool.io.manager.pyperclip") as mock_pyperclip:
        mock_pyperclip.paste.return_value = "test content"
        mock_pyperclip.copy.return_value = None
        yield mock_pyperclip
```

## Tab Completion System

String-Multitool includes a comprehensive Tab completion system built with **Typer**, supporting all commands and MCP operations with intelligent suggestions.

### Features

- **Smart Command Completion**: Auto-complete for all CLI commands
- **Parameter Completion**: Context-aware parameter suggestions
- **MCP Operations**: Tab completion for Context7 and Serena MCP operations
- **Cross-shell Support**: Works with bash, zsh, fish, and PowerShell
- **Fallback System**: Graceful degradation when completion data is unavailable

### Installation

#### Automatic Installation
```bash
# Install completion for current shell (auto-detected)
uv run python -m string_multitool.cli completion --install

# Install for specific shell
uv run python -m string_multitool.cli completion --install --shell bash
```

#### Manual Installation
```bash
# Show completion script for manual setup
uv run python -m string_multitool.cli completion --show bash
uv run python -m string_multitool.cli completion --show zsh

# Using setup script directly
python scripts/setup_completion.py --install
python scripts/setup_completion.py --show zsh
```

#### Manual Shell Configuration

**Bash** (`~/.bashrc`):
```bash
# String-Multitool completion
_STRING_MULTITOOL_COMPLETE=bash_source string-multitool > /dev/null 2>&1 && {
    eval "$(_STRING_MULTITOOL_COMPLETE=bash_source string-multitool)"
}
```

**Zsh** (`~/.zshrc`):
```bash
# String-Multitool completion
_STRING_MULTITOOL_COMPLETE=zsh_source string-multitool > /dev/null 2>&1 && {
    eval "$(_STRING_MULTITOOL_COMPLETE=zsh_source string-multitool)"
}
```

**Fish** (`~/.config/fish/config.fish`):
```bash
# String-Multitool completion
_STRING_MULTITOOL_COMPLETE=fish_source string-multitool > /dev/null 2>&1; and eval (_STRING_MULTITOOL_COMPLETE=fish_source string-multitool)
```

**PowerShell** (`~/Documents/PowerShell/profile.ps1`):
```powershell
# String-Multitool completion
if (Get-Command string-multitool -ErrorAction SilentlyContinue) {
    $env:_STRING_MULTITOOL_COMPLETE = "powershell_source"
    Invoke-Expression "$(string-multitool)"
}
```

### Usage Examples

```bash
# Tab completion for commands
string-multitool <TAB>
# Shows: transform, interactive, encrypt, decrypt, context7, serena, completion, etc.

# Tab completion for transformation rules
string-multitool transform <TAB>
# Shows: /t, /l, /u, /enc, /dec, /b64enc, /b64dec, /r, /S, etc.

# Tab completion for Context7 operations
string-multitool context7 <TAB>
# Shows: resolve-library-id, get-library-docs, search-examples, list-libraries

# Tab completion for Serena operations
string-multitool serena <TAB>
# Shows: find-symbol, get-symbols-overview, search-for-pattern, list-dir, etc.
```

### Architecture

The completion system is implemented in `string_multitool/cli.py` with:

- **Completion Functions**: Dedicated functions for each command type
- **Typer Integration**: Uses Typer's built-in `autocompletion` parameter
- **Fallback Handling**: Graceful error handling when services are unavailable
- **Dynamic Loading**: Lazy loading of transformation rules for performance

### Adding Custom Completions

To add completion for new commands:

```python
def complete_my_operation(incomplete: str) -> list[str]:
    """Provide completion for my custom operations."""
    operations = ["operation1", "operation2", "operation3"]
    return [op for op in operations if incomplete.lower() in op.lower()]

@app.command("my-command")
def my_command(
    operation: Annotated[
        str,
        typer.Argument(help="My operation", autocompletion=complete_my_operation)
    ]
) -> None:
    """Execute my custom command."""
    # Implementation here
```

## MCP Integration (Context7 & Serena)

String-Multitool provides integrated support for **Context7** (library documentation) and **Serena** (code analysis) MCP servers with full Tab completion.

### Context7 MCP

Context7 provides up-to-date library documentation and code examples.

#### Usage
```bash
# Resolve library ID with completion
string-multitool context7 resolve-library-id --library typer

# Get documentation with topic filtering
string-multitool context7 get-library-docs --library /fastapi/typer --topic completion --tokens 5000

# Available operations (with Tab completion):
# - resolve-library-id
# - get-library-docs
# - search-examples
# - list-libraries
```

#### Setup
```bash
# Install Context7 MCP server
npx -y @upstash/context7-mcp@latest --transport stdio

# Or configure in your MCP client
```

### Serena MCP

Serena provides intelligent code analysis and symbol navigation.

#### Usage
```bash
# Find symbols with pattern completion
string-multitool serena find-symbol --path ./string_multitool --pattern "ApplicationInterface"

# Get file overview
string-multitool serena get-symbols-overview --path ./string_multitool/main.py

# Search for patterns
string-multitool serena search-for-pattern --pattern "def complete_" --path .

# Available operations (with Tab completion):
# - find-symbol
# - get-symbols-overview
# - search-for-pattern
# - list-dir
# - find-file
# - read-memory
# - write-memory
# - find-referencing-symbols
```

#### Setup
Serena MCP should be configured in your IDE/development environment.

### Benefits

- **Enhanced Productivity**: Reduce typing and avoid typos with smart completion
- **Discovery**: Explore available operations without memorizing commands
- **Integration**: Seamless workflow with MCP servers
- **Consistency**: Unified interface across different tools and operations

## Adding New Features

### Adding Transformation Rules

1. **Define Rule Metadata** (`config/transformation_rules.json`):

```json
{
  "string_operations": {
    "reverse": {
      "description": "Reverse text",
      "example": "/reverse",
      "category": "string_operations"
    }
  }
}
```

2. **Implement Transformation Method**:

```python
def reverse_text(self, text: str) -> str:
    """Reverse the input text.
    
    Args:
        text: Input text to reverse
        
    Returns:
        Reversed text
        
    Examples:
        >>> engine.reverse_text("hello")
        "olleh"
    """
    return text[::-1]
```

3. **Register Rule**:

```python
def _initialize_rules(self):
    """Initialize transformation rules."""
    # Existing rules...
    self._register_rule("reverse", self.reverse_text, TransformationRuleType.STRING_OPERATIONS)
```

4. **Add Tests**:

```python
def test_reverse_transformation(self, transformation_engine):
    """Test text reversal transformation."""
    result = transformation_engine.apply_transformations("hello", "/reverse")
    assert result == "olleh"
```

5. **Update Documentation**:
   - Add rule to API reference
   - Update help system
   - Include in examples

### Adding New Components

When adding new model components:

1. **Follow MVC Pattern**: Place business logic in `models/`
2. **Define Protocol**: Create protocol interface for loose coupling
3. **Implement Class**: Follow existing patterns and type hints
4. **Add to Factory**: Update `ApplicationFactory` for dependency injection
5. **Comprehensive Tests**: Unit and integration tests
6. **Documentation**: API reference and architecture updates

### Extension Development Guidelines

Following our **simplicity-first architecture**, extensions are developed in separate modules:

#### Core vs. Extension Decision Matrix

| Feature Type | Location | Reasoning |
|-------------|----------|-----------|
| Basic text transformations | `string_multitool_core/` | Essential functionality used by most users |
| Case conversions | `string_multitool_core/` | Fundamental operations |
| Cryptographic functions | `string_multitool_core/` | Core security features |
| Japanese encoding | `string_multitool_extensions/` | Specialized for specific language requirements |
| Advanced regex | `string_multitool_extensions/` | Complex operations for power users |
| Future AI features | `string_multitool_extensions/` | Experimental or resource-intensive features |

#### Extension Development Process

1. **Identify Extension Need**: Determine if the feature belongs in core or extension
2. **Create Extension Module**: Add to `string_multitool_extensions/`
3. **Define Extension Interface**: Use protocols for loose coupling with core
4. **Implement Extension Logic**: Follow same coding standards as core
5. **Optional Configuration**: Add to `config/extension_rules.json` if needed
6. **Comprehensive Testing**: Create tests in `tests/test_extensions.py`
7. **Documentation**: Update extension guide and API reference

#### Extension Integration Pattern

```python
# Extension interface protocol
class ExtensionProtocol(Protocol):
    """Protocol for extension modules."""

    def get_transformation_rules(self) -> dict[str, TransformationRule]:
        """Return transformation rules provided by this extension."""
        ...

    def initialize(self, config_manager: ConfigManagerProtocol) -> None:
        """Initialize extension with configuration."""
        ...

# Extension discovery and loading
def load_extensions() -> list[ExtensionProtocol]:
    """Load available extensions dynamically."""
    extensions = []
    try:
        from string_multitool_extensions import japanese_encoding
        extensions.append(japanese_encoding.JapaneseEncodingExtension())
    except ImportError:
        logger.debug("Japanese encoding extension not available")

    return extensions
```

This approach maintains:
- **Core Simplicity**: Main application remains focused and lightweight
- **Optional Extensions**: Users only load what they need
- **Development Isolation**: Extensions can be developed and tested independently
- **Future Extensibility**: New features can be added without core modifications

## Security Considerations

### Secure Coding Practices

1. **Input Validation**: Always validate and sanitize user input
2. **Error Messages**: Don't leak sensitive information in error messages
3. **Cryptographic Keys**: Never log or print cryptographic material
4. **File Permissions**: Use secure file permissions for sensitive files
5. **Dependencies**: Regularly update dependencies for security patches

### Cryptography Guidelines

When working with cryptographic components:

```python
def encrypt_text(self, plaintext: str) -> str:
    """Encrypt text using hybrid RSA+AES encryption."""
    try:
        # Generate random AES key
        aes_key = os.urandom(32)  # 256-bit key
        
        # Encrypt data with AES
        cipher_text = self._aes_encrypt(plaintext.encode('utf-8'), aes_key)
        
        # Encrypt AES key with RSA
        encrypted_key = self._rsa_encrypt(aes_key)
        
        # Combine and encode
        combined = encrypted_key + cipher_text
        return base64.b64encode(combined).decode('ascii')
        
    except Exception as e:
        # Never log the plaintext or keys
        raise CryptographyError(f"Encryption failed: {type(e).__name__}")
```

### Security Testing

Include security tests for:

```python
@pytest.mark.security
class TestSecurityAspects:
    """Security-related tests."""
    
    @pytest.mark.parametrize("malicious_input", [
        "<script>alert('xss')</script>",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
    ])
    def test_malicious_input_handling(self, transformation_engine, malicious_input):
        """Test handling of potentially malicious inputs."""
        # Should not crash and should return safe output
        result = transformation_engine.apply_transformations(malicious_input, "/t")
        assert isinstance(result, str)
```

## Performance Guidelines

### Optimization Strategies

1. **Lazy Loading**: Load resources only when needed
2. **Caching**: Cache expensive computations and I/O operations
3. **Efficient Algorithms**: Use appropriate algorithms for text processing
4. **Memory Management**: Avoid unnecessary memory allocations

### Performance Testing

```python
@pytest.mark.performance
def test_transformation_performance(transformation_engine):
    """Test transformation performance meets requirements."""
    import time
    
    large_text = "test content " * 10000  # ~130KB
    
    start_time = time.perf_counter()
    result = transformation_engine.apply_transformations(large_text, "/t/l")
    end_time = time.perf_counter()
    
    execution_time = end_time - start_time
    assert execution_time < 0.1  # Should complete in under 100ms
    assert isinstance(result, str)
```

### Profiling

Use Python's built-in profiling tools:

```bash
# Profile specific function
python -m cProfile -s cumtime -m string_multitool.main

# Memory profiling with memory_profiler
pip install memory-profiler
python -m memory_profiler string_multitool/main.py
```

## Debugging and Troubleshooting

### Debug Mode

Enable debug logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_transformation(self, text: str, rule: str) -> str:
    """Debug transformation with detailed logging."""
    logger.debug(f"Processing text: {len(text)} chars, rule: {rule}")
    result = self.apply_transformations(text, rule)
    logger.debug(f"Result: {len(result)} chars")
    return result
```

### Common Issues

#### Configuration Loading Issues

```python
try:
    config = self.load_configuration()
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    logger.debug(f"Configuration directory: {self.config_dir}")
    logger.debug(f"Available files: {list(self.config_dir.glob('*.json'))}")
    raise
```

#### Clipboard Access Issues

```python
def get_clipboard_text(self) -> str:
    """Get clipboard text with debugging."""
    try:
        import pyperclip
        return pyperclip.paste()
    except Exception as e:
        logger.error(f"Clipboard access failed: {e}")
        logger.debug(f"Clipboard available: {CLIPBOARD_AVAILABLE}")
        raise ClipboardError(f"Cannot access clipboard: {e}")
```

### Testing in Isolation

Create isolated test environments:

```python
@pytest.fixture
def isolated_config(tmp_path):
    """Create isolated configuration for testing."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    
    # Create minimal test configuration
    (config_dir / "transformation_rules.json").write_text(json.dumps({
        "basic_transformations": {
            "t": {"description": "Trim", "example": "/t"}
        }
    }))
    
    return ConfigurationManager(config_dir)
```

## Build and Deployment (2025 Standards)

### Modern Build System

String-Multitool uses **hatchling** as the build backend, chosen for its modern design and PEP 621 compliance:

```bash
# Build wheel package with modern backend
uv build

# Install from wheel (using uv for speed)
uv pip install dist/string_multitool-*.whl

# Alternative with traditional pip
pip install dist/string_multitool-*.whl
```

### Why Hatchling?

- **Standards Compliant**: Full PEP 621 support for metadata in pyproject.toml
- **Modern Design**: Built from the ground up for current Python packaging standards
- **Performance**: Faster builds compared to legacy setuptools
- **Extensibility**: Balanced configurability without complexity
- **Industry Adoption**: Recommended by PyPA for new projects in 2025

### Executable Creation

```bash
# Create standalone executable
./build.ps1

# Clean build
./build.ps1 -Clean

# Debug build with extra logging
./build.ps1 -DebugMode
```

### Release Process (2025 Workflow)

1. **Version Bump**: Update version in `pyproject.toml` (hatchling manages version sourcing)
2. **Changelog**: Update `CHANGELOG.md` with new features
3. **Documentation**: Ensure all documentation reflects current 2025 standards
4. **Quality Assurance**: Run comprehensive test suite with modern pytest configuration
5. **Build**: Create distribution packages using `uv build` (hatchling backend)
6. **Security Scan**: Verify no vulnerabilities with modern security tools
7. **Tag Release**: Create git tag for version
8. **Deploy**: Upload to PyPI using modern publishing workflow

---

*This developer guide is a living document. Please keep it updated as development practices evolve.*