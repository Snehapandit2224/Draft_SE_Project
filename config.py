import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secret-jwt-key'
    JWT_TOKEN_LOCATION = ['headers']
    CORS_HEADERS = 'Content-Type'
    # Comma-separated list or single origin for allowed CORS origins
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS') or 'http://localhost:5000'

class DevelopmentConfig(Config):
    DEBUG = True
    # Use SQLite for local development if MySQL is not configured
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///hr_attrition_dev.db'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    JWT_SECRET_KEY = 'test-secret-jwt-key'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://user:password@host/hr_attrition_prod'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
