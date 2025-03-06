import os
import json
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

CORS(app)

# Main AWS Database
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))

mysql = MySQL(app)
jwt = JWTManager(app)

# User Datasctructure
class User:
    def __init__(self, user_id, username, email, password_hash, created_at):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    def toDictionary(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }

# Rout Points Datastructure
class routePoint:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def toDictionary(self):
        return {
            'lat': self.lat,
            'lng': self.lng
        }

# Hike Datastructure
class Hike:
    def __init__(self, trail_id, trail_name, trail_image, difficulty, rating, distance, duration, start_lat, start_lng, end_lat, end_lng, tags, description, creator_id, created_at, routing_points):
        self.trail_id = trail_id
        self.trail_name = trail_name
        self.trail_image = trail_image
        self.difficulty = difficulty
        self.rating = rating
        self.distance = distance
        self.duration = duration
        self.start_lat = start_lat 
        self.start_lng = start_lng
        self.end_lat = end_lat 
        self.end_lng = end_lng 
        self.tags = tags
        self.description = description
        self.creator_id = creator_id
        self.created_at = created_at
        self.routing_points = routing_points

    def toDictionary(self):
        return {
            'trail_id': self.trail_id,
            'trail_name': self.trail_name,
            'trail_image': self.trail_image,
            'difficulty': self.difficulty,
            'rating': self.rating,
            'distance': self.distance,
            'duration': self.duration,
            'start_lat': self.start_lat, 
            'start_lng': self.start_lng,
            'end_lat': self.end_lat, 
            'end_lng': self.end_lng, 
            'tags': self.tags,
            'description': self.description,
            'creator_id': self.creator_id,
            'created_at': self.created_at,
            'routing_points': [(point.lat, point.lng) for point in self.routing_points]
        }
    
# Review Datastructure
class Review:
    def __init__(self, review_id, trail_id, username, rating, review_text, review_date):
        self.review_id = review_id
        self.trail_id = trail_id
        self.username = username
        self.rating = rating
        self.review_text = review_text
        self.review_date = review_date

    def toDictionary(self):
        return {
            'review_id': self.review_id,
            'trail_id': self.trail_id,
            'username': self.username,
            'rating': self.rating,
            'review_text': self.review_text,
            'review_date': self.review_date
        }

# Group Datastructure
class Group:
    def __init__(self, group_id, group_name, group_description, trail_id, created_by, group_host, created_at, start_time, trail_name, total_users_joined, users_joined):
        self.group_id = group_id 
        self.group_name = group_name 
        self.group_description = group_description 
        self.trail_id = trail_id 
        self.created_by = created_by 
        self.group_host = group_host 
        self.created_at = created_at 
        self.start_time = start_time
        self.trail_name = trail_name
        self.total_users_joined = total_users_joined
        self.users_joined = users_joined

    def toDictionary(self):
        return {
            'group_id': self.group_id, 
            'group_name': self.group_name, 
            'group_description': self.group_description, 
            'trail_id': self.trail_id, 
            'created_by': self.created_by, 
            'group_host': self.group_host, 
            'created_at': self.created_at, 
            'start_time': self.start_time,
            'trail_name': self.trail_name,
            'total_users_joined': self.total_users_joined,
            'users_joined': self.users_joined
        } 

# JWT Error Handlers
@jwt.expired_token_loader
def expiredTokenCallback(jwt_header, jwt_data):
    return jsonify({'message' : 'Token has expired', 'error' : 'tokenExpired'}), 401

@jwt.invalid_token_loader
def invalidTokenCallback(error):
    return jsonify({'message' : 'Signature verification failed', 'error' : 'invalidToken'}), 401

@jwt.unauthorized_loader
def missingTokenCallback(error):
    return jsonify({'message' : 'Request doesn\'t contain valid token', 'error' : 'authorizationHeader'}), 401

# JWT Block list Check
# @jwt.token_in_blocklist_loader
# def tokenInBlocklistCallback(jwt_header, jwt_data):
#     jti = jwt_data['jti']
#     cur = mysql.connection.cursor()
#     cur.execute(
#         'SELECT jti ' +
#         'FROM TokenBlacklist ' +
#         'WHERE jti = %s' +
#         'LIMIT 1',
#         (jti,)
#     )
#     token = cur.fetchone()
#     cur.close() 
#     return token is not None

# API Endpoints
@app.route('/')
def home():
    return 'Hikereview API'

