from PyQt6.QtCore import QObject, pyqtSignal, QThread, QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json
import hashlib
import zipfile
import tempfile
import os
import sys


class UpdateWorker(QThread):
    """Background worker for downloading and applying updates"""
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, manifest: dict, base_path: str):
        super().__init__()
        self.manifest = manifest
        self.base_path = base_path
        self._cancelled = False
    
    def cancel(self):
        self._cancelled = True
    
    def run(self):
        try:
            zip_url = self.manifest.get('zip_url', '')
            expected_sha256 = self.manifest.get('sha256', '')
            
            if not zip_url:
                self.error.emit("No zip_url in manifest")
                return
            
            # Import requests here to download (using urllib as fallback)
            import urllib.request
            import urllib.error
            
            # Create temp file in launcher directory
            temp_dir = os.path.join(self.base_path, 'temp_update')
            os.makedirs(temp_dir, exist_ok=True)
            temp_zip_path = os.path.join(temp_dir, 'update.zip')
            
            # Download with progress tracking
            try:
                req = urllib.request.Request(zip_url, headers={'User-Agent': 'MULauncher/1.0'})
                response = urllib.request.urlopen(req, timeout=60)
                
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                chunk_size = 8192
                
                with open(temp_zip_path, 'wb') as f:
                    while True:
                        if self._cancelled:
                            self.error.emit("Update cancelled")
                            return
                        
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress.emit(progress)
                        else:
                            # Emit indeterminate progress
                            self.progress.emit(50)
                
            except urllib.error.URLError as e:
                self.error.emit(f"Download failed: {str(e)}")
                return
            except Exception as e:
                self.error.emit(f"Download error: {str(e)}")
                return
            
            # Verify SHA256 if provided
            if expected_sha256:
                self.progress.emit(95)
                actual_sha256 = self._calculate_sha256(temp_zip_path)
                if actual_sha256.lower() != expected_sha256.lower():
                    self.error.emit(f"SHA256 mismatch. Expected: {expected_sha256}, Got: {actual_sha256}")
                    self._cleanup(temp_dir)
                    return
            
            # Extract zip to base path
            self.progress.emit(98)
            try:
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.base_path)
            except zipfile.BadZipFile:
                self.error.emit("Invalid or corrupted zip file")
                self._cleanup(temp_dir)
                return
            except Exception as e:
                self.error.emit(f"Extraction error: {str(e)}")
                self._cleanup(temp_dir)
                return
            
            # Cleanup temp files
            self._cleanup(temp_dir)
            
            self.progress.emit(100)
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(f"Update failed: {str(e)}")
    
    def _calculate_sha256(self, filepath: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _cleanup(self, temp_dir: str):
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


class UpdateManager(QObject):
    """Manages launcher and client updates"""
    
    # Signals
    updateAvailable = pyqtSignal(str)      # new_version
    downloadProgress = pyqtSignal(int)     # 0-100
    updateError = pyqtSignal(str)          # error message
    updateFinished = pyqtSignal()          # update completed successfully
    
    def __init__(self, settings_manager=None):
        super().__init__()
        self.settings_manager = settings_manager
        self.last_manifest = None
        self.update_worker = None
        self._network_manager = QNetworkAccessManager()
        
        # Determine base path (where launcher/client lives)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.base_path = os.path.dirname(sys.executable)
        else:
            # Running as script - use parent of native folder
            self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def check_for_updates(self, current_version: str = None) -> None:
        """
        Check for updates by fetching launcher-manifest.json from update_url.
        Emits updateAvailable(version) if a newer version is found.
        
        Args:
            current_version: Current launcher version (reads from settings if not provided)
        """
        if current_version is None:
            if self.settings_manager:
                current_version = self.settings_manager.get('version', '1.0.0')
            else:
                current_version = '1.0.0'
        
        # Get update URL from settings
        update_url = ''
        if self.settings_manager:
            update_url = self.settings_manager.get('update_url', '')
        
        if not update_url:
            print("[UpdateManager] No update_url configured")
            return
        
        # Ensure URL ends with /
        if not update_url.endswith('/'):
            update_url += '/'
        
        manifest_url = f"{update_url}launcher-manifest.json"
        print(f"[UpdateManager] Checking for updates at: {manifest_url}")
        
        # Create network request
        request = QNetworkRequest(QUrl(manifest_url))
        request.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader, "MULauncher/1.0")
        
        reply = self._network_manager.get(request)
        reply.finished.connect(lambda: self._on_manifest_received(reply, current_version))
    
    def _on_manifest_received(self, reply: QNetworkReply, current_version: str):
        """Handle manifest download response"""
        if reply.error() != QNetworkReply.NetworkError.NoError:
            print(f"[UpdateManager] Failed to fetch manifest: {reply.errorString()}")
            reply.deleteLater()
            return
        
        try:
            data = reply.readAll().data().decode('utf-8')
            manifest = json.loads(data)
            
            remote_version = manifest.get('version', '')
            
            if remote_version and self._is_newer_version(remote_version, current_version):
                print(f"[UpdateManager] Update available: {current_version} -> {remote_version}")
                self.last_manifest = manifest
                self.updateAvailable.emit(remote_version)
            else:
                print(f"[UpdateManager] No update needed. Current: {current_version}, Remote: {remote_version}")
                
        except json.JSONDecodeError as e:
            print(f"[UpdateManager] Invalid manifest JSON: {e}")
        except Exception as e:
            print(f"[UpdateManager] Error processing manifest: {e}")
        finally:
            reply.deleteLater()
    
    def _is_newer_version(self, remote: str, current: str) -> bool:
        """Compare version strings (simple semver comparison)"""
        try:
            def parse_version(v: str):
                # Remove leading 'v' if present
                v = v.lstrip('vV')
                parts = v.split('.')
                return tuple(int(p) for p in parts[:3])  # Only compare major.minor.patch
            
            remote_tuple = parse_version(remote)
            current_tuple = parse_version(current)
            
            return remote_tuple > current_tuple
        except (ValueError, AttributeError):
            # If parsing fails, do string comparison
            return remote > current
    
    def download_and_apply_update(self, manifest: dict = None) -> None:
        """
        Download and apply an update from the manifest.
        Uses last_manifest if manifest not provided.
        
        Emits:
            downloadProgress(int): 0-100 during download
            updateFinished(): on successful completion
            updateError(str): on any error
        """
        if manifest is None:
            manifest = self.last_manifest
        
        if not manifest:
            self.updateError.emit("No update manifest available")
            return
        
        if self.update_worker and self.update_worker.isRunning():
            self.updateError.emit("Update already in progress")
            return
        
        # Start update worker thread
        self.update_worker = UpdateWorker(manifest, self.base_path)
        self.update_worker.progress.connect(self.downloadProgress.emit)
        self.update_worker.finished.connect(self._on_update_finished)
        self.update_worker.error.connect(self._on_update_error)
        self.update_worker.start()
    
    def _on_update_finished(self):
        """Handle successful update completion"""
        print("[UpdateManager] Update completed successfully")
        
        # Update version in config if available
        if self.last_manifest and self.settings_manager:
            new_version = self.last_manifest.get('version', '')
            if new_version:
                self.settings_manager.set('version', new_version)
        
        self.updateFinished.emit()
    
    def _on_update_error(self, error_msg: str):
        """Handle update error"""
        print(f"[UpdateManager] Update error: {error_msg}")
        self.updateError.emit(error_msg)
    
    def cancel_update(self):
        """Cancel an in-progress update"""
        if self.update_worker and self.update_worker.isRunning():
            self.update_worker.cancel()
            self.update_worker.wait(5000)  # Wait up to 5 seconds
