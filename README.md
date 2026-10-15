# See what is using your disk space

A small read-only disk space report built step by step. It adds up file sizes folder by folder, lists the biggest folders and files, skips shortcuts so it cannot loop, and lists anything it could not read. It never changes, moves or deletes a file.

## Run it

    python make_sample.py                 # makes a practice folder called sample
    python diskreport.py sample           # the report
    python diskreport.py sample --top 2   # fewer lines
    python -m unittest -v                 # twelve automated tests

On Windows, if `python` is not found, use `py`.

## Files

- `diskreport.py` - the tool
- `make_sample.py` - makes made-up practice files (zeros, about 9 MB)
- `test_diskreport.py` - tests
- `expected_output.txt` - the report the lesson shows; the automated check compares against it

## Notes

- Sizes are file sizes (1 KB = 1024 bytes), not the space the disk sets aside, so Windows may show a slightly different number. Files that cloud folders keep online only can be listed with their full size although they are not stored on the PC.
- Shortcuts and links are skipped, not followed. A real hard link (one file with two names) would be counted once per name.
- A folder that cannot be opened is listed under "Could not read". If that list is not empty, the total is too low.
- Uses only what comes with Python 3. Tested on Python 3.10 (Linux) and, by GitHub Actions, Python 3.12 on Windows and Ubuntu. Not tested on a Windows 10 or 11 desktop, a network drive, or a folder with millions of files. On a machine that cannot make symbolic links, one test reports "skipped".
- The practice files are made up. Educational example, no warranty. Use at your own risk. What you delete afterwards is your decision.
- Code is MIT licensed (see LICENSE). Python is a separate project with its own license; this repository does not include it.
- The commands, with real recorded output, are in the companion practice page (published after review). Nothing in it runs on your device.
