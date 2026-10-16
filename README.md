# Report logical file sizes

Read-only teaching tool that ranks top-level folder totals and largest files.
It reads metadata, not content. Logical sizes are not allocated disk usage,
free space or permission to delete. Reports reveal file names.

## Practise

Save the three Python files in a new empty lesson folder. Python 3 is enough:

    python make_sample.py
    python diskreport.py sample
    python diskreport.py sample --top 2
    python -m unittest -v

Setup exclusively creates sample and nine zero-filled files. It refuses any
existing sample path, without resetting or replacing data. The extensions are
practice labels: these are not valid videos, pictures, documents or programs.
Use a different new folder if setup refuses; do not delete old data to force it.

## Evidence and limits

16 temporary-fixture tests cover known totals, ranking, errors, simulated
permission denial, selected link behavior, no-write checks, setup file/folder
collisions, nested unrelated bytes/mtime and repeat-run refusal. All16 tests
pass without skips in two Windows and two Ubuntu recordings. Paired platform
outputs match except unittest time. Displays use first Windows output, not
mixed transcripts. No Windows desktop, macOS or whole-drive run was recorded.

The recorder saves visible versions in a unique temporary folder, first the
incorrect top-level-only report, then the unchanged final checker. It removes
only its temporary recording folder. expected_output.txt is CI's stable sample
report, not a complete session transcript.

Selected link/reparse-point checks do not prove behavior on all filesystems.
Permission errors, concurrent changes, skipped paths and network filesystems
can affect totals. Read the skipped-path report; do not automate deletion.
Keep private names and reports private. Fixture passes are limited evidence,
not a universal safety guarantee.

## License

MIT, see LICENSE. Python is separately licensed and not included.
