#!/bin/bash

# Environment Validation and System Status Check
# Validates all dependencies and configurations

set -e

echo "🔍 AI Journal Summarizer - System Status Check"
echo "=============================================="

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m' 
RED='\033[0;31m'
NC='\033[0m' # No Color

check_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

echo "📋 Phase 1: Core Dependencies"
echo "-----------------------------"

# Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: $NODE_VERSION${NC}"
else
    echo -e "${RED}❌ Node.js: Not installed${NC}"
fi

# npm
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo -e "${GREEN}✅ npm: $NPM_VERSION${NC}"
else
    echo -e "${RED}❌ npm: Not installed${NC}"
fi

# Python
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✅ Python: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ Python: Not installed${NC}"
fi

# Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo -e "${GREEN}✅ Git: $GIT_VERSION${NC}"
else
    echo -e "${RED}❌ Git: Not installed${NC}"
fi

echo ""
echo "📦 Phase 2: Project Dependencies"
echo "--------------------------------"

# Check package.json
if [ -f "package.json" ]; then
    echo -e "${GREEN}✅ package.json: Found${NC}"
    
    # Check if node_modules exists
    if [ -d "node_modules" ]; then
        echo -e "${GREEN}✅ node_modules: Installed${NC}"
    else
        echo -e "${YELLOW}⚠️ node_modules: Not installed (run 'npm install')${NC}"
    fi
else
    echo -e "${RED}❌ package.json: Not found${NC}"
fi

# Check backend requirements
if [ -f "backend/requirements.txt" ]; then
    echo -e "${GREEN}✅ backend/requirements.txt: Found${NC}"
    
    # Check for virtual environment
    if [ -d "backend/.venv" ] || [ -d ".venv" ]; then
        echo -e "${GREEN}✅ Python virtual environment: Found${NC}"
    else
        echo -e "${YELLOW}⚠️ Python virtual environment: Not found${NC}"
    fi
else
    echo -e "${RED}❌ backend/requirements.txt: Not found${NC}"
fi

echo ""
echo "🔧 Phase 3: Configuration Files"
echo "-------------------------------"

# Environment files
[ -f ".env" ] && echo -e "${GREEN}✅ .env: Found${NC}" || echo -e "${YELLOW}⚠️ .env: Not found${NC}"
[ -f "backend/.env" ] && echo -e "${GREEN}✅ backend/.env: Found${NC}" || echo -e "${YELLOW}⚠️ backend/.env: Not found${NC}"

# Docker files
[ -f "docker-compose.yml" ] && echo -e "${GREEN}✅ docker-compose.yml: Found${NC}" || echo -e "${YELLOW}⚠️ docker-compose.yml: Not found${NC}"
[ -f "Dockerfile.backend" ] && echo -e "${GREEN}✅ Dockerfile.backend: Found${NC}" || echo -e "${YELLOW}⚠️ Dockerfile.backend: Not found${NC}"

# GitHub Actions
[ -f ".github/workflows/report-progress.yml" ] && echo -e "${GREEN}✅ GitHub Actions: Configured${NC}" || echo -e "${YELLOW}⚠️ GitHub Actions: Not configured${NC}"

echo ""
echo "🌐 Phase 4: Service Connectivity"
echo "--------------------------------"

# Test Railway backend
if curl -s --max-time 5 https://ai-journal-backend-production.up.railway.app/health > /dev/null; then
    echo -e "${GREEN}✅ Railway Backend: Accessible${NC}"
else
    echo -e "${RED}❌ Railway Backend: Not accessible${NC}"
fi

# Test local backend (if running)
if curl -s --max-time 2 http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Local Backend: Running${NC}"
else
    echo -e "${YELLOW}⚠️ Local Backend: Not running${NC}"
fi

# Test Vercel deployment (if deployed)
if curl -s --max-time 5 https://generative-ai-journal-summarizer.vercel.app > /dev/null; then
    echo -e "${GREEN}✅ Vercel Frontend: Deployed${NC}"
else
    echo -e "${YELLOW}⚠️ Vercel Frontend: Not accessible${NC}"
fi

echo ""
echo "📊 Phase 5: Project Status"
echo "-------------------------"

# Git status
if [ -d ".git" ]; then
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    echo -e "${GREEN}✅ Git Repository: Initialized${NC}"
    echo -e "   📍 Current Branch: $CURRENT_BRANCH"
    echo -e "   📊 Total Commits: $COMMIT_COUNT"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD --; then
        echo -e "${YELLOW}⚠️ Uncommitted Changes: Present${NC}"
    else
        echo -e "${GREEN}✅ Working Directory: Clean${NC}"
    fi
else
    echo -e "${RED}❌ Git Repository: Not initialized${NC}"
fi

# File count
JS_FILES=$(find . -name "*.js" -not -path "./node_modules/*" 2>/dev/null | wc -l)
PY_FILES=$(find . -name "*.py" -not -path "./node_modules/*" 2>/dev/null | wc -l)
echo -e "   📄 JavaScript Files: $JS_FILES"
echo -e "   📄 Python Files: $PY_FILES"

echo ""
echo "🎯 System Status Summary"
echo "======================="

# Overall status
ALL_GOOD=true

if ! command -v node &> /dev/null; then ALL_GOOD=false; fi
if ! command -v python &> /dev/null; then ALL_GOOD=false; fi
if [ ! -f "package.json" ]; then ALL_GOOD=false; fi

if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}🎉 System Status: READY FOR DEVELOPMENT${NC}"
    echo ""
    echo "🚀 Quick Start Commands:"
    echo "   ./setup-dev-environment.sh  - Start development environment"
    echo "   ./test-railway-api.sh        - Test production API"
    echo "   ./deploy-vercel.sh           - Deploy to production"
else
    echo -e "${YELLOW}⚠️ System Status: SETUP REQUIRED${NC}"
    echo ""
    echo "🔧 Required Actions:"
    [ ! -d "node_modules" ] && echo "   📦 Run 'npm install'"
    [ ! -d "backend/.venv" ] && [ ! -d ".venv" ] && echo "   🐍 Create Python virtual environment"
    [ ! -f ".env" ] && echo "   🔑 Create .env file with API keys"
fi
