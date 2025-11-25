import subprocess
import psutil
import os
import time
from PyQt6.QtCore import QProcess, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout

try:
    import win32gui
    import win32con
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("Warning: pywin32 not available. Window embedding will not work.")

class GameLauncher:
    def __init__(self, settings_manager, parent_widget=None):
        self.settings = settings_manager
        self.parent_widget = parent_widget
        self.process = None
        self.game_hwnd = None
        self.embedded_widget = None
        self.process_list = []  # Track all launched processes
        
    def launch(self, config=None):
        """
        Launch the game with optional configuration
        
        Args:
            config (dict): Optional configuration override
            
        Returns:
            tuple: (success: bool, message: str)
        """
        game_path = self.settings.get("game_executable", "main.exe")
        max_clients = self.settings.get("processLimit", 3)
        embed_window = self.settings.get("embedGameWindow", False)
        
        # Check process limit
        if self.count_running_instances(os.path.basename(game_path)) >= max_clients:
            return False, f"Max clients reached ({max_clients})"
        
        # Check if executable exists
        if not os.path.exists(game_path):
            return False, f"Game executable not found: {game_path}"
        
        try:
            if embed_window and WIN32_AVAILABLE and self.parent_widget:
                return self._launch_embedded(game_path)
            else:
                return self._launch_normal(game_path)
        except Exception as e:
            return False, f"Launch error: {str(e)}"
    
    def _launch_normal(self, game_path):
        """Launch game normally without embedding"""
        try:
            process = subprocess.Popen([game_path])
            self.process_list.append(process)
            return True, "Game launched successfully"
        except Exception as e:
            return False, str(e)
    
    def _launch_embedded(self, game_path):
        """Launch game and embed its window into the launcher"""
        if not WIN32_AVAILABLE:
            return False, "Win32 APIs not available for window embedding"
        
        if not self.parent_widget:
            return False, "No parent widget provided for embedding"
        
        # Create QProcess for better control
        self.process = QProcess()
        self.process.setProgram(game_path)
        
        # Start the process
        self.process.start()
        
        if not self.process.waitForStarted(5000):
            return False, "Failed to start game process"
        
        # Get the process ID
        pid = self.process.processId()
        
        # Wait for the game window to appear and embed it
        QTimer.singleShot(1000, lambda: self._find_and_embed_window(pid))
        
        return True, "Game launched (embedding window...)"
    
    def _find_and_embed_window(self, pid):
        """Find the game window by PID and embed it"""
        if not WIN32_AVAILABLE:
            return
        
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid:
                    windows.append(hwnd)
            return True
        
        # Find all windows belonging to this process
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            # Take the first visible window
            self.game_hwnd = windows[0]
            self._embed_window(self.game_hwnd)
        else:
            # Retry after a short delay
            QTimer.singleShot(500, lambda: self._find_and_embed_window(pid))
    
    def _embed_window(self, hwnd):
        """Embed the game window into the parent widget"""
        if not WIN32_AVAILABLE or not self.parent_widget:
            return
        
        try:
            # Create a container widget if not exists
            if not self.embedded_widget:
                self.embedded_widget = QWidget(self.parent_widget)
                layout = QVBoxLayout(self.embedded_widget)
                layout.setContentsMargins(0, 0, 0, 0)
            
            # Get the parent widget's window handle
            parent_hwnd = int(self.embedded_widget.winId())
            
            # Set the game window as a child of our widget
            win32gui.SetParent(hwnd, parent_hwnd)
            
            # Remove window decorations
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            style &= ~win32con.WS_CAPTION
            style &= ~win32con.WS_THICKFRAME
            win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)
            
            # Resize to fit the container
            rect = self.embedded_widget.rect()
            win32gui.MoveWindow(hwnd, 0, 0, rect.width(), rect.height(), True)
            
            # Show the window
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            
            print(f"Game window embedded successfully (HWND: {hwnd})")
            
        except Exception as e:
            print(f"Error embedding window: {e}")
    
    def bring_to_front(self):
        """Bring the game window to front"""
        if not WIN32_AVAILABLE:
            return False
        
        if self.game_hwnd:
            try:
                win32gui.SetForegroundWindow(self.game_hwnd)
                win32gui.ShowWindow(self.game_hwnd, win32con.SW_RESTORE)
                return True
            except Exception as e:
                print(f"Error bringing window to front: {e}")
                return False
        
        # If no embedded window, try to find any game window
        game_name = os.path.basename(self.settings.get("game_executable", "main.exe"))
        hwnd = self._find_window_by_process_name(game_name)
        
        if hwnd:
            try:
                win32gui.SetForegroundWindow(hwnd)
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                return True
            except Exception as e:
                print(f"Error bringing window to front: {e}")
                return False
        
        return False
    
    def close_game(self):
        """Close the game process"""
        success = False
        
        # Close embedded process if exists
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
            success = True
        
        # Close any tracked processes
        for proc in self.process_list:
            try:
                if proc.poll() is None:  # Process is still running
                    proc.terminate()
                    time.sleep(0.5)
                    if proc.poll() is None:
                        proc.kill()
                    success = True
            except Exception as e:
                print(f"Error closing process: {e}")
        
        # Clean up
        self.game_hwnd = None
        self.process_list = []
        
        return success
    
    def _find_window_by_process_name(self, process_name):
        """Find a window handle by process name"""
        if not WIN32_AVAILABLE:
            return None
        
        def enum_windows_callback(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid)
                    if proc.name() == process_name:
                        result.append(hwnd)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        return windows[0] if windows else None
    
    def count_running_instances(self, process_name):
        """Count how many instances of the game are running"""
        count = 0
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] == process_name:
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return count
    
    def get_running_processes(self):
        """Get list of running game processes"""
        game_name = os.path.basename(self.settings.get("game_executable", "main.exe"))
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            try:
                if proc.info['name'] == game_name:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'create_time': proc.info['create_time']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return processes

