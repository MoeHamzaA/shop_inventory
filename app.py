from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import pandas as pd
import os
from flask_mail import Mail, Message
from datetime import datetime
import sqlite3
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = 'car_inventory_secret_key'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER', 'invevmomentum@outlook.com')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASSWORD', 'momentum123')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'invevmomentum@outlook.com')
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)

# Database configuration
DATABASE = 'inventory.db'

def init_db():
    """Initialize the database with required tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                model TEXT NOT NULL,
                year TEXT NOT NULL,
                colour TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                version INTEGER DEFAULT 1,
                UNIQUE(company, model, year, colour)
            )
        ''')
        
        # Create dealership table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dealership (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                model TEXT NOT NULL,
                UNIQUE(company, model)
            )
        ''')
        
        # Initialize dealership data if table is empty
        cursor.execute("SELECT COUNT(*) FROM dealership")
        if cursor.fetchone()[0] == 0:
            sample_data = [
                ('Toyota', 'Camry'),
                ('Toyota', 'Corolla'),
                ('Toyota', 'RAV4'),
                ('Honda', 'Civic'),
                ('Honda', 'Accord'),
                ('Honda', 'CR-V'),
                ('Ford', 'F-150'),
                ('Ford', 'Mustang'),
                ('Ford', 'Escape'),
                ('Chevrolet', 'Silverado'),
                ('Chevrolet', 'Malibu'),
                ('Chevrolet', 'Equinox')
            ]
            cursor.executemany('INSERT INTO dealership (company, model) VALUES (?, ?)', sample_data)
        
        conn.commit()

@contextmanager
def get_db():
    """Get a database connection with proper transaction handling"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def load_inventory():
    """Load inventory from database"""
    with get_db() as conn:
        df = pd.read_sql_query("SELECT * FROM inventory", conn)
        if df.empty:
            return pd.DataFrame(columns=["id", "company", "model", "year", "colour", "quantity", "version"])
        return df

def save_inventory(df):
    """Save inventory to database"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM inventory")
        
        # Insert new data
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO inventory (company, model, year, colour, quantity, version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['company'], row['model'], row['year'], row['colour'], row['quantity'], row['version']))
        
        conn.commit()

def load_dealership():
    """Load dealership database"""
    with get_db() as conn:
        df = pd.read_sql_query("SELECT * FROM dealership", conn)
        if df.empty:
            return pd.DataFrame(columns=["company", "model"])
        return df

def save_dealership(df):
    """Save dealership database"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM dealership")
        
        # Insert new data
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO dealership (company, model)
                VALUES (?, ?)
            ''', (row['company'], row['model']))
        
        conn.commit()

# Initialize database on startup
init_db()

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
                "quantity": quantity
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
    
    companies = sorted(dealership_db["company"].unique())
    
    if request.method == 'POST':
        selected_company = request.form['company']
        
        # For the initial company selection form
        if 'action' in request.form and request.form['action'] == 'select_company':
            # Filter models by selected company
            filtered_db = dealership_db[dealership_db["company"].str.lower() == selected_company.lower()]
            models = sorted(filtered_db["model"].unique())
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
            filtered_db = dealership_db[dealership_db["company"].str.lower() == selected_company.lower()]
            models = sorted(filtered_db["model"].unique())
            return render_template('add_from_database.html', 
                                  companies=companies, 
                                  selected_company=selected_company, 
                                  models=models)
        
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
                "quantity": quantity
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
        mask = inventory["id"] == car_id
        if not any(mask):
            flash('Car ID not found in inventory', 'danger')
            return redirect(url_for('remove_inventory'))
            
        car_idx = inventory.loc[mask].index[0]
        car_info = inventory.loc[car_idx]
        current_quantity = car_info["quantity"]
        
        if quantity_to_remove > current_quantity:
            flash('Cannot remove more than available quantity', 'danger')
            return redirect(url_for('remove_inventory'))
        
        # Remove cars
        if quantity_to_remove >= current_quantity:
            inventory = inventory[~mask]
            flash(f'Removed all {car_info["company"]} {car_info["model"]} (ID: {car_id}) from inventory', 'success')
        else:
            inventory.loc[car_idx, "quantity"] -= quantity_to_remove
            flash(f'Removed {quantity_to_remove} {car_info["company"]} {car_info["model"]} from inventory. Remaining: {inventory.loc[car_idx, "quantity"]}', 'success')
        
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

@app.route('/edit/<int:car_id>', methods=['GET', 'POST'])
@login_required
def edit_car(car_id):
    """Edit car details in inventory"""
    inventory = load_inventory()
    
    # Find the car
    mask = inventory["id"] == car_id
    if not any(mask):
        flash('Car ID not found in inventory', 'danger')
        return redirect(url_for('index'))
    
    car = inventory.loc[mask].iloc[0]
    
    if request.method == 'POST':
        # Get the version number from the form
        submitted_version = int(request.form.get('version', 0))
        current_version = car["version"]
        
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
        inventory.loc[car_idx, "year"] = year
        inventory.loc[car_idx, "colour"] = colour
        inventory.loc[car_idx, "quantity"] = quantity
        inventory.loc[car_idx, "version"] = current_version + 1
        
        save_inventory(inventory)
        flash('Car details updated successfully', 'success')
        return redirect(url_for('index'))
    
    return render_template('edit.html', car=car)

@app.route('/email_inventory', methods=['GET', 'POST'])
@login_required
def email_inventory():
    """Send inventory details via email"""
    inventory = load_inventory()
    
    if request.method == 'POST':
        recipient_email = request.form.get('recipient_email')
        subject = request.form.get('subject', 'Car Inventory Report')
        message = request.form.get('message', '')
        
        if not recipient_email:
            flash('Please enter a recipient email address', 'danger')
            return render_template('email.html', inventory=inventory)
        
        try:
            # Create email body
            email_body = f"""
            <html>
            <head>
                <style>
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .summary {{ margin-bottom: 20px; }}
                </style>
            </head>
            <body>
                <h2>Car Inventory Report</h2>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <div class="summary">
                    <h3>Summary</h3>
                    <p>Total Cars: {len(inventory)}</p>
                    <p>Total Quantity: {inventory['quantity'].sum()}</p>
                    <p>Unique Companies: {inventory['company'].nunique()}</p>
                </div>
                
                <h3>Detailed Inventory</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Company</th>
                        <th>Model</th>
                        <th>Year</th>
                        <th>Colour</th>
                        <th>Quantity</th>
                    </tr>
                    {inventory.to_html(index=False, classes='table table-striped')}
                </table>
                
                {f'<p>{message}</p>' if message else ''}
            </body>
            </html>
            """
            
            # Create and send email
            msg = Message(
                subject=subject,
                recipients=[recipient_email],
                html=email_body
            )
            
            mail.send(msg)
            flash('Inventory report sent successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'danger')
            return render_template('email.html', inventory=inventory)
    
    return render_template('email.html', inventory=inventory)

@app.route('/download_inventory')
@login_required
def download_inventory():
    """Download inventory as CSV file"""
    try:
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'car_inventory_{timestamp}.csv'
        
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
        # Try to delete the file after a short delay
        try:
            import time
            time.sleep(1)  # Wait for file to be sent
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass  # Ignore cleanup errors

if __name__ == '__main__':
    app.run(debug=True)