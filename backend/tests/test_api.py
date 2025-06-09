import pytest
import json
import os
import sys
import tempfile

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app
from app.models import db, User, Contract

@pytest.fixture
def app():
    """Create test app"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return headers"""
    # Register user
    client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    # Login
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    token = json.loads(response.data)['token']
    return {'Authorization': f'Bearer {token}'}

class TestAuthAPI:
    """Test authentication endpoints"""
    
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'user_id' in data
        assert data['message'] == 'User created successfully'
    
    def test_login_user(self, client):
        """Test user login"""
        # First register
        client.post('/api/auth/register', json={
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        # Then login
        response = client.post('/api/auth/login', json={
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user' in data

class TestContractsAPI:
    """Test contract management endpoints"""
    
    def test_upload_contract(self, client, auth_headers):
        """Test contract upload"""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'Sample contract content')
            tmp_path = tmp.name
        
        try:
            with open(tmp_path, 'rb') as f:
                response = client.post('/api/contracts/upload',
                    data={
                        'file': (f, 'test_contract.pdf'),
                        'user_id': '1'
                    },
                    headers=auth_headers
                )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'contract_id' in data
            assert data['message'] == 'Contract uploaded successfully'
        
        finally:
            os.unlink(tmp_path)
    
    def test_get_contracts(self, client, auth_headers):
        """Test retrieving contracts"""
        response = client.get('/api/contracts/?user_id=1', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'contracts' in data
        assert isinstance(data['contracts'], list)

class TestSummariesAPI:
    """Test summary generation endpoints"""
    
    def test_generate_summary(self, client, auth_headers, app):
        """Test summary generation"""
        with app.app_context():
            # Create a test contract first
            contract = Contract(
                user_id=1,
                file_name='test.pdf',
                file_path='/tmp/test.pdf',
                file_size=1024,
                language='en',
                status='pending'
            )
            db.session.add(contract)
            db.session.commit()
            
            contract_id = contract.id
        
        response = client.post(f'/api/summaries/generate/{contract_id}',
            json={'type': 'standard'},
            headers=auth_headers
        )