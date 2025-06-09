# Development scripts
# scripts/setup.sh
#!/bin/bash

echo "Setting up Employment Contract Summarizer..."

# Create project directory structure
mkdir -p data/raw data/processed data/models uploads

# Backend setup
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download spaCy models
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm

# Initialize database
python -c "from app import create_app; from app.models import db; app = create_app(); app.app_context().push(); db.create_all()"

cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
cd ..

echo "Setup complete! Run the following commands to start the development servers:"
echo ""
echo "Backend:"
echo "cd backend && source venv/bin/activate && python app/main.py"
echo ""
echo "Frontend:"
echo "cd frontend && npm run dev"
