#!/bin/bash

# Define the Python script you want to run
PYTHON_SCRIPT="main.py"

# Define the commit message
COMMIT_MESSAGE="Auto-commit: $(date +'%Y-%m-%d %H:%M:%S')"

# Optional: change to a subdirectory if needed
# cd subdirectory

# Run the Python script with the default Python interpreter
python "$PYTHON_SCRIPT"

# Check if the Python script ran successfully
if [ $? -eq 0 ]; then
    echo "Python script ran successfully."
else
    echo "Python script encountered an error."
    exit 1
fi
