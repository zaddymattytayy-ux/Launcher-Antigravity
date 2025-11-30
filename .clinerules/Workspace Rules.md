# Cline Workspace Rules – MU Launcher (PyQt + React/Vite)

This workspace is a custom MU Online launcher built with:

- **Python / PyQt6** (native shell)
- **React + Vite** (web UI embedded via QWebEngineView)

You must respect these rules for all changes in this repo.

---

## 1. Architecture & Layout Rules

- The launcher consists of:
  - A PyQt6 main window (`native/launcher_app.py`)
  - A WebView that renders the React app (`web/`)
  - A bridge layer for Python ↔ JS (`native/launcher_bridge.py`, `web/src/services/bridge.ts`)
- **Do not change overall layout**:
  - Left sidebar is always present.
  - Right side is the content area (React).
- **Sidebar width is fixed at 80px** and must never change:
  - `SIDEBAR_WIDTH = 80` is the canonical value.
  - Window width = `SIDEBAR_WIDTH + content_width`.

### Visual / UX Constraints

- Do **not** alter:
  - Colors
  - Fonts
  - Icon sizes
  - Pill/button sizes
  - Glass panel sizes
  - Spacing and card layout
- The UI should remain pixel-aligned with the existing mockups; no “design improvements” unless explicitly requested by the user.

---

## 2. Resolutions & Window Behavior

- Supported **content resolutions** (right-side content area only):

  - `640x480`
  - `800x600`
  - `1024x768`
  - `1280x1024`
  - `1366x768`
  - `1440x900`
  - `1600x900`
  - `1680x1050`
  - `1920x1080`

- Rules:
  - Sidebar: always 80px wide.
  - Content width/height = selected resolution.
  - Window size = `(80 + content_width) × content_height`.
- When editing resolution logic, ensure:
  - WebView (and any embed container) is resized to the **content** resolution.
  - No scrollbars or unexpected overflow at the base design resolution (e.g. 1366×768).

---

## 3. Dragging Rules

- The launcher window is frameless.
- Window dragging MUST:
  - Only start when the mouse down occurs inside the **sidebar region** (x in `[0, 80)` relative to window).
  - Once started, dragging can move the window freely until mouse release.
- React may *request* dragging (e.g. via `bridge.startDrag(x, y)`), but:
  - The actual drag permission check (`_in_sidebar`) belongs in the **Python / Qt side**.
  - Do not implement full drag logic in React.

---

## 4. Embedding Rules

- The MU client (`main.exe`) runs from the **same folder** as the launcher.
- There will be **two modes**:
  - Embedded mode (`"embed_game_window": true` in `config.json`)
  - External window mode (`false`)
- In embedded mode:
  - Use `QWindow.fromWinId` + `QWidget.createWindowContainer` to host the game client in a dedicated `game_container` in the **content area** (not in the sidebar).
  - The embedded game size must match the content resolution (not including the 80px sidebar).
  - The WebView may be hidden or covered while the game is embedded but must remain logically intact.
- Do not introduce embedding behavior in React; embedding is handled in Python via the bridge and win32 logic.

---

## 5. Bridge & Backend Rules

- Bridge files:
  - `native/launcher_bridge.py`
  - `web/src/services/bridge.ts`
- Rules:
  - Do not remove or rename existing bridge methods without a clear reason.
  - If React calls a bridge method, ensure a matching implementation exists in Python (and vice versa).
  - Prefer extending existing bridge methods over creating many new ones.
- When adding new features:
  - Use the existing patterns for signals/slots (Qt) and subscriptions (JS).

---

## 6. Update System & Anti-Cheat Rules

- The update system uses an `update_url` and a manifest (e.g. `launcher-manifest.json`).
- `UpdateManager`:
  - May download a ZIP and overwrite files in the launcher/client folder.
  - Must report update state via signals (`updateAvailable`, `downloadProgress`, `updateError`, `updateFinished`).
- Anti-direct-launch:
  - `GameLauncher` tracks “managed” PIDs for client processes.
  - There is a config flag `kill_unmanaged_clients` in `config.json`.
  - Do not hard-kill processes or auto-enable dangerous behavior unless instructed; respect the flag.

---

## 7. Event / Rankings / Mute System Rules

- Events, Invasions, Bosses, Others:
  - React events page may initially use mock data but must be ready to consume real events via the bridge.
  - Per-event mute state:
    - All events start muted by default.
    - “Mute All” and per-event toggles must respect one another.
- `notification.wav`:
  - Located under `web/public/notification.wav`.
  - All event notification sounds (for all categories) should use this audio file.
  - Only play when:
    - Event approaching threshold AND
    - Event is unmuted AND
    - Global mute is off.

---

## 8. Files & Documentation Rules

- Key documentation files:
  - `FEATURES.md`: canonical map of what is implemented vs stubbed.
  - `Walkthrough.md`: high-level summary of what was wired and what requires manual configuration.
- Do not contradict these documents; if you update significant functionality, also update or annotate them if the task is about documentation.

---

## 9. Dependency & Tooling Rules

- Do not:
  - Add new Python dependencies (no new pip packages) without explicit user approval.
  - Add new Node dependencies (no new npm/yarn/pnpm packages) without explicit approval.
  - Change Python or Node versions.
- Use existing frameworks:
  - PyQt6 (no replacement)
  - React + Vite (no replacement)

---

## 10. Change Scope & Style

- Prefer **surgical changes**:
  - Modify only the files directly related to the task.
  - Avoid wide project-wide refactors or naming changes.
- Maintain existing:
  - Code style (formatting, naming)
  - Project structure
- Whenever you change behavior in a non-trivial way:
  - Add a short comment or clear code structure so the intent is obvious.
  - Do not over-comment trivial logic.

