from flask import Flask
from flask_mail import Mail
import os

# Initialize Flask-Mail
mail = Mail()

def create_app():
    """Create and configure the Flask application"""
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

    # Initialize Flask-Mail
    mail.init_app(app)

    # Initialize database
    from app.models.database import init_db
    init_db()

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.inventory import inventory_bp
    from app.routes.email import email_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(email_bp)

    return app 