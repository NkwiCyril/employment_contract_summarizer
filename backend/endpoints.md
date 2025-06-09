# Employment Contract Summarizer - API Endpoints

Base URL: `http://localhost:5000`

## 🏥 Health Check Endpoints

### Check API Health
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "employment-contract-api"
}
```

### API Information
```http
GET /
```
**Response:**
```json
{
  "message": "Employment Contract Summarization API",
  "version": "1.0.0",
  "status": "active"
}
```

---

## 🔐 Authentication Endpoints

### Register New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@company.cm",
  "password": "secure_password",
  "role": "user"
}
```

**Response (Success - 201):**
```json
{
  "message": "User created successfully",
  "user_id": 1
}
```

**Response (Error - 400):**
```json
{
  "error": "Email already registered"
}
```

### User Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@company.cm",
  "password": "secure_password"
}
```

**Response (Success - 200):**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@company.cm",
    "role": "user",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Response (Error - 401):**
```json
{
  "error": "Invalid credentials"
}
```

---

## 📄 Contract Management Endpoints

### Upload Employment Contract
```http
POST /api/contracts/upload
Content-Type: multipart/form-data

Form Data:
- file: employment_contract.pdf (PDF/DOCX file)
- user_id: 1 (optional, defaults to 1)
```

**Response (Success - 201):**
```json
{
  "message": "Contract uploaded successfully",
  "contract_id": 15,
  "language": "en",
  "entities_found": 5
}
```

**Response (Error - 400):**
```json
{
  "error": "File type not allowed"
}
```

### Get All Contracts
```http
GET /api/contracts
Query Parameters:
- user_id: 1 (optional)
```

**Response (Success - 200):**
```json
{
  "contracts": [
    {
      "id": 1,
      "file_name": "Software_Developer_Contract.pdf",
      "file_size": 245760,
      "language": "en",
      "status": "completed",
      "uploaded_at": "2024-01-15T10:30:00Z",
      "processed_at": "2024-01-15T10:31:45Z"
    },
    {
      "id": 2,
      "file_name": "HR_Manager_Contract_FR.pdf",
      "file_size": 198400,
      "language": "fr",
      "status": "processing",
      "uploaded_at": "2024-01-15T11:00:00Z",
      "processed_at": null
    }
  ]
}
```

### Get Contract by ID
```http
GET /api/contracts/{contract_id}
```

**Response (Success - 200):**
```json
{
  "contract": {
    "id": 1,
    "file_name": "Software_Developer_Contract.pdf",
    "file_size": 245760,
    "language": "en",
    "status": "completed",
    "uploaded_at": "2024-01-15T10:30:00Z",
    "processed_at": "2024-01-15T10:31:45Z"
  },
  "entities": [
    {
      "id": 1,
      "entity_type": "PERSON",
      "entity_value": "John Doe",
      "confidence": 0.95,
      "section": null
    },
    {
      "id": 2,
      "entity_type": "ORG",
      "entity_value": "TechCorp Cameroon",
      "confidence": 0.92,
      "section": null
    },
    {
      "id": 3,
      "entity_type": "SALARY",
      "entity_value": "2,500,000 FCFA monthly",
      "confidence": 0.88,
      "section": null
    }
  ]
}
```

**Response (Error - 404):**
```json
{
  "error": "Contract not found"
}
```

### Delete Contract
```http
DELETE /api/contracts/{contract_id}
```

**Response (Success - 200):**
```json
{
  "message": "Contract deleted successfully"
}
```

---

## 🤖 Summary Generation Endpoints

### Generate Contract Summary
```http
POST /api/summaries/generate/{contract_id}
Content-Type: application/json

