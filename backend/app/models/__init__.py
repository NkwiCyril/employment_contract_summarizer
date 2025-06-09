# app/models/__init__.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and access control"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # user, hr, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    contracts = db.relationship('Contract', backref='user', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat()
        }

class Contract(db.Model):
    """Employment contract model"""
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(10), nullable=False)  # 'en' or 'fr'
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    summary = db.relationship('Summary', backref='contract', uselist=False)
    entities = db.relationship('Entity', backref='contract', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'language': self.language,
            'status': self.status,
            'uploaded_at': self.uploaded_at.isoformat(),
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class Summary(db.Model):
    """Generated summary model"""
    __tablename__ = 'summaries'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    summary_type = db.Column(db.String(20), default='standard')  # brief, standard, detailed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'content': self.content,
            'confidence_score': self.confidence_score,
            'summary_type': self.summary_type,
            'created_at': self.created_at.isoformat(),
            'approved': self.approved
        }

class Entity(db.Model):
    """Extracted employment entities"""
    __tablename__ = 'entities'
    
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # salary, position, benefits, etc.
    entity_value = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    section = db.Column(db.String(100), nullable=True)  # which section it was found in
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_value': self.entity_value,
            'confidence': self.confidence,
            'section': self.section
        }

class AuditLog(db.Model):
    """Audit log for tracking system activities"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class Config(db.Model):
    """System configuration"""
    __tablename__ = 'config'
    
    id = db.Column(db.Integer, primary_key=True)
    parameter = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'parameter': self.parameter,
            'value': self.value,
            'description': self.description,
            'updated_at': self.updated_at.isoformat()
        }