import os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Main AWS Database
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT', 3306))
mysql = MySQL(app)

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
    
# Review Datastructure
class Review:
    def __init__(self, review_id, trail_id, user_id, rating, review_text, review_date):
        self.review_id = review_id
        self.trail_id = trail_id
        self.user_id = user_id
        self.rating = rating
        self.review_text = review_text
        self.review_date = review_date

    def toDictionary(self):
        return {
            'review_id': self.review_id,
            'trail_id': self.trail_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'review_date': self.review_date
        }

# Setup and route pages
@app.route('/')
def home():
    return 'Hikereview API'

@app.route('/users')
def getUserData():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM Users')
    users = cursor.fetchall()
    userRecords = []
    for user in users:
        userObj = User(str(user[0]), str(user[1]), str(user[2]), str(user[3]), str(user[4]))
        userRecords.append(userObj)
    userDictionaryList = [record.toDictionary() for record in userRecords]
    cursor.close()
    return jsonify(userDictionaryList)

@app.route('/hikes', methods=['GET'])
def getHikeData():
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
            'ORDER BY point_order', (hikeID,)
        )
        routePoints = cursor.fetchall()
        
        # Create list of point objects for routing nodes
        routingPointRecords = [routePoint(str(point[0]), str(point[1])) for point in routePoints]

        # Create new hike objects
        hikeObj = Hike(hikeID, str(hike[1]), str(hike[2]), str(hike[3]), str(hike[4]), str(hike[5]), str(hike[6]), str(hike[7]), str(hike[8]), str(hike[9]), str(hike[10]), str(hike[11]), str(hike[12]), str(hike[13]), routingPointRecords)
        hikeRecords.append(hikeObj)

    hikeDictionaryList = [record.toDictionary() for record in hikeRecords]
    cursor.close()
    return jsonify(hikeDictionaryList)

# Look at and post reviews
@app.route('/reviews', methods=['GET', 'POST'])
def handle_reviews():
    if request.method == 'GET':
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

    elif request.method == 'POST':
        data = request.json

        required_fields = ['trail_id', 'user_id', 'rating', 'review_text']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        trail_id = data['trail_id']
        user_id = data['user_id']
        rating = data['rating']
        review_text = data['review_text']

        if not (1 <= rating <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        cursor = mysql.connection.cursor()
        cursor.execute(
            'INSERT INTO Reviews (trail_id, user_id, rating, review_text) VALUES (%s, %s, %s, %s)',
            (trail_id, user_id, rating, review_text)
        )
        mysql.connection.commit()

        new_id = cursor.lastrowid
        cursor.close()

        return jsonify({'message': 'Review added successfully', 'review_id': new_id}), 201
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080 if not set
    app.run(host="0.0.0.0", port=port)