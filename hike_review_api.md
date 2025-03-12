**Hikereview Server API**

#### \[/auth/register]

    POST: Inserts a new user to the database.
        Input Parameters:
            ‘username’
            ‘email’
            ‘Password’

        Successful code: 201
        Failure codes: 409, 500


#### \[/auth/login]

    POST: Gets a new JWT access token and refresh token if the user is in the database. Login is successful if the username OR the email is in the database.
        Input Parameters:
            ‘username’
            ‘email’
            ‘Password’

        Output:
            ‘tokens’:
                ‘access’: the string for the access token
                ‘refresh’: the string for the refresh token

        Successful code: 200
        Failure codes: 400, 401


#### \[/auth/identity]

    JWToken Required
    GET: Gets the logged-in user details 
        Input Headers:
            ‘Authorization’: ‘Bearer [access token]’

        Successful code: 200
        Failure codes: 400, 401

        Identity Object Example Interface:
        {	
            "groups": [
                {
                    "group_name": "Bob’s Group",
                    "start_time": "Thu, 01 Jan 2026 14:30:00 GMT",
                    "trail_name": “Hike Name A"
                }
            ],
            "user_details": {
                "created_at": "Thu, 06 Mar 2025 02:39:17 GMT",
                "email": "bob123@test.com",
                "favorite_hikes": [
                    “Hike Name A”,
                    “Hike Name B”
                ],
                "user_id": 10,
                "username": "Bob"
            }
        }


#### \[/auth/refresh]

    JWToken Required
    GET: Creates a new access token by sending the refresh token, used when the old access token expires
        Input Headers:
            ‘Authorization’: ‘Bearer [refresh token]’

        Output:
            ‘access’: the newly created access token

        Successful code: 200
        Failure codes: 401


#### \[/hikes] 

    GET: Gets the list of all hikes
        Input Parameters:
            ‘difficulty’: gets the list of hikes under the specified difficulty

        Successful code: 200

        Hike Object Example interface:
        {
            "created_at": "2025-02-06 11:07:16",
            "creator_id": "1",
            "description": "Cool",
            "difficulty": "Easy",
            "distance": "999.99",
            "duration": "5.0",
            "end_lat": 1.000011,
            "end_lng": 1.000011,
            "rating": "0.5",
            "routing_points": [
                [0.1,0.1],
                [0.2,0.2],
                [0.3,0.3]
            ],
            "start_lat": 0.0,
            "start_lng": 0.0,
            "tags": "None",
            "trail_id": "1",
            "trail_image": "app/path/myfile.img",
            "trail_name": "Hike Name A"
        }


#### \[/favorite/hikes]

    POST: Set User’s favorite hike list to the input list of hikes
        Input Headers:
            ‘Authorization’: ‘Bearer [access token]’

        Input Parameters:
            ‘favorite_hikes’

        Successful code: 200
        Failure codes: 400, 401


#### \[/reviews]

    GET: Gets the list of all reviews of a specific hike
        Input Parameters:
            ‘trail_id’: required parameter to get the list of reviews under this particular hike (trail IDs can be found under the /hikes endpoint)

        Successful code: 200

        Review Object Example Interface:
        {
            "rating": "5",
            "review_date": "2025-03-05 04:05:34",
            "review_id": "1",
            "review_text": "Esthetically pleasing.",
            "trail_id": "1",
            "username": "Bob"
        }


    JWToken Required
    POST: Inserts a new review on the database to a specific hike
        Input Headers:
            ‘Authorization’: ‘Bearer [access token]’

        Input Parameters:
            ‘trail_id’
            ‘username’
            ‘rating’
            ‘review_text’

        Successful code: 201
        Failure code: 400


#### \[/groups]

    GET: Gets the list of all groups
        Input Parameters:
            ‘trail_id’: optional number to get the list of groups that associate with a particular hike
            ‘start_date_range’: ‘YYY-MM-DD HH:MM:SS’ the starting range of which hikes to get
            ‘end_date_range’: ‘YYY-MM-DD HH:MM:SS’ the ending range of which hikes to get
                Note: entering an invalid time range where the end date is before the start gets an empty list
        
        Successful code: 200

        Group Object Example Interface:
        {
            "created_at": "2025-03-06 09:18:49",
            "created_by": "10",
            "group_description": "My Group Description",
            "group_host": "Bob",
            "group_id": "1",
            "group_name": "Bob’s Group",
            "start_time": "2026-01-01 14:30:00",
            "total_users_joined": 2,
            "trail_id": "3",
            "trail_name": "Hike Name A",
            "users_joined": [
                10,
                11
            ]
        }


    JWToken Required
    POST: Inserts a new group on the database to a specific hike
        Input Headers:
            ‘Authorization’: ‘Bearer [refresh token]’

        Input Parameters:
            ‘trail_id’
            ‘group_host’: [username]
            ‘group_name’
            ‘group_description’
            ‘start_time’: ‘YYYY-MM-DD HH:MM:SS’
                Ex: “start_time”: "2025-03-02 14:30:00" 
                for March 2nd, 2025, 2:30 pm

        Successful code: 201
        Failure codes: 400


#### \[/join/group]

    JWToken Required
    POST: Inserts new user record related to the group record, and ensures the user isn't already in the group.  
        Input Headers:
            ‘Authorization’: ‘Bearer [refresh token]’

        Input Parameters:
            ‘group_id’
            ‘User_id’

        Successful codes: 201, 200
        Failure codes: 400, 409
