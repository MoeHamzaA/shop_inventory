from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_mail import Message
from app.models.database import load_inventory
from datetime import datetime
import os

# Create a Blueprint for email routes
email_bp = Blueprint('email', __name__)

@email_bp.route('/email_inventory', methods=['GET', 'POST'])
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
            return redirect(url_for('inventory.index'))
            
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'danger')
            return render_template('email.html', inventory=inventory)
    
    return render_template('email.html', inventory=inventory)

@email_bp.route('/download_inventory')
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
        return redirect(url_for('inventory.index'))
    finally:
        # Try to delete the file after a short delay
        try:
            import time
            time.sleep(1)  # Wait for file to be sent
            if os.path.exists(filename):
                os.remove(filename)
        except:
            pass  # Ignore cleanup errors 