Architecture Overview
=====================

This document provides a comprehensive overview of String_Multitool's enterprise-grade architecture, focusing on modular design, security, and extensibility.

System Architecture
-------------------

String_Multitool follows a **modular enterprise architecture** with clear separation of concerns and dependency injection patterns.

High-Level Architecture Diagram
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    ┌─────────────────────────────────────────────────────────────────┐
    │                    ApplicationInterface                         │
    │                 (Main UI & Coordination)                       │
    └─────────────────────┬───────────────────────────────────────────┘
                          │
    ┌─────────────────────┴───────────────────────────────────────────┐
    │                     Dependency Injection Layer                 │
    └─┬──────────┬─────────────┬──────────────┬────────────────────┬──┘
      │          │             │              │                    │
    ┌─▼────────┐ │ ┌───────────▼──┐ ┌─────────▼────┐ ┌─────────────▼────┐
    │Configuration│ │TextTransform-│ │Cryptography- │ │   InputOutput-   │
    │  Manager    │ │    Engine    │ │   Manager    │ │     Manager      │
    │             │ │              │ │              │ │                  │
    │• JSON Cfg   │ │• Rule Engine │ │• RSA-4096    │ │• Clipboard Ops   │
    │• Caching    │ │• Validation  │ │• AES-256-CBC │ │• Pipe Input      │
    │• Security   │ │• Chaining    │ │• Key Mgmt    │ │• UTF-8 Handling  │
    └─────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘
                          │
                    ┌─────▼─────┐
                    │Transform- │
                    │ ation     │
                    │ Classes   │
                    │           │
                    │• Modular  │
                    │• Testable │
                    │• Pluggable│
                    └───────────┘

Core Components
---------------

ApplicationInterface
~~~~~~~~~~~~~~~~~~~~

**Role**: Main application interface and coordination layer
**Responsibilities**:
- Command-line argument parsing
- Mode selection (interactive, command, daemon)
- Component orchestration via dependency injection
- Error handling and user feedback

**Key Features**:
- Supports multiple execution modes
- Flexible component injection for testing
- Comprehensive error handling
- User-friendly help system

TextTransformationEngine
~~~~~~~~~~~~~~~~~~~~~~~~~

**Role**: Core text processing engine
**Responsibilities**:
- Rule parsing and validation
- Sequential transformation chaining
- Dynamic class instantiation
- Performance optimization

**Architecture Pattern**: Factory Pattern + Strategy Pattern

.. code-block:: text

    Rule Input ("/t/l/u")
           │
           ▼
    ┌─────────────┐
    │ Rule Parser │ ──┐
    └─────────────┘   │
                      ▼
    ┌─────────────────────────────┐
    │ Transformation Factory      │
    │ ┌─────────────────────────┐ │
    │ │ get_transformation_     │ │
    │ │ class_map()             │ │
    │ │                         │ │
    │ │ "t" → TrimTransformation│ │
    │ │ "l" → LowercaseTransf.  │ │
    │ │ "u" → UppercaseTransf.  │ │
    │ └─────────────────────────┘ │
    └─────────────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────┐
    │ Sequential Execution        │
    │ ┌─────┐ ┌─────┐ ┌─────┐    │
    │ │ /t  │→│ /l  │→│ /u  │    │
    │ └─────┘ └─────┘ └─────┘    │
    └─────────────────────────────┘

ConfigurationManager
~~~~~~~~~~~~~~~~~~~~

**Role**: Configuration loading and management
**Responsibilities**:
- JSON configuration parsing
- Configuration validation
- Caching for performance
- Security configuration management

**Configuration Files**:
- ``config/transformation_rules.json`` - Rule definitions
- ``config/security_config.json`` - Encryption settings
- ``config/daemon_config.json`` - Daemon mode presets

CryptographyManager
~~~~~~~~~~~~~~~~~~~

**Role**: Security and encryption services
**Responsibilities**:
- RSA key generation and management
- Hybrid AES+RSA encryption
- Secure key storage
- Base64 encoding for text safety

**Security Architecture**:

.. code-block:: text

    Input Text
        │
        ▼
    ┌─────────────────┐
    │ AES-256-CBC     │ ← Random AES key
    │ Encryption      │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ RSA-4096-OAEP   │ ← Public key
    │ Key Encryption  │
    └─────────┬───────┘
              │
              ▼
    ┌─────────────────┐
    │ Base64 Encoding │
    │ (Safe Text)     │
    └─────────────────┘

InputOutputManager
~~~~~~~~~~~~~~~~~~

**Role**: Input/output operations and clipboard management
**Responsibilities**:
- Clipboard access with multiple fallbacks
- Pipe input detection and processing
- UTF-8 encoding handling
- Cross-platform compatibility

Transformation Class Architecture
----------------------------------

Modular Class-Based Design
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each transformation rule is implemented as a separate class inheriting from ``TransformationBase``.

