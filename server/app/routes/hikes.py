import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from server.app.models import Hike, RoutePoint
from server.app import mysql

hikes_bp = Blueprint('hikes', __name__)

@hikes_bp.route('/hikes', methods = ['GET'])
def getHikeData():
    if (request.method == 'GET'):
        difficulty = request.args.get('difficulty', default = '', type = str)

        # Get all hikes or based on difficulty
        cursor = mysql.connection.cursor()
        hikeQuery = '''
            SELECT *
            FROM Hikes
        '''
        if (difficulty):
            hikeQuery += 'WHERE difficulty = %s'
            cursor.execute(hikeQuery, (difficulty,))
        else:
            cursor.execute(hikeQuery)
        hikes = cursor.fetchall()

        # Collect all hikes
        hikeRecords = []
        for hike in hikes:
            hikeID = str(hike[0])

            # Collect all routing nodes for this hike
            cursor.execute(
                '''
                SELECT latitude, longitude
                FROM RoutePoints
                WHERE trail_id = %s
                ORDER BY point_order
                ''',
                (hikeID,)
            )
            routePoints = cursor.fetchall()

            # Create list of point objects for routing nodes
            routingPointRecords = [RoutePoint(float(point[0]), float(point[1])) for point in routePoints]

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

@hikes_bp.route('/favorite/hikes', methods = ['POST'])
@jwt_required()
def postFavoriteHikes():
    username = get_jwt_identity()

    if (request.method == 'POST'):
        data = request.get_json()

        # Default to empty list if not provided
        favorite_hikes = data.get('favorite_hikes', [])

        # Check for valid JSON array
        favorite_hikes_json = json.dumps(favorite_hikes)

        # Update the user's favorite hikes in the database
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            UPDATE Users
            SET favorite_hikes = %s
            WHERE username = %s
            ''',
            (favorite_hikes_json, username,)
        )
        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'Favorite hikes updated successfully', 'favorite_hikes': favorite_hikes}), 200
