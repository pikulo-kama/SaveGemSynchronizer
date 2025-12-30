#!/bin/bash

definition_file="$(pwd)/importData/import.def"
db_path="%APPDATA%/SaveGem/savegem.db"

# Import data.
kama-dbm import --definition_file="$definition_file" --database="$db_path"

# Rebuild window after data was imported.
echo "{\"command\": \"rebuild_window\"}" > /dev/tcp/127.0.0.1/53541
