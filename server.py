from flask import Flask
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

# Setup route pages
@app.route("/")
def home():
    return "Custom API"

@app.route("/data")
def getData():
    # Return template data as JSON
    return {"Users": ["Bob", "Alice", "Chris"]}

@app.route("/MySQLdata")
def getMySQLData():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    usersString = ''
    for record in users:
        usersString += 'Id: ' + str(record[0]) + '\n'
        usersString += 'Username: ' + str(record[1]) + '\n'
        usersString += 'Email: ' + str(record[2]) + '\n'
        usersString += 'Password: ' + str(record[3]) + '\n'
        usersString += 'Created At: ' + str(record[4]) + '\n'
    
    cursor.close()
    return usersString

if __name__ == "__main__":
    app.run(debug=True)