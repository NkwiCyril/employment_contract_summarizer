# scripts/start-dev.sh
# !/bin/bash

# Start development servers
echo "Starting development servers..."

# Start backend in background
cd backend
source venv/bin/activate
python app/main.py &
BACKEND_PID=$!

# Start frontend in background  
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Backend running on http://127.0.0.1:5000"
echo "Frontend running on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait