from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        from config.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    else:
        from config.config import ProductionConfig
        app.config.from_object(ProductionConfig)
    
    # Initialize extensions
    from app.models import db
    db.init_app(app)
    
    # Enable CORS
    CORS(app, origins=['http://localhost:3000'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.contracts import contracts_bp
    from app.routes.summaries import summaries_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')
    app.register_blueprint(summaries_bp, url_prefix='/api/summaries')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app