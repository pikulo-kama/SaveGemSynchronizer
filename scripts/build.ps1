# Install dependencies
pip install -r requirements.txt
.\.venv\Scripts\activate.ps1

# Build executable with pyinstaller
pyinstaller --clean main.spec

# Remove EXE if exists
Remove-Item -Force "*.exe"

# Move built EXE from dist to current folder
Move-Item "dist\*.exe" "."

# Remove dist and build folders
Remove-Item -Recurse -Force dist, build
