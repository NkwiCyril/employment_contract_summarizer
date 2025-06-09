from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app.models import db, Contract, Entity, AuditLog
from app.utils.document_processor import DocumentProcessor
import os
import uuid
from datetime import datetime

contracts_bp = Blueprint('contracts', __name__)
document_processor = DocumentProcessor()

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@contracts_bp.route('/upload', methods=['POST'])
def upload_contract():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        user_id = request.form.get('user_id', 1)  # Default user for demo
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Generate unique filename
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Create upload directory if it doesn't exist
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save file
        file.save(file_path)
        
        # Extract text and process document
        if filename.lower().endswith('.pdf'):
            text = document_processor.extract_text_from_pdf(file_path)
        else:
            text = document_processor.extract_text_from_docx(file_path)
        
        # Clean text and detect language
        cleaned_text = document_processor.clean_text(text)
        language = document_processor.detect_language(cleaned_text)
        
        # Create contract record
        contract = Contract(
            user_id=user_id,
            file_name=file.filename,
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            language=language,
            status='processing'
        )
        
        db.session.add(contract)
        db.session.commit()
        
        # Extract entities
        entities = document_processor.extract_employment_entities(cleaned_text, language)
        
        for entity_data in entities:
            entity = Entity(
                contract_id=contract.id,
                entity_type=entity_data['label'],
                entity_value=entity_data['text'],
                confidence=entity_data['confidence']
            )
            db.session.add(entity)
        
        # Log activity
        log = AuditLog(
            user_id=user_id,
            action='upload_contract',
            resource_type='contract',
            resource_id=contract.id,
            details=f"Uploaded {file.filename}"
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Contract uploaded successfully',
            'contract_id': contract.id,
            'language': language,
            'entities_found': len(entities)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/', methods=['GET'])
def get_contracts():
    try:
        user_id = request.args.get('user_id', 1)
        contracts = Contract.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'contracts': [contract.to_dict() for contract in contracts]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/<int:contract_id>', methods=['GET'])
def get_contract(contract_id):
    try:
        contract = Contract.query.get_or_404(contract_id)
        entities = Entity.query.filter_by(contract_id=contract_id).all()
        
        return jsonify({
            'contract': contract.to_dict(),
            'entities': [entity.to_dict() for entity in entities]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/<int:contract_id>', methods=['DELETE'])
def delete_contract(contract_id):
    try:
        contract = Contract.query.get_or_404(contract_id)
        
        # Delete associated file
        if os.path.exists(contract.file_path):
            os.remove(contract.file_path)
        
        # Delete from database
        db.session.delete(contract)
        db.session.commit()
        
        return jsonify({'message': 'Contract deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500