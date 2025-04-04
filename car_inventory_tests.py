import os
import unittest
from unittest.mock import patch
from app import app, inventory_file, database_file
import pandas as pd

class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        # Configure Flask for testing
        app.config['TESTING'] = True
        # Suppress actual outgoing emails
        app.config['MAIL_SUPPRESS_SEND'] = True

        self.client = app.test_client()

        with open(inventory_file, 'w') as f:
            f.write("ID,Company,Model,Year,Colour,Quantity\n")

        with open(database_file, 'w') as f:
            f.write("Company,Model\n")
            f.write("Toyota,Corolla\n")

        # Force a "logged_in" session 
        with self.client.session_transaction() as sess:
            sess['logged_in'] = True

    def tearDown(self):
        # Clean up test CSVs
        if os.path.exists(inventory_file):
            os.remove(inventory_file)
        if os.path.exists(database_file):
            os.remove(database_file)

    def test_add_car_manually(self):
        """
        POST valid data to /add_manually.
        Then check the final rendered page includes that new car in the table.
        """
        resp = self.client.post('/add_manually', data={
            'company': 'Toyota',
            'model': 'Camry',
            'year': '2020',
            'colour': 'Blue',
            'quantity': '1'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Toyota', resp.data)
        self.assertIn(b'Camry', resp.data)
        self.assertIn(b'2020', resp.data)
        self.assertIn(b'Blue', resp.data)
        self.assertIn(b'<td>1</td>', resp.data)  # quantity

    def test_add_from_dealership(self):
        """
        Add from dealership DB. We do 2 POSTS:
         choose  'Toyota'
         choose 'Corolla', year=2020, colour=Red, quantity=2
        Then confirm the final page has 'Corolla' in the table.
        """
        # Step 1: select company
        self.client.post(
            '/add_from_database',
            data={'company': 'Toyota', 'action': 'select_company'},
            follow_redirects=True
        )
        # Step 2: submit form
        resp = self.client.post(
            '/add_from_database',
            data={
                'company': 'Toyota',
                'model': 'Corolla',
                'year': '2020',
                'colour': 'Red',
                'quantity': '2'
            },
            follow_redirects=True
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Toyota', resp.data)
        self.assertIn(b'Corolla', resp.data)
        self.assertIn(b'2020', resp.data)
        self.assertIn(b'Red', resp.data)
        self.assertIn(b'<td>2</td>', resp.data)

    def test_remove_inventory(self):

        # Add
        self.client.post('/add_manually', data={
            'company': 'Ford',
            'model': 'Focus',
            'year': '2021',
            'colour': 'Gray',
            'quantity': '3'
        }, follow_redirects=True)

        # Remove all 3
        resp = self.client.post('/remove', data={
            'car_id': '1',
            'quantity': '3'
        }, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        # Confirm is not  present in the new HTML
        self.assertNotIn(b'Focus', resp.data)
        self.assertNotIn(b'Ford', resp.data)

    def test_search_inventory(self):
  
        # Add
        self.client.post('/add_manually', data={
            'company': 'Mazda',
            'model': '3',
            'year': '2022',
            'colour': 'Red',
            'quantity': '1'
        }, follow_redirects=True)

        # Search
        resp = self.client.post('/search', data={
            'search_type': 'company',
            'search_term': 'Mazda'
        }, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Mazda', resp.data)
        self.assertIn(b'3', resp.data)
        self.assertIn(b'2022', resp.data)
        self.assertIn(b'Red', resp.data)

    def test_login_logout(self):
       
        #  Log out
        with self.client.session_transaction() as sess:
            sess.pop('logged_in', None)

        # Access index => should be forced to /login
        resp = self.client.get('/', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        # The user sees the login page
        self.assertIn(b'Username', resp.data)
        self.assertIn(b'Password', resp.data)

        #  Log in
        resp = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        # We expect we end up on the index page with "Inventory" or something
        self.assertIn(b'Inventory', resp.data)

        resp = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        # Should see the login form again
        self.assertIn(b'Username', resp.data)
        self.assertIn(b'Password', resp.data)

    def test_download_inventory(self):
        
        self.client.post('/add_manually', data={
            'company': 'Tesla',
            'model': 'Model S',
            'year': '2022',
            'colour': 'White',
            'quantity': '5'
        }, follow_redirects=True)

        resp = self.client.get('/download_inventory')
        self.assertEqual(resp.status_code, 200)

        content_disp = resp.headers.get("Content-Disposition", "")
        self.assertIn("attachment; filename=", content_disp)

    @patch('app.mail.send', return_value=None)  # Mock out sending email
    def test_email_inventory(self, mock_mail):
        
        self.client.post('/add_manually', data={
            'company': 'Hyundai',
            'model': 'Elantra',
            'year': '2020',
            'colour': 'Blue',
            'quantity': '2'
        }, follow_redirects=True)

        resp = self.client.post('/email_inventory', data={
            'recipient_email': 'test@example.com',
            'subject': 'Test Inventory',
            'message': 'This is a test.'
        }, follow_redirects=True)

        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Inventory', resp.data)

if __name__ == '__main__':
    unittest.main()
