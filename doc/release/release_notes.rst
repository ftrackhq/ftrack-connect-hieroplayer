..
    :copyright: Copyright (c) 2015 ftrack

.. _release/release_notes:

*************
Release notes
*************

.. release:: Upcoming

    .. change:: fix
        :tags: API

        Nuke 11 not supported.

    .. change:: changed
        :tags: API

        The integration now uses the new API to resolve file paths and can be
        used to review components only accessible from the new API. Legacy
        locations are still supported through the location compatibility plugin
        in ftrack Connect.

.. release:: 0.1.5
    :date: 2016-06-07

    .. change:: fix
        :tags: Hook

        Hiero Player doesn't get discovered in versions >9.0.

    .. change:: fix
        :tags: API

        Hiero Player is not lading correctly in versions >9.0.

.. release:: 0.1.4
    :date: 2015-09-09

    .. change:: fix
        :tags: Hook

        Added support for `variant` instead of version number in label.

.. release:: 0.1.3
    :date: 2015-04-17

    .. change:: fix
        :tags: Hook, Centos

        Added support for launching plugin on Centos.

.. release:: 0.1.2
    :date: 2015-01-30

    .. change:: fix

        Added alternative installation directory to search path when detecting
        installed HieroPlayer versions.

.. release:: 0.1.1
    :date: 2015-01-23

    .. change:: changed

        Required `ftrack server <http://rtd.ftrack.com/docs/ftrack/en/3.0.5/release/release_notes.html>`_ version is 3.0.5 or higher.

    .. change:: new

        Automatically sign in to ftrack when launching :term:`HIEROPLAYER`.

.. release:: 0.1.0
    :date: 2015-01-16

    .. change:: new

        Initial release of the ftrack connect plugin for :term:`HIEROPLAYER`.

