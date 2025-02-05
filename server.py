from flask import Flask, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for the entire app
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '---'
app.config['MYSQL_DB'] = 'hikereview'
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
    def __init__(self, trail_id, trail_name, location, difficulty, distance, description, created_at):
        self.trail_id = trail_id
        self.trail_name = trail_name
        self.location = location
        self.difficulty = difficulty
        self.distance = distance
        self.description = description
        self.created_at = created_at

    def to_dict(self):
        return {
            'trail_id': self.trail_id,
            'trail_name': self.trail_name,
            'location': self.location,
            'difficulty': self.difficulty,
            'distance': self.distance,
            'description': self.description,
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
        hikeObj = Hike(str(hike[0]), str(hike[1]), str(hike[2]), str(hike[3]), str(hike[4]), str(hike[5]), str(hike[6]))
        hikeRecords.append(hikeObj)
    hikeDictionaryList = [record.to_dict() for record in hikeRecords]
    cursor.close()
    return jsonify(hikeDictionaryList)

if __name__ == "__main__":
    app.run(debug=True)