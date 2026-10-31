#!/bin/bash
# Mac and Linux installer. On a Mac it gets Homebrew and Python in place; on Linux it makes sure
# python3 is there (apt). Then it hands over to runner.py, which walks setup/tools.json.
cd "$(dirname "$0")/.." || exit 1
if [ "$(uname -s)" = "Linux" ]; then
  echo
  echo "Setting up on Linux."
  echo
  if ! command -v python3 >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1; then
    if [ "$(id -u)" = "0" ]; then apt-get install -y python3; else sudo -n apt-get install -y python3; fi
  fi
  command -v python3 >/dev/null 2>&1 || { echo "python3 is missing and did not install"; exit 4; }
  export PATH="$HOME/.local/bin:$PATH"   # uv tool install and pipx put commands here
  python3 setup/runner.py --platform linux "$@"
  exit $?
fi
echo
echo "Setting up on a Mac. Your Mac may ask for your password to install Homebrew."
echo "If it downloads Apple's command-line tools first, that alone can take ten minutes."
echo
if ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || { echo "Homebrew did not install. Run setup again after it does."; exit 4; }
  if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi
  if [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)"; fi
fi
# Apple ships an old python3 stub, so test for a real 3.12+, not just for python3
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null && ! command -v python3.12 >/dev/null 2>&1; then
  brew install python@3.12
fi
export PATH="$HOME/.local/bin:$PATH"   # uv tool install puts commands here
PY=python3; command -v python3.12 >/dev/null 2>&1 && PY=python3.12
"$PY" setup/runner.py --platform mac "$@"
