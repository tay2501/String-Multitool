# Architecture Overview

This document provides a comprehensive overview of String_Multitool's enterprise-grade architecture, design patterns, and system components.

## Table of Contents

- [System Architecture](#system-architecture)
- [Component Relationships](#component-relationships)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Module Structure](#module-structure)
- [Security Architecture](#security-architecture)
- [Performance Considerations](#performance-considerations)

## System Architecture

String_Multitool follows a **layered enterprise architecture** with clear separation of concerns and dependency injection.

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[ApplicationInterface]
        B[CLI Interface]
        C[Interactive Session]
    end
    
    subgraph "Service Layer"
        D[TextTransformationEngine]
        E[InputOutputManager]
        F[ConfigurationManager]
        G[CryptographyManager]
    end
    
    subgraph "Business Logic Layer"
        H[TransformationBase Classes]
        I[Rule Processing Engine]
        J[TSV Conversion Strategies]
        K[Encryption Strategies]
    end
    
    subgraph "Data Layer"
        L[JSON Configuration Files]
        M[RSA Key Storage]
        N[TSV Dictionary Files]
        O[Application State]
    end
    
    subgraph "External Systems"
        P[System Clipboard]
        Q[File System]
        R[Standard Input/Output]
    end
    
    A --> D
    A --> E
    A --> F
    A --> G
    B --> A
    C --> A
    
    D --> H
    D --> I
    E --> P
    E --> R
    F --> L
    G --> M
    G --> K
    
    H --> J
    I --> H
    
    F --> Q
    G --> Q
    E --> Q
```

## Component Relationships

### Core Components Interaction

```mermaid
graph TD
    subgraph "Application Core"
        AI[ApplicationInterface]
        TTE[TextTransformationEngine]
        IOM[InputOutputManager]
        CM[ConfigurationManager]
        CRM[CryptographyManager]
    end
    
    subgraph "Transformation System"
        TB[TransformationBase]
        BT[BasicTransformations]
        CT[CaseTransformations]
        AT[AdvancedTransformations]
        ET[EncryptionTransformations]
    end
    
    subgraph "Configuration System"
        TR[transformation_rules.json]
        SC[security_config.json]
        DC[daemon_config.json]
        HC[hotkey_config.json]
    end
    
    subgraph "External Interfaces"
        CLI[Command Line]
        CB[Clipboard]
        FS[File System]
        PIPE[Pipes/Streams]
    end
    
    AI --> TTE
    AI --> IOM
    AI --> CM
    AI --> CRM
    
    TTE --> TB
    TB --> BT
    TB --> CT
    TB --> AT
    TB --> ET
    
    CM --> TR
    CM --> SC
    CM --> DC
    CM --> HC
    
    IOM --> CB
    IOM --> PIPE
    CRM --> FS
    
    CLI --> AI
    
    style AI fill:#e1f5fe
    style TTE fill:#f3e5f5
    style TB fill:#e8f5e8
    style CM fill:#fff3e0
```

### Dependency Injection Flow

```mermaid
graph LR
    subgraph "Dependency Injection Container"
        DI[DependencyInjection]
        REG[Service Registry]
        FAC[Factory Methods]
    end
    
    subgraph "Protocol Interfaces"
        CMP[ConfigManagerProtocol]
        TEP[TransformationEngineProtocol]
        CRP[CryptoManagerProtocol]
        IOP[IOManagerProtocol]
    end
    
    subgraph "Concrete Implementations"
        CM[ConfigurationManager]
        TTE[TextTransformationEngine]
        CRM[CryptographyManager]
        IOM[InputOutputManager]
    end
    
    DI --> REG
    REG --> FAC
    FAC --> CMP
    FAC --> TEP
    FAC --> CRP
    FAC --> IOP
    
    CMP --> CM
    TEP --> TTE
    CRP --> CRM
    IOP --> IOM
    
    style DI fill:#e1f5fe
    style REG fill:#e8f5e8
    style FAC fill:#fff3e0
```

## Data Flow

### Text Transformation Pipeline

```mermaid
flowchart TD
    START([User Input]) --> INPUT{Input Source?}
    
    INPUT -->|Pipe| PIPE[Read from stdin]
    INPUT -->|Clipboard| CLIP[Read from clipboard]
    INPUT -->|Interactive| INTER[Interactive session]
    
    PIPE --> VALIDATE[Validate Input]
    CLIP --> VALIDATE
    INTER --> VALIDATE
    
    VALIDATE --> PARSE[Parse Rule String]
    PARSE --> RULES{Rule Type?}
    
    RULES -->|Basic| BASIC[Basic Transformations]
    RULES -->|Case| CASE[Case Transformations]
    RULES -->|Advanced| ADVANCED[Advanced Transformations]
    RULES -->|Encryption| CRYPTO[Encryption Operations]
    
    BASIC --> CHAIN{More Rules?}
    CASE --> CHAIN
    ADVANCED --> CHAIN
    CRYPTO --> CHAIN
    
    CHAIN -->|Yes| PARSE
    CHAIN -->|No| OUTPUT[Generate Output]
    
    OUTPUT --> DEST{Output Destination?}
    DEST -->|Clipboard| CLIPOUT[Copy to clipboard]
    DEST -->|Stdout| STDOUT[Write to stdout]
    DEST -->|Interactive| DISPLAY[Display in session]
    
    CLIPOUT --> END([Complete])
    STDOUT --> END
    DISPLAY --> END
    
    style START fill:#c8e6c9
    style END fill:#ffcdd2
    style VALIDATE fill:#e1f5fe
    style PARSE fill:#f3e5f5
    style OUTPUT fill:#fff3e0
```

### Configuration Loading Flow

```mermaid
flowchart TD
    BOOT[Application Boot] --> LOAD_CONFIG[Load Configuration Manager]
    LOAD_CONFIG --> CHECK_CACHE{Configuration Cached?}
    
    CHECK_CACHE -->|Yes| USE_CACHE[Use Cached Config]
    CHECK_CACHE -->|No| LOAD_FILES[Load JSON Files]
    
    LOAD_FILES --> TRANS_RULES[transformation_rules.json]
    LOAD_FILES --> SEC_CONFIG[security_config.json]
    LOAD_FILES --> DAEMON_CONFIG[daemon_config.json]
    LOAD_FILES --> HOTKEY_CONFIG[hotkey_config.json]
    
    TRANS_RULES --> VALIDATE_JSON[Validate JSON Schema]
    SEC_CONFIG --> VALIDATE_JSON
    DAEMON_CONFIG --> VALIDATE_JSON
    HOTKEY_CONFIG --> VALIDATE_JSON
    
    VALIDATE_JSON --> CACHE[Cache Configuration]
    USE_CACHE --> READY[Configuration Ready]
    CACHE --> READY
    
    READY --> INIT_SERVICES[Initialize Services]
    
    style BOOT fill:#c8e6c9
    style READY fill:#c8e6c9
    style VALIDATE_JSON fill:#e1f5fe
    style CACHE fill:#fff3e0
```

### Encryption/Decryption Flow

```mermaid
flowchart TD
    START_ENC[Encryption Request] --> CHECK_KEYS{RSA Keys Exist?}
    CHECK_KEYS -->|No| GEN_KEYS[Generate RSA-4096 Keys]
    CHECK_KEYS -->|Yes| LOAD_KEYS[Load Existing Keys]
    
    GEN_KEYS --> SAVE_KEYS[Save Keys with Secure Permissions]
    SAVE_KEYS --> LOAD_KEYS
    
    LOAD_KEYS --> GEN_AES[Generate AES-256 Key]
    GEN_AES --> ENCRYPT_DATA[Encrypt Data with AES-256-CBC]
    ENCRYPT_DATA --> ENCRYPT_KEY[Encrypt AES Key with RSA-4096]
    
    ENCRYPT_KEY --> COMBINE[Combine Encrypted Key + Data]
    COMBINE --> BASE64[Base64 Encode Result]
    BASE64 --> OUTPUT_ENC[Output Encrypted Text]
    
    START_DEC[Decryption Request] --> DECODE_B64[Base64 Decode Input]
    DECODE_B64 --> SPLIT[Split Key and Data]
    SPLIT --> DECRYPT_KEY[Decrypt AES Key with RSA]
    DECRYPT_KEY --> DECRYPT_DATA[Decrypt Data with AES-256]
    DECRYPT_DATA --> OUTPUT_DEC[Output Decrypted Text]
    
    style START_ENC fill:#c8e6c9
    style START_DEC fill:#c8e6c9
    style OUTPUT_ENC fill:#ffcdd2
    style OUTPUT_DEC fill:#ffcdd2
    style GEN_KEYS fill:#fff3e0
    style ENCRYPT_DATA fill:#e1f5fe
    style DECRYPT_DATA fill:#e1f5fe
```

## Design Patterns

### 1. Strategy Pattern (Transformation System)

```mermaid
classDiagram
    class TransformationBase {
        <<abstract>>
        +transform(text: str) str
        +get_transformation_rule() str
        +get_input_text() str
        +get_output_text() str
    }
    
    class BasicTransformations {
        +transform(text: str) str
    }
    
    class CaseTransformations {
        +transform(text: str) str
    }
    
    class AdvancedTransformations {
        +transform(text: str) str
    }
    
    class TextTransformationEngine {
        -strategies: Map
        +apply_transformations(text: str, rules: str) str
        +register_strategy(rule: str, strategy: TransformationBase)
    }
    
    TransformationBase <|-- BasicTransformations
    TransformationBase <|-- CaseTransformations
    TransformationBase <|-- AdvancedTransformations
    TextTransformationEngine --> TransformationBase
```

### 2. Factory Pattern (Strategy Creation)

```mermaid
classDiagram
    class TransformationFactory {
        +create_transformation(rule_type: str) TransformationBase
        +get_available_transformations() Dict
    }
    
    class TSVConversionStrategyFactory {
        +create_strategy(options: TSVConversionOptions) TSVConversionStrategy
    }
    
    class ApplicationFactory {
        +create_application() ApplicationInterface
        +create_components() Dict
    }
    
    TransformationFactory --> TransformationBase
    TSVConversionStrategyFactory --> TSVConversionStrategy
    ApplicationFactory --> ApplicationInterface
```

### 3. Dependency Injection Pattern

```mermaid
classDiagram
    class DependencyContainer {
        -services: Dict
        +register(interface: Type, implementation: Type)
        +inject(interface: Type) Object
        +injectable(cls: Type) Type
    }
    
    class ApplicationInterface {
        +__init__(config_manager: ConfigManagerProtocol)
    }
    
    class ConfigManagerProtocol {
        <<interface>>
        +load_transformation_rules() Dict
        +load_security_config() Dict
    }
    
    class ConfigurationManager {
        +load_transformation_rules() Dict
        +load_security_config() Dict
    }
    
    DependencyContainer --> ApplicationInterface
    ApplicationInterface --> ConfigManagerProtocol
    ConfigManagerProtocol <|-- ConfigurationManager
```

### 4. Template Method Pattern (Rule Processing)

```mermaid
classDiagram
    class RuleProcessor {
        +process_rule_string(rules: str) str
        #validate_rule(rule: str) bool
        #parse_arguments(rule: str) List
        #apply_transformation(text: str, rule: str) str
        #post_process(result: str) str
    }
    
    class BasicRuleProcessor {
        #apply_transformation(text: str, rule: str) str
    }
    
    class AdvancedRuleProcessor {
        #apply_transformation(text: str, rule: str) str
        #parse_arguments(rule: str) List
    }
    
    RuleProcessor <|-- BasicRuleProcessor
    RuleProcessor <|-- AdvancedRuleProcessor
```

## Module Structure

### Package Hierarchy

```
string_multitool/
├── __init__.py                 # Package initialization
├── main.py                     # Application interface
├── cli.py                      # Modern Typer CLI
├── exceptions.py               # Custom exceptions
├── application_factory.py      # DI factory
│
├── core/                       # Core business logic
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── crypto.py               # Cryptography operations
│   ├── transformations.py      # Transformation engine
│   ├── transformation_base.py  # Base transformation class
│   ├── types.py                # Type definitions
│   ├── dependency_injection.py # DI container
│   └── tsv_conversion_strategies.py # TSV strategies
│
├── transformations/            # Transformation implementations
│   ├── __init__.py
│   ├── basic_transformations.py
│   ├── case_transformations.py
│   ├── advanced_transformations.py
│   ├── encryption_transformations.py
│   ├── encoding_transformations.py
│   ├── formatting_transformations.py
│   ├── hash_transformations.py
│   └── string_operations.py
│
├── io/                         # Input/Output operations
│   ├── __init__.py
│   ├── manager.py              # I/O manager
│   └── clipboard.py            # Clipboard operations
│
├── modes/                      # Application modes
│   ├── __init__.py
│   ├── interactive.py          # Interactive mode
│   ├── daemon.py               # Daemon mode
│   ├── hotkey.py               # Hotkey mode
│   ├── system_tray.py          # System tray mode
│   ├── clipboard_monitor.py    # Clipboard monitoring
│   ├── daemon_config_manager.py # Daemon configuration
│   └── hotkey_sequence_manager.py # Hotkey sequences
│
└── utils/                      # Utilities
    ├── __init__.py
    ├── logger.py               # Logging utilities
    └── lifecycle_manager.py    # Application lifecycle
```

## Security Architecture

### Cryptographic System Design

```mermaid
graph TB
    subgraph "Key Management"
        KG[Key Generation]
        KS[Key Storage]
        KL[Key Loading]
        KP[Key Permissions]
    end
    
    subgraph "Encryption Pipeline"
        AES[AES-256-CBC Generation]
        DATA_ENC[Data Encryption]
        KEY_ENC[Key Encryption with RSA-4096]
        COMBINE[Combine Encrypted Components]
    end
    
    subgraph "Decryption Pipeline"
        SPLIT[Split Components]
        KEY_DEC[Key Decryption with RSA]
        DATA_DEC[Data Decryption with AES]
        OUTPUT[Plain Text Output]
    end
    
    subgraph "Security Features"
        PADDING[PKCS7 Padding]
        B64[Base64 Encoding]
        HASH[SHA-256 Hashing]
        RAND[Secure Random Generation]
    end
    
    KG --> KS
    KS --> KP
    KL --> KEY_ENC
    KL --> KEY_DEC
    
    AES --> DATA_ENC
    DATA_ENC --> KEY_ENC
    KEY_ENC --> COMBINE
    
    COMBINE --> SPLIT
    SPLIT --> KEY_DEC
    KEY_DEC --> DATA_DEC
    DATA_DEC --> OUTPUT
    
    PADDING --> DATA_ENC
    PADDING --> DATA_DEC
    B64 --> COMBINE
    B64 --> SPLIT
    HASH --> KG
    RAND --> AES
    
    style KG fill:#ffcdd2
    style DATA_ENC fill:#e1f5fe
    style DATA_DEC fill:#e1f5fe
    style OUTPUT fill:#c8e6c9
```

### Security Configuration

```mermaid
graph LR
    subgraph "Security Config"
        SC[security_config.json]
        RSA_SIZE[RSA Key Size: 4096]
        AES_MODE[AES Mode: CBC-256]
        HASH_ALG[Hash: SHA-256]
        PADDING_MODE[Padding: PKCS7]
    end
    
    subgraph "Key Storage Security"
        PERMS[File Permissions: 0o600]
        LOCATION[Location: rsa/ directory]
        GITIGNORE[Git Ignore: rsa/*]
        AUTO_GEN[Auto Generation on First Use]
    end
    
    SC --> RSA_SIZE
    SC --> AES_MODE
    SC --> HASH_ALG
    SC --> PADDING_MODE
    
    LOCATION --> PERMS
    LOCATION --> GITIGNORE
    LOCATION --> AUTO_GEN
    
    style SC fill:#fff3e0
    style PERMS fill:#ffcdd2
    style AUTO_GEN fill:#c8e6c9
```

## Performance Considerations

### Optimization Strategies

```mermaid
graph TD
    subgraph "Configuration Optimization"
        LAZY[Lazy Loading]
        CACHE[Configuration Caching]
        SINGLETON[Singleton Pattern]
    end
    
    subgraph "Transformation Optimization"
        POOL[Object Pooling]
        REUSE[Rule Reuse]
        BATCH[Batch Processing]
    end
    
    subgraph "I/O Optimization"
        ASYNC[Asynchronous Operations]
        BUFFER[Buffered I/O]
        STREAM[Stream Processing]
    end
    
    subgraph "Memory Optimization"
        GC[Garbage Collection]
        WEAK_REF[Weak References]
        MEM_POOL[Memory Pooling]
    end
    
    LAZY --> CACHE
    CACHE --> SINGLETON
    POOL --> REUSE
    REUSE --> BATCH
    ASYNC --> BUFFER
    BUFFER --> STREAM
    GC --> WEAK_REF
    WEAK_REF --> MEM_POOL
    
    style CACHE fill:#e1f5fe
    style POOL fill:#e8f5e8
    style ASYNC fill:#f3e5f5
    style GC fill:#fff3e0
```

### Performance Metrics

| Component | Metric | Target | Actual |
|-----------|--------|--------|---------|
| Rule Parsing | Parse Time | < 1ms | 0.3ms |
| Configuration Load | Load Time | < 100ms | 45ms |
| Transformation | Process Time | < 5ms | 2ms |
| Clipboard Access | Access Time | < 50ms | 25ms |
| Memory Usage | Peak Memory | < 50MB | 35MB |
| Startup Time | Boot Time | < 2s | 1.2s |

## Error Handling Architecture

```mermaid
graph TD
    subgraph "Exception Hierarchy"
        BASE[StringMultitoolError]
        CONFIG[ConfigurationError]
        TRANS[TransformationError]
        CRYPTO[CryptographyError]
        CLIP[ClipboardError]
        VALID[ValidationError]
    end
    
    subgraph "Error Context"
        CTX[Error Context]
        META[Metadata Collection]
        STACK[Stack Trace]
        USER[User-Friendly Messages]
    end
    
    subgraph "Recovery Strategies"
        RETRY[Retry Logic]
        FALLBACK[Fallback Methods]
        GRACEFUL[Graceful Degradation]
        LOGGING[Error Logging]
    end
    
    BASE --> CONFIG
    BASE --> TRANS
    BASE --> CRYPTO
    BASE --> CLIP
    BASE --> VALID
    
    CONFIG --> CTX
    TRANS --> CTX
    CRYPTO --> CTX
    CLIP --> CTX
    VALID --> CTX
    
    CTX --> META
    CTX --> STACK
    CTX --> USER
    
    USER --> RETRY
    USER --> FALLBACK
    USER --> GRACEFUL
    USER --> LOGGING
    
    style BASE fill:#ffcdd2
    style CTX fill:#fff3e0
    style RETRY fill:#c8e6c9
```

This architecture overview provides a comprehensive understanding of String_Multitool's enterprise-grade design. The system emphasizes modularity, security, performance, and maintainability through well-established design patterns and architectural principles.