import unittest
import os

from server.app import create_app, mysql

class TestHikeData(unittest.TestCase):
    def setUp(self):
        # Create a test client
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

        # Insert test data into the database
        with self.app.app_context():      
            cursor = mysql.connection.cursor()
            cursor.execute(
                '''
                INSERT INTO Hikes (trail_name, difficulty, rating, distance, duration, start_lat, start_lng, end_lat, end_lng, description)
                VALUES ('Test Hike', 'Easy', 5.0, 200, '60', 1.99, -1.22, 1.98, -1.22, 'A test hike')
                '''
            )
            mysql.connection.commit()
            cursor.close()

    def tearDown(self):
        # Remove test data from the database
        with self.app.app_context():  # Use app context here
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM Hikes WHERE trail_name = 'Test Hike'")
            mysql.connection.commit()
            cursor.close()

    def testGetHikeData(self):
        # GET hike data
        response = self.client.get('/hikes')
        hikes = response.get_json()

        # Assertion Tests
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(hike['trail_name'] == 'Test Hike' for hike in hikes))

if __name__ == '__main__':
    unittest.main()