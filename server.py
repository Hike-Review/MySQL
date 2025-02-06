from flask import Flask, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for the entire app
CORS(app)

# Test Local Database
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'securePassword!@#123'
# app.config['MYSQL_DB'] = 'hikereview'

# Main AWS Database
app.config['MYSQL_HOST'] = 'hikereview.cbi8ecsmy7wx.us-west-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'CSE115A#HikeReview'
app.config['MYSQL_DB'] = 'hikereviewdb'
mysql = MySQL(app)

# User Datasctructure
class User:
    def __init__(self, user_id, username, email, password_hash, created_at):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }

# Hike Datastructure
class Hike:
    def __init__(self, trail_id, trail_name, difficulty, rating, distance, duration, start_lat, start_lng, end_lat, end_lng, tags, description, creator_id, created_at):
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

    def to_dict(self):
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
            'created_at': self.created_at
        }

# Setup and route pages
@app.route("/")
def home():
    return "Hikereview API"

@app.route("/users")
def getUserData():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    userRecords = []
    for user in users:
        userObj = User(str(user[0]), str(user[1]), str(user[2]), str(user[3]), str(user[4]))
        userRecords.append(userObj)
    userDictionaryList = [record.to_dict() for record in userRecords]
    cursor.close()
    return jsonify(userDictionaryList)

@app.route("/hikes")
def getHikeData():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM hikes')
    hikes = cursor.fetchall()
    hikeRecords = []
    for hike in hikes:
        hikeObj = Hike(str(hike[0]), str(hike[1]), str(hike[2]), str(hike[3]), str(hike[4]), str(hike[5]), str(hike[6]), str(hike[7]),
                        str(hike[8]), str(hike[9]), str(hike[10]), str(hike[11]), str(hike[12]), str(hike[13]))
        hikeRecords.append(hikeObj)
    hikeDictionaryList = [record.to_dict() for record in hikeRecords]
    cursor.close()
    return jsonify(hikeDictionaryList)

if __name__ == "__main__":
    app.run(debug=True)