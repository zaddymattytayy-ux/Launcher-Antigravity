# window_embed.py
#
# Embed MU (main.exe) window into a Qt host widget by PID,
# with debug logging and auto-fix helper.

import ctypes
from ctypes import wintypes
import psutil

user32 = ctypes.windll.user32

# ---------------------------------------------------------------------
# Types / constants
# ---------------------------------------------------------------------

if hasattr(wintypes, "LONG_PTR"):
    LONG_PTR = wintypes.LONG_PTR
else:
    LONG_PTR = wintypes.LPARAM

HWND = wintypes.HWND

GWL_STYLE   = -16
GWL_EXSTYLE = -20

WS_CHILD      = 0x40000000
WS_POPUP      = 0x80000000
WS_CAPTION    = 0x00C00000
WS_THICKFRAME = 0x00040000
WS_BORDER     = 0x00800000

SWP_NOSIZE       = 0x0001
SWP_NOMOVE       = 0x0002
SWP_NOZORDER     = 0x0004
SWP_FRAMECHANGED = 0x0020
SWP_SHOWWINDOW   = 0x0040

# Win32 APIs
EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, HWND, wintypes.LPARAM)
GetWindowThreadProcessId = user32.GetWindowThreadProcessId
GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextW = user32.GetWindowTextW
GetClassNameW = user32.GetClassNameW
IsWindowVisible = user32.IsWindowVisible
IsWindow = user32.IsWindow
GetWindowRect = user32.GetWindowRect
SetParent = user32.SetParent
SetWindowPos = user32.SetWindowPos

GetWindowTextW.argtypes = [HWND, wintypes.LPWSTR, ctypes.c_int]
GetClassNameW.argtypes = [HWND, wintypes.LPWSTR, ctypes.c_int]
IsWindowVisible.argtypes = [HWND]
IsWindow.argtypes = [HWND]
GetWindowRect.argtypes = [HWND, ctypes.POINTER(wintypes.RECT)]
SetParent.argtypes = [HWND, HWND]
SetWindowPos.argtypes = [
    HWND, HWND,
    ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int,
    ctypes.c_uint,
]

# 64/32-bit safe Get/SetWindowLongPtr
try:
    GetWindowLongPtrW = user32.GetWindowLongPtrW
    SetWindowLongPtrW = user32.SetWindowLongPtrW
    GetWindowLongPtrW.restype = LONG_PTR
    GetWindowLongPtrW.argtypes = [HWND, ctypes.c_int]
    SetWindowLongPtrW.restype = LONG_PTR
    SetWindowLongPtrW.argtypes = [HWND, ctypes.c_int, LONG_PTR]
except AttributeError:
    GetWindowLongPtrW = user32.GetWindowLongW
    SetWindowLongPtrW = user32.SetWindowLongW
    GetWindowLongPtrW.restype = ctypes.c_long
    GetWindowLongPtrW.argtypes = [HWND, ctypes.c_int]
    SetWindowLongPtrW.restype = ctypes.c_long
    SetWindowLongPtrW.argtypes = [HWND, ctypes.c_int, ctypes.c_long]


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def log(msg: str):
    # Replace with your own logger if needed
    print(f"[EMBED] {msg}")


def _get_title(hwnd: int) -> str:
    length = GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buff = ctypes.create_unicode_buffer(length + 1)
    GetWindowTextW(hwnd, buff, length + 1)
    return buff.value.strip()


def _get_class(hwnd: int) -> str:
    buff = ctypes.create_unicode_buffer(256)
    GetClassNameW(hwnd, buff, 256)
    return buff.value.strip()


def dump_window_info(hwnd: int, label: str = "window"):
    if not hwnd:
        log(f"{label}: hwnd = 0 (invalid)")
        return

    rect = wintypes.RECT()
    GetWindowRect(hwnd, ctypes.byref(rect))
    style = GetWindowLongPtrW(hwnd, GWL_STYLE)
    log(
        f"{label}: hwnd={hwnd}, "
        f"title='{_get_title(hwnd)}', "
        f"class='{_get_class(hwnd)}', "
        f"rect=({rect.left},{rect.top},{rect.right},{rect.bottom}), "
        f"style=0x{style:08X}"
    )


def enum_windows():
    """Optional: dump all visible top-level windows (for debugging)."""
    def callback(hwnd, lParam):
        if IsWindowVisible(hwnd):
            dump_window_info(hwnd, "TOPLEVEL")
        return True

    EnumWindows(EnumWindowsProc(callback), 0)


