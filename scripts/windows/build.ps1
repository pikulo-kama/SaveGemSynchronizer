
Import-Module .\scripts\windows\util.psm1

# Check if configuration files are present.
Assert-File-Exists "credentials.json"
Assert-File-Exists "config.json"

# Install dependencies
pip install .

# Build executable with pyinstaller and create archive.
python -m PyInstaller --distpath output/dist --workpath output --clean --noconfirm build.spec
Remove-Item -Recurse -Force output/build

$DatabasePath = Join-Path $PWD.Path "output\dist\savegem.db"

# 1. Run Migrations
.\.venv\Scripts\kama-dbm.exe migrate `
    --migration_directories="$(Join-Path $PWD.Path "migration")" `
    --database="$DatabasePath"

# 2. Run the Import
.\.venv\Scripts\kama-dbm.exe import `
    --definition_file="$(Join-Path $PWD.Path "importData\import.def")" `
    --database="$DatabasePath"
