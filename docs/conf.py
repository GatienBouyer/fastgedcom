# Configuration file for the Sphinx documentation builder.

project = 'FastGedcom'
copyright = '2026, GatienBouyer'
author = 'GatienBouyer'
release = '1.2.0'
version = '1.2.0'

html_theme = 'sphinx_rtd_theme'

extensions = [
    'sphinx.ext.viewcode',
    'autoapi.extension',
]

autoapi_dirs = ['../fastgedcom']
