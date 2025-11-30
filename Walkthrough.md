# MU Online Launcher - Walkthrough

## Overview

This is a custom MU Online launcher built with a hybrid architecture:

- **Backend Shell**: PyQt6 (Python)
  - Frameless window with custom sidebar (80px fixed width)
  - Native window management and game process control
  - WebChannel bridge for Python ↔ JavaScript communication
  
- **Frontend UI**: React + Vite (TypeScript)
  - Embedded in QWebEngineView
  - Responsive content area supporting multiple resolutions
  - Modern glass-morphism design with tailwind CSS

- **Communication Layer**: 
  - PyQt6 QWebChannel for bidirectional Python ↔ React communication
  - `@pyqtSlot` decorators for Python methods callable from JavaScript
  - `pyqtSignal` for Python → JavaScript events
  - TypeScript bridge service (`web/src/services/bridge.ts`) with typed interfaces

## Project Structure

```
Launcher-Antigravity/
├── native/                        # Python backend
│   ├── launcher_app.py           # Main PyQt6 window
│   ├── launcher_bridge.py        # WebChannel bridge layer
│   ├── game_launcher.py          # Game process management + embedding
│   ├── settings_manager.py       # Config persistence
│   ├── update_manager.py         # Launcher update system
│   ├── event_timer_service.py    # Event scheduling (stubbed)
│   ├── screenshot_service.py     # Screenshot capture (stubbed)
│   ├── anti_cheat.py            # Anti-cheat utilities (stubbed)
│   └── resources/icons/          # Sidebar SVG icons
├── web/                          # React frontend
│   ├── src/
│   │   ├── App.tsx              # Root component with global state
│   │   ├── services/bridge.ts   # TypeScript bridge interface
│   │   ├── pages/               # Main pages (Home, Events, Rankings, etc.)
│   │   ├── components/          # Reusable components
│   │   ├── modals/              # Settings and Exit modals
│   │   ├── hooks/               # Custom hooks (timers, sound)
│   │   └── layout/              # Layout components
│   └── public/
│       ├── notification.wav     # Event notification sound
│       └── background.png       # UI background assets
├── config.json                   # Main configuration
├── session.json                  # Login session state
└── www/CustomLauncher/           # PHP backend APIs (optional)
```

## Completed Features

All features implemented by this project:

### 1. Window Management
- ✅ Frameless window with 80px fixed sidebar
- ✅ Sidebar-only dragging (mouse must be in 0-80px X range)
- ✅ Custom window controls (minimize, maximize, close)
- ✅ Multi-resolution support (9 resolutions from 640x480 to 1920x1080)
- ✅ Window size = 80px sidebar + content resolution

### 2. Settings System
- ✅ Settings modal fully wired to Python `settings_manager.py`
- ✅ Resolution selection persisted to `config.json`
- ✅ Window resizes dynamically when resolution changes
- ✅ Language, sound, music toggles (UI-only, ready for backend)

### 3. Game Launcher
- ✅ START GAME button calls Python `game_launcher.py`
- ✅ Process limit enforcement (default: 3 clients max)
- ✅ Tracks managed PIDs for all launcher-started processes
- ✅ Game launches from same directory as launcher executable
- ✅ Inline error messages for launch failures

### 4. Game Embedding
- ✅ `embed_game_window: true` in `config.json` enables embedding
- ✅ Polls for game window HWND using Win32 APIs (pywin32)
- ✅ Emits `clientWindowFound` signal with HWND
- ✅ Embeds game window into launcher content area via `QWindow.fromWinId`
- ✅ Hides React WebView when game is embedded
- ✅ Resizes embedded window when resolution changes

### 5. Anti-Direct-Launch Protection
- ✅ Background scanner runs every 10 seconds
- ✅ Detects game processes not in `managed_pids` set
- ✅ Emits `unmanagedProcessDetected` signal with PID list
- ✅ Config flag `kill_unmanaged_clients` (default: false)
- ✅ Can terminate unmanaged processes via bridge method

### 6. Update System
- ✅ Full `UpdateManager` implementation
- ✅ Checks for updates on launcher startup
- ✅ Fetches manifest from `{update_url}/launcher-manifest.json`
- ✅ Manifest schema: `{"version": "1.0.1", "zip_url": "...", "sha256": "..."}`
- ✅ Downloads ZIP, verifies SHA256, extracts to launcher directory
- ✅ Progress tracking via `downloadProgress` signal (0-100%)
- ✅ React UI shows update banners and progress

