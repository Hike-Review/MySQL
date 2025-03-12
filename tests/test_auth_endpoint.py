import unittest
import os

from server.app import create_app, mysql

class TestAuthorization(unittest.TestCase):
    def setUp(self):
        # Create a test client
        self.app = create_app()
        self.client = self.app.test_client()
        self.app.testing = True

    def tearDown(self):
        # Remove test data from the database
        with self.app.app_context():  # Use app context here
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM Users WHERE username LIKE 'TestUser%'")
            mysql.connection.commit()
            cursor.close()

    def testregister(self):
        # POST Registration
        userData = {
            'username': 'TestUserA',
            'email': 'testuserA@test.com',
            'password': '123'
        }        
        response = self.client.post('/auth/register', json = userData)
        responseJSON = response.get_json()

        # Assertion Tests
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', responseJSON)
        self.assertEqual(responseJSON['message'], 'User created successfully')
        self.assertEqual(responseJSON['username'], 'TestUserA')

    def testlogin(self):
        # Register User
        userData = {
            'username': 'TestUserB',
            'email': 'testuserB@test.com',
            'password': '123'
        }    
        response = self.client.post('/auth/register', json = userData)
        
        # POST Login
        userData = {
            'username': 'TestUserB',
            'email': '',
            'password': '123'
        }    
        response = self.client.post('/auth/login', json = userData)
        responseJSON = response.get_json()

        # Assertion Tests
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', responseJSON)
        self.assertIn('tokens', responseJSON)
        self.assertEqual(responseJSON['message'], 'You are now logged in!')
        self.assertEqual(responseJSON['username'], 'TestUserB')

    def testgetCurrentIdentity(self):
        # Register User
        userData = {
            'username': 'TestUserC',
            'email': 'testuserC@test.com',
            'password': '123'
        }
        self.client.post('/auth/register', json = userData)
        
        # Login new User
        loginResponse = self.client.post('/auth/login', json = userData)
        loginResponseJSON = loginResponse.get_json()
        accessToken = loginResponseJSON['tokens']['access']

        # POST identity
        headers = {
            'Authorization': f'Bearer {accessToken}'
        }
        identityResponse = self.client.get('/auth/identity', headers = headers)
        identityResponseJSON = identityResponse.get_json()

        # Assertion Tests
        self.assertEqual(identityResponse.status_code, 200)
        self.assertIn('user_details', identityResponseJSON)
        self.assertIn('groups', identityResponseJSON)
        self.assertEqual(identityResponseJSON['user_details']['email'], 'testuserC@test.com')
        self.assertEqual(identityResponseJSON['user_details']['username'], 'TestUserC')

if __name__ == '__main__':
    unittest.main()