import pytest
import pandas as pd
import os
from pathlib import Path
from helpers import (
    load_inventory, save_inventory, load_dealership,
    INVENTORY_FILE, DATABASE_FILE
)

@pytest.fixture
def clean_data_dir(tmp_path, monkeypatch):
    """
    Pytest fixture to redirect the data files (inventory.csv, dealership.csv)
    to a temporary directory so tests don’t affect real data.
    """
    # Point INVENTORY_FILE to a tmp_path
    test_inventory_file = tmp_path / "inventory.csv"
    test_dealership_file = tmp_path / "dealership.csv"
    
    # Monkeypatch the file paths
    monkeypatch.setattr("helpers.INVENTORY_FILE", str(test_inventory_file))
    monkeypatch.setattr("helpers.DATABASE_FILE", str(test_dealership_file))
    
    return tmp_path

def test_UT01_load_inventory_no_file_exists(clean_data_dir):
    """
    UT-01-CB
    Test load_inventory() when no inventory.csv file exists.
    Expected: An empty DataFrame with columns: ID, Company, Model, Year, Colour, Quantity, Version
    """
    df = load_inventory()
    assert df.empty, "DataFrame should be empty if file doesn't exist"
    expected_cols = ["ID", "Company", "Model", "Year", "Colour", "Quantity", "Version"]
    assert list(df.columns) == expected_cols, "DataFrame columns should match the expected schema"

def test_UT02_save_inventory_sequential_ids(clean_data_dir):
    """
    UT-02-CB
    Test save_inventory() to ensure IDs are sequential.
    """
    # Create a small DataFrame
    df = pd.DataFrame({
        "Company": ["Toyota", "Honda"],
        "Model": ["Corolla", "Civic"],
        "Year": ["2020", "2021"],
        "Colour": ["Blue", "Red"],
        "Quantity": [1, 2],
    })
    
    # Manually add ID out of sequence to simulate a user error
    df["ID"] = [10, 20]
    
    # Save the DataFrame
    save_inventory(df)
    
    # Reload inventory and check that IDs have been reassigned sequentially
    loaded_df = load_inventory()
    assert list(loaded_df["ID"]) == [1, 2], "IDs should be reassigned as [1, 2]"
    # Also check that the rest of the data was saved correctly
    assert loaded_df.loc[0, "Company"] == "Toyota"
    assert loaded_df.loc[1, "Model"] == "Civic"

def test_UT03_load_dealership_with_data(clean_data_dir):
    """
    UT-03-CB
    Test load_dealership() with valid dealership.csv having three rows.
    """
    # Prepare a sample dealership CSV
    data = """Company,Model
Toyota,Corolla
Honda,Civic
Ford,F150
"""
    path = Path(DATABASE_FILE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)
    
    df = load_dealership()
    assert len(df) == 3, "Should load exactly three rows of dealership data"
    assert set(df.columns) == {"Company", "Model"}, "Columns should match expected"

