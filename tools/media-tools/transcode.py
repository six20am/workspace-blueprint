"""Re-encode a video with a HandBrake preset. Never edits the original.

    python tools/media-tools/transcode.py <in> [--preset "Fast 1080p30"] [--out <file>]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

PROGRAM = "HandBrakeCLI"
FOLDERS = (r"%ProgramFiles%\HandBrake", r"%ProgramFiles%\HandBrakeCLI")
DEFAULT_PRESET = "Fast 1080p30"


def find():
    return _common.locate(PROGRAM, FOLDERS)


def output_for(path, out=None):
    return out or _common.beside(path, "-handbrake", "mp4")


def command(path, preset=DEFAULT_PRESET, out=None):
    return [PROGRAM, "-i", path, "-o", output_for(path, out), "--preset", preset]


def main(argv=None):
    p = argparse.ArgumentParser(description="Re-encode a video with HandBrakeCLI.")
    p.add_argument("file")
    p.add_argument("--preset", default=DEFAULT_PRESET)
    p.add_argument("--out")
    a = p.parse_args(argv)
    program = find()
    if not program:
        return _common.missing(PROGRAM)
    out = output_for(a.file, a.out)
    code = _common.refuse_unsafe([a.file], out)
    if code is not None:
        return code
    rc = _common.run(command(a.file, a.preset, a.out), program)
    if rc == 0:
        print("Wrote: %s" % out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
