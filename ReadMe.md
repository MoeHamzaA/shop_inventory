# 🚗 Automotive Inventory System

![Python](https://img.shields.io/badge/Python-3.6%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-green)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen)

A **Flask-based web application** for managing car dealership inventory with a clean and responsive UI.

## 📦 Features

- 📊 **Dashboard View** — Visualize your full car inventory
- ➕ **Add Vehicles**
  - Manually with complete details
  - From a dealership database
- ➖ **Remove Vehicles** — Decrease stock or remove entries
- 🔍 **Advanced Search & Filtering**
  - Multi-criteria filtering (Company, Year, Colour)
  - Full-text search across multiple fields
  - Combine filters with text search
  - Real-time filter options based on inventory
- 💾 **Data Persistence** — Uses CSV for simple data management

## 🧰 Tech Stack

- Python 3.6+
- Flask
- Pandas
- HTML

## 🚀 Installation

### 🔁 Clone the Repo

1. Clone this repository or download the files
```bash
git clone https://github.com/MoeHamzaA/shop_inventory.git
cd car-inventory-management
```

2. Install the required dependencies
```bash
pip install -r requirements.txt
```

3. Ensure your file structure matches the following:
```
shop_inventory/
│
├── app.py                   # Main Flask application
├── build.sh                 # Linux/macOS build script
├── build.ps1                # Windows PowerShell build script
├── inventory.csv            # Car inventory data
├── dealership.csv           # Dealership database
│
└── templates/                   # HTML templates
    ├── base.html                # Base template with layout and navigation
    ├── index.html               # Homepage with inventory table
    ├── add_manually.html        # Form to add cars manually
    ├── add_from_database.html   # Form to add cars from dealership DB
    ├── remove.html              # Interface to remove cars from inventory
    └── search.html              # Search interface
```

## Running the Application

You can set up the application manually or use one of the build scripts to automate the process.

### Option 1: Manually

- Set up the environment by running:
```bash
# For Linux/macOS
python3 -m venv venv  # Create a virtual environment
source venv/bin/activate  # Activate the virtual environment

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

- Install the required dependencies:
```bash
pip install -r requirements.txt
```

- Run the application:
```bash
python app.py
```

- Then open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

### Option 2: Using the Build Script for Linux/macOS (build.sh)

To automate the setup process on Linux or macOS:

1. Make the build.sh file executable:
```bash
chmod +x build.sh
```

2. Run the script:
```bash
./build.sh
```

This script will:
- Create a virtual environment
- Install dependencies from requirements.txt
- Run the Flask application

### Option 3: Using the Build Script for Windows (build.ps1)

To automate the setup process on Windows:

1. You may need to set PowerShell execution policy (as administrator):
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. Run the script:
```powershell
.\build.ps1
```

This script will:
- Create a virtual environment
- Install dependencies from requirements.txt
- Run the Flask application

## Usage

1. **View Inventory**: The homepage displays all cars currently in inventory
2. **Add Cars**:
   - Click "Add Manually" to enter all car details directly
   - Click "Add from Database" to select from existing manufacturers and models
3. **Remove Cars**: Use the remove functionality to decrease quantities or completely remove vehicles
4. **Search**: Use the search function to filter inventory based on different criteria

## Data Files

### inventory.csv
Contains the actual inventory with columns:
- ID
- Company
- Model
- Year
- Colour
- Quantity

### dealership.csv
Contains available makes and models with columns:
- Company
- Model

## Demo Video
https://drive.google.com/file/d/1XqB_C28z01U-Vjt_xFSCHk-9G7pHP-fM/view?usp=sharing
