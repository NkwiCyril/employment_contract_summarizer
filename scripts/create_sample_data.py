# scripts/create_sample_data.py
"""
Script to create sample employment contracts and test data
"""

import os
import sys
import json
from datetime import datetime, timedelta

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.app import create_app
from backend.app.models import db, User, Contract, Summary, Entity, AuditLog

def create_sample_contracts():
    """Create sample employment contract data for testing"""
    
    app = create_app('development')
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Create sample users
        users = [
            User(
                username='hr_admin',
                email='hr@company.cm',
                password_hash='hashed_password',
                role='hr'
            ),
            User(
                username='legal_counsel',
                email='legal@lawfirm.cm',
                password_hash='hashed_password',
                role='legal'
            ),
            User(
                username='employee_user',
                email='employee@email.cm',
                password_hash='hashed_password',
                role='user'
            )
        ]
        
        for user in users:
            db.session.add(user)
        
        db.session.commit()
        
        # Sample contract data
        sample_contracts = [
            {
                'file_name': 'Software_Developer_Contract_EN.pdf',
                'language': 'en',
                'status': 'completed',
                'file_size': 245760,
                'summary_content': """Employment Overview: John Doe appointed as Senior Software Developer at TechCorp Cameroon, starting January 15, 2024, under permanent employment contract with 3-month probationary period.

Key Responsibilities: Lead software development projects, mentor junior developers, collaborate with cross-functional teams, and ensure code quality standards. Report directly to Engineering Manager.

Compensation Package: Base salary of 2,500,000 FCFA monthly, performance-based annual bonus up to 20% of salary, health insurance coverage, transport allowance of 150,000 FCFA monthly, and 25 days annual leave.

Working Arrangements: Standard 40-hour work week, Monday to Friday 8:00 AM to 5:00 PM, hybrid work arrangement with 3 days office attendance required. Home office setup allowance provided.

Important Terms: 30-day notice period for resignation, confidentiality agreement covers proprietary technology, intellectual property rights assigned to company, non-compete clause for 6 months post-employment.""",
                'entities': [
                    {'type': 'PERSON', 'value': 'John Doe', 'confidence': 0.95},
                    {'type': 'ORG', 'value': 'TechCorp Cameroon', 'confidence': 0.92},
                    {'type': 'SALARY', 'value': '2,500,000 FCFA monthly', 'confidence': 0.88},
                    {'type': 'DATE', 'value': 'January 15, 2024', 'confidence': 0.90},
                    {'type': 'MONEY', 'value': '150,000 FCFA', 'confidence': 0.85}
                ]
            },
            {
                'file_name': 'Gestionnaire_RH_Contrat_FR.pdf',
                'language': 'fr',
                'status': 'completed',
                'file_size': 198400,
                'summary_content': """Aperçu de l'emploi: Marie Dubois nommée Gestionnaire des Ressources Humaines chez Entreprise Cameroun SARL, début le 1er février 2024, contrat permanent avec période d'essai de 6 mois.

Responsabilités clés: Gérer le recrutement et la sélection, administrer les avantages sociaux, superviser les relations employés, assurer la conformité légale, et développer les politiques RH.

Package de rémunération: Salaire de base 1,800,000 FCFA mensuel, prime de performance trimestrielle, assurance maladie familiale, allocation logement 200,000 FCFA, 30 jours de congé annuel.

Modalités de travail: Horaire standard 35 heures par semaine, lundi au vendredi 8h00 à 16h00, bureau principal à Douala, déplacements occasionnels requis dans les filiales.

Termes importants: Préavis de 60 jours pour démission, clause de confidentialité sur données personnelles employés, formation continue obligatoire, évaluation performance semestrielle.""",
                'entities': [
                    {'type': 'PERSON', 'value': 'Marie Dubois', 'confidence': 0.94},
                    {'type': 'ORG', 'value': 'Entreprise Cameroun SARL', 'confidence': 0.91},
                    {'type': 'SALARY', 'value': '1,800,000 FCFA mensuel', 'confidence': 0.87},
                    {'type': 'DATE', 'value': '1er février 2024', 'confidence': 0.89},
                    {'type': 'MONEY', 'value': '200,000 FCFA', 'confidence': 0.86}
                ]
            },
            {
                'file_name': 'Executive_Manager_Contract_EN.pdf',
                'language': 'en',
                'status': 'processing',
                'file_size': 425600,
                'summary_content': None,
                'entities': []
            },
            {
                'file_name': 'Comptable_Principal_FR.pdf',
                'language': 'fr',
                'status': 'failed',
                'file_size': 187200,
                'summary_content': None,
                'entities': []
            }
        ]
        
        # Create contracts and related data
        for i, contract_data in enumerate(sample_contracts):
            user_id = (i % len(users)) + 1
            
            # Create contract
            contract = Contract(
                user_id=user_id,
                file_name=contract_data['file_name'],
                file_path=f"./uploads/{contract_data['file_name']}",
                file_size=contract_data['file_size'],
                language=contract_data['language'],
                status=contract_data['status'],
                uploaded_at=datetime.utcnow() - timedelta(days=i*2),
                processed_at=datetime.utcnow() - timedelta(days=i*2-1) if contract_data['status'] == 'completed' else None
            )
            
            db.session.add(contract)
            db.session.flush()  # Get the contract ID
            
            # Create summary if contract is completed
            if contract_data['summary_content']:
                summary = Summary(
                    contract_id=contract.id,
                    content=contract_data['summary_content'],
                    confidence_score=0.85 + (i * 0.03),  # Varying confidence scores
                    summary_type='standard',
                    approved=i < 2  # First two summaries are approved
                )
                db.session.add(summary)
            
            # Create entities
            for entity_data in contract_data['entities']:
                entity = Entity(
                    contract_id=contract.id,
                    entity_type=entity_data['type'],
                    entity_value=entity_data['value'],
                    confidence=entity_data['confidence']
                )
                db.session.add(entity)
            
            # Create audit log
            audit_log = AuditLog(
                user_id=user_id,
                action='upload_contract',
                resource_type='contract',
                resource_id=contract.id,
                details=f"Uploaded {contract_data['file_name']}",
                timestamp=contract.uploaded_at
            )
            db.session.add(audit_log)
        
        db.session.commit()
        print("Sample data created successfully!")
        print(f"Created {len(users)} users and {len(sample_contracts)} contracts")

