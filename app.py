from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import os
import pandas as pd
from helpers import (
    load_inventory, save_inventory, load_dealership,
    generate_inventory_filename, cleanup_file
)

app = Flask(__name__)
app.secret_key = 'car_inventory_secret_key'

# Login credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login_required(f):
    """Decorator to require login for routes"""
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Handle logout"""
    session.pop('logged_in', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Display the inventory"""
    inventory = load_inventory()
    return render_template('index.html', inventory=inventory)

@app.route('/add_manually', methods=['GET', 'POST'])
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
@login_required
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
@login_required
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
@login_required
def search_inventory():
    """Search inventory by various criteria"""
    inventory = load_inventory()
    results = pd.DataFrame()
    search_performed = False
    
    if inventory.empty:
        flash('Inventory is empty', 'info')
        return redirect(url_for('index'))
    
    # Get unique values for filters
    companies = sorted(inventory['Company'].unique())
    years = sorted(inventory['Year'].unique())
    colours = sorted(inventory['Colour'].unique())
    
    if request.method == 'POST':
        search_performed = True
        filtered_inventory = inventory.copy()
        
        # Apply filters
        company_filter = request.form.get('company_filter')
        year_filter = request.form.get('year_filter')
        colour_filter = request.form.get('colour_filter')
        search_term = request.form.get('search_term', '').strip().lower()
        
        # Apply each filter if it's set
        if company_filter:
            filtered_inventory = filtered_inventory[filtered_inventory['Company'] == company_filter]
        if year_filter:
            filtered_inventory = filtered_inventory[filtered_inventory['Year'].astype(str) == year_filter]
        if colour_filter:
            filtered_inventory = filtered_inventory[filtered_inventory['Colour'] == colour_filter]
            
        # Apply search term across multiple fields if provided
        if search_term:
            mask = (
                filtered_inventory['Company'].str.lower().str.contains(search_term, na=False) |
                filtered_inventory['Model'].str.lower().str.contains(search_term, na=False) |
                filtered_inventory['Colour'].str.lower().str.contains(search_term, na=False)
            )
            filtered_inventory = filtered_inventory[mask]
        
        results = filtered_inventory
        
        # Pass the filter values back to the template
        return render_template('search.html',
                             results=results,
                             search_performed=search_performed,
                             companies=companies,
                             years=years,
                             colours=colours,
                             company_filter=company_filter,
                             year_filter=year_filter,
                             colour_filter=colour_filter,
                             search_term=search_term)
    
    # GET request - show empty form with filter options
    return render_template('search.html',
                         results=results,
                         search_performed=search_performed,
                         companies=companies,
                         years=years,
                         colours=colours)

@app.route('/edit/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    """Edit car details in inventory"""
    inventory = load_inventory()
    
    # Find the car
    mask = inventory["ID"] == car_id
    if not any(mask):
        flash('Car ID not found in inventory', 'danger')
        return redirect(url_for('index'))
    
    car = inventory.loc[mask].iloc[0]
    
    if request.method == 'POST':
        # Get the version number from the form
        submitted_version = int(request.form.get('version', 0))
        current_version = car["Version"]
        
        # Check for concurrent modifications
        if submitted_version != current_version:
            flash('This car was modified by another user while you were editing. Please review the changes and try again.', 'danger')
            return redirect(url_for('edit_car', car_id=car_id))
        
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
        inventory.loc[car_idx, "Year"] = year
        inventory.loc[car_idx, "Colour"] = colour
        inventory.loc[car_idx, "Quantity"] = quantity
        inventory.loc[car_idx, "Version"] = current_version + 1
        
        save_inventory(inventory)
        flash('Car details updated successfully', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit.html', car=car)

@app.route('/download_inventory')
@login_required
def download_inventory():
    """Download inventory as CSV file"""
    try:
        filename = generate_inventory_filename()
        
        # Create a copy of the inventory file with timestamp
        inventory = load_inventory()
        inventory.to_csv(filename, index=False)
        
        # Send the file and delete it after sending
        return send_file(
            filename,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename,
            conditional=True
        )
    except Exception as e:
        flash(f'Error downloading inventory: {str(e)}', 'danger')
        return redirect(url_for('index'))
    finally:
        cleanup_file(filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)