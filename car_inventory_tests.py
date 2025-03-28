import os
import unittest
import pandas as pd
from app import app, inventory_file, database_file  

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

        with open(inventory_file, 'w') as f:
            f.write("ID,Company,Model,Year,Colour,Quantity\n")

        with open(database_file, 'w') as f:
            f.write("Company,Model\n")
            f.write("Toyota,Corolla\n")

        with self.client.session_transaction() as sess:
            sess['logged_in'] = True

    # clean up test files created inventory and database
    def tearDown(self):
        if os.path.exists(inventory_file):
            os.remove(inventory_file)
        if os.path.exists(database_file):
            os.remove(database_file)

    def test_add_car_manually(self):
        """Test the manual car addition endpoint."""
        response = self.client.post('/add_manually', data={
            'company': 'Toyota',
            'model': 'Camry',
            'year': '2020',
            'colour': 'Blue',
            'quantity': '1'
        }, follow_redirects=True)

        self.assertIn(b'Error: Car not added', response.data)

    def test_add_from_dealership(self):
        """Test adding a car from the dealership database."""
        response = self.client.post('/add_from_database', data={
            'company': 'Toyota',
            'action': 'select_company'
        }, follow_redirects=True)

        response = self.client.post('/add_from_database', data={
            'company': 'Toyota',
            'model': 'Corolla',
            'year': '2020',
            'colour': 'Red',
            'quantity': '2'
        }, follow_redirects=True)

        self.assertIn(b'Error: Car not added from dealership', response.data)

    def test_edit_vehicle(self):
        """Test editing a vehicle."""
        self.client.post('/add_manually', data={
            'company': 'Honda',
            'model': 'Civic',
            'year': '2019',
            'colour': 'Black',
            'quantity': '1'
        }, follow_redirects=True)

        response = self.client.post('/edit/1', data={
            'year': '2018',
            'colour': 'White',
            'quantity': '0'
        }, follow_redirects=True)

        self.assertIn(b'Edit', response.data)

if __name__ == '__main__':
    unittest.main()
