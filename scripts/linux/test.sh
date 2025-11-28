#!/bin/bash


# Import helper methods.
source ./scripts/linux/util.sh

sub_package=$1
test_name=$2

source_package_list=("savegem")
tests_path_list=("tests")

for sub_package_part in $(string_split "$sub_package" "."); do

    # If test file provided directly it shouldn't be
    # included in package name.
    if [[ "$sub_package_part" == "test_"* ]]; then
      tests_path_list+=("$sub_package_part.py")
      continue
    fi

    source_package_list+=("$sub_package_part")
    tests_path_list+=("$sub_package_part")
done

source_package=$(array_join source_package_list ".")
tests_path=$(array_join tests_path_list "/")

if [ -n "$test_name" ]; then
  tests_path="$tests_path::$test_name"
fi

echo "Source package: $source_package"
echo "Tests path: $tests_path"

pytest "$tests_path" --cov="$source_package" --cov-report=term-missing
