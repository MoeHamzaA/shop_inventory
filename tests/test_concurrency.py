import pytest
import pandas as pd
import os
import sqlite3
import time
import threading
from contextlib import contextmanager
from app.models.database import get_db, load_inventory, save_inventory

# Ensure we use a test database
os.environ['DATABASE_PATH'] = 'test_inventory.db'

@pytest.fixture(scope="module")
def setup_test_db():
    """Setup a test database with sample data"""
    # Create test database
    conn = sqlite3.connect('test_inventory.db')
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
    
    # Add some test data
    test_data = [
        ('Toyota', 'Camry', '2020', 'Red', 5, 1),
        ('Honda', 'Civic', '2021', 'Blue', 3, 1),
        ('Ford', 'Mustang', '2019', 'Black', 2, 1)
    ]
    
    cursor.execute("DELETE FROM inventory")  # Clear existing data
    cursor.executemany(
        'INSERT INTO inventory (company, model, year, colour, quantity, version) VALUES (?, ?, ?, ?, ?, ?)',
        test_data
    )
    
    conn.commit()
    conn.close()
    
    yield
    
    # Cleanup after tests
    if os.path.exists('test_inventory.db'):
        os.remove('test_inventory.db')

@contextmanager
def get_test_db():
    """Get a database connection for testing"""
    conn = sqlite3.connect('test_inventory.db')
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def test_version_increment(setup_test_db):
    """Test that version is incremented after editing a car"""
    # Get current version
    with get_test_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM inventory WHERE company = 'Toyota' AND model = 'Camry'")
        initial_version = cursor.fetchone()[0]
    
    # Load inventory
    df = pd.read_sql_query("SELECT * FROM inventory", get_test_db())
    
    # Find Toyota Camry
    mask = (df["company"] == "Toyota") & (df["model"] == "Camry")
    
    # Update quantity
    car_idx = df.loc[mask].index[0]
    current_version = df.loc[car_idx, "version"]
    df.loc[car_idx, "quantity"] = 10
    df.loc[car_idx, "version"] = current_version + 1
    
    # Save inventory back
    with get_test_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory")
        for _, row in df.iterrows():
            cursor.execute('''
                INSERT INTO inventory (company, model, year, colour, quantity, version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['company'], row['model'], row['year'], row['colour'], row['quantity'], row['version']))
        conn.commit()
    
    # Check new version
    with get_test_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM inventory WHERE company = 'Toyota' AND model = 'Camry'")
        new_version = cursor.fetchone()[0]
    
    assert new_version == initial_version + 1

def test_concurrent_edits_no_conflict(setup_test_db):
    """Test concurrent edits to different cars"""
    def update_car(company, model, new_quantity):
        # Get car data
        with get_test_db() as conn:
            df = pd.read_sql_query("SELECT * FROM inventory", conn)
        
        # Find car
        mask = (df["company"] == company) & (df["model"] == model)
        
        # Update quantity
        car_idx = df.loc[mask].index[0]
        current_version = df.loc[car_idx, "version"]
        df.loc[car_idx, "quantity"] = new_quantity
        df.loc[car_idx, "version"] = current_version + 1
        
        # Save inventory back
        with get_test_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE company = ? AND model = ?", (company, model))
            row = df.loc[car_idx]
            cursor.execute('''
                INSERT INTO inventory (company, model, year, colour, quantity, version)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['company'], row['model'], row['year'], row['colour'], row['quantity'], row['version']))
            conn.commit()
    
    # Start threads to update different cars
    thread1 = threading.Thread(target=update_car, args=("Toyota", "Camry", 10))
    thread2 = threading.Thread(target=update_car, args=("Honda", "Civic", 8))
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    # Check results
    with get_test_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT quantity FROM inventory WHERE company = 'Toyota' AND model = 'Camry'")
        toyota_quantity = cursor.fetchone()[0]
        
        cursor.execute("SELECT quantity FROM inventory WHERE company = 'Honda' AND model = 'Civic'")
        honda_quantity = cursor.fetchone()[0]
    
    assert toyota_quantity == 10
    assert honda_quantity == 8

def test_optimistic_locking_simulation(setup_test_db):
    """Test optimistic locking when two users try to update the same car"""
    car_company = "Ford"
    car_model = "Mustang"
    
    # User 1 loads the form
    with get_test_db() as conn:
        df_user1 = pd.read_sql_query(f"SELECT * FROM inventory WHERE company = '{car_company}' AND model = '{car_model}'", conn)
    car_user1 = df_user1.iloc[0]
    user1_version = car_user1["version"]
    
    # User 2 loads the form
    with get_test_db() as conn:
        df_user2 = pd.read_sql_query(f"SELECT * FROM inventory WHERE company = '{car_company}' AND model = '{car_model}'", conn)
    car_user2 = df_user2.iloc[0]
    user2_version = car_user2["version"]
    
    # Both users have the same version initially
    assert user1_version == user2_version
    
    # User 1 submits the form first
    with get_test_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inventory 
            SET quantity = ?, version = ? 
            WHERE company = ? AND model = ? AND version = ?
        """, (10, user1_version + 1, car_company, car_model, user1_version))
        conn.commit()
        rows_updated = cursor.rowcount
    
    assert rows_updated == 1  # User 1's update succeeded
    
    # User 2 tries to submit after User 1
    with get_test_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE inventory 
            SET quantity = ?, version = ? 
            WHERE company = ? AND model = ? AND version = ?
        """, (15, user2_version + 1, car_company, car_model, user2_version))
        conn.commit()
        rows_updated = cursor.rowcount
    
    assert rows_updated == 0  # User 2's update should fail
    
    # Check the final state - it should be User 1's update
    with get_test_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT quantity, version FROM inventory WHERE company = ? AND model = ?", (car_company, car_model))
        result = cursor.fetchone()
        final_quantity, final_version = result
    
    assert final_quantity == 10  # User 1's quantity
    assert final_version == user1_version + 1  # Updated version 