# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import functools
import sys
import os

import ftrack_api




def on_discover_rv_integration(session, event):
    cwd = os.path.dirname(__file__)
    sources = os.path.abspath(os.path.join(cwd, '..', 'dependencies'))
    sys.path.append(sources)

    ftrack_connect_hiero_player_resource_path = os.path.abspath(os.path.join(
        cwd, '..',  'resource')
    )

    from ftrack_connect_hieroplayer import __version__ as integration_version

    hieroplayer_path = os.environ.get(
        'FTRACK_CONNECT_HIEROPLAYER_PATH',
        ftrack_connect_hiero_player_resource_path
    )

    data = {
        'integration': {
            'name': 'ftrack-connect-hieroplayer',
            'version': integration_version,
            'env': {
                'HIERO_PLUGIN_PATH.append': hieroplayer_path,
                'PYTHONPATH.prepend': sources,
            }
        }
    }
    return data


def register(session):
    '''Subscribe to application launch events on *registry*.'''
    if not isinstance(session, ftrack_api.session.Session):
        return

    handle_event = functools.partial(
        on_discover_rv_integration,
        session
    )
    session.event_hub.subscribe(
        'topic=ftrack.connect.application.launch'
        ' and data.application.identifier=nuke*'
        ' and data.application.version >= 13',
        handle_event,
        priority=20
    )

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.discover'
        ' and data.application.identifier=nuke*'
        ' and data.application.version >= 13',
        handle_event,
        priority=20
    )
