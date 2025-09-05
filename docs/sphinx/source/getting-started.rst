Getting Started
===============

This guide helps you get started with String_Multitool in under 5 minutes.

Prerequisites
-------------

* **Python 3.10+** (required)
* Windows, macOS, or Linux
* Basic command-line knowledge

Installation
------------

Step 1: Clone and Setup
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/yourusername/String-Multitool.git
   cd String-Multitool

   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt

Step 2: Verify Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Test the installation
   python String_Multitool.py help

If you see a list of transformation rules, you're ready to go! 🎉

Your First Transformations
---------------------------

Method 1: Pipe Input (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Transform text directly from command line:

.. code-block:: bash

   # Convert to uppercase
   echo "hello world" | python String_Multitool.py /u
   # Result: "HELLO WORLD"

   # Trim whitespace and convert to lowercase  
   echo "  HELLO WORLD  " | python String_Multitool.py /t/l
   # Result: "hello world"

   # Convert to snake_case
   echo "Hello World Test" | python String_Multitool.py /s
   # Result: "hello_world_test"

Method 2: Clipboard Mode
~~~~~~~~~~~~~~~~~~~~~~~~

Work with your clipboard content:

.. code-block:: bash

   # 1. Copy some text to your clipboard first
   # 2. Run transformation on clipboard content
   python String_Multitool.py /u
   # Your clipboard now contains the uppercase version

Method 3: Interactive Mode
~~~~~~~~~~~~~~~~~~~~~~~~~~

For continuous text processing:

.. code-block:: bash

   # Start interactive mode
   python String_Multitool.py

   # You'll see:
   # String_Multitool - Interactive Mode
   # Input text: 'your clipboard content...' (25 chars, from clipboard)
   # Rules: 

   # Type a transformation rule:
   Rules: /u
   # Result: 'YOUR CLIPBOARD CONTENT...'

   # Type 'help' for all available rules
   Rules: help

   # Type 'quit' to exit
   Rules: quit

Essential Rules
---------------

Master these 5 rules to handle 90% of text transformation needs:

.. list-table:: The Big 5 Rules
   :widths: 10 20 30 40
   :header-rows: 1

   * - Rule
     - Name
     - Example
     - Use Case
   * - ``/t``
     - **Trim**
     - ``"  hello  "`` → ``"hello"``
     - Clean up messy text
   * - ``/l``
     - **Lowercase**
     - ``"HELLO"`` → ``"hello"``
     - Normalize case
   * - ``/u``
     - **Uppercase**
     - ``"hello"`` → ``"HELLO"``
     - Emphasize text
   * - ``/s``
     - **snake_case**
     - ``"Hello World"`` → ``"hello_world"``
     - Programming variables
   * - ``/p``
     - **PascalCase**
     - ``"hello world"`` → ``"HelloWorld"``
     - Class names

Chain Multiple Rules
~~~~~~~~~~~~~~~~~~~~

The power comes from combining rules:

.. code-block:: bash

   # Clean and format for programming
   echo "  User Profile Settings  " | python String_Multitool.py /t/s
   # Result: "user_profile_settings"

   # Clean and convert to uppercase
   echo "  hello world  " | python String_Multitool.py /t/u  
   # Result: "HELLO WORLD"

Common Use Cases
----------------

Programming: Variable Names
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Convert UI text to variable names
   echo "User First Name" | python String_Multitool.py /s
   # Result: "user_first_name"

   # Convert to class names  
   echo "user profile manager" | python String_Multitool.py /p
   # Result: "UserProfileManager"

Data Cleaning: Text Cleanup
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clean messy CSV data
   echo "  Product Name  " | python String_Multitool.py /t/l
   # Result: "product name"

   # Normalize database identifiers
   echo "User-Profile-ID" | python String_Multitool.py /hu/s
   # Result: "user_profile_id"

Documentation: Text Formatting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Normalize headings
   echo "  API DOCUMENTATION GUIDE  " | python String_Multitool.py /t/a
   # Result: "Api Documentation Guide"

   # Create URL-friendly text
   echo "My Blog Post Title" | python String_Multitool.py /l/S
   # Result: "my-blog-post-title"

Next Steps
----------

Now that you've mastered the basics:

1. **Explore All Rules**: Run ``python String_Multitool.py help`` to see all available transformations
2. **Try Interactive Mode**: Experience the auto-detection feature with multiple text snippets
3. **Set Up Daemon Mode**: For automatic background processing
4. **Read the Complete Documentation**: Check out the full API reference for advanced features

Need Help?
----------

* **Show All Rules**: ``python String_Multitool.py help``
* **Test a Rule**: ``echo "test" | python String_Multitool.py /rule``
* **Interactive Practice**: ``python String_Multitool.py`` then type rules to experiment

Quick Reference Card
--------------------

Save this for quick access:

.. code-block:: bash

   # Basic transformations
   /t    # Trim whitespace
   /l    # lowercase  
   /u    # UPPERCASE
   /s    # snake_case
   /p    # PascalCase
   /c    # camelCase

   # Text operations
   /R    # Reverse text
   /r 'find' 'replace'  # Replace text

   # Advanced
   /enc  # RSA encrypt
   /dec  # RSA decrypt
   /tsvtr file.tsv  # Convert using TSV dictionary

   # Chain rules with /
   /t/l/s    # trim → lowercase → snake_case

**Congratulations! You're now ready to use String_Multitool effectively.** 🚀