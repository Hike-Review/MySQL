from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Review
from app import mysql

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/reviews', methods = ['GET'])
def getReviews():
    if (request.method == 'GET'):
        trail_id = request.args.get('trail_id', type = int)

        # Check for trail id
        if (trail_id == None):
            return jsonify({'error': 'trail_id parameter is required'}), 400

        # Get list of reviews from database
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            SELECT *
            FROM Reviews
            WHERE trail_id = %s
            ORDER BY review_date DESC
            ''',
            (trail_id,)
        )
        reviews = cursor.fetchall()

        # Collect all reviews
        reviewRecords = []
        for review in reviews:
            # Create review object
            reviewId = str(review[0])
            trailId = str(review[1])
            username = str(review[2])
            rating = str(review[3])
            reviewText = str(review[4])
            reviewDate = str(review[5])
            reviewObj = Review(reviewId, trailId, username, rating, reviewText, reviewDate)
            reviewRecords.append(reviewObj)

        cursor.close()
        return jsonify([review.toDictionary() for review in reviewRecords])


@reviews_bp.route('/reviews', methods = ['POST'])
@jwt_required()
def postReviews():
    if (request.method == 'POST'):
        data = request.json

        # Check for all required parameters
        required_fields = ['trail_id', 'username', 'rating', 'review_text']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400

        trail_id = data['trail_id']
        username = data['username']
        rating = data['rating']
        review_text = data['review_text']

        # Check for valid rating
        if not (1 <= rating <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        # Insert review data into database
        cursor = mysql.connection.cursor()
        cursor.execute(
            '''
            INSERT INTO Reviews (trail_id, username, rating, review_text)
            VALUES (%s, %s, %s, %s)
            ''',
            (trail_id, username, rating, review_text,)
        )
        mysql.connection.commit()

        new_id = cursor.lastrowid
        cursor.close()

        return jsonify({'message': 'Review added successfully', 'review_id': new_id}), 201
