import os
from decouple import config

class Config:
    SECRET_KEY = config('SECRET_KEY', default='dev-secret-key')
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL', default='sqlite:///employment_contracts.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = config('MODEL_PATH', default='./data/models/')
    UPLOAD_FOLDER = config('UPLOAD_FOLDER', default='./uploads/')
    MAX_CONTENT_LENGTH = config('MAX_CONTENT_LENGTH', default=16 * 1024 * 1024, cast=int)
    
class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}