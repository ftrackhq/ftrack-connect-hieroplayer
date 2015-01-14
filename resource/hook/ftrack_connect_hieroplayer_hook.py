# :coding: utf-8
# :copyright: Copyright (c) 2015 ftrack

import getpass
import logging
import sys
import pprint
import os

import ftrack
import ftrack_connect.application


ACTION_IDENTIFIER = 'ftrack-connect-launch-hieroplayer_with_review'

FTRACK_CONNECT_HIEROPLAYER_PATH = os.environ.get(
    'FTRACK_CONNECT_HIEROPLAYER_PATH',
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', 'hieroplayer'
        )
    )
)


class DiscoverApplicationsHook(object):
    '''Default action.discover hook.'''

    identifier = ACTION_IDENTIFIER

    def __init__(self, applicationStore):
        '''Instantiate hook with *applicationStore*.

        *applicationStore* should be an instance of
        :class:`ftrack_connect.application.ApplicationStore`

        '''
        super(DiscoverApplicationsHook, self).__init__()
        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )
        self.applicationStore = applicationStore

    def __call__(self, event):
        '''Handle *event*.'''

        items = []
        applications = self.applicationStore.applications
        applications = sorted(
            applications, key=lambda application: application['label']
        )

        for application in applications:
            applicationIdentifier = application['identifier']
            label = application['label']
            items.append({
                'actionIdentifier': self.identifier,
                'label': label,
                'icon': application.get('icon', 'default'),
                'actionData': {
                    'applicationIdentifier': applicationIdentifier
                }
            })

            if applicationIdentifier.startswith('premiere_pro_cc'):
                items.append({
                    'actionIdentifier': self.identifier,
                    'label': '{label} with latest version'.format(
                        label=label
                    ),
                    'icon': application.get('icon', 'default'),
                    'actionData': {
                        'launchWithLatest': True,
                        'applicationIdentifier': applicationIdentifier
                    }
                })

        return {
            'items': items
        }


class LaunchApplicationHook(object):

    def __init__(self, launcher):
        '''Initialise hook with *launcher*.

        *launcher* should be an instance of
        :class:`ftrack_connect.application.ApplicationLauncher`.

        '''
        super(LaunchApplicationHook, self).__init__()
        self.logger = logging.getLogger(
            'ftrack.hook.' + self.__class__.__name__
        )
        self.launcher = launcher

    def __call__(self, event):
        '''Handle *event*.

        event['data'] should contain:

            context - Context of request to help guide how to launch the
                      application.
            actionData - Is passed and should contain the applicationIdentifier
                         and other values that can be used to provide
                         additional information about how the application
                         should be launched.
        '''
        # Prevent further processing by other listeners.
        # TODO: Only do this when actually have managed to launch a relevant
        # application.
        event.stop()

        applicationIdentifier = (
            event['data']['actionData']['applicationIdentifier']
        )

        context = event['data'].copy()

        return self.launcher.launch(
            applicationIdentifier, context
        )


class ApplicationLauncher(ftrack_connect.application.ApplicationLauncher):
    '''Launch nuke studio.'''

    def _getApplicationEnvironment(self, application, context):
        '''Modify and return environment with legacy plugins added.'''
        environment = super(
            ApplicationLauncher, self
        )._getApplicationEnvironment(
            application, context
        )

        applicationIdentifier = application['identifier']

        # Load Nuke specific environment such as legacy plugins.
        if applicationIdentifier.startswith('hieroplayer_with_review'):
            environment['HIERO_PLUGIN_PATH'] = os.path.join(
                FTRACK_CONNECT_HIEROPLAYER_PATH
            )

        return environment


class ApplicationStore(ftrack_connect.application.ApplicationStore):

    def _discoverApplications(self):
        '''Return a list of applications that can be launched from this host.

        An application should be of the form:

            dict(
                'identifier': 'name_version',
                'label': 'Name version',
                'path': 'Absolute path to the file',
                'version': 'Version of the application',
                'icon': 'URL or name of predefined icon'
            )

        '''
        applications = []

        if sys.platform == 'darwin':
            prefix = ['/', 'Applications']

            applications.extend(self._searchFilesystem(
                expression=prefix + ['HieroPlayer.*', 'HieroPlayer\d[\w.]+.app'],
                label='Review with HieroPlayer {version}',
                applicationIdentifier='hieroplayer_with_review_{version}',
                icon='hieroplayer'
            ))

        elif sys.platform == 'win32':
            prefix = ['C:\\', 'Program Files.*']

            applications.extend(self._searchFilesystem(
                expression=prefix + ['HieroPlayer.*', 'HieroPlayer\d.+.exe'],
                label='Review with HieroPlayer {version}',
                applicationIdentifier='hieroplayer_with_review_{version}',
                icon='hieroplayer'
            ))

        self.logger.debug(
            'Discovered applications:\n{0}'.format(
                pprint.pformat(applications)
            )
        )

        return applications


def register(registry, **kw):
    '''Register hooks for legacy plugins.'''
    applicationStore = ApplicationStore()

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.action.discover and source.user.username={0}'.format(
            getpass.getuser()
        ),
        DiscoverApplicationsHook(applicationStore)
    )

    ftrack.EVENT_HUB.subscribe(
        'topic=ftrack.action.launch and source.user.username={0} '
        'and data.actionIdentifier={1}'.format(
            getpass.getuser(), ACTION_IDENTIFIER
        ),
        LaunchApplicationHook(
            ApplicationLauncher(applicationStore)
        )
    )
