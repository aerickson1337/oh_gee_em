"""Sphinx configuration."""
project = "Oh_Gee_Em"
author = "Andrew Erickson"
copyright = "2023, Andrew Erickson"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
