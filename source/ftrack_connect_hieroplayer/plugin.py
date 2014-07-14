# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from __future__ import absolute_import

import json
import os
import base64
import logging

from PySide.QtNetwork import *
import hiero.ui
import hiero.core

from .session import Session as _Session
from .web_view import WebView as _WebView


class Plugin(object):
    '''ftrack connect HIEROPLAYER plugin.'''

    def __init__(self):
        '''Initialise plugin.'''
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        configuration = {
            'attachments': False,
            'versionsTab': True,
            'notesTab': True,
            'undockable': False
        }

        self.cfg = base64.b64encode(json.dumps(configuration))

        appSettings = hiero.core.ApplicationSettings()

        serverUrl = os.environ.get('FTRACK_SERVER', None)
        appServerUrl = appSettings.value('FTRACK_SERVER', defaultValue=None)

        entityId = None
        entityType = None

        # Check for environment variable specifying additional information to
        # use when loading.
        eventEnvironmentVariable = 'FTRACK_CONNECT_EVENT'

        eventData = os.environ.get(eventEnvironmentVariable)
        if eventData is not None:
            try:
                decodedEventData = json.loads(base64.b64decode(eventData))
            except (TypeError, ValueError):
                self.logger.exception(
                    'Failed to decode {0}: {1}'
                    .format(eventEnvironmentVariable, eventData)
                )
            else:
                context = decodedEventData.get('context', {})
                selection = context.get('selection', [])

                # At present only a single entity which should represent an
                # ftrack List is supported.
                if selection:
                    try:
                        entity = selection[0]
                        entityId = entity.get('entityId')
                        entityType = entity.get('entityType')

                    except (IndexError, AttributeError, KeyError):
                        self.logger.exception(
                            'Failed to extract selection information from: {0}'
                            .format(selection)
                        )
        else:
            self.logger.debug(
                'No event data retrieved. {0} not set.'
                .format(eventEnvironmentVariable)
            )

        if serverUrl is None and appServerUrl in [None, '']:
            url = self.getViewUrl('server_error')

        else:
            self.serverUrl = serverUrl or appServerUrl

            url = self.getViewUrl('freview_nav_v1')
            if entityId and entityType:
                url = '{0}&entityId={1}&entityType={2}'.format(
                    url, entityId, entityType
                )

        self.session = _Session(self)
        if not self.session.api:
            url = self.getViewUrl('api_error')

        cookieJar = QNetworkCookieJar()
        self.nam = QNetworkAccessManager()
        self.nam.setCookieJar(cookieJar)

        self.loginPanel = _WebView(
            name='ftrack Login', nam=self.nam, session=self.session
        )
        self.loginPanel.setUrl(url)
        hiero.ui.windowManager().addWindow(self.loginPanel)

        self.timeline = _WebView(
            name='ftrack Timeline', url='',
            nam=self.nam, session=self.session
        )
        hiero.ui.windowManager().addWindow(self.timeline)

        self.actionpanel = _WebView(
            name='ftrack Action',
            url='',
            nam=self.nam,
            session=self.session
        )
        self.actionpanel.setMinimumWidth(500)
        hiero.ui.windowManager().addWindow(self.actionpanel)

    def getViewUrl(self, name):
        '''Return url for view file with *name*.'''
        url = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'view', '{0}.html'.format(name)
        )

        if not os.path.exists(url):
            # Assume a url served by ftrack server.
            urlTemplate = (
                '{0}/widget?theme=tf&view={{0}}&itemId=freview'
                '&controller=widget&widgetCfg={1}'
                .format(self.serverUrl, self.cfg)
            )
            url = urlTemplate.format(name)

        return url

