# String-Multitool Developer Guide

Modern development guide following best practices for the modular String-Multitool architecture.

## Table of Contents

- [Project Architecture](#project-architecture)
- [Development Setup](#development-setup)
- [Core Package Development](#core-package-development)
- [Extension Package Development](#extension-package-development)
- [Testing Strategy](#testing-strategy)
- [Documentation](#documentation)
- [Contributing Guidelines](#contributing-guidelines)
- [Release Process](#release-process)

## Project Architecture

### Modular Design Overview

String-Multitool follows a **modular monorepo** architecture with two main packages:

```
string-multitool/
├── string_multitool_core/          # Lightweight core (3 dependencies)
│   ├── engine.py                   # Core transformation engine
│   ├── types.py                    # Type definitions
│   ├── config/                     # Configuration management
│   ├── crypto/                     # Basic cryptography
│   └── io/                         # Basic I/O operations
├── string_multitool_extensions/    # Feature-rich extensions
│   ├── loader.py                   # Lazy loading system
│   ├── transformations/            # Advanced transformations
│   ├── tsv/                        # TSV processing
│   └── ui/                         # User interface
└── docs/                           # Comprehensive documentation
```

### Design Principles

1. **Separation of Concerns**: Core vs extensions with clear boundaries
2. **Lazy Loading**: Extensions loaded only when needed
3. **Protocol-Based Design**: Loose coupling via Python protocols
4. **Type Safety**: Full type annotations with strict mypy compliance
5. **Performance First**: Optimized for startup speed and memory efficiency

## Development Setup

### Prerequisites

- Python 3.12+ (recommended 3.13+)
- UV package manager (2025 standard)
- Git with LFS support

### Environment Setup

```bash
# Clone repository
git clone https://github.com/tay2501/String-Multitool.git
cd String-Multitool

# Core package development
cd string_multitool_core
uv sync --dev
uv run pytest

# Extension package development
cd ../string_multitool_extensions
uv sync --dev
uv run pytest

# Both packages together
cd ..
uv run pytest string_multitool_core/tests/ string_multitool_extensions/tests/
```

### IDE Configuration

#### VS Code Setup

```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestPath": "./.venv/bin/pytest",
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "python.sortImports.path": "./.venv/bin/isort"
}
```

#### PyCharm Setup

1. Set Project Interpreter: `.venv/bin/python`
2. Enable pytest as test runner
3. Configure mypy as external tool
4. Set Black as code formatter

## Core Package Development

### Adding Core Transformations

Core transformations should be **minimal, fast, and dependency-free**.

```python
# string_multitool_core/engine.py

def _new_core_transformation(self, text: str) -> str:
    """
    Add new core transformation following these guidelines:
    - Single responsibility
    - No external dependencies
    - Fast execution (<1ms typical)
    - Pure string operations
    """
    return processed_text
```

#### Core Development Guidelines

1. **Minimal Dependencies**: Only add dependencies that are absolutely essential
2. **Performance Critical**: Target <1ms for typical operations
3. **Type Safety**: Full type annotations required
4. **Error Handling**: Graceful failure with meaningful messages
5. **Testing**: 95%+ test coverage required

### Core Architecture Patterns

```python
# Protocol-based design example
from typing import Protocol

class TransformationProtocol(Protocol):
    def transform(self, text: str, rule: str) -> TransformationResult: ...
    def get_available_rules(self) -> List[CoreTransformationRule]: ...

# Dependency injection
class CoreTransformationEngine:
    def __init__(self):
        self._extension_loaders: Dict[str, TransformationProtocol] = {}

    def register_extension_loader(self, name: str, loader: TransformationProtocol):
        self._extension_loaders[name] = loader
```

## Extension Package Development

### Adding Extension Transformations

Extensions can be **feature-rich with external dependencies**.

```python
# string_multitool_extensions/transformations/new_transformation.py

def transform_new_feature(text: str) -> str:
    """
    Extension transformation guidelines:
    - Can use external libraries
    - Should be in separate module
    - Must follow get_transformations() pattern
    """
    # Complex processing allowed here
    return result

def get_transformations() -> Dict[str, Callable]:
    """Required function for loader integration."""
    return {
        "new_feature": transform_new_feature,
    }
```

### Lazy Loading Implementation

```python
# string_multitool_extensions/loader.py

# Add new transformation to loader
class ExtensionTransformationLoader:
    def __init__(self):
        self._transformation_modules = {
            # Existing mappings...
            'new_feature': 'transformations.new_transformation',
        }
```

### Extension Development Best Practices

1. **Modular Design**: Each feature type in separate module
2. **Lazy Loading**: Use importlib for on-demand imports
3. **Error Recovery**: Graceful degradation if dependencies missing
4. **Documentation**: Comprehensive docstrings and examples
5. **Performance**: Consider caching for expensive operations

## Testing Strategy

### Modern pytest Patterns

Following pytest latest best practices with comprehensive parametrization:

```python
# Parametrized fixtures
@pytest.fixture(params=[
    ("input", "/rule", "expected"),
    pytest.param("complex", "/advanced", "result", marks=pytest.mark.slow),
])
def transformation_test_case(request):
    return request.param

# Type-annotated test methods
def test_transformation(
    self,
    transformation_engine: CoreTransformationEngine,
    transformation_test_case: Tuple[str, str, str]
):
    input_text, rule, expected = transformation_test_case
    result = transformation_engine.transform(input_text, rule)
    assert result.success
    assert result.text == expected
```

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures with modern patterns
├── test_core_engine.py      # Core functionality tests
├── test_extension_loader.py # Extension loading tests
├── test_integration.py      # End-to-end integration tests
└── test_performance.py      # Performance benchmarks
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Performance Tests**: Benchmark critical paths
- **Error Handling Tests**: Edge cases and failure scenarios
- **Unicode Tests**: International character support

### Running Tests

```bash
# Core tests only
cd string_multitool_core && uv run pytest

# Extension tests only
cd string_multitool_extensions && uv run pytest

# All tests with coverage
uv run pytest --cov=string_multitool_core --cov=string_multitool_extensions

# Performance tests
uv run pytest -m performance

# Specific test categories
uv run pytest -m "not slow" -v
```

## Documentation

### API Documentation with Sphinx

Auto-generated API documentation using modern Sphinx patterns:

```python
# docs/conf.py
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
]

autosummary_generate = True
napoleon_google_docstring = True
```

### Documentation Structure

```
docs/
├── api/
│   ├── core.rst           # Core API reference
│   └── extensions.rst     # Extensions API reference
├── guides/
│   ├── quickstart.rst     # Getting started
│   ├── architecture.rst   # Architecture overview
│   └── development.rst    # Development guide
└── examples/
    ├── basic_usage.rst    # Basic examples
    └── advanced.rst       # Advanced use cases
```

### Docstring Standards

```python
def transform(self, text: str, rule: str) -> TransformationResult:
    """
    Apply transformation rule to input text.

    This method processes the input text according to the specified rule,
    supporting both core and extension transformations through lazy loading.

    Args:
        text: Input text to transform. Can be empty string.
        rule: Transformation rule (e.g., "/t/l/u" for trim+lower+upper).
              Must start with "/" and contain valid rule names.

    Returns:
        TransformationResult containing:
        - text: Transformed text or original on error
        - success: Boolean indicating transformation success
        - error: Error message if transformation failed, None otherwise

    Raises:
        CoreTransformationError: If rule format is invalid.

    Examples:
        >>> engine = CoreTransformationEngine()
        >>> result = engine.transform("  Hello  ", "/t/l")
        >>> result.text
        'hello'
        >>> result.success
        True

    Note:
        Extension transformations are loaded lazily on first use.
        Performance: Core transformations typically complete in <1ms.
    """
```

## Contributing Guidelines

### Code Style

- **Formatter**: Black (line length: 99)
- **Import Sorting**: isort with Black profile
- **Type Checking**: mypy strict mode
- **Linting**: ruff with performance optimizations

### Commit Message Format

```
type(scope): description

Extended description if needed

- Bullet points for details
- Reference issues with #123

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Pull Request Process

1. **Fork and Branch**: Create feature branch from `main`
2. **Implement**: Follow architecture patterns and add tests
3. **Documentation**: Update relevant docs and API references
4. **Quality Checks**: All CI checks must pass
5. **Review**: Address reviewer feedback
6. **Merge**: Squash merge to maintain clean history

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
- repo: https://github.com/psf/black
  rev: 24.0.0
  hooks:
  - id: black
- repo: https://github.com/pycqa/isort
  rev: 5.12.0
  hooks:
  - id: isort
- repo: https://github.com/charliermarsh/ruff-pre-commit
  rev: v0.6.0
  hooks:
  - id: ruff
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.5.0
  hooks:
  - id: mypy
```

## Release Process

### Version Management

- **Core Package**: Independent semantic versioning
- **Extensions Package**: Tracks core package versions
- **Compatibility**: Extensions specify minimum core version

### Release Checklist

1. **Update Version Numbers**
   ```bash
   # Update pyproject.toml in both packages
   # Update __version__ in __init__.py files
   ```

2. **Run Full Test Suite**
   ```bash
   uv run pytest string_multitool_core/tests/ -v
   uv run pytest string_multitool_extensions/tests/ -v
   ```

3. **Build and Test Packages**
   ```bash
   cd string_multitool_core && uv build
   cd string_multitool_extensions && uv build
   ```

4. **Update Documentation**
   ```bash
   cd docs && make html
   ```

5. **Create Release**
   ```bash
   git tag -a v2.6.0 -m "Release v2.6.0"
   git push origin v2.6.0
   ```

### Deployment Pipeline

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v1
      - name: Build packages
        run: |
          cd string_multitool_core && uv build
          cd string_multitool_extensions && uv build
      - name: Publish to PyPI
        run: |
          uv publish string_multitool_core/dist/*
          uv publish string_multitool_extensions/dist/*
```

## Performance Optimization

### Profiling Guidelines

```python
# Performance testing
@pytest.mark.performance
def test_transformation_performance(benchmark):
    engine = CoreTransformationEngine()

    # Benchmark core operations
    result = benchmark(engine.transform, "test", "/t/l/u")
    assert result.success

    # Target: <1ms for core transformations
    assert benchmark.stats.mean < 0.001
```

### Memory Optimization

- **Lazy Loading**: Extensions loaded on-demand
- **Object Pooling**: Reuse transformation objects where possible
- **Garbage Collection**: Explicit cleanup for large operations

### Monitoring

```python
# Performance monitoring in production
import time
import psutil

def monitor_transformation(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        result = func(*args, **kwargs)

        duration = time.time() - start_time
        memory_used = psutil.Process().memory_info().rss - start_memory

        # Log performance metrics
        logger.info(f"Transformation took {duration:.3f}s, used {memory_used/1024/1024:.1f}MB")

        return result
    return wrapper
```

This guide provides a comprehensive foundation for modern String-Multitool development following best practices for modularity, performance, and maintainability.