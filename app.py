from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'car_inventory_secret_key'

# File paths
inventory_file = "inventory.csv"
database_file = "dealership.csv"

def load_inventory():
    """Load inventory from CSV file or create empty DataFrame if file doesn't exist"""
    try:
        df = pd.read_csv(inventory_file)
        if df.empty:
            return pd.DataFrame(columns=["ID", "Company", "Model", "Year", "Colour", "Quantity"])
        # Ensure ID column exists
        if "ID" not in df.columns:
            df["ID"] = range(1, len(df) + 1)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["ID", "Company", "Model", "Year", "Colour", "Quantity"])

def save_inventory(df):
    """Save inventory DataFrame to CSV file"""
    # Ensure IDs are sequential
    df["ID"] = range(1, len(df) + 1)
    df.to_csv(inventory_file, index=False)

def load_dealership():
    """Load dealership database from CSV file"""
    try:
        return pd.read_csv(database_file)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["Company", "Model"])

@app.route('/')
def index():
    """Display the inventory"""
    inventory = load_inventory()
    return render_template('index.html', inventory=inventory)

@app.route('/add_manually', methods=['GET', 'POST'])
def add_manually():
    """Add car to inventory manually"""
    if request.method == 'POST':
        company = request.form['company'].strip().title()
        model = request.form['model'].strip().title()
        year = request.form['year'].strip()
        colour = request.form['colour'].strip().title()
        
        try:
            quantity = int(request.form['quantity'].strip())
            if quantity <= 0:
                flash('Quantity must be greater than 0', 'danger')
                return redirect(url_for('add_manually'))
        except ValueError:
            flash('Please enter a valid number for quantity', 'danger')
            return redirect(url_for('add_manually'))
            
        # Validate year input
        if not (year.isdigit() and len(year) == 4):
            flash('Invalid year format. Please enter a 4-digit year', 'danger')
            return redirect(url_for('add_manually'))
        
        df = load_inventory()
        
        # Check if identical car already exists in inventory - case insensitive comparison
        mask = (df["Company"].str.lower() == company.lower()) & \
               (df["Model"].str.lower() == model.lower()) & \
               (df["Year"] == year) & \
               (df["Colour"].str.lower() == colour.lower())
        
        if any(mask):
            # Car exists, increment quantity
            idx = df.loc[mask].index[0]
            current_qty = df.loc[idx, "Quantity"]
            df.loc[idx, "Quantity"] = current_qty + quantity
            car_id = df.loc[idx, "ID"]
            flash(f'Added {quantity} to existing inventory (ID: {car_id}). Total quantity now: {df.loc[idx, "Quantity"]}', 'success')
        else:
            # Add new car
            new_row = pd.DataFrame([{
                "ID": len(df) + 1,
                "Company": company,
                "Model": model,
                "Year": year,
                "Colour": colour,
                "Quantity": quantity
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            flash(f'Added new car to inventory (ID: {len(df)})', 'success')
        
        save_inventory(df)
        return redirect(url_for('index'))
        
    return render_template('add_manually.html')

@app.route('/add_from_database', methods=['GET', 'POST'])
def add_from_database():
    """Add car to inventory from dealership database"""
    dealership_db = load_dealership()
    
    if dealership_db.empty:
        flash('Dealership database not found or empty', 'danger')
        return redirect(url_for('index'))
    
    companies = sorted(dealership_db["Company"].unique())
    
    if request.method == 'POST':
        selected_company = request.form['company']
        
        # For the initial company selection form
        if 'action' in request.form and request.form['action'] == 'select_company':
            # Filter models by selected company
            filtered_db = dealership_db[dealership_db["Company"].str.lower() == selected_company.lower()]
            models = sorted(filtered_db["Model"].unique())
            return render_template('add_from_database.html', 
                                  companies=companies, 
                                  selected_company=selected_company, 
                                  models=models)
        
        # For the final form submission
        selected_model = request.form['model']
        year = request.form['year'].strip()
        colour = request.form['colour'].strip().title()
        
        try:
            quantity = int(request.form['quantity'].strip())
            if quantity <= 0:
                flash('Quantity must be greater than 0', 'danger')
                return redirect(url_for('add_from_database'))
        except ValueError:
            flash('Please enter a valid number for quantity', 'danger')
            return redirect(url_for('add_from_database'))
            
        # Validate year input
        if not (year.isdigit() and len(year) == 4):
            flash('Invalid year format. Please enter a 4-digit year', 'danger')
            filtered_db = dealership_db[dealership_db["Company"].str.lower() == selected_company.lower()]
            models = sorted(filtered_db["Model"].unique())
            return render_template('add_from_database.html', 
                                  companies=companies, 
                                  selected_company=selected_company, 
                                  models=models)
        
        df = load_inventory()
        
        # Check if identical car already exists in inventory
        mask = (df["Company"].str.lower() == selected_company.lower()) & \
               (df["Model"].str.lower() == selected_model.lower()) & \
               (df["Year"] == year) & \
               (df["Colour"].str.lower() == colour.lower())
        
        if any(mask):
            # Car exists, increment quantity
            idx = df.loc[mask].index[0]
            current_qty = df.loc[idx, "Quantity"]
            df.loc[idx, "Quantity"] = current_qty + quantity
            car_id = df.loc[idx, "ID"]
            flash(f'Added {quantity} to existing inventory (ID: {car_id}). Total quantity now: {df.loc[idx, "Quantity"]}', 'success')
        else:
            # Add new car
            new_row = pd.DataFrame([{
                "ID": len(df) + 1,
                "Company": selected_company,
                "Model": selected_model,
                "Year": year,
                "Colour": colour,
                "Quantity": quantity
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            flash(f'Added new car to inventory (ID: {len(df)})', 'success')
        
        save_inventory(df)
        return redirect(url_for('index'))
    
    return render_template('add_from_database.html', companies=companies)

@app.route('/remove', methods=['GET', 'POST'])
def remove_inventory():
    """Remove cars from inventory"""
    inventory = load_inventory()
    
    if inventory.empty:
        flash('Inventory is empty', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        car_id = int(request.form['car_id'])
        quantity_to_remove = int(request.form['quantity'])
        
        # Find the car
        mask = inventory["ID"] == car_id
        if not any(mask):
            flash('Car ID not found in inventory', 'danger')
            return redirect(url_for('remove_inventory'))
            
        car_idx = inventory.loc[mask].index[0]
        car_info = inventory.loc[car_idx]
        current_quantity = car_info["Quantity"]
        
        if quantity_to_remove > current_quantity:
            flash('Cannot remove more than available quantity', 'danger')
            return redirect(url_for('remove_inventory'))
        
        # Remove cars
        if quantity_to_remove >= current_quantity:
            inventory = inventory[~mask]
            flash(f'Removed all {car_info["Company"]} {car_info["Model"]} (ID: {car_id}) from inventory', 'success')
        else:
            inventory.loc[car_idx, "Quantity"] -= quantity_to_remove
            flash(f'Removed {quantity_to_remove} {car_info["Company"]} {car_info["Model"]} from inventory. Remaining: {inventory.loc[car_idx, "Quantity"]}', 'success')
        
        save_inventory(inventory)
        return redirect(url_for('index'))
    
    return render_template('remove.html', inventory=inventory)

@app.route('/search', methods=['GET', 'POST'])
def search_inventory():
    """Search inventory by various criteria"""
    inventory = load_inventory()
    results = pd.DataFrame()
    search_performed = False
    
    if inventory.empty:
        flash('Inventory is empty', 'info')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        search_type = request.form['search_type']
        search_term = request.form['search_term'].strip().lower()
        search_performed = True
        
        if search_type == 'company':
            results = inventory[inventory["Company"].str.lower().str.contains(search_term)]
        elif search_type == 'model':
            results = inventory[inventory["Model"].str.lower().str.contains(search_term)]
        elif search_type == 'year':
            results = inventory[inventory["Year"].astype(str) == search_term]
        elif search_type == 'colour':
            results = inventory[inventory["Colour"].str.lower().str.contains(search_term)]
    
    return render_template('search.html', results=results, search_performed=search_performed)

if __name__ == '__main__':
    app.run(debug=True)