# :coding: utf-8
# :copyright: Copyright (c) 2021 ftrack

import functools
import sys
import os
import logging

NAME = 'ftrack-connect-hieroplayer'

logger = logging.getLogger()


cwd = os.path.dirname(__file__)
sources = os.path.abspath(os.path.join(cwd, '..', 'dependencies'))
sys.path.append(sources)

import ftrack_api


def on_discover_hieroplayer_integration(session, event):

    from ftrack_connect_hieroplayer import __version__ as integration_version
    data = {
        'integration': {
            'name': 'ftrack-connect-hieroplayer',
            'version': integration_version
        }
    }

    return data

def on_launch_hieroplayer_integration(session, event):
    hieroplayer_base_data = on_discover_hieroplayer_integration(session, event)


    ftrack_connect_hiero_player_resource_path = os.path.abspath(os.path.join(
        cwd, '..',  'resource')
    )

    hieroplayer_path = os.environ.get(
        'FTRACK_CONNECT_HIEROPLAYER_PATH',
        ftrack_connect_hiero_player_resource_path
    )

    hieroplayer_base_data['integration']['env'] = {
        'HIERO_PLUGIN_PATH.append': hieroplayer_path,
        'PYTHONPATH.prepend': sources,
        'QTWEBENGINE_REMOTE_DEBUGGING.set': '9999'
    }

    return hieroplayer_base_data


def register(session):
    '''Subscribe to application launch events on *registry*.'''
    if not isinstance(session, ftrack_api.session.Session):
        return

    handle_discover_event = functools.partial(
        on_discover_hieroplayer_integration,
        session
    )
    session.event_hub.subscribe(
        'topic=ftrack.connect.application.discover'
        ' and data.application.identifier=hieroplayer_*'
        ' and data.application.version >= 13',
        handle_discover_event
    )

    handle_launch_event = functools.partial(
        on_launch_hieroplayer_integration,
        session
    )

    session.event_hub.subscribe(
        'topic=ftrack.connect.application.launch'
        ' and data.application.identifier=hieroplayer_*'
        ' and data.application.version >= 13',
        handle_launch_event
    )