def create_sample_files():
    """Create sample employment contract files for demonstration"""
    
    # Create uploads directory if it doesn't exist
    uploads_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    # Sample English contract content
    english_contract = """
EMPLOYMENT CONTRACT

This Employment Contract is entered into between TechCorp Cameroon Ltd., a company incorporated under the laws of Cameroon (the "Company"), and John Doe (the "Employee").

1. POSITION AND DUTIES
The Employee is appointed as Senior Software Developer, reporting to the Engineering Manager. The Employee shall perform duties including but not limited to:
- Leading software development projects
- Mentoring junior developers
- Collaborating with cross-functional teams
- Ensuring code quality and best practices

2. COMPENSATION
Base Salary: 2,500,000 FCFA per month
Annual Bonus: Performance-based, up to 20% of annual salary
Benefits: Health insurance, transport allowance (150,000 FCFA/month)

3. WORKING CONDITIONS
Working Hours: 40 hours per week, Monday to Friday, 8:00 AM to 5:00 PM
Location: Hybrid arrangement - 3 days office, 2 days remote
Annual Leave: 25 working days

4. TERMINATION
Notice Period: 30 days written notice required from either party
Confidentiality: Employee agrees to maintain confidentiality of proprietary information

Start Date: January 15, 2024
Contract Type: Permanent Employment
Probation Period: 3 months

Signed:
Company Representative: ________________
Employee: ________________
Date: ________________
"""

    # Sample French contract content
    french_contract = """
CONTRAT DE TRAVAIL

Ce contrat de travail est conclu entre Entreprise Cameroun SARL, société constituée selon les lois du Cameroun (la "Société"), et Marie Dubois (l'"Employée").

1. POSTE ET FONCTIONS
L'Employée est nommée Gestionnaire des Ressources Humaines. Ses fonctions incluent notamment:
- Gestion du recrutement et de la sélection
- Administration des avantages sociaux
- Supervision des relations employés
- Assurance de la conformité légale

2. RÉMUNÉRATION
Salaire de base: 1,800,000 FCFA par mois
Prime de performance: Trimestrielle selon objectifs
Avantages: Assurance maladie familiale, allocation logement (200,000 FCFA/mois)

3. CONDITIONS DE TRAVAIL
Horaires: 35 heures par semaine, lundi au vendredi, 8h00 à 16h00
Lieu: Bureau principal à Douala
Congés annuels: 30 jours ouvrables

4. RÉSILIATION
Préavis: 60 jours de préavis écrit requis
Confidentialité: L'employée s'engage à maintenir la confidentialité des données

Date de début: 1er février 2024
Type de contrat: Emploi permanent
Période d'essai: 6 mois

Signatures:
Représentant de la Société: ________________
Employée: ________________
Date: ________________
"""

    # Save sample files
    with open(os.path.join(uploads_dir, 'Software_Developer_Contract_EN.pdf'), 'w') as f:
        f.write(english_contract)
    
    with open(os.path.join(uploads_dir, 'Gestionnaire_RH_Contrat_FR.pdf'), 'w') as f:
        f.write(french_contract)
    
    print("Sample contract files created in uploads directory")
