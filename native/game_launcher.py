import subprocess
import psutil
import os
import time
from PyQt6.QtCore import QProcess, QTimer, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout

try:
    import win32gui
    import win32con
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("Warning: pywin32 not available. Window embedding will not work.")

# Import the new PID-based window embedding module
from window_embed import find_mu_hwnd, embed_window, verify_and_fix_embed

class GameLauncher(QObject):
    # Signal emitted when game client window is found (for embedding)
    clientWindowFound = pyqtSignal(int)  # HWND
    
    def __init__(self, settings_manager, parent_widget=None):
        super().__init__()
        self.settings = settings_manager
        self.parent_widget = parent_widget
        self.process = None
        self.game_hwnd = None
        self.embedded_widget = None
        self.process_list = []  # Track all launched processes
        self.managed_pids = set()  # PIDs launched by this launcher (for anti-direct-launch detection)
        
    def launch(self, config=None):
        """
        Launch the game with optional configuration
        
        Args:
            config (dict): Optional configuration override
            
        Returns:
            tuple: (success: bool, message: str)
        """
        game_path = self.settings.get("game_executable", "main.exe")
        # Support both config key names
        max_clients = self.settings.get("processLimit") or self.settings.get("max_clients", 3)
        # Fix #1: Support both config key names for embedding
        embed_window = self.settings.get("embed_game_window") or self.settings.get("embedGameWindow", False)
        
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
            # Use the directory of the game executable as the working directory
            game_dir = os.path.dirname(os.path.abspath(game_path))
            process = subprocess.Popen([game_path], cwd=game_dir)
            self.process_list.append(process)
            # Track this PID as managed
            self.managed_pids.add(process.pid)
            print(f"[GameLauncher] Started process with PID {process.pid}")
            return True, "Game launched successfully"
        except Exception as e:
            return False, str(e)
    
    def _launch_embedded(self, game_path):
        """Launch game and embed its window into the launcher"""
        if not WIN32_AVAILABLE:
            return False, "Win32 APIs not available for window embedding"
        
        if not self.parent_widget:
            return False, "No parent widget provided for embedding"
        
        # Use the directory of the game executable as the working directory
        game_dir = os.path.dirname(os.path.abspath(game_path))
        
        # Launch process normally
        try:
            process = subprocess.Popen([game_path], cwd=game_dir)
            self.process_list.append(process)
            self.managed_pids.add(process.pid)
            
            # Start polling for window
            self._poll_for_window(process.pid, attempts=0, max_attempts=10)
            
            return True, "Game launched (embedding window...)"
        except Exception as e:
            return False, f"Failed to launch: {str(e)}"
    
    def _poll_for_window(self, pid, attempts, max_attempts):
        """Poll for the game window to appear and emit signal when found."""
        if attempts >= max_attempts:
            print(f"[GameLauncher] Failed to find window after {max_attempts} attempts")
            return
        
        # Use new PID-based window finder (ignores debugger windows automatically)
        hwnd = find_mu_hwnd()
        
        if hwnd:
            print(f"[GameLauncher] Found game window HWND {hwnd}")
            self.game_hwnd = hwnd
            self.clientWindowFound.emit(hwnd)
        else:
            # Retry after 300ms
            QTimer.singleShot(300, lambda: self._poll_for_window(pid, attempts + 1, max_attempts))
    
    def reparent_game_window_to_container(self, hwnd: int, container_hwnd: int, width: int, height: int) -> bool:
        """
        Re-parent the game window into the Qt container using the new window_embed module.
        
        Args:
            hwnd: Game window handle
            container_hwnd: Container widget window handle
            width: Target width
            height: Target height
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use the new PID-based embedding system
            success = embed_window(hwnd, container_hwnd, width, height)
            
            if success:
                # Track embedded state for verification
                self.game_hwnd = hwnd
                self.hwnd_host = container_hwnd
            
            return success
            
        except Exception as e:
            print(f"[Embed] ERROR: Reparenting failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False
    
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
            pid = self.process.processId()
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
            self.managed_pids.discard(pid)
            success = True
        
        # Close any tracked processes
        for proc in self.process_list:
            try:
                if proc.poll() is None:  # Process is still running
                    pid = proc.pid
                    proc.terminate()
                    time.sleep(0.5)
                    if proc.poll() is None:
                        proc.kill()
                    self.managed_pids.discard(pid)
                    success = True
            except Exception as e:
                print(f"Error closing process: {e}")
        
        # Clean up embedded state
        if self.game_hwnd:
            print(f"[GameLauncher] Clearing embedded HWND {self.game_hwnd}")
        self.game_hwnd = None
        self.process_list = []
        
        return success
    
    def get_unmanaged_processes(self):
        """
        Find game processes that were NOT launched by this launcher.
        Returns list of dicts with pid, name info for unmanaged processes.
        """
        game_name = os.path.basename(self.settings.get("game_executable", "main.exe"))
        unmanaged = []
        
        # Clean up terminated PIDs from managed set
        self._cleanup_terminated_pids()
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == game_name:
                    pid = proc.info['pid']
                    if pid not in self.managed_pids:
                        unmanaged.append({
                            'pid': pid,
                            'name': proc.info['name']
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return unmanaged
    
    def _cleanup_terminated_pids(self):
        """Remove PIDs from managed_pids that are no longer running"""
        to_remove = set()
        for pid in self.managed_pids:
            if not psutil.pid_exists(pid):
                to_remove.add(pid)
        self.managed_pids -= to_remove
    
    def kill_unmanaged_process(self, pid: int) -> bool:
        """
        Kill an unmanaged game process by PID.
        Returns True if successful.
        """
        try:
            proc = psutil.Process(pid)
            game_name = os.path.basename(self.settings.get("game_executable", "main.exe"))
            
            # Safety check: only kill if it's actually the game executable
            if proc.name() == game_name and pid not in self.managed_pids:
                proc.terminate()
                proc.wait(timeout=3)
                print(f"[GameLauncher] Killed unmanaged process PID {pid}")
                return True
        except psutil.NoSuchProcess:
            return True  # Already gone
        except psutil.TimeoutExpired:
            try:
                proc.kill()
                return True
            except Exception:
                pass
        except Exception as e:
            print(f"[GameLauncher] Failed to kill PID {pid}: {e}")
        
        return False
    
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
