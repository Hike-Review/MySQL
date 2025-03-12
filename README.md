# Hike Review Server

The Hike review API servers as a way to manage resources for the Hike Review\
IOS Application. It is the middle mand between the front end user interface\
and the actual saved data in our backend database. The Hike review server uses\
MySQL to exchange data and authorizes user data using JSON Web Token standard.\
The documentation for using the Hike Review API requests can be found in the\
hike_review_api.md file.

## server

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

## tests

The tests directory holds all related unit test files that are used\
to test the main server program. 

Instructions:\
In order to run the unit tests locally you must setup a local MySQL\
database with the schema.sql file and setup all required environment\
variables similar to server setup.

You run all tests by using the command 'python -m unittest discover .\tests\'\
if your current directory is in the project folder.