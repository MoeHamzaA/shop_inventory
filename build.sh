#!/bin/bash

# Update and install system dependencies (if needed)
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies from requirements.txt
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Set environment variables (for Flask app)
echo "Setting Flask environment variables..."
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the Flask application
echo "Starting Flask application..."
flask run
