# Create a virtual environment
Write-Host "Creating virtual environment..."
python -m venv venv

# Activate the virtual environment
Write-Host "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install dependencies from requirements.txt
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Set environment variables (for Flask app)
Write-Host "Setting Flask environment variables..."
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

# Run the Flask application
Write-Host "Starting Flask application..."
flask run 