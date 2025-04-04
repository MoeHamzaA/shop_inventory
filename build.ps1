# build.ps1

Write-Host "Setting up virtual environment..."

# Step 1: Check and create venv if it doesn't exist
if (Test-Path "venv") {
    Write-Host "Removing existing virtual environment..."
    Remove-Item -Recurse -Force venv
}

Write-Host "Creating virtual environment..."
try {
    # Try to create virtual environment with --clear flag
    python -m venv venv --clear
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment"
    }
} catch {
    Write-Host "Error creating virtual environment: $_" -ForegroundColor Red
    Write-Host "Trying alternative method..."
    try {
        # Try alternative method using virtualenv
        pip install virtualenv
        virtualenv venv
    } catch {
        Write-Host "Error with alternative method: $_" -ForegroundColor Red
        exit 1
    }
}

# Step 2: Activate the virtual environment
Write-Host "Activating virtual environment..."
$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Found activation script at: $activateScript"
    & $activateScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error activating virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Error: Could not find virtual environment activation script" -ForegroundColor Red
    Write-Host "Expected path: $activateScript" -ForegroundColor Red
    Write-Host "Current directory: $(Get-Location)" -ForegroundColor Red
    Write-Host "Directory contents:" -ForegroundColor Red
    Get-ChildItem -Path ".\venv" -Recurse | Select-Object FullName
    exit 1
}

# Step 3: Upgrade pip, setuptools, wheel
Write-Host "Upgrading pip, setuptools, wheel..."
try {
    python -m pip install --upgrade pip setuptools wheel
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade pip, setuptools, wheel"
    }
} catch {
    Write-Host "Error upgrading pip: $_" -ForegroundColor Red
    exit 1
}

# Step 4: Install dependencies
Write-Host "Installing dependencies from requirements.txt..."
try {
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
} catch {
    Write-Host "Error installing dependencies: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Verify Flask installation
Write-Host "Verifying Flask installation..."
try {
    python -c "import flask"
    Write-Host "Flask installation verified successfully" -ForegroundColor Green
} catch {
    Write-Host "Error: Flask is not installed correctly" -ForegroundColor Red
    exit 1
}

# Step 6: Set environment variables
Write-Host "Setting Flask environment variables..."
$env:FLASK_APP = "run.py"
$env:FLASK_ENV = "development"

# Step 7: Run the Flask application
Write-Host "Starting Flask application..."
try {
    python -m flask run
} catch {
    Write-Host "Error starting Flask application: $_" -ForegroundColor Red
    exit 1
}
