"""Show what is using the space in a folder. It only looks. It never changes or deletes anything.

Usage:  python diskreport.py FOLDER [--top N]
Sizes are file sizes (1 KB = 1024 bytes), not the space the disk sets aside.
"""
import os
import stat
import sys
from pathlib import Path

def safe_input(value, directory=False):
    path = Path(value).absolute()
    if '..' in path.parts:
        raise OSError('Parent-traversal paths are unsupported.')
    for part in [*reversed(path.parents), path]:
        info = part.lstat()
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise OSError('Links/reparse points are unsupported.')
    info = path.lstat()
    if directory:
        if not stat.S_ISDIR(info.st_mode):
            raise NotADirectoryError('Expected an ordinary directory.')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise OSError('Expected an ordinary singly linked file.')
    return path




REPARSE_POINT = 0x400  # Windows marks shortcuts to other folders (junctions) with this flag


def human(size):
    value = float(size)
    for unit in ("bytes", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{int(value)} bytes" if unit == "bytes" else f"{value:.1f} {unit}"
        value /= 1024


def is_link(info):
    """True for symlinks and Windows junctions. The report never follows them."""
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & REPARSE_POINT)


def scan(folder):
    """Walk the folder. Returns a dict with sizes, counts and everything that could not be read."""
    result = {"total": 0, "files": [], "groups": {}, "folders": 0, "unreadable": [], "links": 0}
    folder = safe_input(folder, directory=True)
    pending = [(folder, None)]
    while pending:
        path, group = pending.pop()
        try:
            path = safe_input(path, directory=True)
            entries = list(os.scandir(path))
        except OSError as error:
            result["unreadable"].append(f"{path}: {error.strerror or error}")
            continue
        for entry in entries:
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError as error:
                result["unreadable"].append(f"{entry.path}: {error.strerror or error}")
                continue
            if is_link(info):
                result["links"] += 1
                continue
            try:
                safe_input(entry.path, directory=stat.S_ISDIR(info.st_mode))
            except OSError as error:
                result["unreadable"].append(f"{entry.path}: {error.strerror or error}")
                continue
            here = group if group is not None else (entry.name if stat.S_ISDIR(info.st_mode) else None)
            if stat.S_ISDIR(info.st_mode):
                result["folders"] += 1
                result["groups"].setdefault(here, 0)
                pending.append((entry.path, here))
            elif stat.S_ISREG(info.st_mode):
                result["total"] += info.st_size
                result["files"].append((info.st_size, entry.path))
                key = here if here is not None else "(files directly in this folder)"
                result["groups"][key] = result["groups"].get(key, 0) + info.st_size
    return result


def report(folder, top=5, data=None):
    data = scan(folder) if data is None else data
    lines = [f"Folder: {folder}", f"Total: {human(data['total'])} in {len(data['files'])} files and {data['folders']} folders", "", "Biggest folders:"]
    groups = sorted(data["groups"].items(), key=lambda item: (-item[1], item[0]))
    lines += [f"  {human(size):>10}  {name}" for name, size in groups[:top]] or ["  (none)"]
    lines += ["", "Biggest files:"]
    files = sorted(data["files"], key=lambda item: (-item[0], item[1]))
    lines += [f"  {human(size):>10}  {os.path.relpath(path, folder)}" for size, path in files[:top]] or ["  (none)"]
    lines.append("")
    lines.append(f"Could not read: {len(data['unreadable'])} item(s)")
    lines += [f"  {line}" for line in data["unreadable"][:top]]
    if data["links"]:
        lines.append(f"Shortcuts and links skipped, not followed: {data['links']}")
    if data["unreadable"] or data["links"]:
        lines.insert(0, "Incomplete report: unreadable or unsupported paths were skipped.")
    return "\n".join(lines)


def main(argv):
    try:
        sys.stdout.reconfigure(errors="replace")  # a name the console cannot show must not crash the report
    except AttributeError:
        pass
    args = list(argv)
    top = 5
    if "--top" in args:
        at = args.index("--top")
        try:
            top = int(args[at + 1])
            if top < 1:
                raise ValueError
        except (IndexError, ValueError):
            print("--top needs a whole number of 1 or more.")
            return 2
        del args[at:at + 2]
    if len(args) != 1:
        print("Usage: python diskreport.py FOLDER [--top N]")
        return 2
    try:
        data = scan(args[0])
        print(report(args[0], top, data))
    except OSError as error:
        print(error)
        return 2
    return 2 if data["unreadable"] or data["links"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
