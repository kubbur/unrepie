#!/bin/bash

echo "Setting up the Unrepie application..."

# Create a virtual environment
python3 -m venv venv

# Install dependencies and the package
source venv/bin/activate
pip install -e .

# Ensure the .ssh directory exists
SSH_DIR="$HOME/.ssh"
mkdir -p "$SSH_DIR"

# Ensure the instances directory exists
INSTANCES_DIR="instances"
mkdir -p "$INSTANCES_DIR"

# Generate SSH key if it doesn't exist
KEY_PATH="$SSH_DIR/id_rsa"
if [ ! -f "$KEY_PATH" ]; then
    ssh-keygen -t rsa -b 2048 -f "$KEY_PATH" -q -N ""
fi

echo "Setup complete. To run the application, use:"
echo "unrepie"
