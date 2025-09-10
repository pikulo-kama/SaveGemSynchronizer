
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
