from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
import sys

class BrowserTab(QWebEngineView):
    def __init__(self, homepage, incognito=False):
        super().__init__()
        self.homepage = homepage
        self.incognito = incognito
        if incognito:
            profile = QWebEngineProfile()
            profile.setOffTheRecord(True)
            page = QWebEnginePage(profile, self)
            self.setPage(page)
        self.setUrl(QUrl(homepage))
        self.zoom_factor = 1.0

    def zoom_in(self):
        self.zoom_factor += 0.5
        self.setZoomFactor(self.zoom_factor)

    def zoom_out(self):
        self.zoom_factor = max(0.2, self.zoom_factor - 0.5)
        self.setZoomFactor(self.zoom_factor)

    def zoom_reset(self):
        self.zoom_factor = 1.0
        self.setZoomFactor(self.zoom_factor)

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self.parent = parent

        layout = QVBoxLayout()

        self.home_edit = QLineEdit(self.parent.homepage)
        home_label = QLabel("Homepage URL:")
        layout.addWidget(home_label)
        layout.addWidget(self.home_edit)

        self.text_size_slider = QSlider(Qt.Horizontal)
        self.text_size_slider.setMinimum(50)
        self.text_size_slider.setMaximum(200)
        self.text_size_slider.setValue(int(self.parent.current_zoom * 100))
        self.text_size_slider.setTickInterval(10)
        self.text_size_slider.setTickPosition(QSlider.TicksBelow)
        text_size_label = QLabel("Text Zoom (%):")
        layout.addWidget(text_size_label)
        layout.addWidget(self.text_size_slider)

        bookmarks_label = QLabel("Bookmarks (one URL per line):")
        self.bookmarks_edit = QTextEdit()
        self.bookmarks_edit.setPlainText("\n".join(self.parent.bookmarks))
        layout.addWidget(bookmarks_label)
        layout.addWidget(self.bookmarks_edit)

        buttons = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def save_settings(self):
        new_home = self.home_edit.text().strip()
        if new_home:
            if not new_home.startswith("http"):
                new_home = "http://" + new_home
            self.parent.homepage = new_home

        new_zoom = self.text_size_slider.value() / 100
        self.parent.current_zoom = new_zoom
        for i in range(self.parent.tabs.count()):
            tab = self.parent.tabs.widget(i)
            tab.setZoomFactor(new_zoom)
            tab.zoom_factor = new_zoom

        new_bookmarks = self.bookmarks_edit.toPlainText().strip().splitlines()
        self.parent.bookmarks = [b for b in new_bookmarks if b.strip()]
        self.parent.update_bookmarks_bar()

        self.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jacob's Browser")
        self.resize(1200, 800)

        self.homepage = "http://www.google.com"
        self.bookmarks = ["http://www.google.com"]
        self.current_zoom = 1.0

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_urlbar_and_title)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)

        self.navtb = QToolBar("Navigation")
        self.navtb.setIconSize(QSize(20, 20))
        self.navtb.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.navtb.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.navtb)
        self.navtb.setFixedHeight(40)

        self.back_btn = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        self.back_btn.triggered.connect(lambda: self.current_browser().back())
        self.navtb.addAction(self.back_btn)

        self.forward_btn = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        self.forward_btn.triggered.connect(lambda: self.current_browser().forward())
        self.navtb.addAction(self.forward_btn)

        self.reload_btn = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        self.reload_btn.triggered.connect(lambda: self.current_browser().reload())
        self.navtb.addAction(self.reload_btn)

        self.stop_btn = QAction(QIcon.fromTheme("process-stop"), "Stop", self)
        self.stop_btn.triggered.connect(lambda: self.current_browser().stop())
        self.navtb.addAction(self.stop_btn)

        self.home_btn = QAction(QIcon.fromTheme("go-home"), "Home", self)
        self.home_btn.triggered.connect(self.navigate_home)
        self.navtb.addAction(self.home_btn)

        self.navtb.addSeparator()

        self.settings_btn = QAction("⋮", self)
        self.settings_btn.triggered.connect(self.open_settings)
        self.navtb.addAction(self.settings_btn)

        central = QWidget()
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(2, 2, 2, 2)
        central_layout.setSpacing(2)

        central_layout.addWidget(self.tabs)
        central_layout.addWidget(self.urlbar)
        central_layout.addWidget(self.navtb)

        self.bookmarks_bar = QToolBar("Bookmarks")
        self.bookmarks_bar.setIconSize(QSize(16, 16))
        self.bookmarks_bar.setMovable(False)
        self.bookmarks_bar.setFixedHeight(30)
        self.update_bookmarks_bar()

        main_layout = QVBoxLayout()
        main_layout.addLayout(central_layout)
        main_layout.addWidget(self.bookmarks_bar)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.add_new_tab(QUrl(self.homepage), "New Tab")

        self.shortcut_bindings()

    def shortcut_bindings(self):
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+T"), self, self.add_new_tab)
        QShortcut(QKeySequence("Ctrl+N"), self, self.new_window)
        QShortcut(QKeySequence("Ctrl+Shift+N"), self, self.new_incognito_window)
        QShortcut(QKeySequence("Ctrl+R"), self, lambda: self.current_browser().reload())
        QShortcut(QKeySequence("Ctrl++"), self, lambda: self.current_browser().zoom_in())
        QShortcut(QKeySequence("Ctrl+-"), self, lambda: self.current_browser().zoom_out())
        QShortcut(QKeySequence("Ctrl+0"), self, lambda: self.current_browser().zoom_reset())
        QShortcut(QKeySequence("Ctrl+C"), self, lambda: self.current_browser().triggerPageAction(QWebEnginePage.Copy))
        QShortcut(QKeySequence("Ctrl+V"), self, lambda: self.current_browser().triggerPageAction(QWebEnginePage.Paste))

    def current_browser(self):
        return self.tabs.currentWidget()

    def add_new_tab(self, qurl=None, label="New Tab", incognito=False):
        if qurl is None:
            qurl = QUrl(self.homepage)
        browser = BrowserTab(self.homepage, incognito)
        if qurl is not None:
            browser.setUrl(qurl)

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda q, b=browser: self.update_urlbar(q, b))
        browser.loadFinished.connect(lambda _, i=i, b=browser: self.tabs.setTabText(i, b.page().title()))
        browser.titleChanged.connect(lambda title, i=i: self.tabs.setTabText(i, title))
        return browser

    def close_tab(self, i=None):
        if self.tabs.count() < 2:
            self.close()
            return
        if i is None:
            i = self.tabs.currentIndex()
        self.tabs.removeTab(i)

    def close_current_tab(self):
        self.close_tab(self.tabs.currentIndex())

    def update_urlbar(self, q, browser=None):
        if browser != self.current_browser():
            return
        text = q.toString()
        if text.startswith(self.homepage):
            text = text[len(self.homepage):]
        self.urlbar.setText(text)

    def update_urlbar_and_title(self, i):
        browser = self.tabs.widget(i)
        if browser:
            self.urlbar.setText(browser.url().toString())
            self.setWindowTitle(browser.page().title() + " - Jacob's Browser")

    def navigate_to_url(self):
        text = self.urlbar.text().strip()
        if not text:
            return
        if " " in text or "." not in text:
            url = QUrl("https://www.google.com/search?q=" + QUrl.toPercentEncoding(text).data().decode())
        else:
            if not text.startswith(("http://", "https://")):
                text = "http://" + text
            url = QUrl(text)
        self.current_browser().setUrl(url)

    def navigate_home(self):
        self.current_browser().setUrl(QUrl(self.homepage))

    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec_()

    def update_bookmarks_bar(self):
        self.bookmarks_bar.clear()
        for bm in self.bookmarks:
            action = QAction(bm, self)
            action.triggered.connect(lambda checked, url=bm: self.current_browser().setUrl(QUrl(url)))
            self.bookmarks_bar.addAction(action)

    def new_window(self):
        self.new_win = MainWindow()
        self.new_win.show()

    def new_incognito_window(self):
        self.incog_win = MainWindow()
        self.incog_win.show()
        self.incog_win.tabs.clear()
        self.incog_win.add_new_tab(QUrl(self.homepage), "Incognito", incognito=True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Jacob's Browser")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())