from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models.database import load_inventory, save_inventory, load_dealership
import pandas as pd
from flask_login import login_required

# Create a Blueprint for inventory routes
inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/')
@login_required
def index():
    """Display the inventory"""
    inventory = load_inventory()
    return render_template('index.html', inventory=inventory)

@inventory_bp.route('/add_manually', methods=['GET', 'POST'])
@login_required
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
                return redirect(url_for('inventory.add_manually'))
        except ValueError:
            flash('Please enter a valid number for quantity', 'danger')
            return redirect(url_for('inventory.add_manually'))
            
        # Validate year input
        if not (year.isdigit() and len(year) == 4):
            flash('Invalid year format. Please enter a 4-digit year', 'danger')
            return redirect(url_for('inventory.add_manually'))
        
        df = load_inventory()
        
        # Check if identical car already exists in inventory
        mask = (df["company"].str.lower() == company.lower()) & \
               (df["model"].str.lower() == model.lower()) & \
               (df["year"] == year) & \
               (df["colour"].str.lower() == colour.lower())
        
        if any(mask):
            # Car exists, increment quantity
            idx = df.loc[mask].index[0]
            current_qty = df.loc[idx, "quantity"]
            df.loc[idx, "quantity"] = current_qty + quantity
            car_id = df.loc[idx, "id"]
            flash(f'Added {quantity} to existing inventory (ID: {car_id}). Total quantity now: {df.loc[idx, "quantity"]}', 'success')
        else:
            # Add new car
            new_row = pd.DataFrame([{
                "id": len(df) + 1,
                "company": company,
                "model": model,
                "year": year,
                "colour": colour,
                "quantity": quantity,
                "version": 1
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            flash(f'Added new car to inventory (ID: {len(df)})', 'success')
        
        save_inventory(df)
        return redirect(url_for('inventory.index'))
        
    return render_template('add_manually.html')

@inventory_bp.route('/add_from_database', methods=['GET', 'POST'])
@login_required
def add_from_database():
    """Add car to inventory from dealership database"""
    dealership_db = load_dealership()
    
    if dealership_db.empty:
        flash('Dealership database not found or empty', 'danger')
        return redirect(url_for('inventory.index'))
    
    companies = sorted(dealership_db["company"].unique())
    
    if request.method == 'POST':
        selected_company = request.form['company']
        selected_model = request.form['model']
        year = request.form['year'].strip()
        colour = request.form['colour'].strip().title()
        
        try:
            quantity = int(request.form['quantity'].strip())
            if quantity <= 0:
                flash('Quantity must be greater than 0', 'danger')
                return redirect(url_for('inventory.add_from_database'))
        except ValueError:
            flash('Please enter a valid number for quantity', 'danger')
            return redirect(url_for('inventory.add_from_database'))
            
        # Validate year input
        if not (year.isdigit() and len(year) == 4):
            flash('Invalid year format. Please enter a 4-digit year', 'danger')
            return redirect(url_for('inventory.add_from_database'))
        
        df = load_inventory()
        
        # Check if identical car already exists in inventory
        mask = (df["company"].str.lower() == selected_company.lower()) & \
               (df["model"].str.lower() == selected_model.lower()) & \
               (df["year"] == year) & \
               (df["colour"].str.lower() == colour.lower())
        
        if any(mask):
            # Car exists, increment quantity
            idx = df.loc[mask].index[0]
            current_qty = df.loc[idx, "quantity"]
            df.loc[idx, "quantity"] = current_qty + quantity
            car_id = df.loc[idx, "id"]
            flash(f'Added {quantity} to existing inventory (ID: {car_id}). Total quantity now: {df.loc[idx, "quantity"]}', 'success')
        else:
            # Add new car
            new_row = pd.DataFrame([{
                "id": len(df) + 1,
                "company": selected_company,
                "model": selected_model,
                "year": year,
                "colour": colour,
                "quantity": quantity,
                "version": 1
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            flash(f'Added new car to inventory (ID: {len(df)})', 'success')
        
        save_inventory(df)
        return redirect(url_for('inventory.index'))
    
    return render_template('add_from_database.html', companies=companies)

@inventory_bp.route('/get_models/<company>')
@login_required
def get_models(company):
    """Get models for a specific company"""
    dealership_db = load_dealership()
    filtered_db = dealership_db[dealership_db["company"].str.lower() == company.lower()]
    models = sorted(filtered_db["model"].unique())
    return jsonify({"models": models})

@inventory_bp.route('/remove', methods=['GET', 'POST'])
@login_required
def remove_inventory():
    """Remove cars from inventory"""
    inventory = load_inventory()
    
    if inventory.empty:
        flash('Inventory is empty', 'info')
        return redirect(url_for('inventory.index'))
    
    if request.method == 'POST':
        car_id = int(request.form['car_id'])
        quantity_to_remove = int(request.form['quantity'])
        
        # Find the car
        mask = inventory["id"] == car_id
        if not any(mask):
            flash('Car ID not found in inventory', 'danger')
            return redirect(url_for('inventory.remove_inventory'))
            
        car_idx = inventory.loc[mask].index[0]
        car_info = inventory.loc[car_idx]
        current_quantity = car_info["quantity"]
        
        if quantity_to_remove > current_quantity:
            flash('Cannot remove more than available quantity', 'danger')
            return redirect(url_for('inventory.remove_inventory'))
        
        # Remove cars
        if quantity_to_remove >= current_quantity:
            inventory = inventory[~mask]
            flash(f'Removed all {car_info["company"]} {car_info["model"]} (ID: {car_id}) from inventory', 'success')
        else:
            inventory.loc[car_idx, "quantity"] -= quantity_to_remove
            flash(f'Removed {quantity_to_remove} {car_info["company"]} {car_info["model"]} from inventory. Remaining: {inventory.loc[car_idx, "quantity"]}', 'success')
        
        save_inventory(inventory)
        return redirect(url_for('inventory.index'))
    
    return render_template('remove.html', inventory=inventory)

@inventory_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search_inventory():
    """Search inventory by various criteria"""
    inventory = load_inventory()
    results = pd.DataFrame()
    search_performed = False
    
    if inventory.empty:
        flash('Inventory is empty', 'info')
        return redirect(url_for('inventory.index'))
    
    if request.method == 'POST':
        search_type = request.form['search_type']
        search_term = request.form['search_term'].strip().lower()
        search_performed = True
        
        if search_type == 'company':
            results = inventory[inventory["company"].str.lower().str.contains(search_term)]
        elif search_type == 'model':
            results = inventory[inventory["model"].str.lower().str.contains(search_term)]
        elif search_type == 'year':
            results = inventory[inventory["year"].astype(str) == search_term]
        elif search_type == 'colour':
            results = inventory[inventory["colour"].str.lower().str.contains(search_term)]
    
    return render_template('search.html', results=results, search_performed=search_performed)

@inventory_bp.route('/edit/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    """Edit car details in inventory"""
    inventory = load_inventory()
    
    # Find the car
    mask = inventory["id"] == car_id
    if not any(mask):
        flash('Car ID not found in inventory', 'danger')
        return redirect(url_for('inventory.index'))
    
    car = inventory.loc[mask].iloc[0]
    
    if request.method == 'POST':
        # Get the version number from the form
        submitted_version = int(request.form.get('version', 0))
        current_version = car["version"]
        
        # Check for concurrent modifications
        if submitted_version != current_version:
            flash('This car was modified by another user while you were editing. Please review the changes and try again.', 'danger')
            return redirect(url_for('inventory.edit_car', car_id=car_id))
        
        year = request.form['year'].strip()
        colour = request.form['colour'].strip().title()
        
        try:
            quantity = int(request.form['quantity'].strip())
            if quantity < 0:
                flash('Quantity cannot be negative', 'danger')
                return render_template('edit.html', car=car)
        except ValueError:
            flash('Please enter a valid number for quantity', 'danger')
            return render_template('edit.html', car=car)
            
        # Validate year input
        if not (year.isdigit() and len(year) == 4):
            flash('Invalid year format. Please enter a 4-digit year', 'danger')
            return render_template('edit.html', car=car)
        
        # Update the car details
        car_idx = inventory.loc[mask].index[0]
        inventory.loc[car_idx, "year"] = year
        inventory.loc[car_idx, "colour"] = colour
        inventory.loc[car_idx, "quantity"] = quantity
        inventory.loc[car_idx, "version"] = current_version + 1
        
        save_inventory(inventory)
        flash('Car details updated successfully', 'success')
        return redirect(url_for('inventory.index'))
    
    return render_template('edit.html', car=car) 