{
  "type": "standard"
}
```

**Summary Types:**
- `"brief"` - 100-150 words
- `"standard"` - 200-250 words  
- `"detailed"` - 300-400 words

**Response (Success - 201):**
```json
{
  "summary": {
    "id": 23,
    "contract_id": 15,
    "content": "Employment Overview: John Doe appointed as Senior Software Developer at TechCorp Cameroon, starting January 15, 2024, under permanent employment contract with 3-month probationary period.\n\nKey Responsibilities: Lead software development projects, mentor junior developers, collaborate with cross-functional teams, and ensure code quality standards. Report directly to Engineering Manager.\n\nCompensation Package: Base salary of 2,500,000 FCFA monthly, performance-based annual bonus up to 20% of salary, health insurance coverage, transport allowance of 150,000 FCFA monthly, and 25 days annual leave.",
    "confidence_score": 0.87,
    "summary_type": "standard",
    "created_at": "2024-01-15T10:30:00Z",
    "approved": false
  },
  "model_info": {
    "model_used": "fine-tuned-t5",
    "processing_time": "45.2s"
  }
}
```

**Response (Error - 500):**
```json
{
  "error": "Error generating summary: Model loading failed"
}
```

### Get Summary by ID
```http
GET /api/summaries/{summary_id}
```

**Response (Success - 200):**
```json
{
  "summary": {
    "id": 23,
    "contract_id": 15,
    "content": "Employment Overview: John Doe appointed...",
    "confidence_score": 0.87,
    "summary_type": "standard",
    "created_at": "2024-01-15T10:30:00Z",
    "approved": false
  },
  "contract": {
    "id": 15,
    "file_name": "Software_Developer_Contract.pdf",
    "file_size": 245760,
    "language": "en",
    "status": "completed",
    "uploaded_at": "2024-01-15T10:25:00Z",
    "processed_at": "2024-01-15T10:30:00Z"
  }
}
```

### Get Summaries by Contract
```http
GET /api/summaries/contract/{contract_id}
```

**Response (Success - 200):**
```json
{
  "summaries": [
    {
      "id": 23,
      "contract_id": 15,
      "content": "Brief summary content...",
      "confidence_score": 0.85,
      "summary_type": "brief",
      "created_at": "2024-01-15T10:30:00Z",
      "approved": true
    },
    {
      "id": 24,
      "contract_id": 15,
      "content": "Standard summary content...",
      "confidence_score": 0.87,
      "summary_type": "standard",
      "created_at": "2024-01-15T10:35:00Z",
      "approved": false
    }
  ]
}
```

### Approve Summary
```http
PUT /api/summaries/{summary_id}/approve
```

**Response (Success - 200):**
```json
{
  "message": "Summary approved successfully"
}
```

### Submit Summary Feedback
```http
POST /api/summaries/{summary_id}/feedback
Content-Type: application/json

{
  "feedback": "The summary accurately captures the key employment terms and is well-structured.",
  "rating": 5
}
```

**Response (Success - 200):**
```json
{
  "message": "Feedback submitted successfully"
}
```

---

## 📊 Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 404 | Not Found | Resource not found |
| 500 | Server Error | Internal server error |

---

## 🔑 Authentication Headers

For protected endpoints (currently optional in development):

```http
Authorization: Bearer <jwt_token>
```

---

## 📝 Example Usage with cURL

### Upload a Contract
```bash
curl -X POST \
  http://localhost:5000/api/contracts/upload \
  -F "file=@employment_contract.pdf" \
  -F "user_id=1"
```

### Generate Summary
```bash
curl -X POST \
  http://localhost:5000/api/summaries/generate/1 \
  -H "Content-Type: application/json" \
  -d '{"type": "standard"}'
```

### Get All Contracts
```bash
curl -X GET "http://localhost:5000/api/contracts?user_id=1"
```

### Health Check
```bash
curl -X GET http://localhost:5000/health
```

---

## 🚀 Testing the API

You can test these endpoints using:
- **Postman** - Import the endpoints and test interactively
- **cURL** - Command line testing (examples above)
- **Frontend** - The Next.js frontend uses these endpoints
- **Python requests** - For automated testing

### Quick Test Script
```python
import requests

# Test health
response = requests.get('http://localhost:5000/health')
print(f"Health: {response.json()}")

# Test contract list
response = requests.get('http://localhost:5000/api/contracts')
print(f"Contracts: {response.json()}")
```

All endpoints are now ready for use! 🎯