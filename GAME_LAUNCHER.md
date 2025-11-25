# Game Launcher - Enhanced Implementation

## Overview

The `GameLauncher` class has been enhanced with advanced features including QProcess-based launching, Win32 window embedding, and comprehensive game process management.

**File:** `native/game_launcher.py`

## Features

### Window Embedding
- Embeds the game window directly into the launcher UI using Win32 APIs
- Controlled by `embedGameWindow` setting
- Removes window decorations and fits the game seamlessly into the launcher

### Process Management
- Tracks all launched game instances
- Enforces process limits (`processLimit` setting)
- Supports graceful termination and forced kill

### Window Control
- Bring game window to front
- Close game processes
- Find windows by process name

## Dependencies

```python
from PyQt6.QtCore import QProcess, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import win32gui, win32con, win32process  # pywin32 package
```

**Note:** Window embedding requires `pywin32` package. If not available, the launcher falls back to normal mode.

## Constructor

```python
GameLauncher(settings_manager, parent_widget=None)
```

**Parameters:**
- `settings_manager` (SettingsManager): Settings manager instance
- `parent_widget` (QWidget, optional): Parent widget for embedding game window

## Methods

### `launch(config=None)`

Launch the game with optional configuration override.

```python
success, message = launcher.launch()
```

**Parameters:**
- `config` (dict, optional): Configuration override (not currently used)

**Returns:** `tuple(bool, str)` - (success status, message)

**Behavior:**
- Checks process limit before launching
- Verifies game executable exists
- If `embedGameWindow` is `True` and Win32 APIs are available:
  - Launches via QProcess
  - Finds the game window by PID
  - Embeds it into the parent widget
- Otherwise:
  - Launches normally via subprocess.Popen

**Settings Used:**
- `game_executable`: Path to main.exe
- `processLimit`: Maximum simultaneous clients
- `embedGameWindow`: Enable window embedding

---

### `bring_to_front()`

Bring the game window to the foreground.

```python
success = launcher.bring_to_front()
```

**Returns:** `bool` - Success status

**Behavior:**
- If embedded window exists, brings it to front
- Otherwise, searches for game window by process name
- Uses Win32 `SetForegroundWindow` and `ShowWindow` APIs

---

### `close_game()`

Close all tracked game processes.

```python
success = launcher.close_game()
```

**Returns:** `bool` - Success status

**Behavior:**
- Terminates embedded QProcess if exists
- Terminates all tracked subprocess.Popen processes
- Waits 3 seconds for graceful termination
- Forces kill if process doesn't terminate
- Cleans up internal state

---

### `count_running_instances(process_name)`

Count how many instances of a process are running.

```python
count = launcher.count_running_instances("main.exe")
```

**Parameters:**
- `process_name` (str): Process name to count

**Returns:** `int` - Number of running instances

---

### `get_running_processes()`

Get list of all running game processes.

```python
processes = launcher.get_running_processes()
```

**Returns:** `list[dict]` - List of process info dictionaries

**Process Info:**
```python
{
    'pid': 1234,
    'name': 'main.exe',
    'create_time': 1234567890.0
}
```

---

## Internal Methods

### `_launch_normal(game_path)`

Launch game normally without embedding.

**Returns:** `tuple(bool, str)` - (success, message)

---

### `_launch_embedded(game_path)`

Launch game with window embedding.

**Process:**
1. Create QProcess
2. Start game executable
3. Get process ID
4. Schedule window finding after 1 second delay

**Returns:** `tuple(bool, str)` - (success, message)

---

### `_find_and_embed_window(pid)`

Find the game window by process ID and embed it.

**Process:**
1. Enumerate all windows
2. Find windows belonging to the PID
3. Embed the first visible window
4. Retry after 500ms if not found

---

### `_embed_window(hwnd)`

Embed a window into the parent widget.

**Process:**
1. Create container widget if needed
2. Set game window as child of container
3. Remove window decorations (caption, thick frame)
4. Resize to fit container
5. Show the window

**Win32 APIs Used:**
- `SetParent`: Make game window a child
- `GetWindowLong` / `SetWindowLong`: Modify window style
- `MoveWindow`: Resize and position
- `ShowWindow`: Display the window

---

### `_find_window_by_process_name(process_name)`

Find a window handle by process name.

**Returns:** `int` - Window handle (HWND) or `None`

---

## Usage Examples

### Basic Launch

```python
from game_launcher import GameLauncher
from settings_manager import SettingsManager

settings = SettingsManager()
launcher = GameLauncher(settings)

# Launch game
success, message = launcher.launch()
if success:
    print(f"Game launched: {message}")
else:
    print(f"Launch failed: {message}")
```

### Launch with Embedding

```python
from PyQt6.QtWidgets import QWidget

# Create parent widget
parent = QWidget()

# Enable embedding in settings
settings.set("embedGameWindow", True)

# Create launcher with parent
launcher = GameLauncher(settings, parent)

# Launch (will embed into parent widget)
success, message = launcher.launch()
```

### Process Management

```python
# Get running processes
processes = launcher.get_running_processes()
print(f"Running instances: {len(processes)}")

# Bring to front
launcher.bring_to_front()

# Close all game instances
launcher.close_game()
```

### Check Process Limit

```python
# Count instances
count = launcher.count_running_instances("main.exe")
limit = settings.get("processLimit", 3)

if count >= limit:
    print(f"Cannot launch: {count}/{limit} instances running")
```

## Integration with WebChannel Bridge

The game launcher is integrated with the WebChannel bridge:

```python
# In launcher_bridge.py
@pyqtSlot(str, result=str)
def startGame(self, config_json):
    if self.game_launcher:
        success, message = self.game_launcher.launch()
        self.gameLaunched.emit(success)
        return json.dumps({"success": success, "message": message})
    return json.dumps({"success": False, "message": "Launcher not initialized"})
```

## Window Embedding Flow

```
1. User clicks "Start Game" in React UI
2. JavaScript calls bridge.startGame()
3. Python GameLauncher.launch() is called
4. If embedGameWindow is True:
   a. QProcess starts main.exe
   b. Get process ID
   c. Wait 1 second for window to appear
   d. Find window by PID
   e. Set window as child of parent widget
   f. Remove decorations
   g. Resize to fit
   h. Show embedded window
5. If embedGameWindow is False:
   a. subprocess.Popen starts main.exe
   b. Game runs in separate window
```

## Error Handling

- **pywin32 not available**: Falls back to normal launch mode
- **No parent widget**: Cannot embed, uses normal launch
- **Process limit reached**: Returns error without launching
- **Executable not found**: Returns error with file path
- **Process start failed**: Returns error message
- **Window not found**: Retries with exponential backoff

## Status: ✅ COMPLETE

All requested features have been implemented:
- ✅ `launch(config)` with embedding support
- ✅ `bring_to_front()` method
- ✅ `close_game()` method
- ✅ QProcess integration
- ✅ Win32 window embedding
- ✅ Process tracking and management
