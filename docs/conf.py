import sys
from pathlib import Path
sys.path.insert(0, str(Path('..', 'src').resolve()))

project = "SGUI"
author = "Elis Eriksson"
html_theme = "sphinx_rtd_theme"
extensions = ['myst_parser','sphinx.ext.autodoc','sphinx.ext.napoleon']
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}