**Benefits**:
- **Testability**: Each transformation can be unit tested independently
- **Extensibility**: New transformations easily added
- **Maintainability**: Clear separation of concerns
- **Debuggability**: Individual transformation state tracking

Class Hierarchy
~~~~~~~~~~~~~~~

.. code-block:: text

    TransformationBase (Abstract)
           │
           ├── BasicTransformations
           │   ├── TrimTransformation
           │   ├── LowercaseTransformation
           │   ├── UppercaseTransformation
           │   └── ReverseTransformation
           │
           ├── CaseTransformations
           │   ├── PascalCaseTransformation
           │   ├── CamelCaseTransformation
           │   ├── SnakeCaseTransformation
           │   └── CapitalizeTransformation
           │
           ├── StringOperations
           │   ├── ReplaceTransformation
           │   └── SlugifyTransformation
           │
           ├── AdvancedTransformations
           │   ├── TSVTransformation
           │   └── HashTransformation
           │
           └── EncryptionTransformations
               ├── EncryptionTransformation
               └── DecryptionTransformation

Factory Pattern Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic class instantiation via factory method:

.. code-block:: python

    def get_transformation_class_map() -> dict[str, type[TransformationBase]]:
        """Factory method for transformation class mapping."""
        return {
            't': TrimTransformation,
            'l': LowercaseTransformation,
            'u': UppercaseTransformation,
            's': SnakeCaseTransformation,
            'p': PascalCaseTransformation,
            'c': CamelCaseTransformation,
            # ... additional mappings
        }

Security Architecture
---------------------

Multi-Layer Security Model
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Layer 1: Input Validation**
- Rule syntax validation
- Parameter sanitization
- Type checking

**Layer 2: Cryptographic Security**
- RSA-4096 bit keys (military-grade)
- AES-256-CBC for bulk encryption
- Secure random key generation

**Layer 3: Key Management**
- Automatic key generation on first use
- Secure file permissions (0o600)
- Keys excluded from version control

**Layer 4: Error Handling**
- No sensitive data in error messages
- Secure failure modes
- Comprehensive logging for security events

Encryption Flow
~~~~~~~~~~~~~~~

.. code-block:: text

    Plaintext Input
          │
          ▼
    ┌─────────────┐
    │Generate     │
    │Random AES   │
    │Key (32 bytes)│
    └──────┬──────┘
           │
           ▼
    ┌─────────────┐    ┌─────────────┐
    │AES Encrypt  │    │RSA Encrypt  │
    │Data Payload │    │AES Key      │
    └──────┬──────┘    └──────┬──────┘
           │                  │
           └────────┬─────────┘
                    │
                    ▼
           ┌─────────────┐
           │Combine &    │
           │Base64 Encode│
           └─────────────┘

Data Flow Architecture
----------------------

Request Processing Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    User Input (CLI/Interactive)
              │
              ▼
    ┌─────────────────────┐
    │ ApplicationInterface │
    │ • Argument Parsing   │
    │ • Mode Selection     │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │ InputOutputManager  │
    │ • Source Detection  │
    │ • UTF-8 Handling    │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │TextTransformation   │
    │Engine               │
    │ • Rule Parsing      │
    │ • Validation        │
    │ • Class Factory     │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │ Transformation      │
    │ Execution Chain     │
    │ • Sequential Rules  │
    │ • Error Handling    │
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────┐
    │ Output Processing   │
    │ • Clipboard Copy    │
    │ • Console Display   │
    └─────────────────────┘

Configuration Loading Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    Application Startup
              │
              ▼
    ┌─────────────────────┐
    │ ConfigurationManager │
    │ Initialization       │
    └─────────┬───────────┘
              │
              ├─────────────────────────┐
              │                         │
              ▼                         ▼
    ┌─────────────────┐      ┌─────────────────┐
    │transformation_  │      │security_config. │
    │rules.json       │      │json             │
    └─────────┬───────┘      └─────────┬───────┘
              │                         │
              └─────────┬───────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Configuration Cache │
              │ • In-Memory Store   │
              │ • Validation        │
              └─────────────────────┘

Performance Architecture
------------------------

Optimization Strategies
~~~~~~~~~~~~~~~~~~~~~~~~

**Configuration Caching**
- JSON files loaded once on startup
- In-memory caching for rule definitions
- Lazy loading for optional components

**String Processing**
- Efficient string operations
- Minimal memory allocations
- Unicode-aware processing

**Clipboard Operations**
- Multiple fallback methods
- Progressive retry delays
- Cross-platform compatibility

**Transformation Classes**
- Stateless design enables pooling
- Minimal object creation overhead
- Efficient rule chaining

Memory Management
~~~~~~~~~~~~~~~~~

