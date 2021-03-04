
scipion-ed
==========

**scipion-ed** is the base plugin defining the Domain for Electron Diffraction image processing.


Installation
------------

For using scipion-ed, we need to have a working Python 3 environment (e.g via virtualenv or conda).
After that, we might easily install by:

.. code-block:: bash

    pip install scipion-ed scipion-ed-dials


Development
-----------

For development, we probably want to download the source code and install from there. In that way
changes can be made and we can test it quickly. We also need a working Python 3 environment and we
recommend to create a development folder to download the source code.

.. code-block:: bash

    # Create a folder for the installation
    mkdir scipion-ed-dev
    cd scipion-ed-dev

    # Then we can install scipion-ed by:
    git clone git@github.com:scipion-ed/scipion-ed.git
    python -m pip install -e scipion-ed  # Install in the environment as development
    
    # And also install the plugins
    git clone git@github.com:scipion-ed/scipion-ed-dials.git
    python -m pip install -e scipion-ed-dials  # Install in the environment as development
    

Publishing the package to PyPI
..............................

In order to make scipion-ed available to install with `pip install scipion-ed`,
we need to:

.. code-block:: bash

    python install twine restructuredtext-lint
    cd scipion-ed

    # It might be a good idea to check the README.rst before uploading:
    rst-lint README.rst

    python setup.py sdist
    twine upload dist/scipion-ed-3.0.1rc1.tar.gz

Running tests (TO BE UPDATED)
.............................

.. code-block:: bash

    cd scipion-ed
    cd pwed/tests
    python -m unittest discover

    # To visualize the test project you need to specify SCIPION_DOMAIN and SCIPION_VERSION
    export SCIPION_DOMAIN=scipion-ed/pwed
    export SCIPION_VERSION=3.0.0

    python scipion-pyworkflow/pyworkflow/apps/pw_project.py TestEdBaseProtocols



Python 3 environments (TO BE UPDATED)
-------------------------------------

For development, we probably want to download the source code and install from there. In that way
changes can be made and we can test it quickly.

We also need a working Python 3 environment and we recommend to create a development folder to download the source code.

.. code-block:: bash

    # Create a clean virtual environment
    python -m virtualenv --python=python3 env
    source env/bin/activate


Troubleshooting
---------------

If you get "error: command 'x86_64-linux-gnu-gcc' failed with exit status 1" you may need to install python3-dev:
sudo apt install python3-dev -y


Tkinter with Python3
....................


Tkinter with Conda
..................

