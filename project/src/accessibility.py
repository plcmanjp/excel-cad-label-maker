"""Expose Tk child-window names to Windows' native accessibility fallback."""
import ctypes
from ctypes import wintypes
import sys


def caption(widget, text):
    if sys.platform != "win32":
        return
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    function = user32.SetWindowTextW
    function.argtypes, function.restype = [wintypes.HWND, wintypes.LPCWSTR], wintypes.BOOL
    function(widget.winfo_id(), text)


def expose_buttons(widget):
    if widget.winfo_class() in {"TButton", "TCheckbutton", "Button", "Checkbutton"}:
        caption(widget, widget.cget("text"))
    for child in widget.winfo_children():
        expose_buttons(child)
