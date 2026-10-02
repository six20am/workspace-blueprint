#!/bin/bash
# Mac installer. Gets Homebrew and Python in place, then hands over to mac_runner.py.
cd "$(dirname "$0")/.." || exit 1
echo
echo "Setting up on a Mac. Your Mac may ask for your password to install Homebrew."
echo "If it downloads Apple's command-line tools first, that alone can take ten minutes."
echo
if ! command -v brew >/dev/null 2>&1; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || { echo "Homebrew did not install. Run setup again after it does."; exit 4; }
  if [ -x /opt/homebrew/bin/brew ]; then eval "$(/opt/homebrew/bin/brew shellenv)"; fi
  if [ -x /usr/local/bin/brew ]; then eval "$(/usr/local/bin/brew shellenv)"; fi
fi
if ! command -v python3 >/dev/null 2>&1; then brew install python@3.12; fi
export PATH="$HOME/.local/bin:$PATH"   # uv tool install puts commands here
python3 setup/mac_runner.py "$@"
