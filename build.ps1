# build.ps1

Write-Host "Setting up virtual environment..."

# Step 1: Check and create venv if it doesn't exist
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

# Step 2: Activate the virtual environment
Write-Host "Activating virtual environment..."
. .\venv\Scripts\Activate.ps1

# Step 3: Upgrade pip, setuptools, wheel
Write-Host "Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

# Step 4: Install dependencies
Write-Host "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Step 5: Set environment variables
Write-Host "Setting Flask environment variables..."
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"

# Step 6: Run the Flask application
Write-Host "Starting Flask application..."
python -m flask run
