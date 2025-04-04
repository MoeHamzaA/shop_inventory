from flask import Blueprint, render_template, request, redirect, url_for, flash, session

# Create a Blueprint for auth routes
auth_bp = Blueprint('auth', __name__)

# Login credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def login_required(f):
    """Decorator to require login for routes"""
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('inventory.index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Handle logout"""
    session.pop('logged_in', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login')) 