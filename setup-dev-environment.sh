#!/bin/bash

# Quick Development Setup and Testing Script
# Starts all services and runs quick validation

set -e

echo "⚡ AI Journal Summarizer - Quick Development Setup"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Run from project root."
    exit 1
fi

# Phase 1: Backend Setup
echo "🐍 Phase 1: Setting up Python backend..."

if [ -d "backend" ]; then
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python -m venv .venv
    fi
    
    # Activate virtual environment
    if [ -f ".venv/Scripts/activate" ]; then
        source .venv/Scripts/activate  # Windows
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate      # Unix/macOS
    fi
    
    # Install requirements
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
    
    # Start backend in background
    echo "🚀 Starting FastAPI backend..."
    python main.py &
    BACKEND_PID=$!
    
    cd ..
else
    echo "⚠️ No backend directory found, skipping backend setup"
fi

# Phase 2: Frontend Setup  
echo "⚛️ Phase 2: Setting up React Native frontend..."

# Install Node.js dependencies
echo "📥 Installing Node.js dependencies..."
npm install > /dev/null 2>&1

# Phase 3: Quick Health Check
echo "🏥 Phase 3: Running health checks..."

# Wait a moment for backend to start
sleep 3

# Test local backend
if command -v curl &> /dev/null; then
    echo "🔍 Testing local backend..."
    curl -s http://localhost:8000/health || echo "⚠️ Local backend not responding"
fi

# Test Railway backend
echo "🔍 Testing Railway production backend..."
curl -s https://ai-journal-backend-production.up.railway.app/health || echo "⚠️ Railway backend not responding"

# Phase 4: Development Options
echo ""
echo "✅ Development Setup Complete!"
echo ""
echo "🎯 Available Commands:"
echo "   npm start          - Start Expo development server"
echo "   npm run web        - Start web development"
echo "   npm run build:html - Build HTML version"
echo "   ./test-railway-api.sh - Test production API"
echo ""
echo "🌐 URLs:"
echo "   Local Backend:  http://localhost:8000"
echo "   Railway Backend: https://ai-journal-backend-production.up.railway.app"
echo "   Frontend (Expo): http://localhost:19006"
echo ""

# Clean up background process
if [ ! -z "$BACKEND_PID" ]; then
    echo "🧹 Backend running in background (PID: $BACKEND_PID)"
    echo "   Use 'kill $BACKEND_PID' to stop it"
fi
