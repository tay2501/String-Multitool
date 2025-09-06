Sphinx Documentation Usage Guide
==================================

This guide provides comprehensive instructions for using and maintaining the Sphinx documentation system for String_Multitool.

Prerequisites
-------------

Ensure you have the required Sphinx packages installed:

.. code-block:: bash

   # Install Sphinx and extensions with uv
   uv add --dev sphinx sphinx-autodoc-typehints sphinx-rtd-theme

   # Or sync all development dependencies
   uv sync --all-extras --dev

Basic Usage
-----------

Building Documentation
~~~~~~~~~~~~~~~~~~~~~~

Navigate to the Sphinx documentation directory and build HTML documentation:

.. code-block:: bash

   # Navigate to Sphinx directory
   cd docs/sphinx

   # Build HTML documentation
   make html

   # Alternative: direct sphinx-build command
   sphinx-build -b html source build/html

The generated HTML files will be available in ``build/html/`` directory. Open ``build/html/index.html`` in your web browser to view the documentation.

Clean Previous Builds
~~~~~~~~~~~~~~~~~~~~~~

To ensure a clean build (recommended after configuration changes):

.. code-block:: bash

   # Clean previous builds
   make clean

   # Then rebuild
   make html

Development Workflow
--------------------

Adding New Documentation Pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Create RST file**: Add new ``.rst`` files in ``docs/sphinx/source/`` directory

   .. code-block:: rst

      New Feature Documentation
      =========================

      Introduction to new feature...

      Usage Examples
      --------------

      .. code-block:: python

         # Example usage
         from string_multitool import NewFeature
         feature = NewFeature()

2. **Update toctree**: Add the new file to appropriate ``toctree`` directive in ``index.rst``:

   .. code-block:: rst

      .. toctree::
         :maxdepth: 2
         :caption: Contents:

         getting-started
         api-reference
         new-feature-doc
         architecture
         modules

3. **Rebuild documentation**: Run ``make html`` to include new pages

Auto-Generated API Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Sphinx configuration is set up to automatically generate API documentation from Python docstrings.

**Updating API Documentation:**

1. **Add docstrings** to your Python code using Google or NumPy style:

   .. code-block:: python

      def transform_text(text: str, rules: str) -> str:
          """Apply transformation rules to input text.

          Args:
              text: The input text to transform
              rules: Rule string like '/t/l' for trim + lowercase

          Returns:
              Transformed text according to specified rules

          Raises:
              ValidationError: If rules are invalid
              TransformationError: If transformation fails

          Example:
              >>> transform_text("  HELLO  ", "/t/l")
              'hello'
          """
          pass

2. **Update modules.rst** if you add new modules:

   .. code-block:: rst

      New Module Documentation
      ~~~~~~~~~~~~~~~~~~~~~~~~

      .. automodule:: string_multitool.new_module
         :members:
         :undoc-members:
         :show-inheritance:

3. **Rebuild** to see updated API documentation

Configuration Management
-------------------------

Key Configuration Files
~~~~~~~~~~~~~~~~~~~~~~~~

``conf.py``
^^^^^^^^^^^

Main Sphinx configuration file with the following key settings:

.. code-block:: python

   # Project information
   project = 'String_Multitool'
   release = '2.6.0'

   # Extensions for advanced features
   extensions = [
       'sphinx.ext.autodoc',        # Auto-generate from docstrings
       'sphinx.ext.viewcode',       # Add source code links
       'sphinx.ext.napoleon',       # Google/NumPy docstring support
       'sphinx.ext.intersphinx',    # Cross-reference external docs
       'sphinx_autodoc_typehints',  # Type hint documentation
   ]

   # Theme configuration
   html_theme = 'sphinx_rtd_theme'

**Important Configuration Options:**

- ``autodoc_member_order = 'bysource'``: Order members as they appear in source
- ``napoleon_google_docstring = True``: Enable Google-style docstrings
- ``autodoc_typehints = 'description'``: Include type hints in descriptions

Advanced Features
-----------------

Cross-References and Links
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create internal links within documentation:

.. code-block:: rst

   # Reference to class
   :class:`string_multitool.main.ApplicationInterface`

   # Reference to method
   :meth:`string_multitool.core.transformations.TextTransformationEngine.apply_transformations`

   # Reference to function
   :func:`string_multitool.io.manager.InputOutputManager.get_input_text`

   # Reference to section
   :ref:`getting-started`

Code Examples with Syntax Highlighting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: rst

   # Python code block
   .. code-block:: python

      from string_multitool.main import ApplicationInterface
      app = ApplicationInterface()
      app.run()

   # Bash command block
   .. code-block:: bash

      echo "hello" | python String_Multitool.py /u

   # JSON configuration block
   .. code-block:: json

      {
          "rule": {
              "name": "uppercase",
              "key": "u"
          }
      }

Mathematical Expressions
~~~~~~~~~~~~~~~~~~~~~~~~~

