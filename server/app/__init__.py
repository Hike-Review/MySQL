from flask import Flask, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config

mysql = MySQL()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)
    jwt.init_app(app)
    CORS(app)

    from .routes.auth import auth_bp
    from .routes.hikes import hikes_bp
    from .routes.groups import groups_bp
    from .routes.reviews import reviews_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(hikes_bp)
    app.register_blueprint(groups_bp)
    app.register_blueprint(reviews_bp)

    # JWT Error Handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({'message': 'Token has expired', 'error': 'tokenExpired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'message': 'Signature verification failed', 'error': 'invalidToken'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'message': 'Request doesn\'t contain valid token', 'error': 'authorizationHeader'}), 401

    return app