### 7. Bridge Communication
- ✅ All methods have proper `@pyqtSlot` signatures with return types
- ✅ Settings: `getSettings()`, `saveSettings()`, `setResolution()`
- ✅ Game: `launchGame()`, `bringGameToFront()`, `closeGame()`
- ✅ Updates: `checkForUpdates()`, `startUpdate()`, `cancelUpdate()`
- ✅ Process management: `getUnmanagedProcesses()`, `killUnmanagedProcess()`
- ✅ Online count: `getOnlineCount()` (returns mock data, ready for API)

### 8. Event System (Ready for Backend)
- ✅ EventsPage with 4 categories: Events, Invasions, Bosses, Others
- ✅ Mock event data with timers
- ✅ Per-event and global mute toggles
- ✅ Notification sound (`notification.wav`) at 0.75 volume
- ✅ Only plays when: approaching threshold + unmuted + global mute off
- ✅ Bridge subscription `onEventUpdated()` ready for Python service
- ✅ Will automatically switch from mock to real data when Python emits

### 9. UI Pages
- ✅ **HomePage**: Character stats, news feed, START GAME button, update controls
- ✅ **EventsPage**: Event timers, mute controls, notifications
- ✅ **RankingsPage**: Character/guild rankings (mock data, API-ready)
- ✅ **DonatePage**: Donation packages (mock data, API-ready)
- ✅ **GuidesPage**: Game guides placeholder
- ✅ **AdminPage**: Admin controls (requires authentication)

### 10. Notification Sound
- ✅ `notification.wav` in `web/public/`
- ✅ `useEventSound` hook with 0.75 volume
- ✅ Plays when event timer reaches threshold
- ✅ Respects per-event and global mute settings
- ✅ Same sound for all event categories

## Manual Setup Required

### 1. PHP Backend APIs (Optional)

If you want real data instead of mock data, you need to set up these PHP endpoints:

#### Events API (`www/CustomLauncher/api/events.php`)
```php
<?php
// Return JSON array of events
echo json_encode([
    [
        'id' => 'event_1',
        'name' => 'Blood Castle',
        'category' => 'Events',
        'nextOccurrence' => time() + 3600, // Unix timestamp
        'interval' => 3600, // seconds
        'description' => 'Enter the Blood Castle'
    ],
    // ... more events
]);
```

#### Login API (`www/CustomLauncher/api/login.php`)
```php
<?php
// Validate credentials and return session token
$username = $_POST['username'] ?? '';
$password = $_POST['password'] ?? '';

// Validate against your database
// Return JSON response
echo json_encode([
    'success' => true,
    'token' => 'session_token_here',
    'username' => $username,
    'isAdmin' => false
]);
```

#### Rankings API (`www/CustomLauncher/api/rankings.php`)
Create endpoint to return:
```json
{
  "characters": [...],
  "guilds": [...]
}
```

#### Donate Settings (`www/CustomLauncher/donate/get_donate_settings.php`)
Return donation packages configuration.

### 2. Update Server Setup

Host these files on your update server:

#### `launcher-manifest.json`
```json
{
    "version": "1.0.1",
    "zip_url": "https://yourserver.com/updates/launcher-v1.0.1.zip",
    "sha256": "optional_hash_for_verification"
}
```

Place at: `{update_url}/launcher-manifest.json` (update_url from config.json)

#### Update ZIP
- Create ZIP containing updated launcher files
- Must extract to same directory structure
- Can overwrite: Python files, React dist/, config changes, etc.

### 3. Event Timer Service

Wire `native/event_timer_service.py` to emit real events:

```python
# In EventTimerService.start()
def _emit_test_event(self):
    event_data = {
        'id': 'event_123',
        'name': 'Blood Castle',
        'category': 'Events',
        'nextOccurrence': int(time.time()) + 300,
        'interval': 3600,
        'description': 'Event starting soon!'
    }
    self.eventUpdated.emit(json.dumps(event_data))
```

### 4. Game Client Setup

- Place `main.exe` (your MU client) in the same directory as the launcher
- Or configure `game_executable` path in `config.json`
- Ensure that `embed_game_window` is set correctly for your needs

### 5. Configuration Flags

Edit `config.json` as needed:

```json
{
    "embed_game_window": true,        // false for external window
    "kill_unmanaged_clients": false,  // true to auto-kill direct launches
    "processLimit": 3,                // max simultaneous clients
    "update_url": "http://...",       // your update server
    "api_url": "http://...",          // your PHP API base URL
}
```

## Testing Guide

### Step 1: Start Development Environment

Terminal 1 - React dev server:
```bash
cd web
npm install
npm run dev
```
This starts the React app at `http://localhost:5175`

Terminal 2 - Python launcher:
```bash
cd native
pip install -r requirements.txt
python main.py
```

### Step 2: Test Settings & Resolution

