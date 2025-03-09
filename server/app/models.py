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

# Route Points Datastructure
class RoutePoint:
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
    def __init__(self, trail_id, trail_name, trail_image, difficulty, rating, distance, duration, start_lat, start_lng, end_lat, end_lng, tags, description, creator_id, created_at, routing_points):
        self.trail_id = trail_id
        self.trail_name = trail_name
        self.trail_image = trail_image
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
            'trail_image': self.trail_image,
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
    def __init__(self, review_id, trail_id, username, rating, review_text, review_date):
        self.review_id = review_id
        self.trail_id = trail_id
        self.username = username
        self.rating = rating
        self.review_text = review_text
        self.review_date = review_date

    def toDictionary(self):
        return {
            'review_id': self.review_id,
            'trail_id': self.trail_id,
            'username': self.username,
            'rating': self.rating,
            'review_text': self.review_text,
            'review_date': self.review_date
        }

# Group Datastructure
class Group:
    def __init__(self, group_id, group_name, group_description, trail_id, created_by, group_host, created_at, start_time, trail_name, total_users_joined, users_joined):
        self.group_id = group_id 
        self.group_name = group_name 
        self.group_description = group_description 
        self.trail_id = trail_id 
        self.created_by = created_by 
        self.group_host = group_host 
        self.created_at = created_at 
        self.start_time = start_time
        self.trail_name = trail_name
        self.total_users_joined = total_users_joined
        self.users_joined = users_joined

    def toDictionary(self):
        return {
            'group_id': self.group_id, 
            'group_name': self.group_name, 
            'group_description': self.group_description, 
            'trail_id': self.trail_id, 
            'created_by': self.created_by, 
            'group_host': self.group_host, 
            'created_at': self.created_at, 
            'start_time': self.start_time,
            'trail_name': self.trail_name,
            'total_users_joined': self.total_users_joined,
            'users_joined': self.users_joined
        }