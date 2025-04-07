import pytest
import pandas as pd
from flask import Flask
from app import app  # <-- If your Flask file is named `app.py`
                     #    otherwise adjust the import accordingly.
from helpers import (
    load_inventory, save_inventory
)

@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Pytest fixture to create a test client for the Flask app.
    Also redirects the inventory file to a temporary location.
    """
    # Point to a temporary inventory file so we don't pollute real data
    test_inventory_file = tmp_path / "inventory.csv"
    monkeypatch.setattr("helpers.INVENTORY_FILE", str(test_inventory_file))
    
    # Create the test client
    app.testing = True
    with app.test_client() as client:
        yield client

def test_UT04_add_manually(client):
    """
    UT-04-TB
    Test the /add_manually route (POST).
    We expect a new entry in the inventory after the request.
    """
    # POST to /add_manually with form data
    response = client.post("/add_manually", data={
        "company": "Toyota",
        "model": "Corolla",
        "year": "2020",
        "colour": "Blue",
        "quantity": "1"
    }, follow_redirects=True)
    
    # Check for success message in the response data
    assert b"Added new car to inventory" in response.data
    
    # Verify the inventory actually has the new entry
    df = load_inventory()
    assert len(df) == 1, "Inventory should have 1 entry"
    car = df.iloc[0]
    assert car["Company"] == "Toyota"
    assert car["Model"] == "Corolla"
    assert car["Year"] == "2020"
    assert car["Colour"] == "Blue"
    assert car["Quantity"] == 1

def test_UT05_remove_car(client):
    """
    UT-05-TB
    Test the /remove route (POST).
    We will add a car first, then remove it via the route.
    """
    # Setup: add an entry manually
    df = pd.DataFrame([{
        "ID": 1,
        "Company": "Honda",
        "Model": "Civic",
        "Year": "2021",
        "Colour": "Red",
        "Quantity": 2,
        "Version": 1
    }])
    save_inventory(df)
    
    # Now remove 1 item from that car (ID=1)
    response = client.post("/remove", data={
        "car_id": 1,
        "quantity": 1
    }, follow_redirects=True)
    
    # Check success message
    assert b"Removed 1 Honda Civic from inventory" in response.data
    
    # Verify inventory updated
    updated_df = load_inventory()
    assert len(updated_df) == 1, "We should still have the row, just with updated quantity"
    assert updated_df.loc[0, "Quantity"] == 1, "Quantity should now be 1"

def test_year_validation(client):
    """
    UT-07-CB (Year Validation)
    Provide invalid year to the /add_manually route.
    Expect a flash message indicating invalid year format.
    """
    response = client.post("/add_manually", data={
        "company": "Toyota",
        "model": "Corolla",
        "year": "20X0",
        "colour": "Blue",
        "quantity": "1"
    }, follow_redirects=True)
    
    # Expect an error message
    assert b"Invalid year format. Please enter a 4-digit year" in response.data
    
    # Inventory should remain empty
    df = load_inventory()
    assert df.empty, "No valid entry should be added for an invalid year"

def test_quantity_validation(client):
    """
    UT-08-CB (Quantity Validation)
    Provide invalid quantity to the /add_manually route.
    Expect a flash message indicating invalid quantity.
    """
    response = client.post("/add_manually", data={
        "company": "Toyota",
        "model": "Corolla",
        "year": "2022",
        "colour": "Blue",
        "quantity": "-2"
    }, follow_redirects=True)
    
    # Expect an error message
    assert b"Please enter a valid number for quantity" in response.data
    
    # Inventory should remain empty
    df = load_inventory()
    assert df.empty, "No valid entry should be added for a negative quantity"
