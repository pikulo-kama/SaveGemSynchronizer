
# verify_file_exists: Verifies that a file exists.
# Usage: verify_file_exists "file.txt"
# Exits with error if the file is missing.
verify_file_exists() {
    local file="$1"

    if [ ! -f "$file" ]; then
        echo -e "\033[31mERROR: $file not found!\033[0m" >&2
        exit 1
    fi
}

# Check if configuration files are present.
verify_file_exists "credentials.json"
verify_file_exists "game-config-file-id.txt"

# Install dependencies
pip install -r requirements.txt
.venv/Scripts/activate

# Build executable with pyinstaller
pyinstaller --clean main.spec

# Move built EXE from dist to current folder
mv dist/*.exe .

# Remove dist and build folders
rm -fr dist build
