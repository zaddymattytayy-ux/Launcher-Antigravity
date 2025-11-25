from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, Qt, QEvent
from PyQt6.QtGui import QCursor

from launcher_bridge import LauncherBridge
from settings_manager import SettingsManager
from game_launcher import GameLauncher
from screenshot_service import ScreenshotService
from event_timer_service import EventTimerService

# Constants
SIDEBAR_WIDTH = 80
CONTENT_WIDTH = 1366  # default content resolution width (excludes sidebar)
CONTENT_HEIGHT = 768  # default content resolution height


class LauncherApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MU Online Launcher")

        # Make window frameless with translucent background
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowSystemMenuHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Initialize drag variables
        self._drag_pos = None
        self._dragging = False

        # Setup central widget with rounded corners
        self.rootFrame = QWidget()
        self.rootFrame.setObjectName("RootFrame")
        self.setCentralWidget(self.rootFrame)

        # Apply stylesheet for rounded corners
        self.setStyleSheet("""
            #RootFrame {
                background-color: #020617;
                border-radius: 24px;
            }
        """)

        # Main layout contains only the webview; sidebar is rendered in React
        layout = QVBoxLayout(self.rootFrame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Initialize managers (pass rootFrame for embedding support)
        self.settings_manager = SettingsManager()
        self.game_launcher = GameLauncher(self.settings_manager, self.rootFrame)
        self.screenshot_service = ScreenshotService(self.settings_manager)
        self.event_timer_service = EventTimerService(self.settings_manager)

        # Setup WebEngineView (full UI width, including React sidebar)
        total_width = SIDEBAR_WIDTH + CONTENT_WIDTH
        self.webview = QWebEngineView()
        self.webview.setMinimumSize(total_width, CONTENT_HEIGHT)
        self.webview.setMaximumSize(total_width, CONTENT_HEIGHT)
        self.webview.installEventFilter(self)

        layout.addWidget(self.webview)

        # Setup WebChannel
        self.channel = QWebChannel()
        self.bridge = LauncherBridge(
            window=self,
            settings_manager=self.settings_manager,
            game_launcher=self.game_launcher,
            screenshot_service=self.screenshot_service,
            event_timer_service=self.event_timer_service
        )
        self.channel.registerObject("launcherBridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        # Start event timer service
        self.event_timer_service.start()

        # Apply default resolution sizes (React sidebar + content)
        self.setFixedSize(total_width, CONTENT_HEIGHT)
        self.resize(total_width, CONTENT_HEIGHT)

        print(f"Window initialized: {total_width} x {CONTENT_HEIGHT} (React sidebar + content)")
        print(f"WINDOW SIZE: {self.size().width()} x {self.size().height()}")
        print(f"WEBVIEW SIZE: {self.webview.size().width()} x {self.webview.size().height()}")

        # Log geometry details
        self.log_geometry("INIT")

        # Load frontend
        url = QUrl("http://localhost:5175")
        print("Loading development server: http://localhost:5175")
        self.webview.load(url)

    def set_resolution(self, width: int, height: int):
        """Set the resolution for the content area"""
        total_width = SIDEBAR_WIDTH + width

        # Set webview size to the total UI width (sidebar + content)
        self.webview.setMinimumSize(total_width, height)
        self.webview.setMaximumSize(total_width, height)

        # Set window total size
        self.setFixedSize(total_width, height)
        self.resize(total_width, height)

        print(f"Resolution changed: {width} x {height} (Total: {total_width} x {height})")
        print(f"WINDOW SIZE: {self.size().width()} x {self.size().height()}")
        print(f"WEBVIEW SIZE: {self.webview.size().width()} x {self.webview.size().height()}")

        # Log geometry details
        self.log_geometry("RESIZE")

    def log_geometry(self, label: str):
        """Log window geometry and screen DPI information"""
        screen = QApplication.primaryScreen()
        print(f"[{label}] WINDOW: {self.size().width()} x {self.size().height()}")
        print(f"[{label}] WEBVIEW: {self.webview.size().width()} x {self.webview.size().height()}")
        print(f"[{label}] SCREEN logical DPI: {screen.logicalDotsPerInch()}")
        print(f"[{label}] SCREEN devicePixelRatio: {screen.devicePixelRatio()}")

    def start_drag_from_sidebar(self):
        """Begin drag when the React sidebar signals a mouse-down."""
        self._dragging = True
        self._drag_pos = QCursor.pos()

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_pos is not None:
            new_pos = event.globalPosition().toPoint()
            diff = new_pos - self._drag_pos
            self.move(self.x() + diff.x(), self.y() + diff.y())
            self._drag_pos = new_pos
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging = False
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def eventFilter(self, obj, event):
        if obj == self.webview and event.type() in (
            QEvent.Type.MouseMove,
            QEvent.Type.MouseButtonRelease,
        ):
            if event.type() == QEvent.Type.MouseMove and self._dragging:
                self.mouseMoveEvent(event)
            if event.type() == QEvent.Type.MouseButtonRelease and self._dragging:
                self.mouseReleaseEvent(event)
            # Allow the webview to continue processing the event
            return False
        return super().eventFilter(obj, event)
