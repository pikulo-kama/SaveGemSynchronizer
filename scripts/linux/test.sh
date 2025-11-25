#!/bin/bash


sub_package=$1

source_package="savegem"
tests_path="tests"

if [ -n "$sub_package" ]; then
  source_package="${source_package}.${sub_package}"
  tests_path="${tests_path}/${sub_package//./\/}"
fi

echo "Source package: $source_package"
echo "Tests path: $tests_path"

pytest "$tests_path" --cov="$source_package" --cov-report=term-missing
