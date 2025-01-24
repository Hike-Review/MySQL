from flask import Flask
# from flask_mysqldb import MySQL

app = Flask(__name__)

# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'password'
# app.config['MYSQL_DB'] = 'HikeReviewDB'
# mysql = MySQL(app)
# cursor = mysql.connection.cursor()

# Setup route pages
@app.route("/")
def home():
    return "Custom API"

@app.route("/data")
def getData():
    # Return template data as JSON
    return {"Users": ["Bob", "Alice", "Chris"]}

    # MySQL Temp fetching
    # cur = mysql.connection.cursor()
    # cur.execute('SELECT * FROM dataRecord')
    # dataObj = cur.fetchall()
    # cur.close()
    # return f"d: {dataObj}"

if __name__ == "__main__":
    app.run(debug=True)