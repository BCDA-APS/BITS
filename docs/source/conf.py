"""Configuration file for the Sphinx documentation builder."""

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import apsbits

project = "APSBITS"
copyright = "2023-2025, APS BCDA"
author = "APS BCDA"
version = apsbits.__version__
release = version.split("+")[0]
if "+" in version:
    release += "..."

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = """
    IPython.sphinxext.ipython_console_highlighting
    IPython.sphinxext.ipython_directive
    myst_parser
    nbsphinx
    sphinx.ext.autodoc
    sphinx.ext.autosummary
    sphinx.ext.coverage
    sphinx.ext.githubpages
    sphinx.ext.inheritance_diagram
    sphinx.ext.mathjax
    sphinx.ext.todo
    sphinx.ext.viewcode
    sphinx.ext.graphviz
    sphinx_design
    sphinx.ext.intersphinx
    sphinx.ext.napoleon
    sphinx.ext.todo
    sphinx.ext.ifconfig
    sphinx.ext.extlinks
""".split()
myst_enable_extensions = ["colon_fence"]

templates_path = ['_templates']
source_suffix = ".rst .md".split()
exclude_patterns = ["**.ipynb_checkpoints", "deprecated/**"]

today_fmt = "%Y-%m-%d %H:%M"

# Ignore errors in notebooks while documenting them
nbsphinx_allow_errors = True

# autodoc
autodoc_default_options = {
    'members': True,
    'private-members': True,
    'member-order': True,
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    "show-inheritance": True,
}



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = "pydata_sphinx_theme"
html_title = project

# -- autodoc_mock packages -------------------------------------------------

autodoc_mock_imports = """
    apstools
    bluesky
    databroker
    dm
    epics
    guarneri
    h5py
    intake
    matplotlib
    numpy
    ophyd
    ophydregistry
    pandas
    pyRestTable
    pysumreg
    spec2nexus
""".split()
