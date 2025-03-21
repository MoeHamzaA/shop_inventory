# Automotive Inventory System

A Flask-based web application with a clean, responsive UI for managing car inventory. This system allows dealerships to track their vehicle stock with ease.

## Features

- **Dashboard View**: Easily visualize your entire inventory
- **Add Vehicles**: 
  - Add cars manually with complete details
  - Add cars from a dealership database for quicker entry
- **Remove Vehicles**: Remove specific quantities from inventory
- **Search Functionality**: Search by company, model, year, or color
- **Data Persistence**: All data is stored in CSV files for simplicity and portability

## Prerequisites

- Python 3.6 or higher
- Flask
- Pandas

## Installation

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
├── build.sh                 # Build script to set up the environment and run the app
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
You can set up the application manually or use the build script to automate the process.
## Option 1: Manually
- Set up the environment by running:
```bash
python3 -m venv venv  # Create a virtual environment
source venv/bin/activate  # Activate the virtual environment (Linux/macOS)
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
## Option 2: Using the Build Script (build.sh)
To automate the setup process, you can run the build script:
- Make the build.sh file executable:
```bash
chmod +x build.sh
```
- Run the script:
```bash
./build.sh
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