@app.route('/auth/register', methods=['POST'])
def register():
    if (request.method == 'POST'):
        data = request.json
        username = data['username']
        email = data['email']
        password = data['password']
        hashedPassword = generate_password_hash(password)

        try:
            cursor = mysql.connection.cursor()

            # Check if username is already in database
            cursor.execute(
                'SELECT username ' +
                'FROM Users ' +
                'WHERE username = %s ' + 
                'LIMIT 1',
                (username,)
            )
            existingUsername = cursor.fetchall()

            if (existingUsername):
                return jsonify({'message': 'Username already in use'}), 409

            # Check if email is already in database
            cursor.execute(
                'SELECT email ' +  
                'FROM Users ' +
                'WHERE email = %s' +
                'LIMIT 1',
                (email,)
            )
            existingUserEmail = cursor.fetchall()

            if (existingUserEmail):
                return jsonify({'message': 'Email already in use'}), 409

            # Insert new user
            cursor.execute(
                'INSERT INTO Users ' +  
                '(username, email, password_hash) ' +
                'VALUES (%s, %s, %s)',
                (username, email, hashedPassword)
            )
            mysql.connection.commit()
            cursor.close()
            return jsonify(
                {
                    'message' : 'User created successfully',
                    'username' : username
                }
            ), 201

        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500

@app.route('/auth/login', methods=['POST'])
def login():
    if (request.method == 'POST'):
        data = request.json
        username = data['username']
        email = data['email']
        password = data['password']

        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT username, email, password_hash ' +
            'FROM Users ' +
            'WHERE username = %s' +
            'OR email = %s' +
            'LIMIT 1',
            (username, email)
        )
        user = cur.fetchone()
        cur.close()

        # Check if Username or email doesn't exist
        if (user == None):
            return jsonify({'message': 'Invalid username or email'}), 400
        
        username = user[0]
        hashedPassword = user[2]

        # Check if Password is correct
        if (check_password_hash(hashedPassword, password)):
            accessToken = create_access_token(identity = username)
            refreshToken = create_refresh_token(identity = username)
            
            return jsonify(
                {
                    'message' : 'You are now logged in!',
                    'username' : username,
                    'tokens' : {
                        'access' : accessToken,
                        'refresh' : refreshToken
                    }
                }
            ), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

# @app.route('/auth/logout', methods=['GET'])
# @jwt_required(verify_type = False)
# def logout():
#     if (request.method == 'GET'):
#         claims = get_jwt()
#         jti = claims.get('jti')
#         tokenType = claims.get('type')

#         # Insert token into databas blacklist
#         cursor = mysql.connection.cursor()
#         cursor.execute(
#             'INSERT INTO tokenblacklist ' +  
#             '(jti) ' +
#             'VALUES (%s)',
#             (jti,)
#         )
#         mysql.connection.commit()
#         cursor.close()
#         return jsonify({'message' : 'Logout successful', 'token_revoked' : f'{tokenType} revoked'}), 200

