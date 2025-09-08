# Developer Guide

This guide provides comprehensive information for developers working on String-Multitool, including setup instructions, development workflows, and contribution guidelines.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Adding New Features](#adding-new-features)
- [Security Considerations](#security-considerations)
- [Performance Guidelines](#performance-guidelines)
- [Debugging and Troubleshooting](#debugging-and-troubleshooting)

## Development Environment Setup

### Prerequisites

- **Python 3.12+**: String-Multitool uses modern Python features
- **uv**: Fast Python package manager (recommended) or pip
- **Git**: Version control
- **VS Code** or **PyCharm**: Recommended IDEs with Python support

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/[your-username]/String-Multitool.git
cd String-Multitool

# Setup virtual environment with uv (recommended)
uv sync

# Or with traditional pip
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Install development dependencies
uv sync --group dev
# Or: pip install -e ".[dev]"

# Run tests to verify setup
uv run python -m pytest tests/ -v
```

### Development Tools Configuration

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.flake8Enabled": true,
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

Understanding the project organization is crucial for effective development:

```
String-Multitool/
├── string_multitool/           # Main package
│   ├── models/                 # Business logic (Model layer)
│   │   ├── config.py          # Configuration management
│   │   ├── transformations.py # Core transformation engine
│   │   ├── crypto.py          # Cryptography operations
│   │   ├── interactive.py     # Interactive session management
│   │   ├── types.py           # Type definitions and protocols
│   │   └── ...               # Other model components
│   ├── io/                    # I/O operations (View/Controller layer)
│   │   ├── manager.py         # I/O manager
│   │   └── clipboard.py       # Clipboard monitoring
│   ├── transformations/       # Transformation implementations
│   │   ├── basic_transformations.py
│   │   ├── case_transformations.py
│   │   ├── encryption_transformations.py
│   │   └── ...               # Other transformation modules
│   ├── utils/                 # Utility components
│   │   ├── unified_logger.py  # Logging infrastructure
│   │   └── lifecycle_manager.py
│   └── main.py               # Application entry point
├── tests/                    # Test suite
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── test_transform.py    # Core transformation tests
│   ├── test_modern_comprehensive.py # Modern pytest patterns
│   └── ...                  # Other test modules
├── config/                  # Configuration files
│   ├── transformation_rules.json
│   ├── security_config.json
│   └── hotkey_config.json
├── docs/                    # Documentation
│   ├── API_REFERENCE.md     # API documentation
│   ├── ARCHITECTURE.md      # System architecture
│   └── DEVELOPER_GUIDE.md   # This guide
└── ...                      # Other project files
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

### Python Code Style

String-Multitool follows **PEP 8** with these additional guidelines:

- **Line Length**: 88 characters (Black default)
- **Type Hints**: Mandatory for all public interfaces
- **Docstrings**: Google-style docstrings following PEP 257
- **Imports**: Sorted with isort using Black profile

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
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test categories
uv run python -m pytest tests/ -m "unit" -v

# Run tests with coverage
uv run python -m pytest tests/ --cov=string_multitool --cov-report=html

# Run performance tests
uv run python -m pytest tests/ -m "performance" -v
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

## Build and Deployment

### Building Distribution

```bash
# Build wheel package
uv build

# Install from wheel
pip install dist/string_multitool-*.whl
```

### Executable Creation

```bash
# Create standalone executable
./build.ps1

# Clean build
./build.ps1 -Clean

# Debug build with extra logging
./build.ps1 -DebugMode
```

### Release Process

1. **Version Bump**: Update version in `pyproject.toml`
2. **Changelog**: Update `CHANGELOG.md` with new features
3. **Documentation**: Ensure all documentation is current
4. **Testing**: Run full test suite
5. **Build**: Create distribution packages
6. **Tag Release**: Create git tag for version
7. **Deploy**: Upload to package repository

---

*This developer guide is a living document. Please keep it updated as development practices evolve.*