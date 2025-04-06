import os
import unittest
from unittest.mock import patch
from app import app, inventory_file, database_file, load_inventory, save_inventory
import pandas as pd


class FlaskAppTests(unittest.TestCase):
   
    def setUp(self):
        app.config["TESTING"] = True
        app.config["MAIL_SUPPRESS_SEND"] = True 
        app.config["WTF_CSRF_ENABLED"] = False 

        self.client = app.test_client()

        with open(inventory_file, "w") as f:
            f.write("ID,Company,Model,Year,Colour,Quantity,Version\n")
        with open(database_file, "w") as f:
            f.write("Company,Model\n")
            f.write("Toyota,Corolla\n")
            f.write("Ford,Focus\n")

        with self.client.session_transaction() as sess:
            sess["logged_in"] = True

    def tearDown(self):
        for f in (inventory_file, database_file):
            if os.path.exists(f):
                os.remove(f)

    def test_add_car_manually(self):
        resp = self.client.post(
            "/add_manually",
            data={
                "company": "Toyota",
                "model": "Camry",
                "year": "2020",
                "colour": "Blue",
                "quantity": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Toyota", resp.data)
        self.assertIn(b"Camry", resp.data)
        self.assertIn(b"2020", resp.data)
        self.assertIn(b"Blue", resp.data)
        self.assertIn(b"<td>1</td>", resp.data)

    def test_add_car_manually_invalid_quantity(self): # <-------------------------------------------- is failing 
        resp = self.client.post(
            "/add_manually",
            data={
                "company": "Toyota",
                "model": "Camry",
                "year": "2020",
                "colour": "Blue",
                "quantity": "0",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Quantity must be greater than 0", resp.data)
        self.assertEqual(load_inventory().empty, True)

    def test_add_car_manually_invalid_year(self):#  <---------------------------------- is failing
        resp = self.client.post(
            "/add_manually",
            data={
                "company": "Honda",
                "model": "Civic",
                "year": "20",
                "colour": "Black",
                "quantity": "1",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Invalid year format", resp.data)
        self.assertTrue(load_inventory().empty)

    def test_add_from_dealership(self):
        # choose company
        self.client.post(
            "/add_from_database",
            data={"company": "Toyota", "action": "select_company"},
            follow_redirects=True,
        )
        # choose model
        resp = self.client.post(
            "/add_from_database",
            data={
                "company": "Toyota",
                "model": "Corolla",
                "year": "2021",
                "colour": "Red",
                "quantity": "2",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Corolla", resp.data)
        self.assertIn(b"<td>2</td>", resp.data)

    def test_add_from_dealership_invalid_year(self): # <---------------------- is failing
        self.client.post(
            "/add_from_database",
            data={"company": "Toyota", "action": "select_company"},
            follow_redirects=True,
        )
        resp = self.client.post(
            "/add_from_database",
            data={
                "company": "Toyota",
                "model": "Corolla",
                "year": "abcd",
                "colour": "Red",
                "quantity": "1",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Invalid year format", resp.data)
        self.assertTrue(load_inventory().empty)

    def test_remove_inventory(self):
        # add first
        self.client.post(
            "/add_manually",
            data={
                "company": "Ford",
                "model": "Focus",
                "year": "2022",
                "colour": "Gray",
                "quantity": "3",
            },
            follow_redirects=True,
        )
        # remove all 3
        resp = self.client.post(
            "/remove",
            data={"car_id": "1", "quantity": "3"},
            follow_redirects=True,
        )
        self.assertNotIn(b"Focus", resp.data)
        self.assertTrue(load_inventory().empty)

    def test_remove_inventory_excess_quantity(self):# <------------------------------------------------ is failing
        self.client.post(
            "/add_manually",
            data={
                "company": "Ford",
                "model": "Fiesta",
                "year": "2021",
                "colour": "Green",
                "quantity": "1",
            },
            follow_redirects=True,
        )
        resp = self.client.post(
            "/remove",
            data={"car_id": "1", "quantity": "5"},
            follow_redirects=True,
        )
        self.assertIn(b"Cannot remove more than available quantity", resp.data)
        self.assertEqual(load_inventory().iloc[0]["Quantity"], 1)

    def test_search_inventory(self): # <--------------------------------------------------------------------- Has AN ERROR
        self.client.post(
            "/add_manually",
            data={
                "company": "Mazda",
                "model": "3",
                "year": "2022",
                "colour": "Red",
                "quantity": "1",
            },
            follow_redirects=True,
        )
        resp = self.client.post(
            "/search",
            data={"search_term": "mazda"},
            follow_redirects=True,
        )
        self.assertIn(b"Mazda", resp.data)
        self.assertIn(b"2022", resp.data)

    def test_search_filters_company_year_colour(self):
        self.client.post(
            "/add_manually",
            data={
                "company": "Tesla",
                "model": "Model S",
                "year": "2022",
                "colour": "White",
                "quantity": "5",
            },
            follow_redirects=True,
        )
        self.client.post(
            "/add_manually",
            data={
                "company": "Tesla",
                "model": "Model 3",
                "year": "2021",
                "colour": "Black",
                "quantity": "4",
            },
            follow_redirects=True,
        )
        resp = self.client.post(
            "/search",
            data={
                "company_filter": "Tesla",
                "year_filter": "2022",
                "colour_filter": "White",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Model S", resp.data)
        self.assertNotIn(b"Model 3", resp.data)

    def test_edit_car_success(self): # <----------------------------------------------- is failing
        self.client.post(
            "/add_manually",
            data={
                "company": "BMW",
                "model": "X5",
                "year": "2020",
                "colour": "Blue",
                "quantity": "2",
            },
            follow_redirects=True,
        )
        edit_page = self.client.get("/edit/1")
        self.assertIn(b"value=\"1\" name=\"version\"", edit_page.data)
        resp = self.client.post(
            "/edit/1",
            data={
                "year": "2020",
                "colour": "Red",
                "quantity": "2",
                "version": "1",
            },
            follow_redirects=True,
        )
        self.assertIn(b"updated successfully", resp.data)
        self.assertIn(b"Red", resp.data)

    def test_edit_car_concurrent_version_mismatch(self):
        self.client.post(
            "/add_manually",
            data={
                "company": "Audi",
                "model": "A4",
                "year": "2019",
                "colour": "White",
                "quantity": "1",
            },
            follow_redirects=True,
        )
        inv = load_inventory()
        inv.loc[0, "Version"] = 2
        save_inventory(inv)
        resp = self.client.post(
            "/edit/1",
            data={
                "year": "2019",
                "colour": "Black",
                "quantity": "1",
                "version": "1",
            },
            follow_redirects=True,
        )
        self.assertIn(b"modified by another user", resp.data)

    def test_login_logout(self):
        # log out
        with self.client.session_transaction() as sess:
            sess.pop("logged_in", None)
        resp = self.client.get("/", follow_redirects=True)
        self.assertIn(b"Username", resp.data)
        # log in
        resp = self.client.post(
            "/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=True,
        )
        self.assertIn(b"Inventory", resp.data)
        # logout route
        resp = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Username", resp.data)

    def test_login_required_redirect(self):
        with self.client.session_transaction() as sess:
            sess.pop("logged_in", None)
        resp = self.client.get("/add_manually", follow_redirects=True)
        self.assertIn(b"Please login", resp.data)

    def test_download_inventory(self):
        self.client.post(
            "/add_manually",
            data={
                "company": "Tesla",
                "model": "Model S",
                "year": "2022",
                "colour": "White",
                "quantity": "5",
            },
            follow_redirects=True,
        )
        resp = self.client.get("/download_inventory")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.headers["Content-Disposition"].startswith("attachment; filename="))

    @patch("app.mail.send", return_value=None)
    def test_email_inventory(self, _mock_send): # <---------------------------------------------------------------------- is failing
        self.client.post(
            "/add_manually",
            data={
                "company": "Hyundai",
                "model": "Elantra",
                "year": "2020",
                "colour": "Blue",
                "quantity": "2",
            },
            follow_redirects=True,
        )
        resp = self.client.post(
            "/email_inventory",
            data={
                "recipient_email": "test@example.com",
                "subject": "Test Inventory",
                "message": "This is a test.",
            },
            follow_redirects=True,
        )
        self.assertIn(b"Inventory report sent successfully", resp.data)

    @patch("app.mail.send", return_value=None)
    def test_email_inventory_missing_recipient(self, _mock_send): # <------------------------------------------------------------- is has an error 
        resp = self.client.post(
            "/email_inventory",
            data={"recipient_email": ""},
            follow_redirects=True,
        )
        self.assertIn(b"Please enter a recipient email", resp.data)

    def test_database_load_empty(self):
        os.remove(database_file)
        from app import load_dealership
        df = load_dealership()
        self.assertTrue(df.empty)

    def test_index_page_renders_inventory(self):
        self.client.post(
            "/add_manually",
            data={
                "company": "Kia",
                "model": "Rio",
                "year": "2018",
                "colour": "Silver",
                "quantity": "2",
            },
            follow_redirects=True,
        )
        resp = self.client.get("/")
        self.assertIn(b"Kia", resp.data)

    def test_session_persistence_after_login(self):
        new_client = app.test_client()
        resp = new_client.post(
            "/login",
            data={"username": "admin", "password": "admin123"},
            follow_redirects=True,
        )
        self.assertIn(b"Inventory", resp.data)
        resp2 = new_client.get("/add_manually")
        self.assertEqual(resp2.status_code, 200)


if __name__ == "__main__":
    unittest.main()
