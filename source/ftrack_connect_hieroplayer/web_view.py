# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from PySide import QtGui, QtCore, QtWebKit


class WebView(QtGui.QWidget):
    '''Display a web view.'''

    def __init__(self, name='', url='', nam=None, plugin=None, parent=None):
        super(WebView, self).__init__(parent=parent)

        self.setObjectName(name.lower().replace(' ', '.'))
        self.setWindowTitle(name)

        self.plugin = plugin

        self.webView = QtWebKit.QWebView()
        self.webView.urlChanged.connect(self.changedLocation)
        self.webView.page().setNetworkAccessManager(nam)

        self.frame = self.webView.page().mainFrame()

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
        QtGui.QShortcut(
            QtGui.QKeySequence('F7'), self,
            self.handleShowInspector
        )

        self.setUrl(url)

    def handleShowInspector(self):
        self.inspector.setShown(self.inspector.isHidden())

    def changedLocation(self):
        # Inject into page the plugin instance as bridge.
        self.frame.addToJavaScriptWindowObject('hierosession', self.plugin)

    def setUrl(self, url):
        '''Load *url*.'''
        self.webView.load(QtCore.QUrl(url))

    def url(self):
        '''Return currently loaded *url*.'''
        return self.webView.url().toString()
