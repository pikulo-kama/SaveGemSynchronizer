
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

# rename_file: used to rename EXE file to have version and type.
# Usage: rename_file "file.exe" -> "file-1.1.1-SNAPSHOT.exe
make_archive() {
  local version
  local branch
  local zipName
  local type="SNAPSHOT"

  version="$(jq -r '.version' ./config/main.json)"
  branch="$(git branch --show-current)"

  if [[ "$branch" == "master" ]]; then
    type="RELEASE"
  fi

  zipName="builds/SaveGem-$version-$type.zip"

  zip -r "$zipName" "dist/SaveGem"
  echo "Created archive: $zipName"
}