1. Click the Settings icon (gear) in sidebar
2. Change resolution from dropdown
3. Click "Save Settings"
4. Window should resize to: 80px + new content width
5. Check `config.json` - resolution should be updated
6. Restart launcher - should load with saved resolution

### Step 3: Test Game Launch

1. Place a dummy `main.exe` in launcher directory (or configure path)
2. Click "START GAME" button on HomePage
3. Should show "Game launched successfully"
4. Try clicking again - should fail if process limit reached
5. Check console for PID tracking logs

### Step 4: Test Game Embedding

1. Set `"embed_game_window": true` in config.json
2. Restart launcher
3. Click "START GAME"
4. Watch console for HWND polling messages
5. If game window found:
   - React WebView should hide
   - Game should appear embedded in content area
   - Should resize with resolution changes

### Step 5: Test Unmanaged Process Detection

1. Manually launch `main.exe` outside the launcher
2. Wait 10 seconds for scanner
3. Check console for "Unmanaged process detected" log
4. If `kill_unmanaged_clients: true` - process should be terminated

### Step 6: Test Update System

1. Host a test manifest at your `update_url`:
   ```json
   {
       "version": "1.0.1",
       "zip_url": "https://yourserver.com/test.zip",
       "sha256": "optional"
   }
   ```
2. Set current version to "1.0.0" in config.json
3. Restart launcher
4. Should show "Update Available" banner
5. Click "UPDATE LAUNCHER"
6. Watch progress bar during download
7. Check for update success/error banners

### Step 7: Test Dragging

1. Click and drag inside sidebar (0-80px X range) - should move window
2. Try dragging from content area - should NOT move window
3. Verify sidebar-only restriction is enforced

### Step 8: Test Event Notifications

1. Go to Events page
2. Unmute an event category
3. Wait for an event timer to approach threshold (< 5 min)
4. Should hear `notification.wav` sound
5. Mute the event - sound should stop for that event
6. Test "Mute All" - should silence all events

### Step 9: Test All Pages

Navigate through sidebar:
- Home - character stats, news, game launch
- Events - timers and notifications
- Rankings - character/guild lists
- Guides - documentation placeholder
- Donate - donation packages
- Admin - locked unless authenticated

Verify no console errors on any page.

## Future TODO

### Features Not Yet Implemented

1. **Authentication System**
   - Real login API integration
   - Session management beyond mock
   - Admin role verification

2. **Real API Integration**
   - Wire Rankings page to database API
   - Wire Donate page to payment gateway
   - Wire online count to server query
   
3. **Event Timer Service**
   - Connect to game server event schedule
   - Real-time event updates from database
   - Event participation tracking

4. **Screenshot Service**
   - Implement actual screenshot capture
   - Save to configured directory
   - Optional upload to server

5. **Anti-Cheat System**
   - Flesh out anti_cheat.py
   - Process integrity checks
   - File validation

6. **News System**
   - Backend API for news feed
   - Admin panel for news management
   - Rich text formatting

7. **Guides System**
   - Markdown or HTML guide content
   - Category organization
   - Search functionality

8. **Localization**
   - Full language file system
   - Support for multiple languages beyond English
   - Dynamic UI text replacement

9. **Analytics**
   - User activity tracking
   - Error reporting
   - Usage statistics

10. **Auto-Launch Features**
    - Launch game on launcher start
    - Remember window position
    - Auto-login option

## Troubleshooting

### Launcher won't start
- Check Python version (requires 3.8+)
- Install all requirements: `pip install -r native/requirements.txt`
- Check for port conflicts (React dev server on 5175)

### Game won't embed
- Verify pywin32 is installed: `pip install pywin32`
- Check game window has a title bar initially
- Try setting `embed_game_window: false` for external window mode

### Updates fail
- Verify update URL is accessible
- Check manifest JSON format
- Ensure launcher has write permissions
- Check SHA256 if provided

### No sound on events
- Verify `notification.wav` exists in `web/public/`
- Check browser audio permissions
- Unmute both the specific event and global mute

### Resolution not saving
- Check `config.json` write permissions
- Verify resolution is in supported list
- Check console for bridge errors

## Development Notes

- **React Hot Reload**: Enabled via Vite dev server
- **Python Changes**: Require launcher restart
- **Bridge Changes**: Require both Python restart AND React reload
- **CSS Changes**: Hot reload automatically

## Build for Production

### Build React:
```bash
cd web
npm run build
```

Creates optimized bundle in `web/dist/`

### Package Python:
Use PyInstaller to create standalone executable:
```bash
pyinstaller --onefile --windowed native/main.py
```

Update `launcher_app.py` to load from `dist/` instead of localhost:5175.

---

**End of Walkthrough**

For additional help, see FEATURES.md for feature status or contact the development team.
