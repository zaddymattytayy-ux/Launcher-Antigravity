# Launcher Feature Map

## 1. Overview

The MU Online Launcher is a desktop application built with:
- **PyQt6 shell** – frameless window with rounded corners, 80px fixed-width sidebar (Qt-rendered), and a web content area
- **React/Vite frontend** – single-page app rendered in a QWebEngineView
- **Python ↔ JS communication** via Qt WebChannel (`launcherBridge` object)

### Architecture Summary
```
┌─────────────────────────────────────────────────────────────┐
│                     LauncherApp (PyQt6)                     │
│  ┌──────────┬────────────────────────────────────────────┐  │
│  │ Qt       │                                            │  │
│  │ Sidebar  │    QWebEngineView (React/Vite frontend)    │  │
│  │ (80px)   │         Content area (resizable)           │  │
│  │          │                                            │  │
│  └──────────┴────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Supported Content Resolutions
Sidebar is always 80px; these are content-area dimensions:
- 640×480, 800×600, 1024×768, 1280×1024, 1366×768, 1440×900, 1600×900, 1680×1050, 1920×1080

Default: **1366×768** (total window: 1446×768)

---

## 2. Implemented Features (Python / Qt side)

### 2.1 Window / Shell Behavior

| Feature | Status | Details | File Reference |
|---------|--------|---------|----------------|
| Frameless window | ✅ Implemented | `Qt.WindowType.FramelessWindowHint` | `native/launcher_app.py:27-30` |
| Translucent background | ✅ Implemented | `WA_TranslucentBackground` attribute | `native/launcher_app.py:31` |
| Rounded corners (24px) | ✅ Implemented | CSS `border-radius: 24px` on `#RootFrame` and `#Sidebar` | `native/launcher_app.py:162-180` |
| Single instance (mutex) | ✅ Implemented | `QSharedMemory` named "MUOnlineLauncherInstance" | `native/main.py:18-22` |
| High-DPI scaling disabled | ✅ Implemented | Environment variables set before QApplication | `native/main.py:8-10` |
| Window dragging (sidebar) | ✅ Implemented | `mousePressEvent/Move/Release` check `_in_sidebar()` | `native/launcher_app.py:257-275` |
| Resolution change | ✅ Implemented | `set_resolution(width, height)` resizes window + webview | `native/launcher_app.py:232-247` |

### 2.2 Qt Sidebar (Native)

