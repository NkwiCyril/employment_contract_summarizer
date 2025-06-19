from app import create_app
import os
from flask_cors import CORS


app = create_app(os.getenv('FLASK_ENV', 'development'))

# Initialize CORS for the Flask app
CORS(app, supports_credentials=True)

@app.route('/')
def index():
    return {
        'message': 'Employment Contract Summarization API',
        'version': '1.0.0',
        'status': 'active'
    }

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'employment-contract-api'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)