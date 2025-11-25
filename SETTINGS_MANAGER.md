# Settings Manager - Enhanced Implementation

## Overview

The `SettingsManager` class has been enhanced to support comprehensive configuration management, including Windows Registry file generation for MU Online resolution settings.

**File:** `native/settings_manager.py`

## Supported Fields

The settings manager now supports the following configuration fields:

### Core Settings
- `language` (str): Language code (default: "en")
- `resolution` (str): Screen resolution in "WIDTHxHEIGHT" format (default: "1920x1080")
- `muteInactiveTabs` (bool): Mute audio when launcher is inactive (default: false)
- `embedGameWindow` (bool): Embed game window inside launcher (default: false)
- `processLimit` (int): Maximum simultaneous game clients (default: 3)

### Game Settings
- `game_executable` (str): Path to main.exe (default: "main.exe")
- `window_mode` (bool): Run game in windowed mode (default: true)
- `sound` (bool): Enable sound (default: true)
- `music` (bool): Enable music (default: true)

### Server Settings
- `server_name` (str): Server display name
- `version` (str): Launcher version
- `update_url` (str): Update server URL
- `api_url` (str): API endpoint URL

## Methods

### Core Methods

#### `load()` / `load_settings()`
Load settings from `config.json`. Merges with default settings to ensure all keys exist.

```python
settings = manager.load()
```

**Returns:** `dict` - Settings dictionary

---

#### `save(settings)` / `save_settings(settings)`
Save settings to `config.json`.

```python
success = manager.save({"resolution": "1920x1080", "processLimit": 5})
```

**Parameters:**
- `settings` (dict): Settings to save

**Returns:** `bool` - Success status

---

#### `get(key, default=None)`
Get a specific setting value.

```python
resolution = manager.get("resolution", "1920x1080")
```

**Parameters:**
- `key` (str): Setting key
- `default` (any): Default value if key doesn't exist

**Returns:** Setting value or default

---

#### `set(key, value)`
Set a specific setting value and save.

```python
manager.set("processLimit", 5)
```

**Parameters:**
- `key` (str): Setting key
- `value` (any): Setting value

**Returns:** `bool` - Success status

---

### Registry Methods

#### `generate_reg(width, height)`
Generate a Windows Registry file (.reg) for MU Online resolution settings.

```python
reg_path = manager.generate_reg(1920, 1080)
```

**Parameters:**
- `width` (int): Screen width in pixels
- `height` (int): Screen height in pixels

**Returns:** `str` - Path to generated .reg file, or `None` on error

**Registry Path:** `HKEY_CURRENT_USER\Software\Webzen\Mu\Config`

**Registry Keys:**
- `Width` (DWORD): Screen width
- `Height` (DWORD): Screen height
- `ColorDepth` (DWORD): Color depth (32-bit)
- `Windowed` (DWORD): Windowed mode (0 = fullscreen)

**Output Location:** `/reg_files/mu_resolution_{width}x{height}.reg`

---

#### `applyResolution()`
Apply the current resolution setting by generating a .reg file.

```python
success, reg_path = manager.applyResolution()
if success:
    print(f"Registry file created: {reg_path}")
```

**Returns:** `tuple(bool, str)` - (success status, registry file path)

**Note:** This method generates the .reg file but does NOT automatically apply it to the registry. To auto-apply, uncomment the lines in the method or use `apply_registry_file()`.

---

#### `apply_registry_file(reg_file_path)`
Apply a registry file using Windows `reg import` command.

```python
success = manager.apply_registry_file(reg_path)
```

**Parameters:**
- `reg_file_path` (str): Path to the .reg file

**Returns:** `bool` - Success status

**Note:** Requires administrator privileges on some systems.

---

## Usage Examples

### Basic Configuration

```python
from settings_manager import SettingsManager

# Initialize
manager = SettingsManager()

# Load settings
settings = manager.load()
print(f"Current resolution: {settings['resolution']}")

# Update settings
manager.save({
    "resolution": "2560x1440",
    "processLimit": 5,
    "muteInactiveTabs": True
})

# Get specific value
limit = manager.get("processLimit", 3)
```

### Resolution Management

```python
# Set resolution
manager.set("resolution", "1920x1080")

# Generate and apply registry file
success, reg_path = manager.applyResolution()

if success:
    print(f"Registry file created: {reg_path}")
    
    # Optionally apply to registry
    if manager.apply_registry_file(reg_path):
        print("Resolution applied to registry!")
```

### Custom Registry Generation

```python
# Generate registry file for specific resolution
reg_path = manager.generate_reg(2560, 1440)

if reg_path:
    print(f"Registry file: {reg_path}")
    # User can manually double-click the .reg file to apply
```

## File Structure

```
/
├── config.json              # Main configuration file
├── reg_files/               # Generated registry files
│   ├── mu_resolution_1920x1080.reg
│   ├── mu_resolution_2560x1440.reg
│   └── ...
└── native/
    └── settings_manager.py  # Settings manager implementation
```

## Integration with WebChannel Bridge

The settings manager is automatically integrated with the WebChannel bridge:

```python
# In launcher_bridge.py
@pyqtSlot(result=str)
def getSettings(self):
    if self.settings_manager:
        settings = self.settings_manager.load()
        return json.dumps(settings)
    return "{}"

@pyqtSlot(str, result=bool)
def saveSettings(self, settings_json):
    if self.settings_manager:
        settings = json.loads(settings_json)
        return self.settings_manager.save(settings)
    return False
```

## Status: ✅ COMPLETE

All requested features have been implemented:
- ✅ `load()` and `save()` methods
- ✅ Support for all requested fields
- ✅ `applyResolution()` method
- ✅ `generate_reg(width, height)` helper
- ✅ Windows Registry file generation
- ✅ Backward compatibility with existing code
