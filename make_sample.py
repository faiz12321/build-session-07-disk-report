"""Creates a small, fixed folder of made-up files called sample/ next to this script.

Run: python make_sample.py
Refuses any existing sample path; never resets or replaces it.
The files hold only zeros. They are a few megabytes in total.
"""
import sys
import stat
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
    root = Path(root).absolute()
    if ".." in root.parts:
        raise OSError("Parent-traversal paths are unsupported.")
    for parent in reversed(root.parents):
        info = parent.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise OSError("Linked/reparse-point parents are unsupported.")
    root.mkdir()  # Refuse any existing file, folder or link.
    for name, size in FILES.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(b"\0" * size)
    return len(FILES)


if __name__ == "__main__":
    here = Path(__file__).absolute().parent
    try:
        count = make(here / "sample")
    except FileExistsError:
        raise SystemExit("Stopped: sample already exists. Nothing was replaced or deleted.")
    print(f"Made {count} files in sample")
    sys.exit(0)
