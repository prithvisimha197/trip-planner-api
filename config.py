import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret-key-change-in-production')

    # Handle both DATABASE_URL and Heroku's postgres:// format
    # Use psycopg (version 3) driver
    database_url = os.getenv('DATABASE_URL', 'postgresql+psycopg://localhost/trip_planner')
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
    elif database_url and database_url.startswith('postgresql://') and '+psycopg' not in database_url:
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,    # Recycle connections after 5 minutes
    }
    JWT_TOKEN_LOCATION = ['headers']
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
