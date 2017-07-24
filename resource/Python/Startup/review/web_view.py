# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from __future__ import absolute_import

import logging

from QtExt import QtGui, QtCore, QtNetwork

try:
    from QtExt import QtWebKitWidgets as QtWebWidgets
    HAS_WEBKIT=True
except ImportError:
    from QtExt import QtWebEngineWidgets as QtWebWidgets
    HAS_WEBKIT=False
    # Create some aliases for old QtWebKit classes.
    QtWebWidgets.QWebPage = QtWebWidgets.QWebEnginePage
    QtWebWidgets.QWebView = QtWebWidgets.QWebEngineView


class WebView(QtGui.QWidget):
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

        self.webView = QtWebWidgets.QWebView()
        self.webView.urlChanged.connect(self.changedLocation)

        # Use plugin network access manager if available.
        if self.plugin and HAS_WEBKIT:
            self.webView.page().setNetworkAccessManager(
                self.plugin.networkAccessManager
            )

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.webView)

        # Load the passed url.
        self.setUrl(url)

    def changedLocation(self):
        '''Handle location changed event.'''
        # Inject the current plugin into the page so that it can be called
        # from JavaScript.
        if HAS_WEBKIT:
            self.webView.page().mainFrame().addToJavaScriptWindowObject('hierosession', self.plugin)
        else:
            # TODO: port me...
            pass

    def setUrl(self, url):
        '''Load *url*.'''
        self.logger.debug('Changing url to {0}.'.format(url))
        self.webView.load(QtCore.QUrl(url))

    def url(self):
        '''Return currently loaded *url*.'''
        return self.webView.url().toString()

    def evaluateJavascript(self, javascript):
        if HAS_WEBKIT:
            self.webView.page().mainFrame().evaluateJavaScript(javascript)
        else:
            self.webView.page().evaluateJavaScript(javascript)
