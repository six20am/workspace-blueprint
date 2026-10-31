# photo-organizer

Renames photos and videos by the date taken, sets exact duplicates aside, and sorts the rest into
year and month folders, all inside one folder.

```
python tools/photo-organizer/organize.py --root "<folder>"              # dry run: print the plan
python tools/photo-organizer/organize.py --root "<folder>" --apply      # move files, write the undo CSV
python tools/photo-organizer/organize.py --undo "<undo csv>" [--apply]  # preview, then put files back
```

Options: `--keep-name` keeps the old name in front of the date; `--skip-mtime` leaves files whose only
date is the file's modified time where they are; `--no-dedupe` skips the duplicate check.

New names are `YYYY-MM-DD_HHMMSS.<ext>` in `<folder>/YYYY/MM/`. Duplicates (same SHA-256) go to
`<folder>/duplicates/`. Dates come from photo EXIF (JPEG, TIFF, DNG, HEIC, WebP, PNG), then MP4/MOV
metadata, then the file name, then the modified time; each plan line says which.

The undo CSV is written beside the folder before anything moves. Undo skips any row whose paths are
outside the folder it recorded, and removes only folders the undo left empty.

It never deletes a file, never writes outside the named folder except the one undo CSV, and never
uses the network. Standard library only. Tests: `python -m unittest tests.test_photo_organizer`.
