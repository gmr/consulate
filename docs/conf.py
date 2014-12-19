#!/usr/bin/env python
import sys
sys.path.insert(0, '../')
from consulate import __version__
needs_sphinx = '1.0'
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']
templates_path = []
source_suffix = '.rst'
master_doc = 'index'
project = 'consulate'
copyright = '2014, Gavin M. Roy'
version = '.'.join(__version__.split('.')[0:1])
release = __version__
intersphinx_mapping = {'python': ('https://docs.python.org/2/', None)}
