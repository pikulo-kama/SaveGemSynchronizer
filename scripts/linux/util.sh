
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


# array_join: Used to join array elements into
# single string using provided delimiter.
# @param array - list with elements that needs to be joined
# @param delimiter - string delimiter that would be used to join array
# Usage: array_join ["1", "2"] ", " -> "12"
array_join() {
  declare -n array="$1"
  local delimiter="$2"

  local old_ifs=$IFS
  IFS="$delimiter"

  local joined_array="${array[*]}"
  IFS=$old_ifs

  echo "$joined_array"
}


# string_split: Used to split string using separator into
# iterable object.
# @param string - string to split into array
# @param delimiter - string that should be used as delimiter when splitting
# Usage: string_split "test:123" ":" -> ["test", "123"]
string_split() {
    local string="$1"
    local delimiter="$2"

    IFS="$delimiter" read -r -a parts <<< "$string"

    printf "%s\n" "${parts[@]}"
}
