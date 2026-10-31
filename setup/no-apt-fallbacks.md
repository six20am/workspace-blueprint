# When apt cannot reach its mirrors

For the agent, on Linux. Read this when `setup/setup-report.md` says the package source was unreachable, or when most of the failed tools are the apt ones.

The installer runs `apt-get update` once before the tools and records whether it worked. When it did not, every apt-based tool fails while the script still runs to the end, so the report can look like the blueprint broke. It did not. Check it yourself first:

```
sudo apt-get update
```

If that prints errors (a 500 from every mirror through a proxy was the case on the first outside run, on Grok's bot, 2026-10-31), use the routes below. They come from that one run and have not been tested here; test every tool after installing it, because a zero exit code is not proof.

| Tools | Route |
|---|---|
| tesseract, ghostscript, imagemagick, exiftool, sox, ocrmypdf | micromamba with the conda-forge channel |
| pandoc, qpdf, rtk | standalone binaries from each project's GitHub releases |
| whisper.cpp | build from source with cmake; conda-forge's `cxx-compiler` serves when there is no system gcc |
| mkvmerge | the MKVToolNix AppImage; conda-forge does not carry MKVToolNix |
| HandBrake | no route around a blocked apt. ffmpeg covers the same jobs; leave it failed |

Say what each route installs before you run it (ADAPT.md § Never). When a tool comes in by one of these routes, run `python3 tools/doctor/doctor.py` afterwards so the report shows it present.
