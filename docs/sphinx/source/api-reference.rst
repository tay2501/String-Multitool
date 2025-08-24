API Reference
=============

This document provides comprehensive API documentation for String_Multitool's public interfaces and classes.

Core Classes
------------

ApplicationInterface
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: string_multitool.main.ApplicationInterface
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

   Main application interface and user interaction handler. Coordinates all components using dependency injection.

   Example usage:

   .. code-block:: python

      from string_multitool.main import ApplicationInterface
      
      # Initialize and run application
      app = ApplicationInterface()
      app.run()

      # Run specific modes
      app.run_interactive_mode("Hello World")
      app.run_command_mode("/t/l")

TextTransformationEngine
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: string_multitool.core.transformations.TextTransformationEngine
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

   Core text transformation engine with configurable rules and comprehensive error handling.

   Example usage:

   .. code-block:: python

      from string_multitool.core.transformations import TextTransformationEngine
      
      # Apply transformations
      engine = TextTransformationEngine(config_manager)
      result = engine.apply_transformations("  HELLO WORLD  ", "/t/l")
      # Returns: "hello world"

InputOutputManager
~~~~~~~~~~~~~~~~~~

.. autoclass:: string_multitool.io.manager.InputOutputManager
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

   Manages input and output operations with proper error handling and fallback mechanisms.

   Example usage:

   .. code-block:: python

      from string_multitool.io.manager import InputOutputManager
      
      # I/O operations
      io_manager = InputOutputManager()
      text = io_manager.get_input_text()
      io_manager.set_output_text("Hello World")

Configuration Management
------------------------

ConfigurationManager
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: string_multitool.core.config.ConfigurationManager
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

   Handles JSON configuration loading with caching and validation.

   Example usage:

   .. code-block:: python

      from string_multitool.core.config import ConfigurationManager
      
      # Load configurations
      config_manager = ConfigurationManager()
      rules = config_manager.load_transformation_rules()
      security_config = config_manager.load_security_config()

Cryptography
------------

CryptographyManager
~~~~~~~~~~~~~~~~~~~

.. autoclass:: string_multitool.core.crypto.CryptographyManager
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

   Manages RSA key generation, encryption, and decryption with hybrid AES+RSA encryption.

   Features:
   - **RSA-4096** bit keys for military-grade security
   - **AES-256-CBC** encryption for data payload
   - **Hybrid encryption** removes RSA size limitations
   - **Base64 encoding** for safe text handling
   - **Auto key generation** on first use

   Example usage:

   .. code-block:: python

      from string_multitool.core.crypto import CryptographyManager
      
      # Encryption/decryption
      crypto = CryptographyManager()
      encrypted = crypto.encrypt_text("Secret message")
      decrypted = crypto.decrypt_text(encrypted)

Transformation Classes
----------------------

TransformationBase
~~~~~~~~~~~~~~~~~~

.. autoclass:: string_multitool.core.transformation_base.TransformationBase
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

   Abstract base class for all transformation implementations.

   Example custom transformation:

   .. code-block:: python

      from string_multitool.core.transformation_base import TransformationBase
      from string_multitool.exceptions import TransformationError

      class CustomTransformation(TransformationBase):
          def transform(self, text: str) -> str:
              try:
                  self._input_text = text
                  self._output_text = text.upper().replace(' ', '_')
                  return self._output_text
              except Exception as e:
                  raise TransformationError(f"Custom transformation failed: {e}") from e

Individual Transformation Classes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each transformation rule is implemented as a separate class for modularity and testability.

Basic Transformations
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: string_multitool.transformations.basic_transformations.UnderbarToHyphenTransformation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: string_multitool.transformations.basic_transformations.HyphenToUnderbarTransformation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: string_multitool.transformations.basic_transformations.FullToHalfWidthTransformation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: string_multitool.transformations.basic_transformations.HalfToFullWidthTransformation
   :members:
   :undoc-members:
   :show-inheritance:

Case Transformations
^^^^^^^^^^^^^^^^^^^^

.. autoclass:: string_multitool.transformations.case_transformations.LowercaseTransformation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: string_multitool.transformations.case_transformations.UppercaseTransformation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: string_multitool.transformations.case_transformations.PascalCaseTransformation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: string_multitool.transformations.case_transformations.CamelCaseTransformation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: string_multitool.transformations.case_transformations.SnakeCaseTransformation
   :members:
   :undoc-members:
   :show-inheritance:

