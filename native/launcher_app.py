from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QToolButton, QButtonGroup
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, Qt, QEvent, QSize
from PyQt6.QtGui import QCursor, QIcon

from pathlib import Path

from launcher_bridge import LauncherBridge
from settings_manager import SettingsManager
from game_launcher import GameLauncher
from screenshot_service import ScreenshotService
from event_timer_service import EventTimerService

# Constants
SIDEBAR_WIDTH = 80
CONTENT_WIDTH = 1366  # default content resolution width (excludes sidebar)
CONTENT_HEIGHT = 768  # default content resolution height

# Icon base path
ICON_BASE = Path(__file__).parent / "resources" / "icons"


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
        self._dragging = False
        self._drag_pos = None

        # Setup central widget
        self.rootFrame = QWidget(self)
        self.rootFrame.setObjectName("RootFrame")
        self.setCentralWidget(self.rootFrame)

        # Main horizontal layout: [Sidebar] [Content/WebView]
        main_layout = QHBoxLayout(self.rootFrame)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)


        # --- Qt Sidebar (80px fixed) ---
        self.sidebar = QWidget(self.rootFrame)
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(SIDEBAR_WIDTH)

        # Layout for sidebar
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(0)

        # Load icons
        self._icon_logo = self._load_icon("diamond.svg")
        self._icon_home = self._load_icon("home.svg")
        self._icon_rankings = self._load_icon("leaderboard.svg")
        self._icon_donate = self._load_icon("paid.svg")
        self._icon_guides = self._load_icon("menu_book.svg")
        self._icon_events = self._load_icon("event.svg")
        self._icon_power = self._load_icon("power_settings_new.svg")

        # Top: Logo button (52x52)
        self.logo_btn = QToolButton(self.sidebar)
        self.logo_btn.setFixedSize(52, 52)
        self.logo_btn.setObjectName("SidebarLogo")
        self.logo_btn.setIcon(self._icon_logo)
        self.logo_btn.setIconSize(QSize(32, 32))
        self.logo_btn.setToolTip("Opal MU - Home")
        sidebar_layout.addWidget(self.logo_btn, 0, Qt.AlignmentFlag.AlignHCenter)

        # Events icon (under logo, 12px gap, no pill)
        sidebar_layout.addSpacing(12)
        self.btn_events = self._create_sidebar_button(self._icon_events, "Events")
        sidebar_layout.addWidget(self.btn_events, 0, Qt.AlignmentFlag.AlignHCenter)

        # Stretch to push nav pill to center
        sidebar_layout.addStretch(1)

        # Navigation pill container (3 main nav icons: Home, Rankings, Guides)
        from PyQt6.QtWidgets import QFrame
        self.nav_pill_frame = QFrame(self.sidebar)
        self.nav_pill_frame.setObjectName("NavPillFrame")
        self.nav_pill_frame.setFixedSize(48, 145)
        
        nav_pill_layout = QVBoxLayout(self.nav_pill_frame)
        nav_pill_layout.setContentsMargins(0, 0, 0, 0)
        nav_pill_layout.setSpacing(0) # Spacing handled by distribution or manual if needed, but user said spacing 16 in prompt setup, let's check
        # User prompt: "self.navPillLayout.setSpacing(16)"
        nav_pill_layout.setSpacing(16)
        nav_pill_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create 3 main nav buttons (Home, Rankings, Guides)
        self.btn_home = self._create_sidebar_button(self._icon_home, "Home")
        self.btn_rankings = self._create_sidebar_button(self._icon_rankings, "Rankings")
        self.btn_guides = self._create_sidebar_button(self._icon_guides, "Guides")

        self.btn_home.setChecked(True)  # Default to home

        for btn in [self.btn_home, self.btn_rankings, self.btn_guides]:
            nav_pill_layout.addWidget(btn, 0, Qt.AlignmentFlag.AlignHCenter)

        sidebar_layout.addWidget(self.nav_pill_frame, 0, Qt.AlignmentFlag.AlignHCenter)

        # Stretch to push bottom icons down
        sidebar_layout.addStretch(1)

        # Bottom group: Donate -> Power
        self.btn_donate = self._create_sidebar_button(self._icon_donate, "Donate")
        sidebar_layout.addWidget(self.btn_donate, 0, Qt.AlignmentFlag.AlignHCenter)

        sidebar_layout.addSpacing(12)

        self.btn_power = self._create_sidebar_button(self._icon_power, "Exit")
        self.btn_power.setCheckable(False)
        self.btn_power.setObjectName("ExitButton")
        self.btn_power.clicked.connect(self.close)
        sidebar_layout.addWidget(self.btn_power, 0, Qt.AlignmentFlag.AlignHCenter)


        # --- Web container ---
        self.web_container = QWidget(self.rootFrame)
        self.web_container.setObjectName("WebContainer")
        web_layout = QVBoxLayout(self.web_container)
        web_layout.setContentsMargins(0, 0, 0, 0)
        web_layout.setSpacing(0)

        # Initialize managers (pass rootFrame for embedding support)
        self.settings_manager = SettingsManager()
        self.game_launcher = GameLauncher(self.settings_manager, self.rootFrame)
        self.screenshot_service = ScreenshotService(self.settings_manager)
        self.event_timer_service = EventTimerService(self.settings_manager)

        # WebEngineView goes inside web_container (content width only)
        self.webview = QWebEngineView(self.web_container)
        self.webview.setMinimumSize(CONTENT_WIDTH, CONTENT_HEIGHT)
        self.webview.setMaximumSize(CONTENT_WIDTH, CONTENT_HEIGHT)
        self.webview.installEventFilter(self)

        web_layout.addWidget(self.webview)

        # Add sidebar + content to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.web_container)

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

        # Apply default resolution sizes (Qt sidebar + content)
        total_width = SIDEBAR_WIDTH + CONTENT_WIDTH
        self.setFixedSize(total_width, CONTENT_HEIGHT)
        self.resize(total_width, CONTENT_HEIGHT)

        print(f"Window initialized: {total_width} x {CONTENT_HEIGHT} (Sidebar: {SIDEBAR_WIDTH} + Content: {CONTENT_WIDTH})")
        print(f"WINDOW SIZE: {self.size().width()} x {self.size().height()}")
        print(f"WEBVIEW SIZE: {self.webview.size().width()} x {self.webview.size().height()}")

        # Log geometry details
        self.log_geometry("INIT")

        # Apply stylesheet matching React sidebar
        self.setStyleSheet("""
            #RootFrame {
                background-color: #020617;
                border-radius: 24px;
            }

            #Sidebar {
                background-color: #2c2f49;
                border-top-left-radius: 24px;
                border-bottom-left-radius: 24px;
                border-top-right-radius: 0;
                border-bottom-right-radius: 0;
            }

            #SidebarLogo {
                border-radius: 18px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #8b5cf6, stop:1 #6366f1);
                border: none;
            }

            #SidebarLogo:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                            stop:0 #9d6fff, stop:1 #7477ff);
            }

            /* Navigation pill container */
            #NavPillFrame {
                background-color: rgba(0, 0, 0, 0.25);
                border-radius: 24px;
            }

            /* Sidebar buttons - transparent, no background */
            #SidebarButton {
                border: none;
                background: transparent;
                padding: 0;
                margin: 0;
                border-radius: 0;
            }

            #SidebarButton:hover {
                background: transparent;
            }
            
            /* Active state styling handled via icon color update in logic or separate mechanism if needed */

            #ExitButton {
                border-radius: 9999px;
                background-color: transparent;
                border: none;
            }

            #ExitButton:hover {
                background-color: rgba(239, 68, 68, 0.12);
            }

            #WebContainer {
                background-color: transparent;
                border-top-right-radius: 24px;
                border-bottom-right-radius: 24px;
                border-top-left-radius: 0;
                border-bottom-left-radius: 0;
            }
        """)

        # Setup button group for exclusive selection across different parents
        self.nav_group = QButtonGroup(self)
        # Logo is not checkable, so don't add to group
        self.nav_group.addButton(self.btn_home)
        self.nav_group.addButton(self.btn_rankings)
        self.nav_group.addButton(self.btn_guides)
        self.nav_group.addButton(self.btn_events)
        self.nav_group.addButton(self.btn_donate)
        
        # Connect buttons to navigation
        self.logo_btn.clicked.connect(lambda: self._handle_logo_click())
        self.btn_home.clicked.connect(lambda: self._navigate_to('home'))
        self.btn_rankings.clicked.connect(lambda: self._navigate_to('rankings'))
        self.btn_guides.clicked.connect(lambda: self._navigate_to('guides'))
        self.btn_events.clicked.connect(lambda: self._navigate_to('events'))
        self.btn_donate.clicked.connect(lambda: self._navigate_to('donate'))

        # Load frontend
        url = QUrl("http://localhost:5175")
        print("Loading development server: http://localhost:5175")
        self.webview.load(url)

    def _navigate_to(self, view_name: str):
        """Navigate to a specific view in the React app."""
        print(f"Navigating to {view_name}")
        self.webview.page().runJavaScript(f"if(window.navigateTo) window.navigateTo('{view_name}');")

    def _handle_logo_click(self):
        """Handle logo click: check home button and navigate home."""
        self.btn_home.setChecked(True)
        self._navigate_to('home')

    def _load_icon(self, name: str) -> QIcon:
        """Load an icon from the resources/icons directory."""
        path = ICON_BASE / name
        return QIcon(str(path))



    def _create_sidebar_button(self, icon: QIcon, tooltip: str = "") -> QToolButton:
        """Create a styled sidebar button with icon (transparent, no bg)."""
        btn = QToolButton(self.sidebar)
        btn.setIcon(icon)
        btn.setIconSize(QSize(32, 32))  # Updated to 32px as per request
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedSize(48, 48)  # Updated to 48px as per request
        btn.setObjectName("SidebarButton")
        return btn

    def set_resolution(self, width: int, height: int):
        """Set the resolution for the content area (Qt sidebar is extra)."""
        total_width = SIDEBAR_WIDTH + width

        self.webview.setMinimumSize(width, height)
        self.webview.setMaximumSize(width, height)

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

    def _in_sidebar(self, event) -> bool:
        """Return True if the mouse event is within the sidebar area."""
        x = int(event.position().x())
        return 0 <= x < SIDEBAR_WIDTH

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._in_sidebar(event):
            self._dragging = True
            self._drag_pos = event.globalPosition().toPoint()
            print(f"[DRAG] Start from sidebar at {self._drag_pos}")
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and self._drag_pos is not None:
            new_pos = event.globalPosition().toPoint()
            diff = new_pos - self._drag_pos
            self.move(self.x() + diff.x(), self.y() + diff.y())
            self._drag_pos = new_pos
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging:
            print("[DRAG] Stop")
        self._dragging = False
        self._drag_pos = None
        super().mouseReleaseEvent(event)

    def eventFilter(self, obj, event):
        # Keep eventFilter for other purposes if needed
        return super().eventFilter(obj, event)
