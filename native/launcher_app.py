from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QApplication, QToolButton, QButtonGroup, QGraphicsColorizeEffect, QStackedLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, Qt, QEvent, QSize
from PyQt6.QtGui import QCursor, QIcon, QColor

from pathlib import Path

from launcher_bridge import LauncherBridge
from settings_manager import SettingsManager
from game_launcher import GameLauncher
from screenshot_service import ScreenshotService
from event_timer_service import EventTimerService
from update_manager import UpdateManager
from window_embed import verify_and_fix_embed

# Check Win32 availability
try:
    import win32gui
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("Warning: pywin32 not available. Window embedding will not work.")

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
        
        # Initialize embedded game window handle
        self.game_hwnd = None
        self.hwnd_host = None
        
        # Timer for verifying and fixing embed (prevents game from escaping)
        self.embed_verify_timer = None

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
        self.nav_pill_frame.setFixedSize(48, 152)
        
        nav_pill_layout = QVBoxLayout(self.nav_pill_frame)
        nav_pill_layout.setContentsMargins(0, 0, 0, 0)
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


        # --- Web container (Fix #4: Use QStackedLayout for proper overlay) ---
        self.web_container = QWidget(self.rootFrame)
        self.web_container.setObjectName("WebContainer")
        self.web_stacked_layout = QStackedLayout(self.web_container)
        self.web_stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.web_stacked_layout.setStackingMode(QStackedLayout.StackingMode.StackOne)

        # Initialize managers (pass rootFrame for embedding support)
        self.settings_manager = SettingsManager()
        self.game_launcher = GameLauncher(self.settings_manager, self.rootFrame)
        self.screenshot_service = ScreenshotService(self.settings_manager)
        self.event_timer_service = EventTimerService(self.settings_manager)
        self.update_manager = UpdateManager(self.settings_manager)

        # WebEngineView goes inside web_container (content width only)
        self.webview = QWebEngineView(self.web_container)
        self.webview.setMinimumSize(CONTENT_WIDTH, CONTENT_HEIGHT)
        self.webview.setMaximumSize(CONTENT_WIDTH, CONTENT_HEIGHT)
        self.webview.installEventFilter(self)

        # Game container for embedding (same size as webview, hidden by default)
        self.game_container = QWidget(self.web_container)
        self.game_container.setMinimumSize(CONTENT_WIDTH, CONTENT_HEIGHT)
        self.game_container.setMaximumSize(CONTENT_WIDTH, CONTENT_HEIGHT)
        game_container_layout = QVBoxLayout(self.game_container)
        game_container_layout.setContentsMargins(0, 0, 0, 0)
        game_container_layout.setSpacing(0)

        # Add to stacked layout - index 0 = webview, index 1 = game_container
        self.web_stacked_layout.addWidget(self.webview)
        self.web_stacked_layout.addWidget(self.game_container)
        self.web_stacked_layout.setCurrentIndex(0)  # Show webview by default

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
            event_timer_service=self.event_timer_service,
            update_manager=self.update_manager
        )
        self.channel.registerObject("launcherBridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)
        
        # Connect game launcher signals for embedding
        self.game_launcher.clientWindowFound.connect(self.embed_client_window)

        # Start event timer service
        self.event_timer_service.start()
        
        # Check for updates on startup
        self._check_updates_on_startup()

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
                background-color: rgba(255, 255, 255, 0.06);
                border-radius: 24px;
            }

            /* Sidebar buttons - transparent, no background */
            #SidebarButton {
                border: none;
                background: transparent;
                padding: 0;
                margin: 0;
                border-radius: 0;
                min-width: 48px;
                max-width: 48px;
                min-height: 48px;
                max-height: 48px;
            }

            #SidebarButton:hover {
                /* No background change on hover */
            }

            /* Active/selected state - no background, icon color handled by code */
            #SidebarButton:checked {
                background: transparent;
                border-radius: 0;
            }

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
        
        # Connect button toggled to update icon colors
        self.nav_group.buttonToggled.connect(self._update_icon_colors)
        
        # Initial icon color update
        self._update_icon_colors(self.btn_home, True)
        
        # Connect buttons to navigation
        self.logo_btn.clicked.connect(lambda: self._handle_logo_click())
        self.btn_home.clicked.connect(lambda: self._navigate_to('home'))
        self.btn_rankings.clicked.connect(lambda: self._navigate_to('rankings'))
        self.btn_guides.clicked.connect(lambda: self._navigate_to('guides'))
        self.btn_events.clicked.connect(lambda: self._navigate_to('events'))
        self.btn_donate.clicked.connect(lambda: self._navigate_to('donate'))

        # Load frontend (Fix #7: Support production mode)
        self._load_frontend()

    def _load_frontend(self) -> None:
        """Load frontend - try dev server first, fallback to dist/index.html."""
        import socket
        
        # Base = repo root (folder that contains `web` and `native`)
        base_path = Path(__file__).resolve().parent.parent
        dist_index = base_path / "web" / "dist" / "index.html"
        
        # Check if dev server is running on localhost:5175
        dev_server_available = False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # 500ms timeout
            result = sock.connect_ex(('localhost', 5175))
            sock.close()
            dev_server_available = (result == 0)
        except Exception as e:
            print(f"[FRONTEND] Dev server check failed: {e}")
            dev_server_available = False
        
        if dev_server_available:
            # Dev mode: use Vite dev server
            url = QUrl("http://localhost:5175")
            print(f"[FRONTEND] Loading dev server: {url.toString()}")
        elif dist_index.exists():
            # Production mode: use built dist
            url = QUrl.fromLocalFile(str(dist_index))
            print(f"[FRONTEND] Loading dist file: {dist_index}")
        else:
            # Error: neither available
            print("[FRONTEND] ERROR: Could not find dev server or dist/index.html")
            print("[FRONTEND] Attempting to load dev server anyway (will show blank if unavailable)")
            url = QUrl("http://localhost:5175")
        
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
        btn.setIconSize(QSize(26, 26))  # Updated to 26px as per request
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedSize(48, 48)  # Updated to 48px as per request
        btn.setObjectName("SidebarButton")
        return btn

    def _update_icon_colors(self, button, checked):
        """Apply purple colorize effect to active button, remove from others."""
        if not button:
            return
            
        if checked:
            effect = QGraphicsColorizeEffect(button)
            effect.setColor(QColor("#7B4DFB"))
            button.setGraphicsEffect(effect)
        else:
            button.setGraphicsEffect(None)

    def get_game_container_hwnd(self) -> int:
        """Get the native window handle of the game container widget."""
        return int(self.game_container.winId())
    
    def set_resolution(self, width: int, height: int):
        """Set the resolution for the content area (Qt sidebar is extra)."""
        total_width = SIDEBAR_WIDTH + width

        self.webview.setMinimumSize(width, height)
        self.webview.setMaximumSize(width, height)
        
        self.game_container.setMinimumSize(width, height)
        self.game_container.setMaximumSize(width, height)

        self.setFixedSize(total_width, height)
        self.resize(total_width, height)

        print(f"Resolution changed: {width} x {height} (Total: {total_width} x {height})")
        print(f"WINDOW SIZE: {self.size().width()} x {self.size().height()}")
        print(f"WEBVIEW SIZE: {self.webview.size().width()} x {self.webview.size().height()}")

        # Log geometry details
        self.log_geometry("RESIZE")
        
        # If game is embedded, resize the embedded window
        if self.game_container.isVisible():
            self._resize_game_container_to_content()

    def log_geometry(self, label: str):
        """Log window geometry and screen DPI information"""
        screen = QApplication.primaryScreen()
        print(f"[{label}] WINDOW: {self.size().width()} x {self.size().height()}")
        print(f"[{label}] WEBVIEW: {self.webview.size().width()} x {self.webview.size().height()}")
        print(f"[{label}] SCREEN logical DPI: {screen.logicalDotsPerInch()}")
        print(f"[{label}] SCREEN devicePixelRatio: {screen.devicePixelRatio()}")

    def _in_sidebar(self, global_x: int, global_y: int) -> bool:
        """Return True if the global coordinates are within the sidebar area."""
        from PyQt6.QtCore import QPoint
        local = self.mapFromGlobal(QPoint(global_x, global_y))
        return 0 <= local.x() < SIDEBAR_WIDTH

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            global_pos = event.globalPosition().toPoint()
            if self._in_sidebar(global_pos.x(), global_pos.y()):
                self._dragging = True
                self._drag_pos = global_pos
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
    
    def start_drag_from_bridge(self, global_x: int, global_y: int):
        """
        Start window dragging from a bridge call (only if inside sidebar).
        """
        from PyQt6.QtCore import QPoint
        if self._in_sidebar(global_x, global_y):
            self._dragging = True
            self._drag_pos = QPoint(global_x, global_y)
            print(f"[DRAG] Started from bridge at ({global_x}, {global_y})")
        else:
            print(f"[DRAG] Rejected - not in sidebar region")
    
    def embed_client_window(self, hwnd: int):
        """Embed the game client window into the launcher using Win32 re-parenting."""
        try:
            if not WIN32_AVAILABLE:
                print("[Embed] Win32 APIs not available")
                self._restore_webview()
                return
            
            print(f"[Embed] Preparing to embed game window HWND: {hwnd}")
            
            # CRITICAL: Ensure game_container has a native window created
            # Qt won't create the native window until the widget is shown or winId() is called
            print("[Embed] Ensuring game_container is realized...")
            self.game_container.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
            self.game_container.show()  # Make sure native window is created
            
            # Get container info
            container_hwnd = self.get_game_container_hwnd()
            width = self.game_container.width()
            height = self.game_container.height()
            
            print(f"[Embed] Container HWND: {container_hwnd}")
            print(f"[Embed] Container size: {width}x{height}")
            print(f"[Embed] Container visible: {self.game_container.isVisible()}")
            
            # Validate container HWND
            if container_hwnd == 0:
                print("[Embed] ERROR: Container HWND is 0 (invalid)")
                self._restore_webview()
                return
            
            # Use GameLauncher's Win32 re-parenting method
            success = self.game_launcher.reparent_game_window_to_container(
                hwnd, container_hwnd, width, height
            )
            
            if success:
                # Switch stacked layout to game container
                self.web_stacked_layout.setCurrentIndex(1)
                
                # Store the hwnd for later use (LauncherApp also tracks it)
                self.game_hwnd = hwnd
                self.hwnd_host = container_hwnd
                
                # Start timer to verify and maintain embedding
                self._start_embed_verification_timer()
                
                print(f"[Embed] Successfully embedded game window (HWND: {hwnd})")
                print(f"[Embed] Stacked layout now showing index: {self.web_stacked_layout.currentIndex()}")
            else:
                # Fall back to external window mode
                print("[Embed] Failed to embed client, falling back to external window mode")
                self._restore_webview()
            
        except Exception as e:
            print(f"[Embed] Error embedding window: {e}")
            import traceback
            traceback.print_exc()
            self._restore_webview()

    def _restore_webview(self):
        """Fix #8: Restore webview visibility on embed failure."""
        self.web_stacked_layout.setCurrentIndex(0)
        self._stop_embed_verification_timer()
        print("[Embed] Restored webview after embed failure")
    
    def _resize_game_container_to_content(self):
        """Resize embedded game window to match content area size."""
        if not self.game_hwnd or not WIN32_AVAILABLE:
            return
        
        try:
            import win32gui
            
            width = self.game_container.width()
            height = self.game_container.height()
            
            # Resize the embedded window using stored hwnd
            win32gui.MoveWindow(self.game_hwnd, 0, 0, width, height, True)
            print(f"[Embed] Resized embedded window to {width}x{height}")
        except Exception as e:
            print(f"[Embed] Error resizing embedded window: {e}")
    
    def _start_embed_verification_timer(self):
        """Start periodic verification of window embedding to prevent game from escaping."""
        from PyQt6.QtCore import QTimer
        
        if self.embed_verify_timer:
            self.embed_verify_timer.stop()
        
        self.embed_verify_timer = QTimer(self)
        self.embed_verify_timer.setInterval(1000)  # Check every 1 second
        self.embed_verify_timer.timeout.connect(self._verify_embed)
        self.embed_verify_timer.start()
        print("[Embed] Started verification timer (checking every 1s)")
    
    def _stop_embed_verification_timer(self):
        """Stop the embed verification timer."""
        if self.embed_verify_timer:
            self.embed_verify_timer.stop()
            self.embed_verify_timer = None
            print("[Embed] Stopped verification timer")
    
    def _verify_embed(self):
        """Verify and re-apply embedding if needed (called by timer)."""
        if not self.game_hwnd or not self.hwnd_host:
            return
        
        width = self.game_container.width()
        height = self.game_container.height()
        
        # Use window_embed module's verify function
        verify_and_fix_embed(self.game_hwnd, self.hwnd_host, width, height)
    
    def _check_updates_on_startup(self):
        """Check for updates when launcher starts"""
        if self.update_manager:
            current_version = self.settings_manager.get('version', '1.0.0')
            print(f"[Launcher] Checking for updates... Current version: {current_version}")
            self.update_manager.check_for_updates(current_version)
