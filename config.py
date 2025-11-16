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
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'redis'
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or 'redis://localhost:6379/0'
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT') or 300)

class DevelopmentConfig(Config):
    DEBUG = True
    # Use SQLite for local development if MySQL is not configured
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///hr_attrition_dev.db'
    if not SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
        SQLALCHEMY_POOL_SIZE = int(os.environ.get('SQLALCHEMY_POOL_SIZE') or 5)
        SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT') or 30)
        SQLALCHEMY_POOL_RECYCLE = int(os.environ.get('SQLALCHEMY_POOL_RECYCLE') or 1800)
        SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW') or 10)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    JWT_SECRET_KEY = 'test-secret-jwt-key'
    CACHE_TYPE = 'SimpleCache'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+mysqlconnector://user:password@host/hr_attrition_prod'
    if not SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
        SQLALCHEMY_POOL_SIZE = int(os.environ.get('SQLALCHEMY_POOL_SIZE') or 5)
        SQLALCHEMY_POOL_TIMEOUT = int(os.environ.get('SQLALCHEMY_POOL_TIMEOUT') or 30)
        SQLALCHEMY_POOL_RECYCLE = int(os.environ.get('SQLALCHEMY_POOL_RECYCLE') or 1800)
        SQLALCHEMY_MAX_OVERFLOW = int(os.environ.get('SQLALCHEMY_MAX_OVERFLOW') or 10)

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