Advanced Transformations
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: string_multitool.transformations.advanced_transformations.ReplaceTransformation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: string_multitool.transformations.advanced_transformations.SlugifyTransformation
   :members:
   :undoc-members:
   :show-inheritance:

Exception Classes
-----------------

StringMultitoolError
~~~~~~~~~~~~~~~~~~~~

.. autoexception:: string_multitool.exceptions.StringMultitoolError
   :members:
   :undoc-members:
   :show-inheritance:

   Base exception class for all application errors.

Specific Exceptions
~~~~~~~~~~~~~~~~~~~

.. autoexception:: string_multitool.exceptions.ValidationError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoexception:: string_multitool.exceptions.TransformationError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoexception:: string_multitool.exceptions.ConfigurationError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoexception:: string_multitool.exceptions.CryptographyError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoexception:: string_multitool.exceptions.ClipboardError
   :members:
   :undoc-members:
   :show-inheritance:

Type Definitions
----------------

TransformationRule
~~~~~~~~~~~~~~~~~~

.. autoclass:: string_multitool.core.types.TransformationRule
   :members:
   :undoc-members:
   :show-inheritance:

   Dataclass for type-safe rule definitions.

TransformationRuleType
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: string_multitool.core.types.TransformationRuleType
   :members:
   :undoc-members:
   :show-inheritance:

   Enumeration of rule categories.

TSVConversionOptions
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: string_multitool.core.types.TSVConversionOptions
   :members:
   :undoc-members:
   :show-inheritance:

   Configuration for TSV-based text conversion.

Usage Examples
--------------

Basic API Usage
~~~~~~~~~~~~~~~

.. code-block:: python

   from string_multitool.main import ApplicationInterface
   from string_multitool.core.transformations import TextTransformationEngine
   from string_multitool.io.manager import InputOutputManager

   # Initialize components
   app = ApplicationInterface()
   io_manager = InputOutputManager()
   engine = TextTransformationEngine(config_manager)

   # Basic text transformation
   text = "  HELLO WORLD  "
   result = engine.apply_transformations(text, "/t/l")
   print(result)  # "hello world"

   # Multiple transformations
   result = engine.apply_transformations("Hello World", "/s/u")
   print(result)  # "HELLO_WORLD"

   # Clipboard operations
   io_manager.set_output_text("Hello")
   text = io_manager.get_clipboard_text()

Configuration Usage
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from string_multitool.core.config import ConfigurationManager

   # Load configurations
   config_manager = ConfigurationManager()
   rules = config_manager.load_transformation_rules()
   security_config = config_manager.load_security_config()

   # Access rule definitions
   for category, rules_dict in rules.items():
       for rule_key, rule_data in rules_dict.items():
           print(f"{rule_key}: {rule_data['description']}")

Error Handling
~~~~~~~~~~~~~~

.. code-block:: python

   from string_multitool.exceptions import (
       ValidationError, 
       TransformationError,
       ClipboardError
   )

   try:
       result = engine.apply_transformations(text, "/invalid")
   except ValidationError as e:
       print(f"Invalid rule: {e}")
   except TransformationError as e:
       print(f"Transformation failed: {e}")
   except ClipboardError as e:
       print(f"Clipboard error: {e}")

Thread Safety Notes
-------------------

* **ApplicationInterface**: Not thread-safe, create separate instances per thread
* **TextTransformationEngine**: Thread-safe for read operations, not for configuration changes
* **InputOutputManager**: Thread-safe for clipboard operations
* **ConfigurationManager**: Thread-safe with internal caching

Performance Considerations
--------------------------

* **Rule Parsing**: Rules are parsed once and cached
* **Configuration Loading**: JSON files cached after first load  
* **Clipboard Operations**: Multiple fallback methods with progressive delays
* **Memory Usage**: Minimal memory footprint with efficient string operations
* **Transformation Classes**: Stateless design enables reuse and pooling

Security Notes
--------------

* **RSA Keys**: Auto-generated with secure permissions (0o600)
* **Key Storage**: Private keys excluded from version control
* **Encryption**: Military-grade RSA-4096 + AES-256-CBC hybrid encryption
* **Input Validation**: All user input validated before processing
* **Error Handling**: Sensitive information not exposed in error messages