import builtins
import contextlib
import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import diskreport
import make_sample


def snapshot(root):
    """Every name, size and modified time under root."""
    seen = {}
    for folder, dirs, files in os.walk(root):
        for name in dirs + files:
            path = os.path.join(folder, name)
            info = os.stat(path)
            seen[os.path.relpath(path, root)] = (info.st_size, info.st_mtime_ns)
    return seen


class DiskReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "sample"
        make_sample.make(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def run_main(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = diskreport.main([str(a) for a in args])
        return code, out.getvalue()

    def test_human_sizes(self):
        self.assertEqual(diskreport.human(0), "0 bytes")
        self.assertEqual(diskreport.human(1023), "1023 bytes")
        self.assertEqual(diskreport.human(1024), "1.0 KB")
        self.assertEqual(diskreport.human(1536 * 1024), "1.5 MB")
        self.assertEqual(diskreport.human(3 * 1024 ** 3), "3.0 GB")

    def test_total_and_counts_are_exact(self):
        data = diskreport.scan(self.root)
        self.assertEqual(data["total"], sum(make_sample.FILES.values()))
        self.assertEqual(len(data["files"]), len(make_sample.FILES))
        self.assertEqual(data["folders"], 5)

    def test_folders_are_ranked_by_size_and_include_sub_folders(self):
        groups = diskreport.scan(self.root)["groups"]
        self.assertEqual(groups["videos"], (3000 + 1200 + 900) * 1024)
        ranked = sorted(groups, key=lambda name: -groups[name])
        self.assertEqual(ranked[:2], ["videos", "downloads"])
        self.assertEqual(groups["(files directly in this folder)"], 1024)

    def test_biggest_files_come_first(self):
        _, text = self.run_main(self.root, "--top", 2)
        files = text.split("Biggest files:")[1]
        self.assertLess(files.index("holiday.mp4"), files.index("setup-installer.exe"))
        self.assertNotIn("clip2.mp4", files)

    def test_the_report_changes_nothing(self):
        before = snapshot(self.root)
        self.run_main(self.root)
        self.assertEqual(snapshot(self.root), before)

    def test_the_report_works_when_every_change_is_forbidden(self):
        real_open = builtins.open

        def read_only_open(file, mode="r", *args, **kwargs):
            if any(flag in mode for flag in "wax+"):
                raise AssertionError("tried to open a file for writing")
            return real_open(file, mode, *args, **kwargs)

        def forbidden(*args, **kwargs):
            raise AssertionError("tried to change the folder")

        names = ["remove", "unlink", "rename", "replace", "rmdir", "mkdir", "makedirs", "utime", "chmod", "truncate"]
        with contextlib.ExitStack() as stack:
            for name in names:
                stack.enter_context(mock.patch.object(os, name, forbidden))
            stack.enter_context(mock.patch.object(shutil, "rmtree", forbidden))
            stack.enter_context(mock.patch.object(builtins, "open", read_only_open))
            code, text = self.run_main(self.root)
        self.assertEqual(code, 0)
        self.assertIn("Total:", text)

    def test_an_unreadable_folder_is_listed_and_the_rest_still_counts(self):
        real = os.scandir
        blocked = str(self.root / "videos")

        def picky(path):
            if str(path) == blocked:
                raise PermissionError(13, "Permission denied")
            return real(path)

        with mock.patch.object(os, "scandir", picky):
            code, text = self.run_main(self.root)
        self.assertEqual(code, 0)
        self.assertIn("Could not read: 1 item(s)", text)
        self.assertIn("Permission denied", text)
        self.assertIn("downloads", text)

    def test_link_detection(self):
        class Fake:
            def __init__(self, mode, attributes=0):
                self.st_mode = mode
                self.st_file_attributes = attributes

        self.assertTrue(diskreport.is_link(Fake(0o120777)))
        self.assertTrue(diskreport.is_link(Fake(0o040777, 0x400)))
        self.assertFalse(diskreport.is_link(Fake(0o100644)))
        self.assertFalse(diskreport.is_link(Fake(0o040755, 0x10)))

    def test_links_to_folders_are_not_followed_even_in_a_loop(self):
        try:
            os.symlink(self.root, self.root / "videos" / "loop", target_is_directory=True)
            os.symlink(self.root / "photos", self.root / "documents" / "to-photos", target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"this machine cannot make symbolic links: {error}")
        data = diskreport.scan(self.root)
        self.assertEqual(data["total"], sum(make_sample.FILES.values()))
        self.assertEqual(data["links"], 2)

    def test_an_empty_folder_and_bad_folders(self):
        empty = Path(self.tmp.name) / "empty"
        empty.mkdir()
        code, text = self.run_main(empty)
        self.assertEqual(code, 0)
        self.assertIn("Total: 0 bytes in 0 files and 0 folders", text)
        self.assertEqual(self.run_main(Path(self.tmp.name) / "nope")[0], 2)
        self.assertEqual(self.run_main(self.root / "readme.txt")[0], 2)

    def test_bad_arguments(self):
        for args in ([], [self.root, "--top"], [self.root, "--top", "x"], [self.root, "--top", 0], [self.root, "extra"]):
            self.assertEqual(self.run_main(*args)[0], 2, args)

    def test_a_name_the_console_cannot_show_does_not_crash(self):
        (self.root / "documents" / "\u65e5\u672c\u8a9e.txt").write_text("x", encoding="utf-8")
        raw = io.BytesIO()
        console = io.TextIOWrapper(raw, encoding="cp1252", errors="strict")
        with contextlib.redirect_stdout(console):
            code = diskreport.main([str(self.root), "--top", "20"])
            console.flush()
        self.assertEqual(code, 0)
        self.assertIn(b"?", raw.getvalue())


if __name__ == "__main__":
    unittest.main()
