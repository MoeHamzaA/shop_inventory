import sqlite3
from contextlib import contextmanager
import pandas as pd

# Database configuration
DATABASE = 'inventory.db'

@contextmanager
def get_db():
    """Get a database connection with proper transaction handling"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

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