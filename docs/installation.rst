.. _installation:

Installation
===========

This page provides instructions for installing the celparser package.

Requirements
-----------

- Python 3.8 or higher

Installing from PyPI
-------------------

The recommended way to install celparser is from PyPI using pip:

.. code-block:: bash

    pip install celparser

Using uv
--------

You can also install celparser using uv:

.. code-block:: bash

    uv pip install celparser

Installing from Source
--------------------

To install the latest development version from source:

1. Clone the repository:

   .. code-block:: bash

       git clone https://github.com/mrb101/celparser.git
       cd celparser

2. Install the package:

   .. code-block:: bash

       pip install .

Development Installation
----------------------

If you want to contribute to celparser, you can install it in development mode:

.. code-block:: bash

    git clone https://github.com/mrb101/celparser.git
    cd celparser
    pip install -e .

This will install the package in "editable" mode, meaning changes to the source code will be immediately available without reinstalling.

For development, you may want to install additional dependencies:

.. code-block:: bash

    pip install -e ".[dev]"

Or using uv:

.. code-block:: bash

    uv pip install -e ".[dev]"