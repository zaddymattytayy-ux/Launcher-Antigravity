from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer
from PyQt6.QtGui import QCursor
import json
import os


class LauncherBridge(QObject):
    # Signals for React to subscribe to
    updateAvailable = pyqtSignal(str)       # new_version string
    downloadProgress = pyqtSignal(int)       # 0-100 percentage
    updateError = pyqtSignal(str)            # error message
    updateFinished = pyqtSignal()            # update completed
    gameLaunched = pyqtSignal(bool)          # success status
    eventUpdated = pyqtSignal(str)           # Forward from EventTimerService (JSON string)
    eventNotification = pyqtSignal(str, int) # Forward from EventTimerService
    unmanagedProcessDetected = pyqtSignal(str)  # JSON with unmanaged process info

    def __init__(self, window=None, settings_manager=None, game_launcher=None, 
                 screenshot_service=None, event_timer_service=None, update_manager=None):
        super().__init__()
        self.window = window
        self.settings_manager = settings_manager
        self.game_launcher = game_launcher
        self.screenshot_service = screenshot_service
        self.event_timer_service = event_timer_service
        self.update_manager = update_manager
        
        # Connect event timer signals if available
        if self.event_timer_service:
            self.event_timer_service.eventUpdated.connect(self.eventUpdated.emit)
            self.event_timer_service.eventNotification.connect(self.eventNotification.emit)
        
        # Connect update manager signals if available
        if self.update_manager:
            self.update_manager.updateAvailable.connect(self.updateAvailable.emit)
            self.update_manager.downloadProgress.connect(self.downloadProgress.emit)
            self.update_manager.updateError.connect(self.updateError.emit)
            self.update_manager.updateFinished.connect(self.updateFinished.emit)
        
        # Setup background process scanner for unmanaged clients
        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._check_unmanaged_processes)
        # Start scanning every 10 seconds
        self._scan_timer.start(10000)
        
        print("LauncherBridge initialized")

    # ==================== Settings ====================
    
    @pyqtSlot(result=str)
    def getSettings(self):
        """Get all settings as JSON string"""
        print("[Bridge] getSettings called")
        if self.settings_manager:
            settings = self.settings_manager.load_settings()
            return json.dumps(settings)
        return "{}"

    @pyqtSlot(str, result=bool)
    def saveSettings(self, settings_json):
        """Save settings from JSON string"""
        print(f"[Bridge] saveSettings called: {settings_json}")
        if self.settings_manager:
            try:
                settings = json.loads(settings_json)
                return self.settings_manager.save_settings(settings)
            except json.JSONDecodeError as e:
                print(f"[Bridge] Invalid JSON format: {e}")
                return False
        return False

    @pyqtSlot(int, int, bool)
    def setResolution(self, width, height, windowed):
        """
        Set launcher resolution and window mode.
        This resizes the Qt window and saves to config.
        """
        print(f"[Bridge] setResolution called: {width}x{height}, windowed={windowed}")
        
        # Resize window
        if self.window and hasattr(self.window, 'set_resolution'):
            self.window.set_resolution(width, height)
        
        # Save to config
        if self.settings_manager:
            self.settings_manager.set('resolution', f"{width}x{height}")
            self.settings_manager.set('window_mode', windowed)
            self.settings_manager.save(self.settings_manager.settings)

    # ==================== Game Launch ====================

    @pyqtSlot(result=str)
    def launchGame(self):
        """Launch the game using GameLauncher"""
        print("[Bridge] launchGame called")
        if self.game_launcher:
            success, message = self.game_launcher.launch()
            self.gameLaunched.emit(success)
            return json.dumps({"success": success, "message": message})
        return json.dumps({"success": False, "message": "Game launcher not initialized"})

    @pyqtSlot(str, result=str)
    def startGame(self, config_json):
        """Start game with optional config override (legacy method)"""
        print(f"[Bridge] startGame called with config: {config_json}")
        # Just delegate to launchGame for now
        return self.launchGame()

    # ==================== Session ====================

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
            print(f"[Bridge] Error loading session: {e}")
        
        # Default session if file doesn't exist or error
        return json.dumps({
            "logged": False,
            "username": "",
            "is_admin": False
        })

    # ==================== Online Count ====================

    @pyqtSlot(result=int)
    def getOnlineCount(self):
        """Get online player count (stub - will be implemented with server API)"""
        # TODO: Implement actual server query when API is ready
        return 1

    # ==================== Screenshot ====================

    @pyqtSlot(result=str)
    def requestScreenshot(self):
        """Capture screenshot of the game window"""
        if self.screenshot_service:
            filepath = self.screenshot_service.capture_active_window()
            if filepath:
                return filepath
            return ""
        return ""

    # ==================== Events ====================

    @pyqtSlot(result=str)
    def getEvents(self):
        """Get events (mock data for now - will be replaced by EventTimerService)"""
        events = [
            {"name": "Blood Castle", "time": "00:30:00", "status": "Open"},
            {"name": "Devil Square", "time": "01:15:00", "status": "Closed"},
            {"name": "Chaos Castle", "time": "02:00:00", "status": "Closed"}
        ]
        return json.dumps(events)

    # ==================== Update System ====================

    @pyqtSlot()
    def checkForUpdates(self):
        """Check for launcher/client updates"""
        print("[Bridge] checkForUpdates called")
        if self.update_manager:
            current_version = None
            if self.settings_manager:
                current_version = self.settings_manager.get('version', '1.0.0')
            self.update_manager.check_for_updates(current_version)
        else:
            print("[Bridge] UpdateManager not available")

    @pyqtSlot()
    def startUpdate(self):
        """Start downloading and applying the available update"""
        print("[Bridge] startUpdate called")
        if self.update_manager:
            self.update_manager.download_and_apply_update()
        else:
            self.updateError.emit("Update manager not available")

    @pyqtSlot()
    def cancelUpdate(self):
        """Cancel an in-progress update"""
        print("[Bridge] cancelUpdate called")
        if self.update_manager:
            self.update_manager.cancel_update()

    # ==================== Window Drag ====================

    @pyqtSlot(int, int)
    def startDrag(self, x, y):
        """
        Begin dragging the window.
        Note: Qt sidebar already handles native dragging via mouse events.
        This method is kept for compatibility but dragging is handled natively.
        """
        print(f"[Bridge] startDrag called at ({x}, {y})")
        # The Qt window already handles dragging via mousePressEvent on the sidebar.
        # This method exists for compatibility with React code that might call it,
        # but actual dragging is handled by the Qt event handlers.
        if self.window and hasattr(self.window, 'start_drag_from_bridge'):
            self.window.start_drag_from_bridge(x, y)

    # ==================== Process Management ====================

    @pyqtSlot(result=str)
    def getUnmanagedProcesses(self):
        """Get list of game processes not launched by this launcher"""
        if self.game_launcher:
            processes = self.game_launcher.get_unmanaged_processes()
            return json.dumps(processes)
        return "[]"

    @pyqtSlot(int, result=bool)
    def killUnmanagedProcess(self, pid):
        """Kill an unmanaged game process"""
        if self.game_launcher:
            return self.game_launcher.kill_unmanaged_process(pid)
        return False

    def _check_unmanaged_processes(self):
        """Background check for unmanaged game processes"""
        if not self.game_launcher:
            return
        
        # Check config flag
        kill_unmanaged = False
        if self.settings_manager:
            kill_unmanaged = self.settings_manager.get('kill_unmanaged_clients', False)
        
        unmanaged = self.game_launcher.get_unmanaged_processes()
        
        for proc in unmanaged:
            pid = proc.get('pid')
            print(f"[Bridge] Detected unmanaged game process: PID {pid}")
            
            # Emit signal for React to potentially show a warning
            self.unmanagedProcessDetected.emit(json.dumps(proc))
            
            # Kill if configured to do so
            if kill_unmanaged:
                self.game_launcher.kill_unmanaged_process(pid)

    # ==================== Utility Methods ====================

    @pyqtSlot(result=bool)
    def bringGameToFront(self):
        """Bring the game window to front (Fix #2)"""
        print("[Bridge] bringGameToFront called")
        if self.game_launcher:
            return self.game_launcher.bring_to_front()
        return False

    @pyqtSlot(result=bool)
    def closeGame(self):
        """Close the game process (Fix #2)"""
        print("[Bridge] closeGame called")
        if self.game_launcher:
            return self.game_launcher.close_game()
        return False

    @pyqtSlot()
    def exitLauncher(self):
        """Exit the launcher application"""
        print("[Bridge] exitLauncher called")
        if self.window:
            self.window.close()
