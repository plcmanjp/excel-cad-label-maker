"""Windows GDI glyph preview with the layout's horizontal width factor."""
import ctypes as ct
from ctypes import wintypes as wt
import struct
import zlib
import tkinter as tk


class BitmapHeader(ct.Structure):
    _fields_ = [("size", wt.DWORD), ("width", wt.LONG), ("height", wt.LONG), ("planes", wt.WORD), ("bits", wt.WORD),
                ("compression", wt.DWORD), ("image_size", wt.DWORD), ("xppm", wt.LONG), ("yppm", wt.LONG), ("used", wt.DWORD), ("important", wt.DWORD)]


def _chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)


def glyph_png(text, family, pixels, factor, color):
    """Return transparent PNG bytes; do not change the input or DXF text."""
    gdi = ct.WinDLL("gdi32", use_last_error=True)
    declarations = {
        "CreateCompatibleDC": ([wt.HDC], wt.HDC),
        "CreateFontW": ([ct.c_int] * 5 + [wt.DWORD] * 8 + [wt.LPCWSTR], wt.HANDLE),
        "SelectObject": ([wt.HDC, wt.HANDLE], wt.HANDLE),
        "GetTextExtentPoint32W": ([wt.HDC, wt.LPCWSTR, ct.c_int, ct.POINTER(wt.SIZE)], wt.BOOL),
        "CreateDIBSection": ([wt.HDC, ct.POINTER(BitmapHeader), wt.UINT, ct.POINTER(ct.c_void_p), wt.HANDLE, wt.DWORD], wt.HANDLE),
        "TextOutW": ([wt.HDC, ct.c_int, ct.c_int, wt.LPCWSTR, ct.c_int], wt.BOOL),
        "SetTextColor": ([wt.HDC, wt.DWORD], wt.DWORD), "SetBkMode": ([wt.HDC, ct.c_int], ct.c_int),
        "DeleteObject": ([wt.HANDLE], wt.BOOL), "DeleteDC": ([wt.HDC], wt.BOOL),
        "GdiFlush": ([], wt.BOOL),
    }
    for name, (args, result) in declarations.items():
        function = getattr(gdi, name)
        function.argtypes, function.restype = args, result
    dc = gdi.CreateCompatibleDC(None)
    face = bitmap = old_font = old_bitmap = None
    if not dc:
        raise OSError("미리보기 글꼴을 준비하지 못했습니다.")
    try:
        face = gdi.CreateFontW(-pixels, 0, 0, 0, 400, 0, 0, 0, 1, 0, 0, 4, 0, family)
        if not face:
            raise OSError("미리보기 글꼴을 준비하지 못했습니다.")
        old_font = gdi.SelectObject(dc, face)
        length = len(text.encode("utf-16-le")) // 2
        size = wt.SIZE()
        if not gdi.GetTextExtentPoint32W(dc, text, length, ct.byref(size)):
            raise OSError("미리보기 문자 크기를 읽지 못했습니다.")
        w, h = max(1, size.cx), max(1, size.cy)
        if w > 4096 or h > 512:
            return None
        header = BitmapHeader(40, w, -h, 1, 32, 0, w * h * 4, 0, 0, 0, 0)
        bits = ct.c_void_p()
        bitmap = gdi.CreateDIBSection(dc, ct.byref(header), 0, ct.byref(bits), None, 0)
        if not bitmap or not bits.value:
            raise OSError("미리보기 이미지를 준비하지 못했습니다.")
        old_bitmap = gdi.SelectObject(dc, bitmap)
        ct.memset(bits, 255, w * h * 4)
        rgb = int(color.lstrip("#"), 16)
        gdi.SetTextColor(dc, ((rgb >> 16) & 255) | (rgb & 0xff00) | ((rgb & 255) << 16))
        gdi.SetBkMode(dc, 1)
        if not gdi.TextOutW(dc, 0, 0, text, length):
            raise OSError("미리보기 문자를 그리지 못했습니다.")
        gdi.GdiFlush()
        raw = ct.string_at(bits, w * h * 4)
        target = max(1, round(w * factor))
        rows = bytearray()
        for y in range(h):
            rows.append(0)
            for x in range(target):
                offset = (y * w + min(w - 1, int(x / factor))) * 4
                b, g, r = raw[offset:offset + 3]
                rows.extend((r, g, b, 0 if r == g == b == 255 else 255))
        return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", struct.pack(">IIBBBBB", target, h, 8, 6, 0, 0, 0)) + _chunk(b"IDAT", zlib.compress(rows)) + _chunk(b"IEND", b"")
    finally:
        if old_bitmap:
            gdi.SelectObject(dc, old_bitmap)
        if old_font:
            gdi.SelectObject(dc, old_font)
        if bitmap:
            gdi.DeleteObject(bitmap)
        if face:
            gdi.DeleteObject(face)
        gdi.DeleteDC(dc)


def glyph_image(root, text, family, pixels, factor, color):
    data = glyph_png(text, family, pixels, factor, color)
    return tk.PhotoImage(master=root, data=data) if data else None
