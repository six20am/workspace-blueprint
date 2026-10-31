#!/bin/bash
cd "$(dirname "$0")" || exit 1
bash setup/setup.sh
echo
read -r -p "Press Enter to close this window."
