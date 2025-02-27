import unittest
import os

from flask import Flask
from server import app, mysql

class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        # Create a test client
        self.app = app.test_client()
        self.app.testing = True

        # Insert test data into the database
        with app.app_context():
            app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
            app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
            app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
            app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
            app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
            app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))
            
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO Hikes (trail_name, difficulty, rating, distance, duration, start_lat, start_lng, end_lat, end_lng, description)
                VALUES ('Test Hike', 'Easy', 5.0, 200, '60', 1.99, -1.22, 1.98, -1.22, 'A test hike')
            """)
            mysql.connection.commit()
            cursor.close()

    def tearDown(self):
        # Remove test data from the database
        with app.app_context():
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM Hikes WHERE trail_name = 'Test Hike'")
            mysql.connection.commit()
            cursor.close()

    def testHomePage(self):
        # Get Home page Data
        response = self.app.get('/')

        # Assertion Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hikereview API')

    def testGetHikeData(self):
        # GET hike data
        response = self.app.get('/hikes')
        hikes = response.get_json()

        # Assertpion Tests
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(hike['trail_name'] == 'Test Hike' for hike in hikes))

if __name__ == '__main__':
    unittest.main()