Include mathematical expressions using LaTeX syntax:

.. code-block:: rst

   # Inline math
   The encryption uses :math:`RSA_{4096}` keys.

   # Block math
   .. math::

      E(m) = m^e \bmod n

Tables and Lists
~~~~~~~~~~~~~~~~

.. code-block:: rst

   # Simple table
   .. list-table:: Transformation Rules
      :widths: 10 20 70
      :header-rows: 1

      * - Rule
        - Name
        - Description
      * - /t
        - Trim
        - Remove leading/trailing whitespace
      * - /l
        - Lowercase
        - Convert text to lowercase

Troubleshooting
---------------

Common Issues and Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Issue: "Module not found" errors during build**

Solution:
  Update ``sys.path`` in ``conf.py`` to include your project root:

  .. code-block:: python

     import os
     import sys
     sys.path.insert(0, os.path.abspath('../../../'))

**Issue: Type hints not showing in documentation**

Solution:
  Ensure ``sphinx-autodoc-typehints`` is installed and configured:

  .. code-block:: python

     extensions = [..., 'sphinx_autodoc_typehints']
     autodoc_typehints = 'description'

**Issue: Docstrings not appearing**

Solution:
  Check docstring format (use Google or NumPy style) and ensure Napoleon is enabled:

  .. code-block:: python

     napoleon_google_docstring = True
     napoleon_numpy_docstring = True

**Issue: Build warnings about missing references**

Solution:
  Use proper cross-reference syntax and ensure referenced items exist:

  .. code-block:: rst

     # Correct
     :class:`string_multitool.main.ApplicationInterface`
     
     # Incorrect
     :class:`ApplicationInterface`

Deployment and Publishing
-------------------------

Local Documentation Server
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Serve documentation locally for testing:

.. code-block:: bash

   # Navigate to build directory
   cd docs/sphinx/build/html

   # Start simple HTTP server
   python -m http.server 8000

   # Open http://localhost:8000 in browser

GitHub Pages Deployment
~~~~~~~~~~~~~~~~~~~~~~~~

For GitHub Pages deployment, consider using GitHub Actions workflow:

.. code-block:: yaml

   # .github/workflows/docs.yml
   name: Build and Deploy Documentation

   on:
     push:
       branches: [ main ]

   jobs:
     docs:
       runs-on: ubuntu-latest
       steps:
       - uses: actions/checkout@v2
       - uses: actions/setup-python@v2
         with:
           python-version: '3.10'
       - name: Install dependencies
         run: |
           uv sync --all-extras --dev
           uv add --dev sphinx sphinx-autodoc-typehints sphinx-rtd-theme
       - name: Build documentation
         run: |
           cd docs/sphinx
           make html
       - name: Deploy to GitHub Pages
         uses: peaceiris/actions-gh-pages@v3
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}
           publish_dir: docs/sphinx/build/html

Documentation Standards
-----------------------

Writing Guidelines
~~~~~~~~~~~~~~~~~~

1. **Use clear, concise language** suitable for both beginners and experienced users
2. **Include practical examples** for every API function and feature
3. **Maintain consistent formatting** using RST conventions
4. **Add cross-references** to related sections and API elements
5. **Update version information** when making significant changes

Docstring Standards
~~~~~~~~~~~~~~~~~~~

Follow Google-style docstrings for consistency:

.. code-block:: python

   def example_function(param1: str, param2: int = 10) -> bool:
       """Brief description of the function.

       Longer description explaining the function's purpose,
       behavior, and any important implementation details.

       Args:
           param1: Description of the first parameter.
           param2: Description of the second parameter. Defaults to 10.

       Returns:
           Description of the return value.

       Raises:
           ValueError: When param1 is empty.
           TypeError: When param2 is not an integer.

       Example:
           Basic usage example:

           >>> result = example_function("test", 5)
           >>> print(result)
           True

       Note:
           Any additional notes or warnings.
       """
       pass

Maintenance Schedule
--------------------

Regular Maintenance Tasks
~~~~~~~~~~~~~~~~~~~~~~~~~

**Weekly:**
- Review and update outdated examples
- Check for broken internal links
- Verify new API changes are documented

**Monthly:**
- Update version information in ``conf.py``
- Review and improve documentation structure
- Check external link validity

**Release Cycle:**
- Generate fresh API documentation
- Update getting started guide with new features
- Review and update architecture documentation
- Publish updated documentation

Quality Assurance
~~~~~~~~~~~~~~~~~~

Before publishing documentation updates:

1. **Build without warnings**: ``make html`` should complete cleanly
2. **Test all examples**: Verify code examples work as documented  
3. **Check cross-references**: Ensure all internal links resolve correctly
4. **Review rendered output**: Manually check HTML output in browser
5. **Validate markup**: Use RST validators for syntax checking

This comprehensive guide ensures consistent, high-quality documentation maintenance for the String_Multitool project.