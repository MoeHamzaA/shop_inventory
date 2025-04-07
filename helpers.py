import pandas as pd
import portalocker
import os
from datetime import datetime

# File paths
DATA_DIR = "data"
INVENTORY_FILE = os.path.join(DATA_DIR, "inventory.csv")
DATABASE_FILE = os.path.join(DATA_DIR, "dealership.csv")
LOCK_FILE = os.path.join(DATA_DIR, "inventory.lock")

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def acquire_lock():
    """Acquire a file lock to prevent concurrent writes"""
    lock = open(LOCK_FILE, 'w')
    try:
        portalocker.lock(lock, portalocker.LOCK_EX)
        return lock
    except:
        lock.close()
        raise

def release_lock(lock):
    """Release the file lock"""
    try:
        portalocker.unlock(lock)
    finally:
        lock.close()

def load_inventory():
    """Load inventory from CSV file or create empty DataFrame if file doesn't exist"""
    try:
        df = pd.read_csv(INVENTORY_FILE)
        if df.empty:
            return pd.DataFrame(columns=["ID", "Company", "Model", "Year", "Colour", "Quantity", "Version"])
        # Ensure ID and Version columns exist
        if "ID" not in df.columns:
            df["ID"] = range(1, len(df) + 1)
        if "Version" not in df.columns:
            df["Version"] = 1
        # Convert Version column to integer
        df["Version"] = df["Version"].fillna(1).astype(int)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["ID", "Company", "Model", "Year", "Colour", "Quantity", "Version"])

def save_inventory(df):
    """Save inventory DataFrame to CSV file with locking"""
    lock = acquire_lock()
    try:
        # Ensure IDs and Versions are sequential
        df["ID"] = range(1, len(df) + 1)
        if "Version" not in df.columns:
            df["Version"] = 1
        # Convert Version column to integer
        df["Version"] = df["Version"].fillna(1).astype(int)
        df.to_csv(INVENTORY_FILE, index=False)
    finally:
        release_lock(lock)

def load_dealership():
    """Load dealership database from CSV file"""
    try:
        return pd.read_csv(DATABASE_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=["Company", "Model"])

def generate_inventory_filename():
    """Generate a filename for inventory download with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(DATA_DIR, f'car_inventory_{timestamp}.csv')

def cleanup_file(filename):
    """Clean up a file after a short delay"""
    try:
        import time
        time.sleep(1)  # Wait for file to be sent
        if os.path.exists(filename):
            os.remove(filename)
    except:
        pass  # Ignore cleanup errors 