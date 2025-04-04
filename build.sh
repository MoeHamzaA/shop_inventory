#!/bin/bash

echo "Setting up virtual environment..."

# Step 1: Check and create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment" >&2
        exit 1
    fi
fi

# Step 2: Activate the virtual environment
echo "Activating virtual environment..."
if [ -f "venv/Scripts/activate" ]; then
    # Windows Git Bash
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    # Unix/Linux
    source venv/bin/activate
else
    echo "Error: Could not find virtual environment activation script" >&2
    echo "Expected paths:" >&2
    echo "  - venv/Scripts/activate (Windows)" >&2
    echo "  - venv/bin/activate (Unix/Linux)" >&2
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "Error: Could not activate virtual environment" >&2
    exit 1
fi

# Step 3: Upgrade pip, setuptools, wheel
echo "Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo "Error: Failed to upgrade pip, setuptools, wheel" >&2
    exit 1
fi

# Step 4: Install dependencies
echo "Installing dependencies from requirements.txt..."
python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies" >&2
    exit 1
fi

# Step 5: Verify Flask installation
echo "Verifying Flask installation..."
python -c "import flask"
if [ $? -ne 0 ]; then
    echo "Error: Flask is not installed correctly" >&2
    exit 1
fi
echo "Flask installation verified successfully"

# Step 6: Set environment variables
echo "Setting Flask environment variables..."
export FLASK_APP="app.py"
export FLASK_ENV="development"

# Step 7: Run the Flask application
echo "Starting Flask application..."
python -m flask run
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Flask application" >&2
    exit 1
fi
