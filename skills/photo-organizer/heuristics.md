# How photo-organizer decides

The guiding rule: miss a case rather than harm a file. When the tool cannot read a format, it does not guess; it falls back to the next date source and says so.

The original tool also sorted out screenshots, thumbnails, heavily compressed copies and look-alike photos. This version does not; it handles exact duplicates, dates, names and year and month folders only.

## 1. Exact duplicates

- Files are grouped by size first, then by the SHA-256 of their first 64 KB, then by the SHA-256 of the whole file. Only files with exactly the same bytes count as duplicates. A resized or re-saved copy is not a duplicate.
- Empty files are never treated as duplicates.
- In each group, one file stays. It is chosen in this order:
  1. its name does not look like a copy (no "copy", no "(1)");
  2. it sits in a shallower folder;
  3. it has the older modified time;
  4. it has the shorter name.
- The others move to `duplicates/` inside the named folder, keeping their subfolder path. The plan says which file each one matches.

## 2. The date taken

Order of trust: photo EXIF, then video metadata, then the file name, then the file's modified time.

- **Photo EXIF:** `DateTimeOriginal` (tag 0x9003), then `DateTimeDigitized` (0x9004), then `DateTime` (0x0132). The first two live in the Exif sub-directory, reached through the pointer tag 0x8769 in the first directory; 0x0132 in the first directory is often the time the photo was last edited. JPEG, TIFF and DNG are read directly; HEIC, WebP and PNG are searched for an embedded EXIF block.
- **Video metadata:** the creation time in the `moov/mvhd` box of MP4, MOV, M4V and 3GP files. It counts seconds from 1904 in UTC and is shown in local time. A value of zero or anything before 1971 means the field was never filled in.
- **File name:** patterns like `IMG_20190501_123456`, `Screenshot_2019-05-01-12-34-56`, this tool's own `2019-05-01_123456`, and messaging-app exports that carry a 13-digit millisecond timestamp.
- **File modified time:** often the day the file was copied. It is used so every file gets a place, and every line that uses it is marked in the plan. With `--skip-mtime` those files stay where they are.

No outside program is used to read dates; the tool reads the bytes itself.

## 3. Names

- Format: `YYYY-MM-DD_HHMMSS`, every part padded to two digits so names sort in date order. Example: `2012:04:30 22:48:25` becomes `2012-04-30_224825`.
- With `--keep-name`, the old name stays in front: `Graduation_2012-04-30_224825.jpg`. A second run first strips the date it added last time, so names do not grow longer each run. A file that already has the right name and place is left alone.
- Two photos from the same second: the second gets `_2`, the third `_3`, and so on.
- Files in one folder with one base name are a group: a photo `IMG_1234.HEIC` with its clip `IMG_1234.MOV`, a RAW with its JPG, an `.AAE` edit file, a `.xmp` side file. The group uses the most trusted date among its members, gets one new base name, and moves together.

## 4. Year and month folders

- Each file goes to `<folder>/YYYY/MM/`. A file already in its right folder with its right name is not moved.
- The `duplicates` folder at the top of the named folder is never read again, so a second run does not sort duplicates back in.

## 5. EXIF reading pitfalls (fixed in the original)

- In a TIFF header, offset 0 holds the byte order (`II` or `MM`) and the value 0x002A sits at **offset 2**. An early version checked offset 0 and failed to read any EXIF at all.
- **Values of 4 bytes or less sit inside the directory entry itself**, not at an offset. Reading them as an offset gives garbage.
