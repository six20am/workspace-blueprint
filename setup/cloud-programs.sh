#!/usr/bin/env bash
# Puts the Blueprint programs back on a hosted cloud computer that an AI agent runs on.
# Those computers are rebuilt every few hours and lose what was installed, while the files
# in the agent's own folder stay. Run this before a task that needs the programs.
#
#   bash setup/cloud-programs.sh           # install what is missing
#   bash setup/cloud-programs.sh --check   # say what is missing, install nothing
#
# Safe to run any time: it skips anything already there, so a second run takes seconds.
# Installs only. Nothing here signs in, takes a key or a cookie, or puts anything live.
# Claude Code itself, its plugins, its hooks and its MCP hookups are left out: they belong
# to a desktop install (setup/setup.sh). setup/tools.json stays the full list; this file
# follows its Linux column for the programs a cloud agent can use, plus two image editors.
# Log: /tmp/cloud-programs.log

LOG=/tmp/cloud-programs.log
VENV=/opt/wb-venv
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
START=$(date +%s)
echo "== $(date -u +%FT%TZ) cloud-programs run" >> "$LOG"
say() { echo "$*" | tee -a "$LOG"; }
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
export PATH="$HOME/.local/bin:$PATH"
UV=$(command -v uv || echo "$HOME/.local/bin/uv")

# --check: one line per program, ok or missing, and nothing installed
if [ "$1" = "--check" ]; then
  for c in tesseract qpdf exiftool sox gs mkvmerge HandBrakeCLI ffmpeg convert pandoc pdftotext jq gimp-console inkscape \
           markitdown trafilatura yt-dlp gallery-dl ocrmypdf agent-reach scrapling notebooklm wrangler defuddle repomix; do
    if command -v "$c" >/dev/null 2>&1 || [ -x "$VENV/bin/$c" ]; then echo "ok      $c"; else echo "missing $c"; fi
  done
  [ -x "$HOME/tools/whisper/src/build/bin/whisper-cli" ] && echo "ok      whisper-cli" || echo "missing whisper-cli"
  [ -f "$HOME/tools/whisper/models/ggml-base.en.bin" ] && echo "ok      whisper model" || echo "missing whisper model"
  [ -f /opt/wb-chromium/node_modules/@sparticuz/chromium/package.json ] && echo "ok      chromium package" || echo "missing chromium package"
  [ -d /opt/wb-motion/node_modules/remotion ] && echo "ok      remotion" || echo "missing remotion"
  [ -f "$HOME/tools/video-shotcraft/SKILL.md" ] && echo "ok      video-shotcraft" || echo "missing video-shotcraft"
  [ -f "$HOME/tools/awesome-ai-motion/index.json" ] && echo "ok      awesome-ai-motion" || echo "missing awesome-ai-motion"
  exit 0
fi

