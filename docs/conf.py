import sys
from pathlib import Path
sys.path.insert(0, str(Path('..', 'src').resolve()))
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

project = "SGUI"
author = "Elis Eriksson"
html_theme = "sphinx_rtd_theme"
extensions = ['myst_parser','sphinx.ext.autodoc','sphinx.ext.napoleon']
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}
