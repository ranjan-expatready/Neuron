#!/bin/bash
# Backend Startup Script
# Canada Immigration OS

set -e

echo "🚀 Starting Canada Immigration OS Backend..."

# Navigate to backend directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cat > .env << EOF
DATABASE_URL=sqlite:///./test.db
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DOCUMENT_STORAGE_PATH=./uploads
EOF
    echo "✅ .env file created"
fi

# Create uploads directory
mkdir -p uploads

# Check if database exists, create if not
if [ ! -f "test.db" ]; then
    echo "🗄️  Database will be created on first run..."
fi

# Start the server
echo "🌟 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
