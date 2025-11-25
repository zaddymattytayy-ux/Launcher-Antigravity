from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
from PyQt6.QtGui import QCursor
import json
import os

class LauncherBridge(QObject):
    # Signals
    updateAvailable = pyqtSignal(str)
    downloadProgress = pyqtSignal(int)
    gameLaunched = pyqtSignal(bool)
    eventUpdated = pyqtSignal(str)  # Forward from EventTimerService
    eventNotification = pyqtSignal(str, int)  # Forward from EventTimerService

    def __init__(self, window=None, settings_manager=None, game_launcher=None, screenshot_service=None, event_timer_service=None):
        super().__init__()
        self.window = window
        self.settings_manager = settings_manager
        self.game_launcher = game_launcher
        self.screenshot_service = screenshot_service
        self.event_timer_service = event_timer_service
        
        # Connect event timer signals if available
        if self.event_timer_service:
            self.event_timer_service.eventUpdated.connect(self.eventUpdated.emit)
            self.event_timer_service.eventNotification.connect(self.eventNotification.emit)
        
        print("LauncherBridge initialized")

    @pyqtSlot(result=str)
    def getSettings(self):
        print("Get Settings requested")
        if self.settings_manager:
            settings = self.settings_manager.load_settings()
            return json.dumps(settings)
        return "{}"

    @pyqtSlot(str, result=bool)
    def saveSettings(self, settings_json):
        print(f"Save Settings requested: {settings_json}")
        if self.settings_manager:
            try:
                settings = json.loads(settings_json)
                return self.settings_manager.save_settings(settings)
            except json.JSONDecodeError:
                print("Invalid JSON format")
                return False
        return False

    @pyqtSlot(str, result=str)
    def startGame(self, config_json):
        print(f"Start Game requested with config: {config_json}")
        if self.game_launcher:
            success, message = self.game_launcher.launch()
            self.gameLaunched.emit(success)
            return json.dumps({"success": success, "message": message})
        return json.dumps({"success": False, "message": "Launcher not initialized"})


    @pyqtSlot(result=str)
    def getSession(self):
        """Get current session from session.json"""
        try:
            session_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session.json")
            if os.path.exists(session_path):
                with open(session_path, 'r') as f:
                    session_data = json.load(f)
                    return json.dumps(session_data)
        except Exception as e:
            print(f"Error loading session: {e}")
        
        # Default session if file doesn't exist or error
        return json.dumps({
            "logged": False,
            "username": "",
            "is_admin": False
        })

    @pyqtSlot(result=int)
    def getOnlineCount(self):
        # Temporary stub
        return 1


    @pyqtSlot(result=str)
    def requestScreenshot(self):
        """Capture screenshot of the game window"""
        if self.screenshot_service:
            filepath = self.screenshot_service.capture_active_window()
            if filepath:
                return filepath
            return ""
        return "screenshots/placeholder.png"

    @pyqtSlot(result=str)
    def getEvents(self):
        # Mock JSON events
        events = [
            {"name": "Blood Castle", "time": "00:30:00", "status": "Open"},
            {"name": "Devil Square", "time": "01:15:00", "status": "Closed"},
            {"name": "Chaos Castle", "time": "02:00:00", "status": "Closed"}
        ]
        return json.dumps(events)

    # Legacy/Helper methods
    @pyqtSlot(str, str)
    def launchGame(self, resolution, windowMode):
        # Wrapper for backward compatibility if needed
        return self.startGame(json.dumps({"resolution": resolution, "windowMode": windowMode}))

    @pyqtSlot()
    def startDrag(self):
        """Begin dragging the window from the sidebar region."""
        if self.window and hasattr(self.window, "start_drag_from_sidebar"):
            self.window.start_drag_from_sidebar()
