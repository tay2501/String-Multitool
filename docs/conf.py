# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document) are located in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

# Add both packages to path for autodoc
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../string_multitool_core'))
sys.path.insert(0, os.path.abspath('../string_multitool_extensions'))

# -- Project information -----------------------------------------------------

project = 'String-Multitool'
copyright = '2025, String-Multitool Contributors'
author = 'String-Multitool Contributors'

# The full version, including alpha/beta/rc tags
release = '2.6.0'
version = '2.6.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension modules here, they are strings of module names
# that can be imported.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.githubpages',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': None,
    '.txt': None,
    '.md': 'markdown',
}

# The master toctree document.
master_doc = 'index'

# -- Options for autodoc extension ------------------------------------------

# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = 'description'

# Don't show class signature with the class name.
autodoc_class_signature = 'separated'

# This value selects if automatically documented members are sorted
# alphabetically (value 'alphabetical'), by member type (value 'groupwise')
# or by source order (value 'bysource'). Default is alphabetical.
autodoc_member_order = 'bysource'

# This value is a list of autodoc directive flags that should be automatically
# applied to all autodoc directives.
autodoc_default_flags = ['members', 'undoc-members', 'show-inheritance']

# Mock imports for packages that might not be available during build
autodoc_mock_imports = []

# -- Options for autosummary extension --------------------------------------

# Boolean indicating whether to scan all found documents for autosummary
# directives, and to generate stub pages for each.
autosummary_generate = True

# If true, autosummary overwrites existing files by generated stub pages.
autosummary_generate_overwrite = True

# A dictionary of values to pass into the template engine's context for
# autosummary stubs files.
autosummary_context = {}

# This value contains a list of modules to be mocked up.
autosummary_mock_imports = []

# A boolean flag indicating whether to document classes and functions
# imported in modules.
autosummary_imported_members = False

# -- Options for napoleon extension -----------------------------------------

# True to parse NumPy style docstrings. False to disable NumPy style docstrings.
napoleon_numpy_docstring = True

# True to parse Google style docstrings. False to disable Google style docstrings.
napoleon_google_docstring = True

# True to include special members (like __membername__) with docstrings in the documentation.
napoleon_include_special_with_doc = True

# True to include private members (like _membername) with docstrings in the documentation.
napoleon_include_private_with_doc = False

# True to include init docstrings in the documentation.
napoleon_include_init_with_doc = False

# True to use the .. admonition:: directive for the Example and Examples sections.
napoleon_use_admonition_for_examples = False

# True to use the .. admonition:: directive for the Note and Notes sections.
napoleon_use_admonition_for_notes = False

# True to use the .. admonition:: directive for the Parameters section.
napoleon_use_admonition_for_parameters = False

# True to use the .. admonition:: directive for the References section.
napoleon_use_admonition_for_references = False

# True to use the :ivar: role for instance variables.
napoleon_use_ivar = False

# True to use a :param: role for each function parameter.
napoleon_use_param = True

# True to use a :keyword: role for each function keyword argument.
napoleon_use_keyword = True

# True to use the :rtype: role for the return type.
napoleon_use_rtype = True

# -- Options for intersphinx extension --------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'typing': ('https://docs.python.org/3/', None),
    'pathlib': ('https://docs.python.org/3/', None),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = 'sphinx_rtd_theme'

# Theme options are theme-specific and customize the look and feel of a theme
# further.
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'style_nav_header_background': '#2980b9',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS files
html_css_files = [
    'css/custom.css',
]

# Custom JavaScript files
html_js_files = [
    'js/custom.js',
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    'preamble': '',

    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'String-Multitool.tex', 'String-Multitool Documentation',
     'String-Multitool Contributors', 'manual'),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'string-multitool', 'String-Multitool Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'String-Multitool', 'String-Multitool Documentation',
     author, 'String-Multitool', 'Modular string transformation toolkit.',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
epub_identifier = 'https://github.com/tay2501/String-Multitool'

# A unique identification for the text.
epub_uid = 'String-Multitool'

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# -- Custom configuration for String-Multitool ------------------------------

# Custom roles and directives
def setup(app):
    """Setup function for custom Sphinx configuration."""
    app.add_css_file('css/custom.css')
    app.add_js_file('js/custom.js')

    # Add custom domain for transformation rules
    from sphinx.domains import Domain, ObjType
    from sphinx.directives import ObjectDescription
    from sphinx.roles import XRefRole

    class TransformationRule(ObjectDescription):
        """Custom directive for documenting transformation rules."""
        def handle_signature(self, sig, signode):
            signode += [
                sphinx.addnodes.desc_name(text=sig)
            ]
            return sig

    class TransformationDomain(Domain):
        """Domain for transformation rule documentation."""
        name = 'transform'
        label = 'Transformation Rules'

        object_types = {
            'rule': ObjType('rule', 'rule'),
        }

        directives = {
            'rule': TransformationRule,
        }

        roles = {
            'rule': XRefRole(),
        }

    app.add_domain(TransformationDomain)

# Suppress warnings for missing references
suppress_warnings = ['ref.citation']

# Show more detailed error messages
keep_warnings = True
nitpicky = True

# Configure code-block highlighting
highlight_language = 'python3'
highlight_options = {}

# Configure autosectionlabel
autosectionlabel_prefix_document = True

# Configure todo extension
todo_include_todos = True
todo_emit_warnings = True

# Configure coverage extension
coverage_ignore_modules = []
coverage_ignore_functions = []
coverage_ignore_classes = []

# Configure doctest extension
doctest_global_setup = '''
import string_multitool_core
import string_multitool_extensions
'''

doctest_test_doctest_blocks = 'default'