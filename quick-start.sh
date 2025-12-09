#!/bin/bash

# Quick Start Script for Canada Immigration OS
# This script helps you launch the application quickly

set -e

echo "🚀 Canada Immigration OS - Quick Start"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Starting PostgreSQL database...${NC}"
docker-compose up -d postgres
echo -e "${GREEN}✅ Database started${NC}"
echo ""

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

echo -e "${YELLOW}Step 2: Setting up backend...${NC}"
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/canada_immigration_os
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DOCUMENT_STORAGE_PATH=./uploads
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
fi

cd ..

echo -e "${YELLOW}Step 3: Setting up frontend...${NC}"
cd frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install > /dev/null 2>&1
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo -e "${GREEN}✅ .env.local file created${NC}"
fi

cd ..

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. Start Backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2. Start Frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "3. Access the application:"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📖 For detailed instructions, see LAUNCH_GUIDE.md"
echo ""
