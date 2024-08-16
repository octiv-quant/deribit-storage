#!/bin/bash

# Define the Python script you want to run
PYTHON_SCRIPT="main.py"

# Define the commit message
COMMIT_MESSAGE="Auto-commit: $(date +'%Y-%m-%d %H:%M:%S')"

# Run the Python script
/app/octiv-pms/py311/bin/python3 $PYTHON_SCRIPT

# Check if the Python script ran successfully
if [ $? -eq 0 ]; then
    echo "Python script ran successfully."

    # Stage all changes (including new and modified files)
    git add .

    # Commit the changes with the timestamped commit message
    git commit -m "$COMMIT_MESSAGE"

    # Optional: Push the changes to the remote repository
    git push origin main

    echo "Changes have been committed."
else
    echo "Python script encountered an error."
fi