| Feature | Status | Details | File Reference |
|---------|--------|---------|----------------|
| Fixed 80px width | ✅ Implemented | `setFixedWidth(SIDEBAR_WIDTH)` | `native/launcher_app.py:51` |
| Logo button (diamond icon) | ✅ Implemented | 52×52 button with gradient background | `native/launcher_app.py:67-73` |
| Navigation buttons | ✅ Implemented | Home, Rankings, Guides, Events, Donate | `native/launcher_app.py:76-118` |
| Exit button | ✅ Implemented | Closes launcher via `self.close()` | `native/launcher_app.py:114-117` |
| Button group (exclusive selection) | ✅ Implemented | `QButtonGroup` for mutual exclusivity | `native/launcher_app.py:199-206` |
| Active icon colorization | ✅ Implemented | `QGraphicsColorizeEffect` with purple (#7B4DFB) | `native/launcher_app.py:224-231` |
| Navigation to React views | ✅ Implemented | Calls `window.navigateTo(view)` via JS | `native/launcher_app.py:134-142` |

### 2.3 Services (Python)

| Service | Status | Details | File Reference |
|---------|--------|---------|----------------|
| SettingsManager | ✅ Implemented | Load/save JSON config, generate registry files for MU resolution | `native/settings_manager.py` |
| GameLauncher | ✅ Implemented | Launch main.exe, process limit, optional window embedding (win32) | `native/game_launcher.py` |
| ScreenshotService | ✅ Implemented | Capture game window to PNG (uses win32gui) | `native/screenshot_service.py` |
| EventTimerService | ✅ Implemented | Background thread fetches events, calculates countdowns, emits signals | `native/event_timer_service.py` |
| UpdateManager | ⚠️ Stub only | Methods exist but have no implementation | `native/update_manager.py` |
| AntiCheat | ⚠️ Stub only | `get_hwid()` returns placeholder, `scan_processes()` is empty | `native/anti_cheat.py` |
| ErrorLogger | ✅ Implemented | Sets up file + console logging | `native/error_logger.py` |

### 2.4 Configuration Persistence

| Item | Status | Location | Details |
|------|--------|----------|---------|
| Main settings | ✅ Implemented | `config.json` (repo root) | resolution, language, sound, music, api_url, etc. |
| Session data | ✅ Implemented | `native/session.json` | logged, username, is_admin |
| Registry generation | ✅ Implemented | `reg_files/` folder | MU Online resolution registry files |

---

## 3. Implemented Features (React / Web side)

### 3.1 Layout / Pages

| Page | Status | Details |
|------|--------|---------|
| **HomePage** | ✅ Implemented | Hero section, START GAME button, Settings button, Admin button (conditional), 3 glass panels (News, Changelogs, Events) |
| **EventsPage** | ✅ Implemented | Category tabs (Events/Invasions/Bosses/Others), event list with countdowns, per-event mute toggles, Mute All button, event details panel |
| **RankingsPage** | ⚠️ UI only | Category tabs, class filter, search input, rankings table with mock data (no backend fetch) |
| **GuidesPage** | ⚠️ UI only | Category pills, topic list with pagination, guide content panel (all static/mock) |
| **DonatePage** | ⚠️ Stub only | Placeholder text only, no integration with donate PHP endpoints |
| **AdminPage** | ⚠️ UI only | Quick stats cards, admin action buttons (all non-functional) |

### 3.2 Components

| Component | Status | Details | File Reference |
|-----------|--------|---------|----------------|
| **StatusHeader** | ⚠️ Partially wired | Displays online count (hardcoded to 1/500), download progress bar (mock state) | `web/src/components/layout/StatusHeader.tsx` |
| **BackgroundShell** | ✅ Implemented | Wrapper with background image | `web/src/components/layout/BackgroundShell.tsx` |
| **GlassCard** | ✅ Implemented | Reusable glass-morphism card | `web/src/components/GlassCard.tsx` |
| **Sidebar (React)** | ⚠️ Dead code | Exists but NOT used – Qt sidebar is rendered instead | `web/src/layout/Sidebar.tsx` |
| **TopBar** | ⚠️ Dead code | Exists but NOT used in current App.tsx | `web/src/layout/TopBar.tsx` |
| **MainLayout** | ⚠️ Dead code | Generic layout wrapper, not currently used | `web/src/layout/MainLayout.tsx` |
| **SettingsModal** | ⚠️ UI only | Resolution dropdown, music/SFX toggles, language selector – no bridge calls to save | `web/src/modals/SettingsModal.tsx` |
| **ExitModal** | ✅ Implemented (UI) | Confirmation dialog, but exit action is stub (just closes modal) | `web/src/modals/ExitModal.tsx` |

### 3.3 Navigation

| Feature | Status | Details |
|---------|--------|---------|
| Page switching | ✅ Implemented | `window.navigateTo(view)` called from Qt sidebar, sets React state | `web/src/App.tsx:13-16` |
| React Router | ❌ Not used | Navigation is via simple state (`currentView`) |

### 3.4 Event System (React side)

| Feature | Status | Details | File Reference |
|---------|--------|---------|----------------|
| Event timer countdown | ✅ Implemented | `useEventTimers` hook calculates remaining time, updates every second | `web/src/hooks/useEventTimers.ts` |
| Per-event mute toggle | ✅ Implemented | UI + localStorage persistence (`launcher_event_mutes`) | `web/src/pages/EventsPage.tsx:73-88` |
| Mute All / Unmute All | ✅ Implemented | Toggles all events in current category | `web/src/pages/EventsPage.tsx:108-117` |
| Sound notification | ✅ Implemented | `useEventSound` plays audio 60 seconds before event | `web/src/hooks/useEventSound.ts` |
| Event data source | ⚠️ Mock data | Hardcoded in EventsPage, NOT fetched from Python/PHP | `web/src/pages/EventsPage.tsx:17-65` |

---

## 4. Python ↔ React Bridge

### 4.1 Bridge Methods Exposed to JavaScript

| Method | Python Implementation | JS Usage | Status |
|--------|----------------------|----------|--------|
| `getSettings()` | Returns `settings_manager.load_settings()` as JSON | `bridge.getSettings()` | ✅ Wired |
| `saveSettings(settings_json)` | Calls `settings_manager.save_settings()` | Not used in React | ⚠️ Available but unused |
| `startGame(config_json)` | Calls `game_launcher.launch()` | `bridge.launchGame()` | ✅ Wired |
| `getSession()` | Reads `session.json` | `bridge.getSession()` | ✅ Wired (returns mock in browser) |
| `getOnlineCount()` | Returns stub value `1` | Not used | ⚠️ Available but unused |
| `requestScreenshot()` | Captures game window via ScreenshotService | Not used in React | ⚠️ Available but unused |
| `getEvents()` | Returns mock JSON (3 events) | Not used | ⚠️ Dead code – React uses own mock |
| `launchGame(resolution, windowMode)` | Legacy wrapper for startGame | Used by TopBar (dead code) | ⚠️ Legacy |
| `startDrag()` | Should call window drag, but `start_drag_from_sidebar` doesn't exist | Called from React Sidebar | ❌ Broken (method missing) |

**File references:** `native/launcher_bridge.py`, `web/src/services/bridge.ts`

### 4.2 Signals (Python → JavaScript)

| Signal | Emission Source | JS Connection | Status |
|--------|-----------------|---------------|--------|
| `updateAvailable(str)` | Not emitted anywhere | Not connected | ⚠️ Declared but unused |
| `downloadProgress(int)` | Not emitted anywhere | Not connected | ⚠️ Declared but unused |
| `gameLaunched(bool)` | Emitted in `startGame()` | Not connected | ⚠️ Available but unused |
| `eventUpdated(str)` | Forwarded from EventTimerService | `bridge.onEventUpdated()` | ⚠️ Wired but React ignores it |
| `eventNotification(str, int)` | Forwarded from EventTimerService | Not connected | ⚠️ Available but unused |

### 4.3 Data Structures

**Settings (config.json)**
```json
{
    "language": "en",
    "resolution": "1920x1080",
    "game_executable": "main.exe",
    "window_mode": true,
    "sound": true,
    "music": true,
    "server_name": "MU Online Custom Server",
    "version": "1.0.0",
    "update_url": "http://localhost/update/",
    "api_url": "http://localhost/CustomLauncher/api/"
}
```

**Session (session.json)**
```json
{
    "logged": true,
    "username": "Admin",
    "is_admin": true
}
```

---

## 5. External Endpoints & Paths

### 5.1 PHP Endpoints (in `www/CustomLauncher/`)

| Endpoint | Purpose | Used By | Status |
|----------|---------|---------|--------|
| `/CustomLauncher/api/events.php` | Returns event schedule JSON | `event_timer_service.py` | ✅ Wired (Python fetches) |
| `/CustomLauncher/api/login.php` | Stub login (admin/admin) | Not used | ⚠️ Defined but unused |
| `/CustomLauncher/export_characters.php` | Returns stub character data | Not used | ⚠️ Defined but unused |
| `/CustomLauncher/donate/get_donate_settings.php` | Returns donation config | Not used | ⚠️ Defined but unused |
| `/CustomLauncher/donate/config.php` | PayPal/Stripe config + packages | Included by above | ⚠️ Defined but unused |

### 5.2 Referenced URLs (from config.json)

| Config Key | Default Value | Used By | Status |
|------------|---------------|---------|--------|
| `api_url` | `http://localhost/CustomLauncher/api/` | EventTimerService | ✅ Used |
| `update_url` | `http://localhost/update/` | UpdateManager (stub) | ⚠️ Referenced but not implemented |

### 5.3 Local Paths

| Path | Purpose | Status |
|------|---------|--------|
| `config.json` | Main settings persistence | ✅ Used |
| `native/session.json` | Session/login state | ✅ Used |
| `screenshots/` | Screenshot output folder | ✅ Used |
| `native/logs/` | Error logs | ✅ Used |
| `reg_files/` | Generated MU registry files | ✅ Created on demand |
| `main.exe` | MU client executable (expected in same folder as launcher) | ✅ Configured |

---

## 6. Known Gaps / TODOs

### 6.1 Logic Missing Behind Existing UI

| UI Element | Gap | Details |
|------------|-----|---------|
| **Settings Modal Save** | No bridge call | Resolution, music, SFX, language changes don't call Python | `SettingsModal.tsx` |
| **Online Players count** | Hardcoded | Shows "1/500", no real backend fetch | `StatusHeader.tsx`, `HomePage.tsx`, `EventsPage.tsx` |
| **Download Progress** | Mock state | `launcherUpdateState` is hardcoded to 'downloading' at 90% | `App.tsx:12` |
| **Rankings data** | All mock | No API fetch, table shows placeholder Player1-7 | `RankingsPage.tsx` |
| **Guides content** | All static | No backend, welcome text is hardcoded | `GuidesPage.tsx` |
| **Donate page** | Stub only | Empty page, PHP endpoints exist but unused | `DonatePage.tsx` |
| **Admin page** | UI only | All buttons non-functional, stats hardcoded | `AdminPage.tsx` |
| **Exit Modal confirm** | Stub | Logs to console, doesn't actually close launcher | `App.tsx:22-25` |
| **News/Changelog panels** | Mock data | Hardcoded items, pagination does nothing useful | `HomePage.tsx` |
| **Events on HomePage** | Mock data | Different from EventsPage, not synced | `HomePage.tsx` |

### 6.2 Broken or Incomplete Wiring

| Feature | Issue | Details |
|---------|-------|---------|
| `startDrag()` bridge | **Method missing** | Calls `window.start_drag_from_sidebar()` which doesn't exist | `launcher_bridge.py:101-105` |
| React Sidebar | **Dead code** | Exists (`layout/Sidebar.tsx`) but App.tsx doesn't use it – Qt sidebar handles navigation |
| React TopBar | **Dead code** | Exists (`layout/TopBar.tsx`) but not imported/used |
| `bridge.onEventUpdated()` | **Unused by React** | EventsPage uses its own mock data, ignores Python events |
| `getEvents()` bridge method | **Dead code** | Returns mock data but React never calls it |

### 6.3 Missing Features (Planned for Future)

| Feature | Current State | Notes |
|---------|---------------|-------|
| **Prevent direct main.exe launch** | Not implemented | No check if user runs main.exe outside launcher |
| **Auto-update pipeline** | Stub only | UpdateManager has empty methods |
| **MD5/hash verification** | Not implemented | No file integrity checks |
| **Download from remote hosting** | Not implemented | update_url configured but not used |
| **File patching/overwrite** | Not implemented | — |
| **Login system** | Stub PHP only | No React integration |
| **Character export** | Stub PHP only | Endpoint exists, not wired |
| **Donation processing** | Config only | PayPal/Stripe keys in PHP, no UI |

---

## 7. Notes for Future Implementation

### 7.1 Design Constraints (Inferred from Code)

1. **Sidebar must remain exactly 80px** regardless of resolution (`SIDEBAR_WIDTH` constant)
2. **Window size = 80px + content width × content height**
3. **Supported content resolutions:** 640×480, 800×600, 1024×768, 1280×1024, 1366×768, 1440×900, 1600×900, 1680×1050, 1920×1080
4. **Dragging should start from Qt sidebar only** (React sidebar is dead code, Qt handles it)
5. **Single instance enforced** via QSharedMemory

### 7.2 Data Flow Patterns

- **Settings:** Python loads from `config.json` → Bridge exposes `getSettings()` → React can read (but Save doesn't call back)
- **Events (Python path):** EventTimerService fetches from PHP → emits `eventUpdated` signal → bridge forwards to JS (but React ignores it)
- **Events (React path):** EventsPage has hardcoded mock data → `useEventTimers` calculates countdowns → sounds via `useEventSound`
- **Game launch:** React calls `bridge.launchGame()` → Python `GameLauncher.launch()` → spawns subprocess

### 7.3 Code Duplication / Dead Code

| Location | Issue |
|----------|-------|
| `web/src/layout/Sidebar.tsx` | Unused React sidebar (Qt handles it) |
| `web/src/layout/TopBar.tsx` | Unused top bar component |
| `web/src/layout/MainLayout.tsx` | Unused layout wrapper |
| `launcher_bridge.py:getEvents()` | Returns mock events but never called |
| Event mocking | Both `EventTimerService` (Python) and `EventsPage` (React) have separate mock event data |
| `bridge.startDrag()` | Calls non-existent Python method |

### 7.4 Sound Files

- Expected at `/sounds/event-notify.mp3` (React public folder)
- Currently a README placeholder exists at `web/public/sounds/README.md`
- Sound playback is wired but will fail silently if file missing

---

## 8. Quick Reference: What Works vs. What Doesn't

### ✅ Fully Functional
- Frameless rounded window with Qt sidebar
- Window dragging from sidebar
- Resolution resize (from code)
- Navigation between pages (Qt → React)
- Game launch via bridge
- Per-event mute toggles with localStorage
- Event countdown timers (React-side mock)
- Single instance protection

### ⚠️ Partially Working
- Event timer service (Python fetches, React ignores)
- Settings loading (Python → React works, React → Python save doesn't)
- Screenshot capture (Python works, not exposed to React UI)

### ❌ Not Working / Stub Only
- Settings modal save
- Update/patching system
- Anti-cheat
- Login system
- Donate page
- Admin actions
- Rankings data fetch
- Guides content fetch
- Online player count
- Exit modal (doesn't close app)
- `startDrag()` from React (broken)

---

*Generated from codebase inspection on 2025-11-29*
