#!/bin/bash

# Import helper methods.
source ./scripts/linux/util.sh

# Check if configuration files are present.
verify_file_exists "credentials.json"
verify_file_exists "config.json"

# Install dependencies
pip install .
apt install jq zip

# Build executable with pyinstaller
python -m PyInstaller --distpath output/dist --workpath output --clean --noconfirm build.spec
rm -fr output/build

database_path="$(pwd)/output/dist/savegem.db"
.venv/Scripts/kama-dbm migrate --migration_directories="$(pwd)/migration" --database="$database_path"
.venv/Scripts/kama-dbm import --definition_file="$(pwd)/importData/import.def" --database="$database_path"
