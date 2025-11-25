import json
import os
import subprocess

class SettingsManager:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
        self.settings = self.load()
    
    def get_default_settings(self):
        """Return default settings structure"""
        return {
            "language": "en",
            "resolution": "1920x1080",
            "muteInactiveTabs": False,
            "embedGameWindow": False,
            "processLimit": 3,
            "game_executable": "main.exe",
            "window_mode": True,
            "sound": True,
            "music": True,
            "server_name": "MU Online Custom Server",
            "version": "1.0.0",
            "update_url": "http://localhost/update/",
            "api_url": "http://localhost/CustomLauncher/api/"
        }

    def load(self):
        """Load settings from config.json"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    defaults = self.get_default_settings()
                    defaults.update(loaded)
                    return defaults
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.get_default_settings()
        return self.get_default_settings()

    def load_settings(self):
        """Alias for load() for backward compatibility"""
        return self.load()

    def save(self, settings):
        """Save settings to config.json"""
        self.settings.update(settings)
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def save_settings(self, settings):
        """Alias for save() for backward compatibility"""
        return self.save(settings)

    def get(self, key, default=None):
        """Get a specific setting value"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a specific setting value"""
        self.settings[key] = value
        return self.save(self.settings)

    def generate_reg(self, width, height):
        """
        Generate a Windows Registry file (.reg) for MU Online resolution settings
        
        Args:
            width (int): Screen width
            height (int): Screen height
            
        Returns:
            str: Path to the generated .reg file
        """
        reg_content = f"""Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\\Software\\Webzen\\Mu\\Config]
"Width"=dword:{width:08x}
"Height"=dword:{height:08x}
"ColorDepth"=dword:00000020
"Windowed"=dword:00000000
"""
        
        # Create reg files directory if it doesn't exist
        reg_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reg_files")
        if not os.path.exists(reg_dir):
            os.makedirs(reg_dir)
        
        reg_file_path = os.path.join(reg_dir, f"mu_resolution_{width}x{height}.reg")
        
        try:
            with open(reg_file_path, 'w', encoding='utf-16le') as f:
                # Write BOM for UTF-16 LE
                f.write('\ufeff')
                f.write(reg_content)
            print(f"Registry file created: {reg_file_path}")
            return reg_file_path
        except Exception as e:
            print(f"Error creating registry file: {e}")
            return None

    def applyResolution(self):
        """
        Apply the current resolution setting by generating and optionally applying a .reg file
        
        Returns:
            tuple: (success: bool, reg_file_path: str)
        """
        resolution = self.get("resolution", "1920x1080")
        
        try:
            # Parse resolution string (e.g., "1920x1080")
            width, height = map(int, resolution.split('x'))
            
            # Generate the registry file
            reg_file_path = self.generate_reg(width, height)
            
            if reg_file_path:
                # Optionally auto-apply the registry file
                # Uncomment the following lines to automatically apply:
                # subprocess.run(['reg', 'import', reg_file_path], check=True)
                # print(f"Registry settings applied for {width}x{height}")
                
                return True, reg_file_path
            else:
                return False, None
                
        except ValueError as e:
            print(f"Invalid resolution format: {resolution}. Expected format: WIDTHxHEIGHT")
            return False, None
        except Exception as e:
            print(f"Error applying resolution: {e}")
            return False, None

    def apply_registry_file(self, reg_file_path):
        """
        Apply a registry file using Windows reg command
        
        Args:
            reg_file_path (str): Path to the .reg file
            
        Returns:
            bool: Success status
        """
        try:
            result = subprocess.run(['reg', 'import', reg_file_path], 
                                  capture_output=True, 
                                  text=True, 
                                  check=True)
            print(f"Registry file applied successfully: {reg_file_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error applying registry file: {e.stderr}")
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False

