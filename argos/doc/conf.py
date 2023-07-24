# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'pyArgos'
copyright = '2019, Yehuda Arav, Eyal Fattal'
author = 'Eden Nitzan, Yehuda Arav, Eyal Fattal, Hadas Saroussi, Benny Saroussi'

# The short X.Y version
version = '1.1'
# The full version, including alpha/beta/rc tags
release = '1.1.0'

# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
#			'sphinx.ext.autosummary',
	      'nbsphinx',
	      'numpydoc',
		  'sphinx.ext.mathjax',
#		  'sphinx_gallery.gen_gallery',
		  'sphinx.ext.autosectionlabel'
	     ]

autosummary_generate = True

#sphinx_gallery_conf = {'examples_dirs': 'examples',   # path to your example scripts
#		       'gallery_dirs': 'auto_examples',  # path to where to save gallery generated output
#		      }

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['build', '_templates','auto_examples','auto_examples.old','examples','old','.ipynb_checkpoints']

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'pandas_sphinx_theme'
#html_theme = 'pydata_sphinx_theme'
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []
