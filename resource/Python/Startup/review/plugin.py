# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from __future__ import absolute_import

import json
import os
import base64
import logging
import uuid

from PySide.QtNetwork import *
from PySide.QtCore import QObject, Slot
import hiero.ui
import hiero.core

from .web_view import WebView as _WebView


class Plugin(QObject):
    '''ftrack connect HIEROPLAYER plugin.'''

    def __init__(self):
        '''Initialise plugin.'''
        super(Plugin, self).__init__()

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self._loaded = False
        self._api = None

        self._project = None
        self._previousSequence = None
        self.inCompareMode = False
        self._componentPathCache = {}

        appSettings = hiero.core.ApplicationSettings()

        serverUrl = os.environ.get('FTRACK_SERVER', None)
        appServerUrl = appSettings.value('FTRACK_SERVER', defaultValue=None)

        self.entityId = None
        self.entityType = None

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
                data = decodedEventData.get('data', {})
                selection = data.get('selection', [])

                # At present only a single entity which should represent an
                # ftrack List is supported.
                if selection:
                    try:
                        entity = selection[0]
                        self.entityId = entity.get('entityId')
                        self.entityType = entity.get('entityType')

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

        if not self.api:
            url = self.getViewUrl('api_error')

        # Create cookie jar to store authentication credentials in for session.
        cookieJar = QNetworkCookieJar()
        self.networkAccessManager = QNetworkAccessManager()
        self.networkAccessManager.setCookieJar(cookieJar)

        # Construct ftrack panels.
        self.loginPanel = _WebView('ftrack Login', url=url, plugin=self)
        hiero.ui.windowManager().addWindow(self.loginPanel)

        self.timelinePanel = _WebView('ftrack Timeline', plugin=self)
        hiero.ui.windowManager().addWindow(self.timelinePanel)

        self.actionPanel = _WebView('ftrack Action', plugin=self)
        self.actionPanel.setMinimumWidth(500)
        hiero.ui.windowManager().addWindow(self.actionPanel)

    def getViewUrl(self, name):
        '''Return url for view file with *name*.'''
        url = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'view', '{0}.html'.format(name)
        )

        if not os.path.exists(url):
            # Assume a url served by ftrack server.
            configuration = base64.b64encode(
                json.dumps({
                    'attachments': False,
                    'versionsTab': True,
                    'notesTab': True,
                    'undockable': False
                })
            )

            urlTemplate = (
                '{0}/widget?theme=tf&view={{0}}&itemId=freview'
                '&controller=widget&widgetCfg={1}'
                .format(self.serverUrl, configuration)
            )
            url = urlTemplate.format(name)

            if self.entityId and self.entityType:
                url = '{0}&entityId={1}&entityType={2}'.format(
                    url, self.entityId, self.entityType
                )

        return url

    @property
    def api(self):
        '''Return ftrack API.'''
        if not self._api:
            try:
                import ftrack as ftrack
                ftrack.setup(actions=False)
            except ImportError:
                self.logger.warning(
                    'Could not load ftrack Python API. Please check it is '
                    'available on the PYTHONPATH.'
                )
                return False
            else:
                self._api = ftrack
                self.logger.debug('Loaded ftrack Python API successfully.')

        return self._api

    def _markBrokenClip(self, versionId):
        '''Mark clip representing version with *versionId* as unplayable.'''
        if not self._loaded:
            return

        self.timelinePanel.frame.evaluateJavaScript(
            'FT.Mediator.breakItem("{0}")'.format(versionId)
        )
        self.actionPanel.frame.evaluateJavaScript(
            'FT.Mediator.breakItem("{0}")'.format(versionId)
        )

    def _getFilePath(self, componentId):
        '''Return a single filesystem path for *componentId*.'''
        path = self._componentPathCache.get(componentId, None)

        if path is None:
            location = self.api.pickLocation(componentId)

            if not location:
                raise IOError(
                    'Could not retrieve file path for component {0} as no '
                    'location for component accessible.'.format(componentId)
                )

            component = location.getComponent(componentId)
            path = component.getFilesystemPath()
            self._componentPathCache[componentId] = path

        return path

    @Slot()
    def loadActionPanel(self):
        '''Load action panel.

        Called from Javascript once login has completed.

        .. note::

            This method should ideally be called something less specific such as
            onLoad.

        '''
        self.onLoad()

    @Slot()
    def onLoad(self):
        '''Load panel contents if not already loaded.'''
        if self._loaded:
            return

        self._loaded = True

        # Display authenticated page.
        # TODO: Find a way to change focus to Viewer tab / close this tab.
        self.loginPanel.setUrl(
            self.getViewUrl('authenticated')
        )

        # Load other views.
        self.timelinePanel.setUrl(
            self.getViewUrl('freview_nav_v1')
        )
        self.actionPanel.setUrl(
            self.getViewUrl('freview_action_v1')
        )

        # Ensure action panel updated when playback clip changed.
        def updateActionPanel(event):
            '''Update action panel on *event*.'''
            if not self.inCompareMode:
                player = event.sender
                sequence = player.sequence()

                if sequence is None:
                    # Can happen when closing HIEROPLAYER for example.
                    return

                time = player.time()

                trackItem = sequence.trackItemAt(time)
                if trackItem:
                    self.sendEvent(
                        'changedVersion',
                        base64.b64encode(
                            json.dumps({
                                'type': 'changedVersion',
                                'version': trackItem.name()
                            })
                        )
                    )

        hiero.core.events.registerInterest(
            'kPlaybackClipChanged', updateActionPanel
        )

    @Slot(str, str)
    def sendEvent(self, eventName, eventData):
        '''Send event with *eventName* and *eventData*.'''
        if not self._loaded:
            return

        self.timelinePanel.frame.evaluateJavaScript(
            'FT.updateFtrack("{0}")'.format(eventData)
        )
        self.actionPanel.frame.evaluateJavaScript(
            'FT.updateFtrack("{0}")'.format(eventData)
        )

    @Slot(int)
    def jumpToIndex(self, index):
        '''Set viewer position to item at *index*.'''
        try:
            view = hiero.ui.currentViewer()
            player = view.player()
            sequence = player.sequence()

            startPos = sequence.videoTrack(0).items()[index].handleInTime()
            view.setTime(startPos)

        except Exception:
            self.logger.exception('Error loading index.')

    @Slot(str, str, str)
    def compareMode(self, componentIdA, componentIdB, mode='tile'):
        '''Replace current sequence with comparison of two components.

        *componentIdA* and *componentIdB* should be the ids of the components
        to compare.

        *mode* determines the comparison view (e.g. tile, wipe, load).

        '''
        if mode == 'load' and componentIdA is None:
            return

        elif mode != 'load' and (not componentIdA or not componentIdB):
            return

        filesystemPathA = self._getFilePath(componentIdA)
        try:
            filesystemPathB = self._getFilePath(componentIdB)
        except Exception:
            if mode != 'load':
                raise

        clipsBin = self._project.clipsBin()

        sourceA = hiero.core.MediaSource(filesystemPathA)
        clipA = hiero.core.Clip(sourceA)
        clipsBin.addItem(hiero.core.BinItem(clipA))

        if mode != 'load':
            sourceB = hiero.core.MediaSource(filesystemPathB)
            clipB = hiero.core.Clip(sourceB)
            clipsBin.addItem(hiero.core.BinItem(clipB))

        view = hiero.ui.currentViewer()
        view.wipeTool().setActive(False)

        if mode in ('wipe', 'load'):
            view.setLayoutMode(view.LayoutMode.eLayoutStack)

            if mode == 'wipe':
                view.wipeTool().setActive(True)

        else:
            view.setLayoutMode(view.LayoutMode.eLayoutHorizontal)

        if self._previousSequence is None:
            self._previousSequence = view.player(0).sequence()

        self.inCompareMode = True

        view.player(0).setSequence(clipA)

        if mode != 'load':
            view.player(1).setSequence(clipB)
        else:
            view.player(1).setSequence(clipA)

        view.setTime(0)

    @Slot(int)
    def compareOff(self, idx=-1):
        '''Cancel compare view and return to previous loaded sequence.'''
        self.inCompareMode = False
        view = hiero.ui.currentViewer()

        view.setLayoutMode(view.LayoutMode.eLayoutStack)
        view.wipeTool().setActive(False)

        sequence = self._previousSequence
        self._previousSequence = None
        view.player(0).setSequence(sequence)
        view.player(1).setSequence(sequence)

        if idx != -1:
            self.jumpToIndex(idx)

    @Slot(str)
    def loadSequence(self, versions):
        '''Load list of *versions* into new unique sequence on timeline.'''
        try:
            versions = json.loads(versions)
        except Exception:
            return

        self._previousSequence = None

        def createTrackItem(
                track, trackItemName, sourceClip, lastTrackItem=None
        ):
            '''Helper method to create track items from clips.'''
            trackItem = track.createTrackItem(trackItemName)
            trackItem.setName(trackItemName)
            trackItem.setSource(sourceClip)

            if lastTrackItem:
                trackItem.setTimelineIn(
                    lastTrackItem.timelineOut() + 1
                )

                trackItem.setTimelineOut(
                    lastTrackItem.timelineOut() + sourceClip.duration()
                )

            else:
                trackItem.setTimelineIn(0)
                trackItem.setTimelineOut(
                    trackItem.sourceDuration() - 1
                )

            track.addItem(trackItem)
            return trackItem

        if not self._project:
            project = hiero.core.projects()[-1]
            if not project:
                project = hiero.core.newProject()

            self._project = project

        clipsBin = self._project.clipsBin()

        sequence = hiero.core.Sequence(str(uuid.uuid1()))
        clipsBin.addItem(hiero.core.BinItem(sequence))

        track = hiero.core.VideoTrack('VideoTrack')
        trackItem = None

        for version in versions:
            try:
                # Get filesystem path for a component from the most suitable
                # location.
                version['source'] = self._getFilePath(
                    version.get('componentId')
                )
                source = hiero.core.MediaSource(version.get('source'))
                clip = hiero.core.Clip(source)

                trackItem = createTrackItem(
                    track, version.get('versionId'),
                    clip, lastTrackItem=trackItem
                )

            except Exception:
                self.logger.exception(
                    'Something is wrong, marking version as broken'
                )
                self._markBrokenClip(version.get('versionId'))

        sequence.addTrack(track)

        view = hiero.ui.currentViewer()
        player = view.player(0)
        player.setSequence(sequence)

        view.stop()

    @Slot(str, str)
    def validateComponentLocation(self, componentId, versionId):
        '''Validate if the *componentId* is accessible in a local location.

        Mark clip as broken if not accessible.

        '''
        try:
            self._getFilePath(componentId)
        except IOError:
            self._markBrokenClip(versionId)