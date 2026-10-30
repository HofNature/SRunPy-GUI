"""Keep the native Windows frame and animations behind the HTML title bar."""

import ctypes
import logging
from ctypes import wintypes


WM_NCDESTROY = 0x0082
WM_SIZE = 0x0005
WM_NCCALCSIZE = 0x0083
WM_NCHITTEST = 0x0084
WM_DPICHANGED = 0x02E0


def enable_per_monitor_dpi():
    # Must run before WinForms creates any windows. Older Windows can fall back
    # to pywebview's own system-DPI awareness.
    try:
        function = ctypes.windll.user32.SetProcessDpiAwarenessContext
        function.argtypes = [ctypes.c_void_p]
        function.restype = wintypes.BOOL
        function(ctypes.c_void_p(-4))  # PER_MONITOR_AWARE_V2
    except AttributeError:
        pass


class WindowsFrame:
    def __init__(self, window):
        self._window = window
        self._was_minimized = False
        self._hwnd = int(window.native.Handle.ToInt64())
        self._user = ctypes.WinDLL('user32', use_last_error=True)
        self._comctl = ctypes.WinDLL('comctl32', use_last_error=True)
        callback_type = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT,
            ctypes.c_size_t, ctypes.c_ssize_t, ctypes.c_size_t, ctypes.c_size_t)
        # Keep this callback alive until the native window is destroyed.
        self._callback = callback_type(self._procedure)
        self._comctl.SetWindowSubclass.argtypes = [
            wintypes.HWND, callback_type, ctypes.c_size_t, ctypes.c_size_t]
        self._comctl.SetWindowSubclass.restype = wintypes.BOOL
        self._comctl.RemoveWindowSubclass.argtypes = [
            wintypes.HWND, callback_type, ctypes.c_size_t]
        self._comctl.RemoveWindowSubclass.restype = wintypes.BOOL
        self._comctl.DefSubclassProc.argtypes = [
            wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t]
        self._comctl.DefSubclassProc.restype = ctypes.c_ssize_t
        self._user.SetWindowPos.argtypes = [
            wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, wintypes.UINT]
        self._user.SetWindowPos.restype = wintypes.BOOL
        self._user.PostMessageW.argtypes = [
            wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t]
        self._user.PostMessageW.restype = wintypes.BOOL
        if not self._comctl.SetWindowSubclass(self._hwnd, self._callback, 1, 0):
            raise ctypes.WinError(ctypes.get_last_error())
        # Recalculate the client area without stripping WS_CAPTION or the
        # system buttons, which Windows needs for native minimize/restore.
        self._user.SetWindowPos(self._hwnd, None, 0, 0, 0, 0, 0x0027)

    def _procedure(self, hwnd, message, wparam, lparam, _id, _data):
        try:
            if message == WM_NCCALCSIZE:
                # Both forms of this message leave the entire window as client area.
                return 0
            if message == WM_NCHITTEST:
                return 1  # HTCLIENT: no invisible caption buttons or resize edges.
            if message == WM_NCDESTROY:
                self._comctl.RemoveWindowSubclass(hwnd, self._callback, 1)
            result = self._comctl.DefSubclassProc(hwnd, message, wparam, lparam)
            if message == WM_SIZE:
                if wparam == 1:  # SIZE_MINIMIZED
                    self._was_minimized = True
                    self._window.native.webview.Visible = False
                elif self._was_minimized:
                    from System import Action
                    self._was_minimized = False
                    self._window.native.BeginInvoke(Action(self._resume_webview))
            elif message == WM_DPICHANGED:
                rect = ctypes.cast(lparam, ctypes.POINTER(wintypes.RECT)).contents
                scale = (wparam & 0xFFFF) / 96
                self._user.SetWindowPos(
                    hwnd, None, rect.left, rect.top,
                    round(self._window.initial_width * scale),
                    round(self._window.initial_height * scale), 0x0014)
            return result
        except Exception:
            logging.exception('Native window frame message failed')
            return self._comctl.DefSubclassProc(hwnd, message, wparam, lparam)

    def _resume_webview(self):
        form = self._window.native
        if form.IsDisposed or self._was_minimized:
            return
        # Resume the WebView2 compositor after WinForms finishes restoring.
        form.webview.Visible = False
        form.webview.Visible = True
        form.PerformLayout()
        form.webview.Invalidate(True)
        form.webview.Update()

    def minimize(self):
        self._user.PostMessageW(self._hwnd, 0x0112, 0xF020, 0)  # SC_MINIMIZE
