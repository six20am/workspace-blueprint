# When apt cannot reach its mirrors

For the agent, on Linux. Read this when `setup/setup-report.md` says the package source was unreachable, or when most of the failed tools are the apt ones.

The installer runs `apt-get update` once before the tools and records whether it worked. When it did not, every apt-based tool fails while the script still runs to the end, so the report can look like the blueprint broke. It did not. Check it yourself first:

```
sudo apt-get update
```

## First: do curl and apt disagree?

Before any route around apt, test whether apt is blocked or only lost. Take a mirror URL from the error and fetch it with curl:

```
curl -sI http://deb.debian.org/debian/ | head -1
```

If curl gets an answer and apt gets `500 Internal Server Error` or `SSL connection failed` from the same place, apt is not blocked. It is going straight out while curl goes through an egress proxy. Point apt at the same proxy. The address is in `$https_proxy` or `$http_proxy` when the machine sets one; on a hosted agent sandbox it was `http://127.0.0.1:8791` (2026-10-31):

```
echo 'Acquire::http::Proxy "http://127.0.0.1:8791"; Acquire::https::Proxy "http://127.0.0.1:8791";' | sudo tee /etc/apt/apt.conf.d/99egress-proxy
sudo apt-get update
```

The installer already tries this once on its own when `apt-get update` fails (the proxy from the environment first, then that address) and says so in the report. If it worked, the report has no "Package source unreachable" section and nothing here applies.

Then prove it with one real package, not an exit code:

```
sudo apt-get install -y jq && jq --version
```

Only when that proxy address is not present, or apt still fails with it, go to the routes below. Never conclude apt is blocked for good without the curl test.

## Routes around a blocked apt

The routes come from one outside run (a 500 from every mirror, on a hosted bot, 2026-10-31; the proxy fix above was found afterwards and would have ended it) and have not been tested here; test every tool after installing it, because a zero exit code is not proof.

| Tools | Route |
|---|---|
| tesseract, ghostscript, imagemagick, exiftool, sox, ocrmypdf | micromamba with the conda-forge channel |
| pandoc, qpdf, rtk | standalone binaries from each project's GitHub releases |
| whisper.cpp | build from source with cmake; conda-forge's `cxx-compiler` serves when there is no system gcc |
| mkvmerge | the MKVToolNix AppImage; conda-forge does not carry MKVToolNix |
| HandBrake | no route around a blocked apt. ffmpeg covers the same jobs; leave it failed |

Say what each route installs before you run it (ADAPT.md § Never). When a tool comes in by one of these routes, run `python3 tools/doctor/doctor.py` afterwards so the report shows it present.
