#!/bin/bash

# Usage:
# bash run.sh --repo <Your-Github-Repo> --model <Huggingface-model-path>

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --repo) REPO_URL="$2"; shift ;;
        --model) MODEL_PATH="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Validate inputs
if [ -z "$REPO_URL" ] || [ -z "$MODEL_PATH" ]; then
    echo "Missing arguments."
    echo "Usage: bash run.sh --repo <Your-Github-Repo> --model <Huggingface-model-path>"
    exit 1
fi

# Run Streamlit app and pass arguments
echo "Starting Streamlit app with provided arguments..."
streamlit run src/app.py -- --repo_url "$REPO_URL" --model_name "$MODEL_PATH"