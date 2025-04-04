#!/bin/bash

echo "Setting up virtual environment..."

# Step 1: Check and create venv if it doesn't exist
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
fi

echo "Creating virtual environment..."
if ! python3 -m venv venv; then
    echo "Error: Failed to create virtual environment" >&2
    echo "Trying alternative method..."
    if ! pip install virtualenv; then
        echo "Error: Failed to install virtualenv" >&2
        exit 1
    fi
    if ! virtualenv venv; then
        echo "Error: Failed to create virtual environment with virtualenv" >&2
        exit 1
    fi
fi

# Step 2: Activate the virtual environment
echo "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "Error: Could not find virtual environment activation script" >&2
    echo "Current directory: $(pwd)" >&2
    echo "Directory contents:" >&2
    ls -R venv
    exit 1
fi

# Step 3: Upgrade pip, setuptools, wheel
echo "Upgrading pip, setuptools, wheel..."
if ! python -m pip install --upgrade pip setuptools wheel; then
    echo "Error: Failed to upgrade pip, setuptools, wheel" >&2
    exit 1
fi

# Step 4: Install dependencies
echo "Installing dependencies from requirements.txt..."
if ! python -m pip install -r requirements.txt; then
    echo "Error: Failed to install dependencies" >&2
    exit 1
fi

# Step 5: Verify Flask installation
echo "Verifying Flask installation..."
if ! python -c "import flask"; then
    echo "Error: Flask is not installed correctly" >&2
    exit 1
fi

# Step 6: Set environment variables
echo "Setting Flask environment variables..."
export FLASK_APP=run.py
export FLASK_ENV=development

# Step 7: Run the Flask application
echo "Starting Flask application..."
if ! python -m flask run; then
    echo "Error: Failed to start Flask application" >&2
    exit 1
fi
