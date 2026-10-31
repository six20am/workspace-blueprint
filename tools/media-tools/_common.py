"""Shared helpers for the media-tools wrappers. Standard library only."""
import glob
import os
import shutil
import subprocess
import sys

MISSING_EXIT = 3
REFUSED_EXIT = 1
DOCTOR = "python tools/doctor/doctor.py (python3 on Mac and Linux)"


def winget_links():
    base = os.environ.get("LOCALAPPDATA")
    return os.path.join(base, "Microsoft", "WinGet", "Links") if base else None


def locate(program, folder_patterns=()):
    """Return the full path to a program, or None.

    Looks on PATH first, then in each folder pattern (environment variables
    expanded, wildcards allowed), then in the WinGet Links folder.
    """
    found = shutil.which(program)
    if found:
        return found
    names = [program + ".exe", program] if os.name == "nt" else [program]
    folders = []
    for pattern in folder_patterns:
        expanded = os.path.expandvars(pattern)
        if "%" in expanded or "$" in expanded:
            continue  # the variable is not set on this machine
        folders.extend(sorted(glob.glob(expanded)))
    links = winget_links()
    if links:
        folders.append(links)
    for folder in folders:
        for name in names:
            candidate = os.path.join(folder, name)
            if os.path.isfile(candidate):
                return candidate
    return None


def missing(program):
    print("Missing: %s. Run: %s" % (program, DOCTOR), file=sys.stderr)
    return MISSING_EXIT


def beside(path, suffix, ext=None):
    """A new file name beside the input: <name><suffix>.<ext>."""
    folder, base = os.path.split(path)
    stem, old_ext = os.path.splitext(base)
    ext = ext if ext is not None else old_ext.lstrip(".")
    return os.path.join(folder, "%s%s.%s" % (stem, suffix, ext))


def same_file(a, b):
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def refuse_unsafe(inputs, output):
    """Return an exit code when writing output would touch an input or an existing file."""
    for item in inputs:
        if item and same_file(item, output):
            print("Refused: %s is an input. Pick another output name." % output, file=sys.stderr)
            return REFUSED_EXIT
    if os.path.exists(output):
        print("Refused: %s already exists. Move it or pick another name." % output, file=sys.stderr)
        return REFUSED_EXIT
    return None


def run(argv, program_path):
    """Run argv with its first item swapped for the located program."""
    full = [program_path] + list(argv[1:])
    return subprocess.run(full).returncode
