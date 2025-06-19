from flask import Blueprint, request, jsonify
from app.models import db, Contract, Summary, AuditLog
from app.utils.model_handler import ModelHandler
from app.utils.document_processor import DocumentProcessor
from datetime import datetime

summaries_bp = Blueprint('summaries', __name__)
model_handler = ModelHandler()
document_processor = DocumentProcessor()

@summaries_bp.route('/generate/<int:contract_id>', methods=['POST'])
def generate_summary(contract_id):
    try:
        contract = Contract.query.get_or_404(contract_id)
        
        # Get summary parameters
        data = request.get_json() or {}
        summary_type = data.get('type', 'standard')  # brief, standard, detailed
        max_length = {
            'brief': 3000,
            'standard': 5000,
            'detailed': 8000
        }.get(summary_type, 5000)
        
        # Extract text from contract
        if contract.file_path.lower().endswith('.pdf'):
            text = document_processor.extract_text_from_pdf(contract.file_path)
        else:
            text = document_processor.extract_text_from_docx(contract.file_path)
        
        cleaned_text = document_processor.clean_text(text)
        
        # Generate summary using ML model
        result = model_handler.generate_summary(cleaned_text, max_length)
        
        # Check if summary already exists
        existing_summary = Summary.query.filter_by(
            contract_id=contract_id, 
            summary_type=summary_type
        ).first()
        
        if existing_summary:
            # Update existing summary
            existing_summary.content = result['summary']
            existing_summary.confidence_score = result['confidence']
            existing_summary.created_at = datetime.utcnow()
            summary = existing_summary
        else:
            # Create new summary
            summary = Summary(
                contract_id=contract_id,
                content=result['summary'],
                confidence_score=result['confidence'],
                summary_type=summary_type
            )
            db.session.add(summary)
        
        # Update contract status
        contract.status = 'completed'
        contract.processed_at = datetime.utcnow()
        
        # Log activity
        log = AuditLog(
            user_id=contract.user_id,
            action='generate_summary',
            resource_type='summary',
            resource_id=summary.id,
            details=f"Generated {summary_type} summary for contract {contract_id}"
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'summary': summary.to_dict(),
            'model_info': {
                'model_used': result['model_used'],
                'processing_time': 'simulated'
            }
        }), 201
        
    except Exception as e:
        # Update contract status to failed
        if 'contract' in locals():
            contract.status = 'failed'
            db.session.commit()
        
        return jsonify({'error': str(e)}), 500

@summaries_bp.route('/<int:summary_id>', methods=['GET'])
def get_summary(summary_id):
    try:
        summary = Summary.query.get_or_404(summary_id)
        contract = Contract.query.get(summary.contract_id)
        
        return jsonify({
            'summary': summary.to_dict(),
            'contract': contract.to_dict() if contract else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@summaries_bp.route('/contract/<int:contract_id>', methods=['GET'])
def get_summaries_by_contract(contract_id):
    try:
        summaries = Summary.query.filter_by(contract_id=contract_id).all()
        
        return jsonify({
            'summaries': [summary.to_dict() for summary in summaries]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@summaries_bp.route('/<int:summary_id>/approve', methods=['PUT'])
def approve_summary(summary_id):
    try:
        summary = Summary.query.get_or_404(summary_id)
        summary.approved = True
        
        # Log activity
        log = AuditLog(
            action='approve_summary',
            resource_type='summary',
            resource_id=summary_id,
            details=f"Summary {summary_id} approved"
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({'message': 'Summary approved successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@summaries_bp.route('/<int:summary_id>/feedback', methods=['POST'])
def submit_feedback(summary_id):
    try:
        data = request.get_json()
        feedback = data.get('feedback', '')
        rating = data.get('rating', 0)
        
        # Log feedback
        log = AuditLog(
            action='submit_feedback',
            resource_type='summary',
            resource_id=summary_id,
            details=f"Feedback: {feedback}, Rating: {rating}"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'message': 'Feedback submitted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500