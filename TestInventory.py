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
        Before each test, create a blank inventory file with the proper headers.
        """
        df = pd.DataFrame(columns=["ID", "Company", "Model", "Year", "Colour", "Quantity"])
        df.to_csv("inventory.csv", index=False)

    # =========================
    # Tests for non-interactive functions
    # =========================

    def test_load_inventory_file_missing(self):
        """
        Test load_inventory() when the inventory file is missing.
        It should return an empty DataFrame with the expected columns.
        """
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
    # Additional Test Cases
    # =========================

    def test_save_and_load_inventory(self):
        """
        Test if data is saved and loaded correctly.
        """
        df = pd.DataFrame([{
            "Company": "Honda", "Model": "Civic", "Year": "2022", "Colour": "Black", "Quantity": 5
        }])
        app.save_inventory(df)
        loaded_df = app.load_inventory()
        self.assertFalse(loaded_df.empty)
        self.assertEqual(loaded_df.at[0, "Company"], "Honda")

    def test_add_duplicate_inventory(self):
        """
        Test adding the same car multiple times to ensure quantity increments correctly.
        """
        df = pd.DataFrame([{
            "ID": 1, "Company": "Toyota", "Model": "Camry", "Year": "2020", "Colour": "Blue", "Quantity": 3
        }])
        df.to_csv("inventory.csv", index=False)
        with patch("builtins.input", side_effect=["Toyota", "Camry", "2020", "Blue", "2"]):
            with patch("builtins.print"):
                app.add_manually()
        loaded_df = app.load_inventory()
        self.assertEqual(loaded_df.at[0, "Quantity"], 5)

    def test_remove_inventory(self):
        """
        Test removing an item from inventory.
        """
        df = pd.DataFrame([{
            "ID": 1, "Company": "Nissan", "Model": "Altima", "Year": "2019", "Colour": "Red", "Quantity": 4
        }])
        df.to_csv("inventory.csv", index=False)
        with patch("builtins.input", side_effect=["1", "2"]):
            with patch("builtins.print"):
                app.remove_inventory()
        loaded_df = app.load_inventory()
        self.assertEqual(loaded_df.at[0, "Quantity"], 2)

    def test_remove_entire_inventory(self):
        """
        Test completely removing a car from the inventory.
        """
        df = pd.DataFrame([{
            "ID": 1, "Company": "BMW", "Model": "X5", "Year": "2021", "Colour": "White", "Quantity": 2
        }])
        df.to_csv("inventory.csv", index=False)
        with patch("builtins.input", side_effect=["1", "2"]):
            with patch("builtins.print"):
                app.remove_inventory()
        loaded_df = app.load_inventory()
        self.assertTrue(loaded_df.empty)

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCarInventoryFull)
    runner = unittest.TextTestRunner(resultclass=unittest.TextTestResult)

    result = runner.run(suite)

    print("\n====================")
    print("   TEST RESULTS")
    print("====================\n")

    for i, (test_case, error) in enumerate(result.failures + result.errors, 1):
        print(f"Case {i}: FAIL - {test_case}")
        print(error)
        print("\n--------------------")

    passed = result.testsRun - len(result.failures) - len(result.errors)
    for i in range(passed):
        print(f"Case {i+1+len(result.failures)+len(result.errors)}: PASS")

    print("\n====================")
    print(f"Total Cases: {result.testsRun}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("====================\n")

    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED ✅")
    else:
        print("❌ SOME TESTS FAILED ❌")