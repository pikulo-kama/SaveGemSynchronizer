# Install dependencies
pip install -r requirements.txt
.venv/Scripts/activate

# Build executable with pyinstaller
pyinstaller --clean main.spec

# Move built EXE from dist to current folder
mv dist/*.exe .

# Remove dist and build folders
rm -fr dist build
