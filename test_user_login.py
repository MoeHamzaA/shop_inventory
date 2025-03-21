import unittest
from app import app

class TestUserLogin(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_login_page_exists(self):
       
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200, "Expect /login to return 200")
        print(" response statcode {response.status_code}")

if __name__ == '__main__':
    unittest.main()
