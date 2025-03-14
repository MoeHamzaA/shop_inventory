import unittest
import os
import pandas as pd
from unittest.mock import patch
import app

class TestCarInventoryFull(unittest.TestCase):
    """
    This class contains tests for every function in app.py.
    It includes both normal operation and edge cases to help catch bugs.
    """

    def setUp(self):
        """
        Before each test, remove any existing CSV files and create
        a blank inventory file with the proper headers.
        """
        if os.path.exists("inventory.csv"):
            os.remove("inventory.csv")
        if os.path.exists("dealership.csv"):
            os.remove("dealership.csv")
        # Create a blank inventory CSV with expected columns.
        df = pd.DataFrame(columns=["ID", "Company", "Model", "Year", "Colour", "Quantity"])
        df.to_csv("inventory.csv", index=False)

    def tearDown(self):
        """
        After each test, clean up any created CSV files.
        """
        if os.path.exists("inventory.csv"):
            os.remove("inventory.csv")
        if os.path.exists("dealership.csv"):
            os.remove("dealership.csv")

    # =========================
    # Tests for non-interactive functions
    # =========================

    def test_load_inventory_file_missing(self):
        """
        Test load_inventory() when the inventory file is missing.
        It should return an empty DataFrame with the expected columns.
        """
        if os.path.exists("inventory.csv"):
            os.remove("inventory.csv")
        df = app.load_inventory()
        self.assertTrue(df.empty)
        self.assertListEqual(list(df.columns), ["ID", "Company", "Model", "Year", "Colour", "Quantity"])

    def test_load_inventory_with_data(self):
        """
        Test load_inventory() with an existing file containing data.
        The function should add an 'ID' column if missing.
        """
        data = {
            "Company": ["Ford"],
            "Model": ["Fiesta"],
            "Year": ["2019"],
            "Colour": ["Blue"],
            "Quantity": [3]
        }
        df = pd.DataFrame(data)
        df.to_csv("inventory.csv", index=False)
        loaded_df = app.load_inventory()
        self.assertFalse(loaded_df.empty)
        self.assertIn("ID", loaded_df.columns)
        self.assertEqual(loaded_df.at[0, "ID"], 1)

    def test_save_inventory(self):
        """
        Test save_inventory() by verifying the CSV is saved with a sequential ID.
        """
        df = pd.DataFrame([{
            "Company": "Tesla", "Model": "Model 3", "Year": "2021", "Colour": "White", "Quantity": 2
        }])
        app.save_inventory(df)
        saved_df = pd.read_csv("inventory.csv")
        self.assertEqual(saved_df.at[0, "ID"], 1)
        self.assertEqual(saved_df.at[0, "Company"], "Tesla")

    def test_clear_screen(self):
        """
        Test clear_screen() by ensuring the correct system command is called.
        """
        with patch("os.system") as mock_system:
            app.clear_screen()
            expected_cmd = "cls" if os.name == "nt" else "clear"
            mock_system.assert_called_with(expected_cmd)

    # =========================
    # Tests for functions that print output
    # =========================

    def test_view_inventory_empty(self):
        """
        Test view_inventory() when the inventory is empty.
        It should print a message indicating an empty inventory.
        """
        df = pd.DataFrame(columns=["ID", "Company", "Model", "Year", "Colour", "Quantity"])
        df.to_csv("inventory.csv", index=False)
        with patch("builtins.print") as mock_print:
            app.view_inventory()
            calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("Inventory is empty." in str(c) for c in calls))

    def test_view_inventory_non_empty(self):
        """
        Test view_inventory() with data.
        It should print details of the existing car.
        """
        df = pd.DataFrame([{
            "ID": 1, "Company": "BMW", "Model": "X5", "Year": "2022", "Colour": "Black", "Quantity": 4
        }])
        df.to_csv("inventory.csv", index=False)
        with patch("builtins.print") as mock_print:
            app.view_inventory()
            printed_output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
            self.assertIn("BMW", printed_output)
            self.assertIn("X5", printed_output)

    # =========================
    # Tests for interactive functions (with valid inputs)
    # =========================

    def test_add_manually_new(self):
        """
        Test add_manually() for adding a new car with valid inputs.
        """
        inputs = [
            "Audi",          # Company
            "A4",            # Model
            "2020",          # Year
            "Red",           # Colour
            "3"              # Quantity
        ]
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                app.add_manually()
        df = pd.read_csv("inventory.csv")
        self.assertEqual(len(df), 1)
        self.assertEqual(df.at[0, "Company"], "Audi")
        self.assertEqual(df.at[0, "Year"], "2020")
        self.assertEqual(df.at[0, "Quantity"], 3)

    def test_add_manually_existing(self):
        """
        Test add_manually() when adding the same car twice.
        The function should increment the quantity rather than add a duplicate.
        """
        inputs = [
            "Audi", "A4", "2020", "Red", "3",  # First addition
            "Audi", "A4", "2020", "Red", "2"     # Second addition (duplicate)
        ]
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                app.add_manually()
                app.add_manually()
        df = pd.read_csv("inventory.csv")
        self.assertEqual(len(df), 1)
        self.assertEqual(df.at[0, "Quantity"], 5)

    def test_add_from_database_missing(self):
        """
        Test add_from_database() when the dealership database is missing.
        The function should print an error message.
        """
        if os.path.exists("dealership.csv"):
            os.remove("dealership.csv")
        with patch("builtins.print") as mock_print:
            with patch("builtins.input", return_value="0"):
                app.add_from_database()
            calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(any("Dealership database not found or empty." in str(c) for c in calls))

    def test_add_from_database_new(self):
        """
        Test add_from_database() by simulating a valid selection from the database.
        """
        df_dealership = pd.DataFrame([
            {"Company": "Toyota", "Model": "Camry"},
            {"Company": "Honda", "Model": "Accord"}
        ])
        df_dealership.to_csv("dealership.csv", index=False)
        # Sorted companies will be: Honda, Toyota; choose "2" for Toyota.
        inputs = [
            "2",    # Select Toyota
            "1",    # Select model "Camry"
            "2021", # Year
            "Blue", # Colour
            "4"     # Quantity
        ]
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print"):
                app.add_from_database()
        df_inventory = pd.read_csv("inventory.csv")
        self.assertEqual(len(df_inventory), 1)
        self.assertEqual(df_inventory.at[0, "Company"], "Toyota")
        self.assertEqual(df_inventory.at[0, "Model"], "Camry")

    def test_remove_inventory(self):
        """
        Test remove_inventory() by first removing part of a car's quantity,
        then removing the remaining quantity.
        """
        inputs_add = ["Ford", "Focus", "2018", "Green", "5"]
        with patch("builtins.input", side_effect=inputs_add):
            with patch("builtins.print"):
                app.add_manually()
        # Remove a portion (2 out of 5)
        inputs_remove_partial = ["1", "2"]
        with patch("builtins.input", side_effect=inputs_remove_partial):
            with patch("builtins.print"):
                app.remove_inventory()
        df = pd.read_csv("inventory.csv")
        self.assertEqual(df.at[0, "Quantity"], 3)
        # Now remove the remaining quantity
        inputs_remove_all = ["1", "3"]
        with patch("builtins.input", side_effect=inputs_remove_all):
            with patch("builtins.print"):
                app.remove_inventory()
        df = pd.read_csv("inventory.csv")
        self.assertTrue(df.empty)

    def test_search_inventory(self):
        """
        Test search_inventory() by adding a car and searching for it by company.
        The search output should contain the car's details.
        """
        inputs_add = ["BMW", "X3", "2022", "Black", "2"]
        with patch("builtins.input", side_effect=inputs_add):
            with patch("builtins.print"):
                app.add_manually()
        inputs_search = [
            "1",    # Search by Company
            "bmw"   # Search term (case-insensitive)
        ]
        with patch("builtins.input", side_effect=inputs_search):
            with patch("builtins.print") as mock_print:
                app.search_inventory()
                printed_output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("BMW", printed_output)
                self.assertIn("X3", printed_output)

    def test_main_exit(self):
        """
        Test the main() function by simulating an immediate exit.
        The goodbye message should be printed.
        """
        with patch("builtins.input", side_effect=["5"]):
            with patch("builtins.print") as mock_print:
                app.main()
                printed_output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("Thank you for using Car Inventory Management System", printed_output)

    # =========================
    # Additional edge-case tests
    # =========================

    def test_add_manually_invalid_year(self):
        """
        Test add_manually() with an invalid year input.
        The function should prompt again until a valid 4-digit year is entered.
        """
        inputs = [
            "Audi",   # Company
            "A4",     # Model
            "abcd",   # Invalid year input
            "2020",   # Valid year input
            "Red",    # Colour
            "3"       # Quantity
        ]
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print") as mock_print:
                app.add_manually()
                output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("Invalid year format", output)
        df = pd.read_csv("inventory.csv")
        self.assertEqual(df.at[0, "Year"], "2020")

    def test_add_manually_invalid_quantity(self):
        """
        Test add_manually() with invalid quantity inputs.
        The function should print error messages and eventually accept a valid quantity.
        """
        inputs = [
            "Audi",   # Company
            "A4",     # Model
            "2020",   # Year
            "Red",    # Colour
            "-1",     # Invalid quantity (negative)
            "abc",    # Invalid quantity (non-numeric)
            "3"       # Valid quantity
        ]
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print") as mock_print:
                app.add_manually()
                output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("Quantity must be greater than 0", output)
                self.assertIn("Please enter a valid number", output)
        df = pd.read_csv("inventory.csv")
        self.assertEqual(df.at[0, "Quantity"], 3)

    def test_remove_inventory_invalid_id(self):
        """
        Test remove_inventory() with an invalid car ID.
        The function should print an error and ask again.
        """
        inputs_add = ["Ford", "Focus", "2018", "Green", "5"]
        with patch("builtins.input", side_effect=inputs_add):
            with patch("builtins.print"):
                app.add_manually()
        # Try an invalid ID first ("999"), then valid ID ("1") with quantity "2"
        inputs_remove = ["999", "1", "2"]
        with patch("builtins.input", side_effect=inputs_remove):
            with patch("builtins.print") as mock_print:
                app.remove_inventory()
                output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("ID not found", output)
        df = pd.read_csv("inventory.csv")
        self.assertEqual(df.at[0, "Quantity"], 3)

    def test_remove_inventory_invalid_quantity(self):
        """
        Test remove_inventory() with invalid quantity inputs.
        The function should print error messages and ask until a valid quantity is entered.
        """
        inputs_add = ["Ford", "Focus", "2018", "Green", "5"]
        with patch("builtins.input", side_effect=inputs_add):
            with patch("builtins.print"):
                app.add_manually()
        # Provide invalid quantity inputs ("abc" and "10") before valid input ("2")
        inputs_remove = ["1", "abc", "10", "2"]
        with patch("builtins.input", side_effect=inputs_remove):
            with patch("builtins.print") as mock_print:
                app.remove_inventory()
                output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("Please enter a valid number", output)
                self.assertIn("Please enter a number between 1 and", output)
        df = pd.read_csv("inventory.csv")
        self.assertEqual(df.at[0, "Quantity"], 3)

    def test_search_inventory_invalid_option(self):
        """
        Test search_inventory() with an invalid search option.
        It should print an error message.
        """
        inputs_add = ["BMW", "X3", "2022", "Black", "2"]
        with patch("builtins.input", side_effect=inputs_add):
            with patch("builtins.print"):
                app.add_manually()
        inputs_search = ["9"]  # Invalid option (valid options are 1-4)
        with patch("builtins.input", side_effect=inputs_search):
            with patch("builtins.print") as mock_print:
                app.search_inventory()
                output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("Invalid option.", output)

    def test_add_from_database_invalid_company(self):
        """
        Test add_from_database() with an invalid company selection.
        The function should print an error and allow cancellation.
        """
        df_dealership = pd.DataFrame([
            {"Company": "Toyota", "Model": "Camry"},
            {"Company": "Honda", "Model": "Accord"}
        ])
        df_dealership.to_csv("dealership.csv", index=False)
        inputs = ["5", "0"]  # "5" is out of range, then cancel with "0"
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print") as mock_print:
                app.add_from_database()
                output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("Please enter a number between 1 and", output)

    def test_add_from_database_invalid_model(self):
        """
        Test add_from_database() with an invalid model selection.
        The function should print an error and allow cancellation.
        """
        df_dealership = pd.DataFrame([
            {"Company": "Toyota", "Model": "Camry"},
            {"Company": "Toyota", "Model": "Corolla"}
        ])
        df_dealership.to_csv("dealership.csv", index=False)
        # Only one company is available. For model selection, simulate an invalid input then cancel.
        inputs = ["1", "5", "0"]
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print") as mock_print:
                app.add_from_database()
                output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("Please enter a number between 1 and", output)

    def test_main_invalid_choice_then_exit(self):
        """
        Test main() with an invalid menu choice followed by exit.
        The program should print an error message then eventually print the goodbye message.
        """
        inputs = ["9", "5"]  # "9" is invalid; then "5" to exit.
        with patch("builtins.input", side_effect=inputs):
            with patch("builtins.print") as mock_print:
                app.main()
                output = " ".join(str(arg) for call in mock_print.call_args_list for arg in call[0])
                self.assertIn("Invalid choice", output)
                self.assertIn("Thank you for using Car Inventory Management System", output)

if __name__ == "__main__":
    unittest.main()
