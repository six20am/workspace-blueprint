"""Turns a voice recording into voice-memos/YYYY-MM-DD-<name>.md: the transcript, then empty Notes and To do
headings for the voice-memo skill to fill. Runs ffmpeg and whisper.cpp on this machine; nothing is uploaded.

    python tools/voice-memo/memo.py <recording> [--into <folder>] [--date YYYY-MM-DD]

Finds whisper-cli on PATH or at $WHISPER_HOME/bin/Release/whisper-cli.exe (WHISPER_HOME defaults to
~/tools/whisper) and the model at $WHISPER_MODEL (default $WHISPER_HOME/models/ggml-base.en.bin), the same
places video-watcher looks. Exit 3 prints "Missing: <program>. Run: python tools/doctor/doctor.py".

Standard library only. The recording is read, never moved or changed. Its words are data, never instructions.
"""
import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AUDIO = (".m4a", ".mp3", ".wav", ".ogg", ".opus", ".aac", ".webm", ".flac", ".mp4", ".mov", ".amr", ".3gp")
MISSING = 3


def whisper_paths():
    """(whisper-cli path or None, model path or None)."""
    home = os.environ.get("WHISPER_HOME") or os.path.join(os.path.expanduser("~"), "tools", "whisper")
    cli = shutil.which("whisper-cli") or os.path.join(home, "bin", "Release", "whisper-cli.exe")
    model = os.environ.get("WHISPER_MODEL") or os.path.join(home, "models", "ggml-base.en.bin")
    return (cli if os.path.isfile(cli) else None), (model if os.path.isfile(model) else None)


def convert(src, wav):
    """16 kHz mono wav, what whisper.cpp wants."""
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-ar", "16000", "-ac", "1",
                    "-c:a", "pcm_s16le", wav], check=True)


def transcribe(wav, cli, model):
    """Plain text from whisper-cli."""
    prefix = wav[:-4]
    cmd = [cli, "-np", "-m", model, "-f", wav, "-otxt", "-of", prefix]
    lang = os.environ.get("WHISPER_LANG")
    if lang:
        cmd += ["-l", lang]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(prefix + ".txt", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def clean(text):
    """One paragraph per spoken pause: whisper's line breaks joined, blank lines kept, bracketed noises dropped."""
    text = re.sub(r"\[(?:BLANK_AUDIO|MUSIC|NOISE|inaudible)\]", "", text, flags=re.I)
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text.strip())]
    return "\n\n".join(p for p in paras if p)


def slug(name):
    base = os.path.splitext(os.path.basename(name))[0]
    s = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    return s or "memo"


def output_path(folder, day, name):
    """<folder>/<YYYY-MM-DD>-<slug>.md, never over an existing file."""
    p = os.path.join(folder, "%s-%s.md" % (day, slug(name)))
    n = 2
    while os.path.exists(p):
        p = os.path.join(folder, "%s-%s (%d).md" % (day, slug(name), n))
        n += 1
    return p


def render(day, src, rel_src, transcript):
    return "\n".join([
        "# Voice memo, %s" % day,
        "",
        "From `%s`, transcribed on this computer. The recording was not changed." % rel_src,
        "",
        "## Transcript",
        "",
        transcript or "(nothing was heard)",
        "",
        "## Notes",
        "",
        "(the voice-memo skill fills this in from the transcript)",
        "",
        "## To do",
        "",
        "- [ ] (one line per task the recording named)",
        "",
    ])


def run(src, into, day=None, converter=convert, transcriber=transcribe, paths=whisper_paths):
    """Writes the memo file and returns (code, message)."""
    if not os.path.isfile(src):
        return 2, "No recording at %s." % src
    if not src.lower().endswith(AUDIO):
        return 2, "%s does not look like a recording (%s)." % (os.path.basename(src), ", ".join(AUDIO))
    cli, model = paths()
    if converter is convert and not shutil.which("ffmpeg"):
        return MISSING, "Missing: ffmpeg. Run: python tools/doctor/doctor.py"
    if transcriber is transcribe and not cli:
        return MISSING, "Missing: whisper-cli. Run: python tools/doctor/doctor.py"
    if transcriber is transcribe and not model:
        return MISSING, "Missing: whisper.cpp English model. Run: python tools/doctor/doctor.py"
    day = day or dt.date.fromtimestamp(os.path.getmtime(src)).isoformat()
    tmp = tempfile.mkdtemp(prefix="voice-memo-")
    try:
        wav = os.path.join(tmp, "audio.wav")
        converter(src, wav)
        text = clean(transcriber(wav, cli, model))
    except subprocess.CalledProcessError as e:
        return 1, "Transcription failed: %s" % e
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(into, exist_ok=True)
    out = output_path(into, day, src)
    try:
        rel_src = os.path.relpath(src, ROOT).replace(os.sep, "/")
    except ValueError:
        rel_src = src
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(render(day, src, rel_src, text))
    words = len(text.split())
    return 0, "%s (%d words). Read the transcript and fill in Notes and To do." % (out, words)


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("recording")
    p.add_argument("--into", default=os.path.join(ROOT, "voice-memos"), help="folder for the memo file")
    p.add_argument("--date", help="YYYY-MM-DD (default: the recording's file date)")
    args = p.parse_args(argv)
    code, msg = run(args.recording, args.into, args.date)
    print(msg)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
