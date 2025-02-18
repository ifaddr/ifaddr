# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

from sphinx.application import Sphinx

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use Path.absolute to make it absolute.
sys.path.insert(0, str(Path(__file__).parent.parent))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'ifaddr'
project_copyright = '2014, Stefan C. Mueller'
# author = ''

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '0.1.1'
# The full version, including alpha/beta/rc tags.
release = '0.1.1'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

htmlhelp_basename = 'pythondoc'


# -- Options for LaTeX output --------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    #'preamble': '',
}

latex_documents = [
    ('index', 'python.tex', 'ifaddr Documentation', 'Stefan C. Mueller', 'manual'),
]


# -- Options for manual page output --------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-manual-page-output

man_pages = [('index', 'python', 'ifaddr Documentation', ['Stefan C. Mueller'], 1)]


# -- Options for Texinfo output ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-texinfo-output

texinfo_documents = [
    (
        'index',
        'python',
        'ifaddr Documentation',
        'Stefan C. Mueller',
        'python',
        'Enumerates all IP addresses on all network adapters of the system.',
        'Miscellaneous',
    ),
]


# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

# -- Options for autodoc extension -------------------------------------------


def skip(app, what, name: str, obj, skip: bool, options) -> bool:
    if name == '__init__':
        return False
    return skip


def setup(app: Sphinx) -> None:
    app.connect('autodoc-skip-member', skip)
