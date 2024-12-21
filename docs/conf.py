import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = "SGUI"
author = "Elis Eriksson"
html_theme = "sphinx_rtd_theme"
extensions = ['myst_parser','sphinx.ext.autodoc']
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}
