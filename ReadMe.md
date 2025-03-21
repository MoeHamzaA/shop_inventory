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
car_inventory_web_app/
│
├── app.py                   # Main Flask application
├── inventory.csv            # Car inventory data
├── dealership.csv           # Dealership database
│
└── templates/               # HTML templates
    ├── base.html            # Base template with layout and navigation
    ├── index.html           # Homepage with inventory table
    ├── add_manually.html    # Form to add cars manually
    ├── add_from_database.html  # Form to add cars from dealership DB
    ├── remove.html          # Interface to remove cars from inventory
    └── search.html          # Search interface
```

## Running the Application

Run the application with:
```bash
python app.py
```

Then open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

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

## Customization

You can easily customize the application by:
- Modifying the templates to change the UI
- Adding new fields to the inventory structure
- Extending functionality with additional features
