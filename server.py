import os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

CORS(app)

# Main AWS Database
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

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
    def __init__(self, trail_id, trail_name, difficulty, rating, distance, duration, start_lat, start_lng, end_lat, end_lng, tags, description, creator_id, created_at, routing_points):
        self.trail_id = trail_id
        self.trail_name = trail_name
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
@jwt.token_in_blocklist_loader
def tokenInBlocklistCallback(jwt_header, jwt_data):
    jti = jwt_data['jti']
    cur = mysql.connection.cursor()
    cur.execute(
        'SELECT jti ' +
        'FROM TokenBlacklist ' +
        'WHERE jti = %s' +
        'LIMIT 1',
        (jti,)
    )
    token = cur.fetchone()
    cur.close() 
    return token is not None

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
                'INSERT INTO users ' +  
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

@app.route('/auth/logout', methods=['GET'])
@jwt_required(verify_type = False)
def logout():
    if (request.method == 'GET'):
        claims = get_jwt()
        jti = claims.get('jti')
        tokenType = claims.get('type')

        # Insert token into databas blacklist
        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO tokenblacklist ' +  
            '(jti) ' +
            'VALUES (%s)',
            (jti,)
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({'message' : 'Logout successful', 'token_revoked' : f'{tokenType} revoked'}), 200

@app.route('/auth/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refreshToken():
    if (request.method == 'GET'):
        username = get_jwt_identity()
        newAccessToken = create_access_token(identity = username)
        return jsonify({'access' : newAccessToken})

@app.route('/auth/identity', methods=['GET'])
@jwt_required()
def getCurrentIdentity():
    if (request.method == 'GET'):
        claims = get_jwt()
        username = claims.get('sub')

        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT username, email, created_at ' +
            'FROM Users ' +
            'WHERE username = %s' +
            'LIMIT 1',
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        
        if (user):
            return jsonify(
                {
                    'claims' : claims,
                    'user_details' : {
                        'username' : user[0],
                        'email' : user[1],
                        'created_at' : user[2]
                    } 
                }
            ), 200
        else:
            return jsonify({'message': 'no login detected'}), 400

@app.route('/hikes', methods=['GET'])
def getHikeData():
    if (request.method == 'GET'):
        difficulty = request.args.get('difficulty', default='', type=str)

        cursor = mysql.connection.cursor()
        hikeQuery = 'SELECT * FROM Hikes'
        if (difficulty):
            hikeQuery +=  ' WHERE difficulty = %s'
            cursor.execute(hikeQuery, (difficulty,))
        else:
            cursor.execute(hikeQuery)

        hikes = cursor.fetchall()

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
            routingPointRecords = [routePoint(str(point[0]), str(point[1])) for point in routePoints]

            # Create new hike objects
            hikeObj = Hike(hikeID, str(hike[1]), str(hike[2]), str(hike[3]), str(hike[4]), str(hike[5]), str(hike[6]), str(hike[7]), str(hike[8]), str(hike[9]), str(hike[10]), str(hike[11]), str(hike[12]), str(hike[13]), routingPointRecords)
            hikeRecords.append(hikeObj)

        hikeDictionaryList = [record.toDictionary() for record in hikeRecords]
        cursor.close()
        return jsonify(hikeDictionaryList), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if not set
    # app.run(host="0.0.0.0", port=port)
    app.run(debug = True)