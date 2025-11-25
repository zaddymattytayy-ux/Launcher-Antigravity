import os
import datetime
from PIL import ImageGrab
import psutil

try:
    import win32gui
    import win32ui
    import win32con
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("Warning: pywin32 not available. Screenshot capture will not work.")

class ScreenshotService:
    def __init__(self, settings_manager=None):
        self.settings = settings_manager
        self.screenshots_dir = self._get_screenshots_dir()
        
    def _get_screenshots_dir(self):
        """Get or create screenshots directory"""
        # Get project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        screenshots_dir = os.path.join(project_root, "screenshots")
        
        # Create directory if it doesn't exist
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            
        return screenshots_dir
    
    def capture_active_window(self):
        """
        Capture the active game window (main.exe) to a PNG file
        
        Returns:
            str: Path to the saved screenshot file, or None on error
        """
        if not WIN32_AVAILABLE:
            print("Error: pywin32 not available for screenshot capture")
            return None
        
        # Get game executable name from settings
        game_exe = "main.exe"
        if self.settings:
            game_exe = os.path.basename(self.settings.get("game_executable", "main.exe"))
        
        # Find the game window
        hwnd = self._find_window_by_process_name(game_exe)
        
        if not hwnd:
            print(f"Error: Could not find window for {game_exe}")
            return None
        
        try:
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # Bring window to front (optional)
            win32gui.SetForegroundWindow(hwnd)
            
            # Capture the window
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Copy the window content
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
            
            # Convert to PIL Image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            
            from PIL import Image
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Save the image
            img.save(filepath, 'PNG')
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            print(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None
    
    def capture(self):
        """Alias for capture_active_window for backward compatibility"""
        return self.capture_active_window()
    
    def capture_fullscreen(self):
        """
        Capture the entire screen
        
        Returns:
            str: Path to the saved screenshot file
        """
        try:
            # Capture entire screen using PIL
            img = ImageGrab.grab()
            
            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"fullscreen_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Save the image
            img.save(filepath, 'PNG')
            
            print(f"Fullscreen screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error capturing fullscreen: {e}")
            return None
    
    def _find_window_by_process_name(self, process_name):
        """
        Find a window handle by process name
        
        Args:
            process_name (str): Name of the process (e.g., "main.exe")
            
        Returns:
            int: Window handle (HWND) or None
        """
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
    
    def get_screenshots(self, limit=10):
        """
        Get list of recent screenshots
        
        Args:
            limit (int): Maximum number of screenshots to return
            
        Returns:
            list: List of screenshot file paths
        """
        try:
            files = []
            for filename in os.listdir(self.screenshots_dir):
                if filename.endswith('.png'):
                    filepath = os.path.join(self.screenshots_dir, filename)
                    files.append({
                        'path': filepath,
                        'filename': filename,
                        'timestamp': os.path.getmtime(filepath)
                    })
            
            # Sort by timestamp (newest first)
            files.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Return only the paths, limited
            return [f['path'] for f in files[:limit]]
            
        except Exception as e:
            print(f"Error getting screenshots: {e}")
            return []
    
    def delete_screenshot(self, filepath):
        """
        Delete a screenshot file
        
        Args:
            filepath (str): Path to the screenshot file
            
        Returns:
            bool: Success status
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Screenshot deleted: {filepath}")
                return True
            return False
        except Exception as e:
            print(f"Error deleting screenshot: {e}")
            return False

