#!/bin/bash

# Import helper methods.
source ./scripts/linux/util.sh

# Check if configuration files are present.
verify_file_exists "credentials.json"
verify_file_exists "game-config-file-id.txt"

# Install dependencies
pip install -r requirements.txt
apt install jq zip

# Build executable with pyinstaller
python -m PyInstaller --distpath output/dist --workpath output/build --clean --noconfirm main.spec