.. code-block:: text

    Memory Layout
    
    ┌─────────────────────┐
    │ Configuration Cache │ ← Persistent
    │ • Rules Dictionary  │
    │ • Security Settings │
    └─────────────────────┘
    
    ┌─────────────────────┐
    │ Transformation      │ ← Per Request
    │ Instance Memory     │
    │ • Input Text        │
    │ • Output Text       │
    │ • Intermediate      │
    └─────────────────────┘
    
    ┌─────────────────────┐
    │ Clipboard Buffer    │ ← Transient
    │ • Input Buffer      │
    │ • Output Buffer     │
    └─────────────────────┘

Extensibility Architecture
--------------------------

Plugin System Design
~~~~~~~~~~~~~~~~~~~~

**Adding New Transformations**:
1. Create class inheriting from ``TransformationBase``
2. Add rule definition to ``transformation_rules.json``
3. Register in factory method
4. Add unit tests

**Adding New Modes**:
1. Create mode module in ``modes/`` directory
2. Implement mode interface
3. Register in ``ApplicationInterface``
4. Add configuration support

Extension Points
~~~~~~~~~~~~~~~~

.. code-block:: text

    Core System
    │
    ├── Transformation Extensions
    │   ├── Custom Rule Classes
    │   ├── External Libraries
    │   └── Plugin Modules
    │
    ├── Mode Extensions
    │   ├── Custom Modes
    │   ├── Integration APIs
    │   └── Event Handlers
    │
    ├── Configuration Extensions
    │   ├── Custom Config Sources
    │   ├── Environment Variables
    │   └── Runtime Settings
    │
    └── I/O Extensions
        ├── Custom Input Sources
        ├── Output Destinations
        └── Protocol Handlers

Cross-Platform Architecture
---------------------------

Platform Abstraction
~~~~~~~~~~~~~~~~~~~~

**Clipboard Operations**:
- Windows: ``pyperclip`` with fallbacks
- macOS: ``pbcopy``/``pbpaste`` integration
- Linux: ``xclip``/``xsel`` support

**File System Operations**:
- Path handling via ``pathlib``
- Permission management
- Unicode file names

**Process Management**:
- Cross-platform daemon mode
- Signal handling
- Process isolation

Error Handling Architecture
---------------------------

Exception Hierarchy
~~~~~~~~~~~~~~~~~~~

.. code-block:: text

    Exception
    │
    └── StringMultitoolError
        │
        ├── ValidationError
        │   ├── RuleValidationError
        │   └── InputValidationError
        │
        ├── TransformationError
        │   ├── RuleNotFoundError
        │   └── TransformationFailedError
        │
        ├── ConfigurationError
        │   ├── ConfigFileError
        │   └── ConfigValidationError
        │
        ├── CryptographyError
        │   ├── KeyGenerationError
        │   └── EncryptionError
        │
        └── ClipboardError
            ├── ClipboardAccessError
            └── ClipboardWriteError

Error Recovery Strategy
~~~~~~~~~~~~~~~~~~~~~~~

**Graceful Degradation**:
- Clipboard failures → Use stdin/stdout
- Configuration errors → Use defaults
- Transformation errors → Skip invalid rules
- Network errors → Local operation mode

**User Experience**:
- Clear error messages
- Actionable suggestions
- Help system integration
- Debug mode availability

Testing Architecture
--------------------

Test Organization
~~~~~~~~~~~~~~~~~

.. code-block:: text

    tests/
    │
    ├── unit/
    │   ├── test_transformations.py
    │   ├── test_config.py
    │   └── test_crypto.py
    │
    ├── integration/
    │   ├── test_application.py
    │   └── test_workflows.py
    │
    ├── fixtures/
    │   ├── test_data.json
    │   └── sample_configs/
    │
    └── conftest.py

Testing Strategies
~~~~~~~~~~~~~~~~~~

**Unit Testing**:
- Each transformation class individually tested
- Mock external dependencies
- Comprehensive edge case coverage

**Integration Testing**:
- End-to-end rule application workflows
- Multi-component interaction testing
- Cross-platform compatibility verification

**Security Testing**:
- Cryptographic operation validation
- Key generation and management
- Input sanitization verification

Deployment Architecture
-----------------------

Distribution Packaging
~~~~~~~~~~~~~~~~~~~~~~

**PyInstaller Executable**:
- Single-file distribution
- Embedded Python runtime
- Cross-platform compatibility
- Optimized size and startup time

**Package Structure**:

.. code-block:: text

    String_Multitool.exe
    │
    ├── Python Runtime
    ├── Application Code
    ├── Configuration Files
    ├── Dependencies
    │   ├── pyperclip
    │   ├── cryptography
    │   └── pynput
    └── Resources
        ├── Default Configs
        └── Documentation

Installation Modes
~~~~~~~~~~~~~~~~~~

**Portable Mode**:
- Self-contained executable
- Configuration in executable directory
- No system registration required

**System Installation**:
- PATH environment integration
- System-wide configuration
- Service registration (daemon mode)

This architecture ensures String_Multitool remains maintainable, extensible, and secure while providing excellent performance and user experience across all supported platforms.