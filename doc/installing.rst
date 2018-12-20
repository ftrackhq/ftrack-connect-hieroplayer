..
    :copyright: Copyright (c) 2015 ftrack

.. _installing:

************
Installation
************

Using ftrack connect
--------------------

The ftrack connect hieroplayer review plugin is included in the built version
of :term:`ftrack connect package` to use it `download and run ftrack connect. <https://www.ftrack.com/downloads>`_

Running from source
-------------------

You can clone the public repository::

    $ git clone git@bitbucket.org:ftrack/ftrack-connect-hieroplayer.git

Or download the
`zipball <https://bitbucket.org/ftrack/ftrack-connect-hieroplayer/get/master.zip>`_

Then you can build and install the package against your current Python

.. code::
    python setup.py build_plugin

The result plugin will then be available under the build folder.
Copy or symlink the result plugin folder in your FTRACK_CONNECT_PLUGIN_PATH.    

Building documentation from source
----------------------------------

To build the documentation from source::

    python setup.py build_sphinx

Then view in your browser::

    file:///path/to/ftrack-connect-hieroplayer/build/doc/html/index.html

Running tests against the source
--------------------------------

With a copy of the source it is also possible to run the unit tests::

    python setup.py test

Dependencies
============

* ftrack Python API (Download from your ftrack server and make available on
  ``PYTHONPATH``)
* `HIEROPLAYER or Hiero <http://www.thefoundry.co.uk/products/hiero-product-family>`_

Additional For building
-----------------------

* `Sphinx <http://sphinx-doc.org/>`_ >= 1.2.2, < 2
* `sphinx_rtd_theme <https://github.com/snide/sphinx_rtd_theme>`_ >= 0.1.6, < 1

Additional For testing
----------------------

* `Pytest <http://pytest.org>`_  >= 2.3.5