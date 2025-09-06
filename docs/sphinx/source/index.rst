String_Multitool Documentation
===============================

Welcome to String_Multitool's comprehensive documentation. This enterprise-grade text transformation tool provides powerful, configurable text processing with military-grade encryption capabilities.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   getting-started
   api-reference
   sphinx-usage
   architecture
   modules

Overview
--------

String_Multitool is an advanced text transformation tool featuring:

* **Enterprise Architecture**: Modular design with dependency injection
* **Intuitive Syntax**: Rule-based transformations (e.g., `/t/l` for trim + lowercase)
* **Military-Grade Security**: RSA-4096 + AES-256 hybrid encryption
* **Cross-Platform**: Windows, macOS, Linux support
* **Multiple Modes**: Interactive, daemon, hotkey, and system tray modes

Quick Start
-----------

Basic installation and usage:

.. code-block:: bash

   # Install with uv
   uv sync
   
   # Basic transformation
   echo "  HELLO WORLD  " | python String_Multitool.py /t/l
   # Result: "hello world"
   
   # Interactive mode
   python String_Multitool.py

Features
--------

Core Functionality
~~~~~~~~~~~~~~~~~~

* **Text Transformations**: 25+ built-in transformation rules
* **Sequential Processing**: Chain multiple transformations
* **Pipe Support**: Seamless shell integration
* **Clipboard Integration**: Automatic clipboard operations
* **Unicode Support**: Full-width ↔ half-width conversion

Enterprise Features
~~~~~~~~~~~~~~~~~~~

* **Type Safety**: Comprehensive type hints and validation
* **Configuration-Driven**: External JSON rule definitions
* **Error Handling**: Professional error recovery
* **Extensible Design**: Easy custom rule addition
* **Performance Optimized**: Efficient processing algorithms

Security Features
~~~~~~~~~~~~~~~~~

* **RSA-4096 Encryption**: Military-grade key generation
* **AES-256-CBC**: Unlimited text size encryption
* **Secure Key Storage**: Automatic key management
* **Base64 Encoding**: Safe text representation

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`