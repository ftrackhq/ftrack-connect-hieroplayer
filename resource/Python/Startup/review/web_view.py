# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack
# https://doc.qt.io/qt-5/qtwebenginewidgets-qtwebkitportingguide.html

from __future__ import absolute_import

import logging

# qt.py seems to be having issue importing QtWebEngineWidgets
from PySide2 import QtGui, QtWidgets, QtCore, QtWebEngineWidgets, QtWebChannel


class WebView(QtWidgets.QWidget):
    '''Display a web view.'''

    def __init__(self, name, url=None, plugin=None, parent=None):
        '''Initialise web view with *name* and *url*.

        *name* will be used as the title of the widget and also will be
        converted to a lowercase dotted name which the panel can be referenced
        with. For example, "My Panel" -> "my.panel".

        *url* should be the initial url to display.

        *plugin* should be an instance of
        *:py:class:`ftrack_connect_hieroplayer.plugin.Plugin` which will be
        *injected into the JavaScript window object of any loaded page.

        *parent* is the optional parent of this widget.

        '''
        super(WebView, self).__init__(parent=parent)

        self.logger = logging.getLogger(
            __name__ + '.' + self.__class__.__name__
        )

        self.setObjectName(name.lower().replace(' ', '.'))
        self.setWindowTitle(name)
        self.plugin = plugin

        self.webView = QtWebEngineWidgets.QWebEngineView()
        self.webView.urlChanged.connect(self.changedLocation)

        # # Use plugin network access manager if available.
        # if self.plugin:
        #     self.webView.setNetworkAccessManager(
        #         self.plugin.networkAccessManager
        #     )

        self.page = self.webView.page()

        # Enable developer tools for debugging loaded page.
        # self.webView.settings().setAttribute(
        #     QtWebEngineWidgets.QWebSettings.WebAttribute.DeveloperExtrasEnabled, True
        # )
        # self.inspector = QtWebEngineWidgets.QWebInspector(self)
        # self.inspector.setPage(self.webView.page())
        # self.inspector.hide()

        self.splitter = QtWidgets.QSplitter(self)
        self.splitter.addWidget(self.webView)
        # self.splitter.addWidget(self.inspector)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.splitter)

        # Load the passed url.
        self.setUrl(url)

    def changedLocation(self):
        '''Handle location changed event.'''
        # Inject the current plugin into the page so that it can be called
        # from JavaScript.
        channel = QtWebChannel.QWebChannel(self)
        self.page.setWebChannel(channel)
        channel.registerObject('hierosession', self.plugin)

    def setUrl(self, url):
        '''Load *url*.'''
        self.logger.debug('Changing url to {0}.'.format(url))
        self.webView.load(QtCore.QUrl(url))

    def url(self):
        '''Return currently loaded *url*.'''
        return self.webView.url().toString()
