"""List the tracks in a video, or put video, audio and subtitles into one .mkv,
with MKVToolNix. Never edits the originals.

    python tools/media-tools/container.py info <file>
    python tools/media-tools/container.py mux <video> [--audio <file>] [--subs <file>]
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

PROGRAM = "mkvmerge"
FOLDERS = (r"%ProgramFiles%\MKVToolNix", r"%ProgramFiles(x86)%\MKVToolNix")


def find():
    return _common.locate(PROGRAM, FOLDERS)


def output_for(action, path):
    if action != "mux":
        return None
    out = _common.beside(path, "", "mkv")
    return out if not _common.same_file(out, path) else _common.beside(path, "-muxed", "mkv")


def command(action, path, audio=None, subs=None):
    if action == "info":
        return [PROGRAM, "-i", path]
    if action == "mux":
        argv = [PROGRAM, "-o", output_for(action, path), path]
        argv += [x for x in (audio, subs) if x]
        return argv
    raise ValueError("unknown action: %s" % action)


def main(argv=None):
    p = argparse.ArgumentParser(description="Inspect or mux a video with mkvmerge.")
    p.add_argument("action", choices=("info", "mux"))
    p.add_argument("file")
    p.add_argument("--audio")
    p.add_argument("--subs")
    a = p.parse_args(argv)
    program = find()
    if not program:
        return _common.missing(PROGRAM)
    out = output_for(a.action, a.file)
    if out:
        code = _common.refuse_unsafe([a.file, a.audio, a.subs], out)
        if code is not None:
            return code
    rc = _common.run(command(a.action, a.file, a.audio, a.subs), program)
    if rc == 0 and out:
        print("Wrote: %s" % out)
    return rc


if __name__ == "__main__":
    sys.exit(main())
