# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "My Unofficial Lab Guides"
copyright = "2023, Vince Tognaci"
author = "Vince Tognaci"
release = "main"
today_fmt = "%b %d, %Y @ %H:%M"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# import sphinx_rtd_theme

extensions = ["sphinx_rtd_theme", "sphinx_copybutton"]

templates_path = ["_templates"]
exclude_patterns = []

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_path = [
    "_themes",
]
html_logo = "_static/redhat.png"

html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
