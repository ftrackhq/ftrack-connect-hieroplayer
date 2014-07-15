# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore, QtWebKit


class WebView(QtGui.QWidget):
    '''Display a web view.'''

    def __init__(self, name, url='', plugin=None, parent=None):
        super(WebView, self).__init__(parent=parent)

        self.setObjectName(name.lower().replace(' ', '.'))
        self.setWindowTitle(name)

        self.plugin = plugin

        self.webView = QtWebKit.QWebView()
        self.webView.urlChanged.connect(self.changedLocation)

        # Use plugin network access manager if available.
        if self.plugin:
            self.webView.page().setNetworkAccessManager(
                self.plugin.networkAccessManager
            )

        self.frame = self.webView.page().mainFrame()

        # Enable developer tools for debugging loaded page.
        self.webView.settings().setAttribute(
            QtWebKit.QWebSettings.WebAttribute.DeveloperExtrasEnabled, True
        )
        self.inspector = QtWebKit.QWebInspector(self)
        self.inspector.setPage(self.webView.page())
        self.inspector.hide()

        self.splitter = QtGui.QSplitter(self)
        self.splitter.addWidget(self.webView)
        self.splitter.addWidget(self.inspector)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.splitter)

        # Load the passed url.
        self.setUrl(url)

    def changedLocation(self):
        '''Handle location changed event.'''
        # Inject the current plugin into the page so that it can be called
        # from JavaScript.
        self.frame.addToJavaScriptWindowObject('hierosession', self.plugin)

    def setUrl(self, url):
        '''Load *url*.'''
        self.webView.load(QtCore.QUrl(url))

    def url(self):
        '''Return currently loaded *url*.'''
        return self.webView.url().toString()
