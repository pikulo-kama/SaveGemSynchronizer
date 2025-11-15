#!/bin/bash

# Check if a Python file path was provided
if [ -z "$1" ]; then
    echo "Error: Service name was not provided."
    echo "Usage: ./profiler.sh app"
    exit 1
fi

service_name=$1
profile_file="output/$(basename "$service_name").prof"

echo "--- Starting cProfile on: $service_name ---"
python -m cProfile -o "$profile_file" "savegem/$service_name/main.py"
echo "--- Profile data saved to: $profile_file ---"

echo "--- Starting SnakeViz visualization ---"
snakeviz "$profile_file"