# ---------------------------------------------------------------------
# Process → PID → HWND
# ---------------------------------------------------------------------

def get_mu_pid() -> int | None:
    """
    Find PID for main.exe (MU client).
    Returns PID or None if not running.
    """
    for proc in psutil.process_iter(['pid', 'name']):
        name = proc.info.get('name') or ""
        if name.lower() == "main.exe":
            return proc.info['pid']
    return None


def find_mu_hwnd() -> int:
    """
    Find top-level MU window by PID of main.exe, ignoring "debugger" windows.
    No reliance on static titles or class names.
    """
    mu_pid = get_mu_pid()
    if not mu_pid:
        log("main.exe not found (is the client running?)")
        return 0

    log(f"Found MU PID: {mu_pid}")
    result = {"hwnd": 0}

    def callback(hwnd, lParam):
        if not IsWindowVisible(hwnd):
            return True

        pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value != mu_pid:
            return True

        title = _get_title(hwnd)
        # Ignore debugger/aux windows
        if title and "debugger" in title.lower():
            return True

        # First visible non-debugger window for this PID = game window
        result["hwnd"] = hwnd
        return False

    EnumWindows(EnumWindowsProc(callback), 0)

    if result["hwnd"]:
        dump_window_info(result["hwnd"], "FOUND_GAME")
    else:
        log("No visible MU window found for main.exe PID")

    return result["hwnd"]


# ---------------------------------------------------------------------
# Embed logic
# ---------------------------------------------------------------------

def embed_window(hwnd_game: int, hwnd_host: int, width: int, height: int) -> bool:
    """
    Turn MU game window into a child of hwnd_host and resize it to (width, height).
    """
    log("=== EMBED START ===")
    dump_window_info(hwnd_game, "GAME_BEFORE")
    dump_window_info(hwnd_host, "HOST")

    if not hwnd_game or not IsWindow(hwnd_game):
        log("embed_window: hwnd_game invalid")
        return False
    if not hwnd_host or not IsWindow(hwnd_host):
        log("embed_window: hwnd_host invalid")
        return False

    # Read current style
    style = GetWindowLongPtrW(hwnd_game, GWL_STYLE)
    log(f"GAME style before: 0x{style:08X}")

    # Remove top-level styles, add WS_CHILD
    style &= ~WS_POPUP
    style &= ~WS_CAPTION
    style &= ~WS_THICKFRAME
    style &= ~WS_BORDER
    style |= WS_CHILD

    # Apply style
    prev = SetWindowLongPtrW(hwnd_game, GWL_STYLE, style)
    if prev == 0:
        # Note: a 0 return is not always an error, just log
        log("WARNING: SetWindowLongPtrW returned 0 (may still be ok)")

    log(f"GAME style after: 0x{style:08X}")

    # Reparent
    if not SetParent(hwnd_game, hwnd_host):
        log("SetParent failed (GetLastError may explain why)")

    # Resize and force frame recompute
    if not SetWindowPos(
        hwnd_game,
        None,
        0, 0,
        width, height,
        SWP_NOZORDER | SWP_SHOWWINDOW | SWP_FRAMECHANGED
    ):
        log("SetWindowPos failed")

    dump_window_info(hwnd_game, "GAME_AFTER")
    log("=== EMBED END ===")
    return True


def verify_and_fix_embed(hwnd_game: int, hwnd_host: int, width: int, height: int) -> bool:
    """
    Call periodically (e.g. from a Qt timer) to detect if the game
    reasserted top-level styles and re-embed if needed.
    """
    if not hwnd_game or not IsWindow(hwnd_game):
        log("verify: hwnd_game invalid")
        return False
    if not hwnd_host or not IsWindow(hwnd_host):
        log("verify: hwnd_host invalid")
        return False

    style = GetWindowLongPtrW(hwnd_game, GWL_STYLE)
    must_fix = False

    # If WS_CHILD is gone or top-level styles are back, fix
    if not (style & WS_CHILD):
        log("verify: WS_CHILD missing, re-embedding")
        must_fix = True
    if style & (WS_POPUP | WS_CAPTION | WS_THICKFRAME | WS_BORDER):
        log("verify: top-level styles present again, re-embedding")
        must_fix = True

    if must_fix:
        return embed_window(hwnd_game, hwnd_host, width, height)

    return True
