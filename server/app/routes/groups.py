from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.models import Group
from app import mysql

groups_bp = Blueprint('groups', __name__)

@groups_bp.route('/groups', methods = ['GET'])
def getGroups():
    if (request.method == 'GET'):
        trailIdInput = request.args.get('trail_id', default = '', type = str)
        startDateInput = request.args.get('start_date_range', type = str)
        endDateInput = request.args.get('end_date_range', type = str)

        # Check for required parameters
        if (startDateInput == None or endDateInput == None):
            return jsonify({"error": "missing start and/or end date"}), 400

        #Check for valid date timestamps
        try:
            startDate = datetime.strptime(startDateInput, '%Y-%m-%d %H:%M:%S')
            endDate = datetime.strptime(endDateInput, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({"error": "Invalid date format format used. Use 'YYYY-MM-DD HH:MM:SS'"}), 400

        # Get All groups or groups based on Trail Id
        cursor = mysql.connection.cursor()
        groupQuery = '''
            SELECT *
            FROM UserGroups
            WHERE start_time >= %s
            AND start_time <= %s
        '''
        if (trailIdInput):
            groupQuery += '''
                AND trail_id = %s
                ORDER BY start_time ASC
            '''
            cursor.execute(groupQuery, (startDate, endDate, trailIdInput,))
        else:
            groupQuery += 'ORDER BY start_time ASC'
            cursor.execute(groupQuery, (startDate, endDate,))
        groups = cursor.fetchall()

        if (groups == None):
            return jsonify({"error": "invalid group_id, group does not exist"}), 400

        groupRecords = []
        for group in groups:
            groupId = str(group[0])
            trailId = str(group[3])

            # Get group member user_ids
            cursor.execute(
                '''
                SELECT user_id
                FROM UserGroupMembers
                WHERE group_id = %s
                ''',
                (groupId,)
            )
            usersInGroup = cursor.fetchall()
            joinedUsers = [user[0] for user in usersInGroup]
            totalJoinedUsers = len(joinedUsers)

            # Get trail name
            cursor.execute(
                '''
                SELECT trail_name
                FROM Hikes
                WHERE trail_id = %s
                ''',
                (trailId,)
            )
            trail = cursor.fetchone()
            trailName = str(trail[0])

            # Create Group Object
            groupName = str(group[1])
            groupDescription = str(group[2])
            createdByUserId = str(group[4])
            groupHostUsername = str(group[5])
            groupCreatedAt = str(group[6])
            groupStartTime = str(group[7])
            groupObj = Group(
                groupId, groupName, groupDescription, trailId, createdByUserId,
                groupHostUsername, groupCreatedAt, groupStartTime, trailName,
                totalJoinedUsers, joinedUsers
            )
            groupRecords.append(groupObj)

        cursor.close()
        return jsonify([group.toDictionary() for group in groupRecords]), 200

@groups_bp.route('/groups', methods = ['POST'])
@jwt_required()
def postGroups():
    if (request.method == 'POST'):
        data = request.json

        # Check for all required parameters
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
        cursor.execute(
            '''
            SELECT user_id
            FROM Users
            WHERE username = %s
            ''',
            (hostName,)
        )
        hostUser = cursor.fetchone()
        if (hostUser == None):
            return jsonify({"error": "Invalid user posting to database."}), 400

        hostUserId = str(hostUser[0])

        # Insert new group to database
        cursor.execute(
            '''
            INSERT INTO UserGroups (trail_id, created_by, group_host, group_name, group_description, start_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            ''',
            (trailId, hostUserId, hostName, groupName, groupDescription, startTimeStamp,)
        )
        newGroupId = cursor.lastrowid

        # Automatically Join Host to the group
        cursor.execute(
            '''
            INSERT INTO
            UserGroupMembers (user_id, group_id)
            VALUES (%s, %s)
            ''',
            (hostUserId, newGroupId,)
        )

        mysql.connection.commit()
        cursor.close()

        return jsonify({'message': 'Group added successfully', 'groupId': newGroupId}), 201

@groups_bp.route('/join/group', methods = ['POST'])
@jwt_required()
def joinGroup():
    if (request.method == 'POST'):
        data = request.json

        # Check for all required parameters
        required_fields = ['group_id', 'user_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        groupId = data['group_id']
        userId = data['user_id']
        
        # Get group object
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            SELECT trail_id, start_time
            FROM UserGroups WHERE group_id = %s
            ''',
            (groupId,)
        )
        group = cursor.fetchone()
        if (group == None):
            return jsonify({"error": "invalid group_id, group does not exist"}), 400

        startTime = str(group[1])

        # Validate if joining before start time
        currentTime = datetime.now()
        startTimeStamp = datetime.strptime(startTime, '%Y-%m-%d %H:%M:%S')
        if (currentTime > startTimeStamp):
            # Remove from database once hike has started
            cursor.execute(
                '''
                DELETE FROM UserGroupMembers
                WHERE group_id = %s
                ''',
                (groupId,)
            )
            cursor.execute(
                '''
                DELETE FROM UserGroups
                WHERE group_id = %s
                ''',
                (groupId,)
            )
            mysql.connection.commit()
            cursor.close()
            return jsonify({"message": "Did not join in time"}), 409

        # Attempt to join into group
        try:
            cursor.execute(
                '''
                INSERT INTO UserGroupMembers
                (user_id, group_id) VALUES (%s, %s)
                ''',
                (userId, groupId,)
            )
            mysql.connection.commit()
        except Exception as e:
            cursor.close()
            return jsonify({"error": "already joined the group"}), 400

        cursor.close()
        return jsonify({"message": "Joined group successfully", "group_id": groupId}), 201
