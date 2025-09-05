
Import-Module .\scripts\windows\util.psm1

# Check if configuration files are present.
Assert-File-Exists "credentials.json"
Assert-File-Exists "game-config-file-id.txt"

# Install dependencies
pip install -r requirements.txt

# Build executable with pyinstaller and create archive.
python -m PyInstaller --clean --noconfirm main.spec
New-Archive

# Remove build directory.
Remove-Item -Recurse -Force build
