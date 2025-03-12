# Hike Review Server

The Hike review API servers as a way to manage resources for the Hike Review\
IOS Application. It is the middle mand between the front end user interface\
and the actual saved data in our backend database. The Hike review server uses\
MySQL to exchange data and authorizes user data using JSON Web Token standard.\
The documentation for using the Hike Review API requests can be found in the\
hike_review_api.md file.

## server/

The server directory holds all files that contain inplementation of the main\
server framework. It contains the runnable file to run the server locally and\
contains a directory with all of the endpoints that Hike Review uses.

Instructions:\
To be able to run the server locally you must already have a local MySQL\
server running using the schema.sql file in this repo. for the server to\
actually run and connect to the MySQL database you must setup all of the\
following required environment variables:
- MYSQL_HOST
- MYSQL_USER
- MYSQL_PASSWORD
- MYSQL_DB
- JWT_SECRET_KEY

Finally you can run the run.py file using python. You can use the\
command 'python run.py' to run a local instance of the server if\
your current directory is in the project folder.

## tests/

The tests directory holds all related unit test files that are used\
to test the main server program. 

Instructions:\
In order to run the unit tests locally you must setup a local MySQL\
database with the schema.sql file and setup all required environment\
variables similar to server setup.

You run all tests by using the command 'python -m unittest discover .\tests\'\
if your current directory is in the project folder.

## Server Design

Registration\
    Checks if username or email is taken (already in the database). Then it will return a conflict error otherwise, it will return a successful code and add the username, email, and password into the database. The password gets encrypted using the Werkzeug hash encoder when placed inside the database.

Login\
    Checks if given username or email is inside of the database, get the password, hash it using Werkzeug encoder and check if it matches the database. Login authorizes only matching passwords. Lastly, it will give the client app the JWT access token and the JWT refresh token.

Get Identity\
    If logged in via JWT Authorization (client uses access token in header field), get user information from the database based on the given token. Get the list of joined groups from the user and get the list of favorited hikes. Return this data to the client.

Get Hikes\
    Go through the list of hikes in the database. For each hike, get all routing points of the current hike from the database and save them as a list. With the routing points, make a new Hike object and save it into a separate list. Return the list of all hike objects created.

Post Favorite Hikes\
    If logged in via JWT Authorization (client uses access token in header field), get the input header of the list of hikes. Insert that data into the database with the JSON dump version of the input list. This sets the field value of a user with this new list of favorite hikes.

Get Reviews\
    If the client sends the trail\_id header field, get the list of reviews under this particular trail\_id. For each review, make a new Review object and save it into a new list. Return the list of review objects created.

Post Reviews\
    If logged in via JWT Authorization (client uses access token in header field), get all input parameters for a review to be posted. Check if the rating is from 1 to 5, and if it is, insert this data into the database. Otherwise, return an error code.

Get Groups\
    If the client sends the trail\_id header field, get the list of groups under this particular trail\_id. For each group, get all user members that have joined the group. With the UserGroupMember list, create a new Group object and save it into a list. Return the list of all group objects that were created.

Post Groups\
    If logged in via JWT Authorization (client uses access token in header field), get all input parameters for a group to be posted. Get the user who is posting. Insert input data and user data into the database to create a new group. Add the user to the list of joined users for this group.

Join Group\
    If logged in via JWT Authorization (client uses access token in header field), get user\_id and group\_id. Check if the start time of the group is already past the current time, then delete all the user members related to this group and delete the group from the database, then send a did not join in time message. Otherwise, if the user is already joined in the group, send an already joined message. If that wasn’t the case insert this user in the related user members related list in the database.
