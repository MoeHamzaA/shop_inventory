import pytest
import sqlite3
import re
from unittest.mock import patch
import time

def test_edit_version_increment(client, app):
    """Test that version number increments after edit"""
    # Insert test data directly into the database
    with app.app_context():
        conn = sqlite3.connect('test_inventory.db')
        cursor = conn.cursor()
        
        # Create inventory table if needed
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
        
        # Clear and insert test data
        cursor.execute("DELETE FROM inventory")
        cursor.execute('''
            INSERT INTO inventory (company, model, year, colour, quantity, version)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Test', 'Car', '2023', 'Red', 5, 1))
        conn.commit()
        
        # Get the ID of the inserted car
        cursor.execute("SELECT id FROM inventory WHERE company = 'Test'")
        car_id = cursor.fetchone()[0]
        conn.close()
    
    # Login first (simplified)
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    # Access the edit page for our test car
    response = client.get(f'/inventory/edit/{car_id}')
    assert response.status_code == 200
    
    # Extract version number from form for validation
    html = response.data.decode('utf-8')
    version_match = re.search(r'<input type="hidden" name="version" value="(\d+)"', html)
    assert version_match is not None
    current_version = int(version_match.group(1))
    
    # Submit edit form
    edit_response = client.post(f'/inventory/edit/{car_id}', data={
        'year': '2024',
        'colour': 'Blue',
        'quantity': '10',
        'version': current_version
    }, follow_redirects=True)
    assert edit_response.status_code == 200
    
    # Check that the version was incremented in the database
    with app.app_context():
        conn = sqlite3.connect('test_inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM inventory WHERE id = ?", (car_id,))
        new_version = cursor.fetchone()[0]
        conn.close()
    
    assert new_version == current_version + 1

def test_concurrent_edit_detection(client, app):
    """Test that concurrent edits are detected and prevented"""
    # Insert test data
    with app.app_context():
        conn = sqlite3.connect('test_inventory.db')
        cursor = conn.cursor()
        
        # Create inventory table if needed
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
        
        # Clear and insert test data
        cursor.execute("DELETE FROM inventory")
        cursor.execute('''
            INSERT INTO inventory (company, model, year, colour, quantity, version)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Concurrent', 'Test', '2023', 'Green', 3, 1))
        conn.commit()
        
        # Get the ID of the inserted car
        cursor.execute("SELECT id FROM inventory WHERE company = 'Concurrent'")
        car_id = cursor.fetchone()[0]
        conn.close()
    
    # Login
    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    # Simulate User 1 loading the edit form
    user1_response = client.get(f'/inventory/edit/{car_id}')
    assert user1_response.status_code == 200
    
    # Extract version from User 1's form
    html = user1_response.data.decode('utf-8')
    version_match = re.search(r'<input type="hidden" name="version" value="(\d+)"', html)
    assert version_match is not None
    user1_version = int(version_match.group(1))
    
    # Simulate User 2 loading the edit form
    user2_response = client.get(f'/inventory/edit/{car_id}')
    assert user2_response.status_code == 200
    
    # Extract version from User 2's form (should be the same as User 1)
    html = user2_response.data.decode('utf-8')
    version_match = re.search(r'<input type="hidden" name="version" value="(\d+)"', html)
    assert version_match is not None
    user2_version = int(version_match.group(1))
    
    assert user1_version == user2_version
    
    # User 1 submits their edit first
    user1_edit = client.post(f'/inventory/edit/{car_id}', data={
        'year': '2024',
        'colour': 'Yellow',
        'quantity': '7',
        'version': user1_version
    }, follow_redirects=True)
    assert user1_edit.status_code == 200
    
    # Check that User 1's edit was successful
    with app.app_context():
        conn = sqlite3.connect('test_inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT colour, version FROM inventory WHERE id = ?", (car_id,))
        row = cursor.fetchone()
        colour, new_version = row
        conn.close()
    
    assert colour == 'Yellow'
    assert new_version == user1_version + 1
    
    # User 2 attempts to submit their edit with the old version number
    user2_edit = client.post(f'/inventory/edit/{car_id}', data={
        'year': '2024',
        'colour': 'Purple',
        'quantity': '5',
        'version': user2_version
    }, follow_redirects=True)
    assert user2_edit.status_code == 200
    
    # Check that the response contains a concurrency error message
    assert b'modified by another user' in user2_edit.data
    
    # Verify that the database still has User 1's values
    with app.app_context():
        conn = sqlite3.connect('test_inventory.db')
        cursor = conn.cursor()
        cursor.execute("SELECT colour, version FROM inventory WHERE id = ?", (car_id,))
        row = cursor.fetchone()
        final_colour, final_version = row
        conn.close()
    
    assert final_colour == 'Yellow'  # User 1's value remains
    assert final_version == user1_version + 1  # Version after User 1's update 