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

Once you have a copy of the repository, copy the *Python* folder from the
*resource* folder into the plugin folder for :term:`HIEROPLAYER`.
To find out where the plugin folder is on your system consult the
`The Foundry developer documentation <http://docs.thefoundry.co.uk/products/hiero/developers/1.8/hieropythondevguide/setup.html>`_.

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