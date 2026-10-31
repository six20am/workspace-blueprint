"""Show or strip photo and video metadata with ExifTool. Never edits the original.

    python tools/media-tools/exif.py show <file>
    python tools/media-tools/exif.py strip <file>    writes <name>-clean.<ext> beside it
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

PROGRAM = "exiftool"
FOLDERS = (r"%ProgramFiles%\exiftool", r"%ProgramFiles(x86)%\exiftool")


def find():
    return _common.locate(PROGRAM, FOLDERS)


def output_for(action, path):
    return _common.beside(path, "-clean") if action == "strip" else None


def command(action, path):
    if action == "show":
        return [PROGRAM, "-s", path]
    if action == "strip":
        return [PROGRAM, "-all=", "-o", output_for(action, path), path]
    raise ValueError("unknown action: %s" % action)


def main(argv=None):
    p = argparse.ArgumentParser(description="Show or strip metadata with ExifTool.")
    p.add_argument("action", choices=("show", "strip"))
    p.add_argument("file")
    a = p.parse_args(argv)
    program = find()
    if not program:
        return _common.missing(PROGRAM)
    out = output_for(a.action, a.file)
    if out:
        code = _common.refuse_unsafe([a.file], out)
        if code is not None:
            return code
    rc = _common.run(command(a.action, a.file), program)
    if rc == 0 and out:
        print("Wrote: %s" % out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
