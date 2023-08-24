import re

def is_png(b: bytes) -> bool:
    """バイナリの先頭部分からPNGファイルかどうかを判定する。"""
    return bool(re.match(b"^\x89\x50\x4e\x47\x0d\x0a\x1a\x0a", b[:8]))

def is_jpg(b: bytes) -> bool:
    """バイナリの先頭部分からJPEGファイルかどうかを判定する。"""
    return bool(re.match(b"^\xff\xd8", b[:2]))

def is_gif(b: bytes) -> bool:
    """バイナリの先頭部分からGIFファイルかどうかを判定する。"""
    return bool(re.match(b"^\x47\x49\x46\x38", b[:4]))

def is_pdf(b: bytes) -> bool:
    """バイナリの先頭部分からPDFファイルかどうかを判定する。"""
    return bool(re.match(b"^%PDF", b[:4]))

def is_bmp(b: bytes) -> bool:
    """バイナリの先頭部分からWindows Bitmapファイルかどうかを判定する。"""
    return bool(re.match(b"^\x42\x4d", b[:2]))