import os

class Config:
    # Main Google SQL Database
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.getenv('MYSQL_DB')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))