"""Trim, convert or normalize audio with SoX. Never edits the original.

    python tools/media-tools/audio.py trim <file> --start 5 --end 20
    python tools/media-tools/audio.py convert <file> --to mp3
    python tools/media-tools/audio.py normalize <file> [--to wav]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

PROGRAM = "sox"
FOLDERS = (r"%ProgramFiles(x86)%\sox-*", r"%ProgramFiles%\sox-*")
FORMATS = ("wav", "mp3", "flac")


def find():
    return _common.locate(PROGRAM, FOLDERS)


def output_for(action, path, to=None):
    if action == "trim":
        return _common.beside(path, "-trim", to)
    if action == "normalize":
        return _common.beside(path, "-normalized", to)
    if action == "convert":
        if not to:
            raise ValueError("convert needs --to wav, mp3 or flac")
        out = _common.beside(path, "", to)
        return out if not _common.same_file(out, path) else _common.beside(path, "-converted", to)
    raise ValueError("unknown action: %s" % action)


def command(action, path, start=None, end=None, to=None):
    out = output_for(action, path, to)
    if action == "trim":
        if start is None:
            raise ValueError("trim needs --start")
        argv = [PROGRAM, path, out, "trim", str(start)]
        if end is not None:
            argv.append("=%s" % end)  # an absolute end time, not a length
        return argv
    if action == "normalize":
        return [PROGRAM, "--norm", path, out]
    return [PROGRAM, path, out]


def main(argv=None):
    p = argparse.ArgumentParser(description="Trim, convert or normalize audio with SoX.")
    p.add_argument("action", choices=("trim", "convert", "normalize"))
    p.add_argument("file")
    p.add_argument("--start", help="seconds, or hh:mm:ss")
    p.add_argument("--end", help="seconds, or hh:mm:ss (an absolute time)")
    p.add_argument("--to", choices=FORMATS)
    a = p.parse_args(argv)
    try:
        built = command(a.action, a.file, a.start, a.end, a.to)
    except ValueError as exc:
        p.error(str(exc))
    program = find()
    if not program:
        return _common.missing(PROGRAM)
    out = output_for(a.action, a.file, a.to)
    code = _common.refuse_unsafe([a.file], out)
    if code is not None:
        return code
    rc = _common.run(built, program)
    if rc == 0:
        print("Wrote: %s" % out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
