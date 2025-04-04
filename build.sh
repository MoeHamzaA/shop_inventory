#!/bin/bash

echo "Setting up virtual environment..."

# Step 1: Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Step 2: Activate virtual environment
echo "Activating virtual environment..."
source venv/Scripts/activate  # Use this for Git Bash on Windows
# For Linux/Mac/WSL, use: source venv/bin/activate

# Step 3: Upgrade pip, setuptools, wheel
echo "Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

# Step 4: Install requirements
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Step 5: Set environment variables
echo "Setting Flask environment variables..."
export FLASK_APP=app.py
export FLASK_ENV=development

# Step 6: Run the app
echo "Starting Flask application..."
python -m flask run
