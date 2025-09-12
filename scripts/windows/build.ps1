
Import-Module .\scripts\windows\util.psm1

# Check if configuration files are present.
Assert-File-Exists "credentials.json"
Assert-File-Exists "config.json"

# Install dependencies
pip install -r requirements.txt

# Build executable with pyinstaller and create archive.
python -m PyInstaller --distpath output/dist --workpath output/build --clean --noconfirm build.spec