@app.route('/auth/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refreshToken():
    if (request.method == 'GET'):
        username = get_jwt_identity()
        newAccessToken = create_access_token(identity = username)
        return jsonify({'access' : newAccessToken})

@app.route('/auth/identity', methods=['GET', 'POST']) 
@jwt_required()
def getCurrentIdentity():
    claims = get_jwt()
    username = claims.get('sub')
    cur = mysql.connection.cursor()

    if (request.method == 'GET'):
        cur.execute(
            'SELECT user_id, username, email, created_at, favorite_hikes ' +
            'FROM Users ' +
            'WHERE username = %s' +
            'LIMIT 1',
            (username,)
        )
        user = cur.fetchone()

        cur.execute(
            '''
            SELECT ug.group_name, ug.start_time, h.trail_name
            FROM UserGroups ug
            JOIN UserGroupMembers ugm ON ug.group_id = ugm.group_id
            JOIN Hikes h ON ug.trail_id = h.trail_id
            JOIN Users u ON u.user_id = ugm.user_id
            WHERE u.username = %s
            ''',
            (username,)
        )
        groups = cur.fetchall()
        cur.close()
        
        if (user):
            return jsonify(
                {
                    'claims': claims,
                    'user_details': {
                        'user_id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'created_at': user[3],
                        'favorite_hikes': json.loads(user[4]) if user[4] else []  # Convert JSON string to list
                    },
                    'groups': [
                        {
                            'group_name': g[0],
                            'start_time': g[1],
                            'trail_name': g[2]
                        }
                        for g in groups
                    ]
                }
            ), 200
        else:
            return jsonify({'message': 'no login detected'}), 400

    elif request.method == 'POST':
        # Add a hike name to favorite_hikes
        data = request.get_json()
        new_hike = data.get('trail_name')

        if not new_hike:
            return jsonify({'message': 'Hike name required'}), 400
        
        # Fetch current favorite hikes
        cur.execute('SELECT favorite_hikes FROM Users WHERE username = %s LIMIT 1', (username,))
        result = cur.fetchone()
        favorite_hikes = json.loads(result[0]) if result and result[0] else []

        # Prevent duplicates
        if new_hike in favorite_hikes:
            return jsonify({'message': 'Hike already favorited'}), 409

        favorite_hikes.append(new_hike)  # Add new hike
        cur.execute(
            'UPDATE Users SET favorite_hikes = %s WHERE username = %s',
            (json.dumps(favorite_hikes), username)
            )
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Hike added to favorites', 'favorite_hikes': favorite_hikes}), 201

@app.route('/hikes', methods=['GET'])
def getHikeData():
    if (request.method == 'GET'):
        difficulty = request.args.get('difficulty', default='', type=str)
        cursor = mysql.connection.cursor()

        # Display all hikes or based on difficulty  
        hikeQuery = 'SELECT * FROM Hikes'
        if (difficulty):
            hikeQuery +=  ' WHERE difficulty = %s'
            cursor.execute(hikeQuery, (difficulty,))
        else:
            cursor.execute(hikeQuery)

        hikes = cursor.fetchall()

        # Display Each Hike
        hikeRecords = []
        for hike in hikes:
            hikeID = str(hike[0])

            # Collect all routing nodes for this hike
            cursor.execute(
                'SELECT latitude, longitude ' +
                'FROM RoutePoints ' +
                'WHERE trail_id = %s ' + 
                'ORDER BY point_order',
                (hikeID,)
            )
            routePoints = cursor.fetchall()
            
            # Create list of point objects for routing nodes
            routingPointRecords = [routePoint(float(point[0]), float(point[1])) for point in routePoints]

            # Create new hike objects
            trailName = str(hike[1])
            trailImage = str(hike[2])
            trailDifficulty = str(hike[3])
            trailRating = str(hike[4])
            trailDistance = str(hike[5])
            trailDuration = str(hike[6])
            startLat = float(hike[7])
            startLng = float(hike[8])
            endLat = float(hike[9])
            endLng = float(hike[10])
            trailTags = str(hike[11])
            trailDescription = str(hike[12])
            trailCreatorUserId = str(hike[13])
            trailCreatedAt = str(hike[14])
            hikeObj = Hike(
                hikeID, trailName, trailImage, trailDifficulty, trailRating, trailDistance, 
                trailDuration, startLat, startLng, endLat, endLng, trailTags, trailDescription,
                trailCreatorUserId, trailCreatedAt, routingPointRecords
            )
            hikeRecords.append(hikeObj)

        hikeDictionaryList = [record.toDictionary() for record in hikeRecords]
        cursor.close()
        return jsonify(hikeDictionaryList), 200

@app.route('/reviews', methods=['GET'])
def getReviews():
    if (request.method == 'GET'):
        trail_id = request.args.get('trail_id', type=int)
        if not trail_id:
            return jsonify({'error': 'trail_id parameter is required'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Reviews WHERE trail_id = %s', (trail_id,))
        reviews = cursor.fetchall()

        reviewRecords = [
            Review(str(r[0]), str(r[1]), str(r[2]), str(r[3]), str(r[4]), str(r[5]))
            for r in reviews
        ]

        cursor.close()
        return jsonify([review.toDictionary() for review in reviewRecords])

@app.route('/reviews', methods=['POST'])
@jwt_required()
def postReviews():
    if (request.method == 'POST'):
        data = request.json

        required_fields = ['trail_id', 'username', 'rating', 'review_text']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        trail_id = data['trail_id']
        username = data['username']
        rating = data['rating']
        review_text = data['review_text']

        if not (1 <= rating <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO Reviews (trail_id, username, rating, review_text) VALUES (%s, %s, %s, %s)',
            (trail_id, username, rating, review_text)
        )
        mysql.connection.commit()

        new_id = cursor.lastrowid
        cursor.close()

        return jsonify({'message': 'Review added successfully', 'review_id': new_id}), 201

@app.route('/groups', methods=['GET'])
def getGroups():
    if (request.method == 'GET'):
        startDateInput = request.args.get('start_date_range', type = str)
        endDateInput = request.args.get('end_date_range', type = str)

        if (startDateInput == None or endDateInput == None):
            return jsonify({"error": "missing start and/or end date"}), 400

        try:
            startDate = datetime.strptime(startDateInput, '%Y-%m-%d')
            endDate = datetime.strptime(endDateInput, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format format. Use 'YYYY-MM-DD'"}), 400    

        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * ' + 
            'FROM UserGroups ' + 
            'WHERE start_time >= %s ' + 
            'AND start_time <= %s',
            (startDate.strftime('%Y-%m-%d 00:00:00'), endDate.strftime('%Y-%m-%d 23:59:59'))
        )
        groups = cursor.fetchall()

        if (groups == None):
            return jsonify({"error": "invalid group_id, group does not exist"}), 400

        groupRecords = []
        for group in groups:
            groupId = str(group[0])
            trailId = str(group[3])

            # Get group member user_id's
            cursor.execute(
                'SELECT user_id ' +
                'FROM UserGroupMembers ' +
                'WHERE group_id = %s ',
                (groupId,)
            )
            usersInGroup = cursor.fetchall()
            joinedUsers = [user[0] for user in usersInGroup]
            totalJoinedUsers = len(joinedUsers)

            # Get trail name
            cursor.execute(
                'SELECT trail_name ' + 
                'FROM Hikes ' + 
                'WHERE trail_id = %s',
                (trailId,)
            )
            trail = cursor.fetchone()
            trailName = str(trail[0])

            groupObj = Group(groupId, str(group[1]), str(group[2]), trailId, str(group[4]), str(group[5]), str(group[6]), str(group[7]), trailName, totalJoinedUsers,  joinedUsers)
            groupRecords.append(groupObj)
        
        cursor.close()
        return jsonify([group.toDictionary() for group in groupRecords])

@app.route('/groups', methods=['POST'])
@jwt_required()
def postGroups():
    if (request.method == 'POST'):
        data = request.json

        required_fields = ['trail_id', 'group_host', 'group_name', 'group_description', 'start_time']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        trailId = data['trail_id']
        hostName = data['group_host']
        groupName = data['group_name']
        groupDescription = data['group_description']
        startTimeInput = data['start_time']
        
        # Extract and validate start time
        try:
            startTimeStamp = datetime.strptime(startTimeInput, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({"error": "Invalid startTimeStamp format. Use 'YYYY-MM-DD HH:MM:SS'"}), 400

        # Get id of the user created
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT user_id FROM Users WHERE username = %s', (hostName,))
        hostUser = cursor.fetchone()
        if (hostUser == None):
            return jsonify({"error": "Invalid user posting to database."}), 400
        
        hostUserId = str(hostUser[0])

        # Insert new group to database
        cursor.execute(
            'INSERT INTO UserGroups (trail_id, created_by, group_host, group_name, group_description, start_time) VALUES (%s, %s, %s, %s, %s, %s)',
            (trailId, hostUserId, hostName, groupName, groupDescription, startTimeStamp)
        )
        newGroupId = cursor.lastrowid

        # Automatically Join Host to the group
        cursor.execute(
            'INSERT INTO UserGroupMembers (user_id, group_id) VALUES (%s, %s)',
            (hostUserId, newGroupId)
        )

        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'Review added successfully', 'groupId': newGroupId}), 201

@app.route('/join/group', methods=['POST'])
@jwt_required()
def joinGroup():
    if (request.method == 'POST'):
        data = request.json

        required_fields = ['group_id', 'user_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        groupId = data['group_id']
        userId = data['user_id']
        
        # Get group object
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT trail_id, start_time FROM UserGroups WHERE group_id = %s', (groupId,))
        group = cursor.fetchone()
        if (group == None):
            return jsonify({"error": "invalid group_id, group does not exist"}), 400

        startTime = str(group[1])

        # Validate if joining before start time
        currentTime = datetime.now()
        startTimeStamp = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
        if (currentTime > startTimeStamp):
            # Remove from database once hike has started
            cursor.execute('DELETE FROM UserGroupMembers WHERE group_id = %s', (groupId,))
            cursor.execute('DELETE FROM UserGroups WHERE group_id = %s', (groupId,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Did not join in time"}), 409

        try:
            cursor.execute(
                'INSERT INTO UserGroupMembers (user_id, group_id) VALUES (%s, %s)',
                (userId, groupId,)
            )
            mysql.connection.commit()
        except:
            cursor.close()
            return jsonify({"error": "already joined the group"}), 400

        cursor.close()
        return jsonify({"message": "Joined group successfully", "group_id": groupId}), 201

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if not set
    # app.run(host="0.0.0.0", port=port)
    app.run(debug = True)
