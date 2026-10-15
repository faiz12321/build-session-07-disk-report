"""Creates a small, fixed folder of made-up files called sample/ next to this script.

Run: python make_sample.py
The files hold only zeros. They are a few megabytes in total.
"""
import sys
from pathlib import Path

KB = 1024
FILES = {
    "videos/holiday.mp4": 3000 * KB,
    "videos/old-clips/clip1.mp4": 1200 * KB,
    "videos/old-clips/clip2.mp4": 900 * KB,
    "photos/beach.jpg": 700 * KB,
    "photos/city.jpg": 500 * KB,
    "documents/report.docx": 90 * KB,
    "documents/notes.txt": 2 * KB,
    "downloads/setup-installer.exe": 2400 * KB,
    "readme.txt": 1 * KB,
}


def make(root):
    root = Path(root)
    for name, size in FILES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\0" * size)
    return len(FILES)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    count = make(here / "sample")
    print(f"Made {count} files in sample")
    sys.exit(0)
