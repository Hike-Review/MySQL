import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, get_jwt, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from server.app import mysql

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods = ['POST'])
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
                '''
                SELECT username
                FROM Users
                WHERE username = %s
                LIMIT 1
                ''',
                (username,)
            )
            existingUsername = cursor.fetchall()

            if (existingUsername):
                return jsonify({'message': 'Username already in use'}), 409

            # Check if email is already in database
            cursor.execute(
                '''
                SELECT email
                FROM Users
                WHERE email = %s
                LIMIT 1
                ''',
                (email,)
            )
            existingUserEmail = cursor.fetchall()

            if (existingUserEmail):
                return jsonify({'message': 'Email already in use'}), 409

            # Insert new user
            cursor.execute(
                '''
                INSERT INTO Users
                (username, email, password_hash)
                VALUES (%s, %s, %s)
                ''',
                (username, email, hashedPassword,)
            )
            mysql.connection.commit()
            cursor.close()
            return jsonify({'message' : 'User created successfully', 'username' : username}), 201

        except Exception as e:
            cursor.close()
            return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/login', methods = ['POST'])
def login():
    if (request.method == 'POST'):
        data = request.json
        username = data['username']
        email = data['email']
        password = data['password']

        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            SELECT username, email, password_hash
            FROM Users
            WHERE username = %s
            OR email = %s
            LIMIT 1
            ''',
            (username, email,)
        )
        user = cursor.fetchone()
        cursor.close()

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

@auth_bp.route('/auth/refresh', methods = ['GET'])
@jwt_required(refresh = True)
def refreshToken():
    if (request.method == 'GET'):
        username = get_jwt_identity()
        newAccessToken = create_access_token(identity = username)
        return jsonify({'access' : newAccessToken})

@auth_bp.route('/auth/identity', methods = ['GET'])
@jwt_required()
def getCurrentIdentity():
    claims = get_jwt()
    username = claims.get('sub')

    if (request.method == 'GET'):
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            SELECT user_id, username, email, created_at, favorite_hikes
            FROM Users
            WHERE username = %s
            LIMIT 1
            ''',
            (username,)
        )
        user = cursor.fetchone()

        cursor.execute(
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
        groups = cursor.fetchall()
        cursor.close()

        if (user):
            return jsonify(
                {
                    'claims': claims,
                    'user_details': {
                        'user_id': user[0],
                        'username': user[1],
                        'email': user[2],
                        'created_at': user[3],
                        'favorite_hikes': json.loads(user[4]) if user[4] else []
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