# 1. System programs (apt), plus GIMP and Inkscape for image and vector work.
#    Pairs are command:package.
APT_PAIRS="tesseract:tesseract-ocr qpdf:qpdf exiftool:libimage-exiftool-perl sox:sox gs:ghostscript mkvmerge:mkvtoolnix HandBrakeCLI:handbrake-cli ffmpeg:ffmpeg convert:imagemagick pandoc:pandoc pdftotext:poppler-utils jq:jq gimp-console:gimp inkscape:inkscape"
MISSING_APT=""
for pair in $APT_PAIRS; do
  cmd=${pair%%:*}; pkg=${pair#*:}
  if command -v "$cmd" >/dev/null 2>&1; then say "ok      $cmd"; else MISSING_APT="$MISSING_APT $pkg"; fi
done
if [ -n "$MISSING_APT" ]; then
  say "install apt:$MISSING_APT"
  if $SUDO apt-get update -qq >>"$LOG" 2>&1 && $SUDO apt-get install -y -qq --no-install-recommends $MISSING_APT >>"$LOG" 2>&1; then
    say "done    apt"
  else
    say "FAILED  apt (see $LOG, then setup/no-apt-fallbacks.md)"
  fi
fi

# 2. Python programs, in their own environment at $VENV
PY_PKGS="markitdown[all] trafilatura yt-dlp gallery-dl ocrmypdf"
PY_CMDS="markitdown trafilatura yt-dlp gallery-dl ocrmypdf"
NEED_PY=0
for c in $PY_CMDS; do [ -x "$VENV/bin/$c" ] && say "ok      $c" || NEED_PY=1; done
if [ "$NEED_PY" = 1 ]; then
  say "install python: $PY_PKGS"
  if [ -x "$UV" ]; then
    [ -d "$VENV" ] || "$UV" venv -q "$VENV" >>"$LOG" 2>&1
    "$UV" pip install -q --python "$VENV/bin/python" $PY_PKGS >>"$LOG" 2>&1 && say "done    python" || say "FAILED  python (see $LOG)"
  else
    python3 -m venv "$VENV" >>"$LOG" 2>&1 && "$VENV/bin/pip" install -q $PY_PKGS >>"$LOG" 2>&1 && say "done    python" || say "FAILED  python (see $LOG)"
  fi
fi
# Put the Python programs on the path for this shell and later ones
for c in $PY_CMDS; do
  [ -x "$VENV/bin/$c" ] && [ ! -e "/usr/local/bin/$c" ] && $SUDO ln -s "$VENV/bin/$c" "/usr/local/bin/$c" 2>/dev/null
done

# 3. The command-line tools from setup/tools.json. Install only: these sign in to nothing here.
for tool in "agent-reach:agent-reach" "scrapling:scrapling[fetchers]" "notebooklm:notebooklm-py[browser]"; do
  cmd=${tool%%:*}; spec=${tool#*:}
  if command -v "$cmd" >/dev/null 2>&1; then say "ok      $cmd"
  else "$UV" tool install -q "$spec" >>"$LOG" 2>&1 && say "done    $cmd" || say "FAILED  $cmd (see $LOG)"; fi
done
for tool in wrangler defuddle repomix; do
  if command -v "$tool" >/dev/null 2>&1; then say "ok      $tool"
  else npm install -g --no-audit --no-fund "$tool" >>"$LOG" 2>&1 && say "done    $tool" || say "FAILED  $tool (see $LOG)"; fi
done

# 4. whisper.cpp v1.9.1, built from source, plus its English base model
W="$HOME/tools/whisper"
if [ -x "$W/src/build/bin/whisper-cli" ]; then say "ok      whisper-cli"
else
  command -v cmake >/dev/null 2>&1 || $SUDO apt-get install -y -qq build-essential cmake >>"$LOG" 2>&1
  mkdir -p "$W/models"
  [ -d "$W/src" ] || git clone -q --depth 1 --branch v1.9.1 https://github.com/ggml-org/whisper.cpp "$W/src" >>"$LOG" 2>&1
  cmake -S "$W/src" -B "$W/src/build" -DCMAKE_BUILD_TYPE=Release >>"$LOG" 2>&1 \
    && cmake --build "$W/src/build" -j --config Release >>"$LOG" 2>&1 \
    && say "done    whisper-cli" || say "FAILED  whisper-cli (see $LOG)"
fi
if [ -f "$W/models/ggml-base.en.bin" ]; then say "ok      whisper model"
else
  mkdir -p "$W/models"
  curl -fsSL -o "$W/models/ggml-base.en.bin.part" https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin >>"$LOG" 2>&1 \
    && mv -f "$W/models/ggml-base.en.bin.part" "$W/models/ggml-base.en.bin" && say "done    whisper model" \
    || { rm -f "$W/models/ggml-base.en.bin.part"; say "FAILED  whisper model (the download site is blocked from here; use a transcription service instead)"; }
fi

# 5. A Chromium browser from the npm registry, for computers whose network blocks the usual
#    browser downloads but allows npm. Remotion renders with it (step 6) and Playwright can use it.
#    Pinned to one version. The binary unpacks to /tmp/chromium the first time it is asked for.
CHROME_DIR=/opt/wb-chromium
CHROME_VER=131.0.1
if [ -f "$CHROME_DIR/node_modules/@sparticuz/chromium/package.json" ]; then say "ok      chromium package"
else
  $SUDO mkdir -p "$CHROME_DIR" && $SUDO chown "$(id -u)" "$CHROME_DIR"
  npm install --prefix "$CHROME_DIR" --no-audit --no-fund "@sparticuz/chromium@$CHROME_VER" >>"$LOG" 2>&1 \
    && say "done    chromium package" || say "FAILED  chromium package (see $LOG)"
fi
CHROME_BIN=$(cd "$CHROME_DIR" 2>/dev/null && node -e "const c=require('@sparticuz/chromium');(c.default||c).executablePath().then(p=>console.log(p)).catch(()=>{})" 2>>"$LOG")
if [ -n "$CHROME_BIN" ] && "$CHROME_BIN" --version >>"$LOG" 2>&1; then
  say "ok      chromium ($CHROME_BIN)"
  echo "export REMOTION_BROWSER_EXECUTABLE=$CHROME_BIN" > /tmp/wb-browser.env
else
  say "FAILED  chromium (see $LOG)"
fi

# 6. Remotion: a working copy of tools/motion at /opt/wb-motion, kept out of the agent's own
#    folder because node_modules is large. --ignore-scripts skips its own browser download,
#    which step 5 replaces.
MOTION=/opt/wb-motion
SRC="$ROOT/tools/motion"
if [ -d "$MOTION/node_modules/remotion" ]; then
  say "ok      remotion"
  cp "$SRC/render.mjs" "$MOTION/render.mjs" 2>/dev/null   # keep the render script current
elif [ -f "$SRC/package.json" ]; then
  $SUDO mkdir -p "$MOTION" && $SUDO chown "$(id -u)" "$MOTION" && cp -r "$SRC/." "$MOTION/"
  npm install --prefix "$MOTION" --no-audit --no-fund --ignore-scripts >>"$LOG" 2>&1 && say "done    remotion (in $MOTION)" || say "FAILED  remotion (see $LOG)"
fi

# 7. The two shot libraries, pinned to the commits setup/tools.json names
clone_pinned() { # name url commit check-file
  if [ -f "$HOME/tools/$1/$4" ]; then say "ok      $1"; return; fi
  mkdir -p "$HOME/tools"; rm -rf "$HOME/tools/$1.part"
  git clone -q "$2" "$HOME/tools/$1.part" >>"$LOG" 2>&1 && git -C "$HOME/tools/$1.part" checkout -q "$3" >>"$LOG" 2>&1 \
    && mv "$HOME/tools/$1.part" "$HOME/tools/$1" && say "done    $1" || say "FAILED  $1 (see $LOG)"
}
clone_pinned video-shotcraft https://github.com/Vincentwei1021/video-shotcraft.git 41ee360d82f4c491ba9d88a24a4add7d8ff1cf8b SKILL.md
clone_pinned awesome-ai-motion https://github.com/gongnyang/awesome-ai-motion.git 1e3c249073c61b42ceb556d7800f628d565d9312 index.json

say "finished in $(( $(date +%s) - START ))s"
[ -f /tmp/wb-browser.env ] && say "To render video: source /tmp/wb-browser.env, then node $MOTION/render.mjs ..."
