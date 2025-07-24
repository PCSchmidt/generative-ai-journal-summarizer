# GitHub Copilot Instructions for AI Journal Summarizer

## Project Overview
This is an AI-powered journal summarizer mobile app built with React Native (Expo) frontend and FastAPI backend, featuring **7 AI models** across **dual providers** (Groq + HuggingFace) with intelligent fallbacks for sentiment analysis, text summarization, and personal insights.

## Architecture
- **Frontend**: React Native + Expo (~49.0.0) deployed on Vercel
- **Backend**: FastAPI + Python 3.11+ deployed on Railway  
- **AI Services**: **Dual-Provider Architecture** - Groq (3 models) + HuggingFace (4 models)
- **Models**: Llama 3, Mixtral, Mistral 7B, Phi-3, Gemma 7B, Zephyr 7B
- **Database**: SQLite (development) / PostgreSQL (future)
- **Containerization**: Docker + Docker Compose (optional)
- **Package Management**: UV (Python - recommended), npm (Node.js)
- **Testing**: Comprehensive browser-based and CLI model validation tools

## Current Status (July 23, 2025)
- **✅ Phase 1 MVP**: Complete with enhanced AI integration
- **✅ Production Deployments**: Both frontend and backend live
- **✅ AI Integration**: 7 models with intelligent fallbacks working
- **✅ Testing Infrastructure**: Comprehensive validation tools
- **🔄 Next Phase**: Vector database integration or mobile app compilation

## Development Environment Setup

### Python Environment with UV (Recommended)

UV is the modern Python package manager that's faster and more reliable than pip/conda.

#### Install UV
```bash
# Windows (PowerShell)
irm https://astral.sh/uv/install.ps1 | iex

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via pip (if you prefer)
pip install uv
```

#### Setup Virtual Environment
```bash
# Create virtual environment with Python 3.11
uv venv --python 3.11

# Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies from requirements.txt
uv pip install -r backend/requirements.txt

# Or install specific packages
uv pip install fastapi uvicorn langchain-groq python-dotenv
```

#### UV Project Management
```bash
# Initialize UV project (creates pyproject.toml)
uv init

# Add dependencies
uv add fastapi uvicorn langchain-groq
uv add --dev pytest black flake8

# Install from pyproject.toml
uv sync

# Run commands in UV environment
uv run python backend/main.py
uv run pytest
```

### Node.js Environment
```bash
# Install dependencies
npm install

# Start Expo development server
npm start

# Or use specific Expo commands
npx expo start
npx expo start --web
```

## Project Structure
```
/
├── .env                          # Environment variables (API keys)
├── .env.example                  # Environment template
├── App.js                        # React Native main app
├── package.json                  # Node.js dependencies
├── docker-compose.yml            # Docker services
├── backend/
│   ├── main.py                   # FastAPI entry point
│   ├── requirements.txt          # Python dependencies
│   ├── .env                      # Backend environment variables
│   └── app/
│       ├── api/endpoints/        # API route handlers
│       ├── services/             # Business logic
│       ├── models/               # Data models
│       └── core/                 # Configuration
├── generative-ai-journal-summarizer/
│   └── generative-ai-journal-summarizer/
│       └── backend/              # Nested backend structure
└── .github/
    ├── workflows/                # CI/CD pipelines
    └── copilot-instructions.md   # This file
```

## Key Files and Their Purpose

### Frontend (React Native)
- `App.js` - Main application with tabbed interface (Write/Analysis)
- Uses enhanced dark theme with cyberpunk-inspired colors
- Features: Journal input, AI analysis buttons, results display

### Backend (FastAPI)
- `main.py` - FastAPI application with CORS and routing
- `app/services/ai_service_enhanced.py` - Enhanced AI processing with Groq integration
- `app/api/endpoints/ai_enhanced.py` - AI API endpoints (/sentiment, /insights, /summarize)

### Environment Configuration
- `.env` - Contains API keys (GROQ_API_KEY, HUGGINGFACE_API_KEY, etc.)
- `backend/.env` - Backend-specific environment variables

## API Endpoints

### AI Processing
- `POST /api/ai/sentiment` - Sentiment analysis
- `POST /api/ai/insights` - Personal insights extraction
- `POST /api/ai/summarize` - Text summarization
- `GET /api/ai/health` - Service health check

### Request Format
```json
{
  "text": "Your journal entry text here",
  "task_type": "sentiment|insights|summarize"
}
```

### Response Format
```json
{
  "result": "AI-generated analysis",
  "task_type": "sentiment",
  "confidence": 0.85,
  "metadata": {
    "model": "groq-llama3-8b",
    "word_count": 42,
    "sentiment": "positive",
    "timestamp": "2025-07-20T23:00:00"
  }
}
```

## Development Workflow

### Starting Development Environment
```bash
# Method 1: Using UV (Recommended)
uv venv --python 3.11
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -r backend/requirements.txt
uv run python backend/main.py

# Method 2: Using Docker
docker-compose up -d

# Start frontend
npm start
```

### Testing API Endpoints
```bash
# Health check
curl http://localhost:8000/api/ai/health

# Sentiment analysis
curl -X POST "http://localhost:8000/api/ai/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "Today was amazing!", "task_type": "sentiment"}'
```

## AI Integration

### Current AI Providers & Models
1. **Groq** (Primary) - Ultra-fast inference
   - **llama3-8b-8192**: General-purpose analysis 
   - **llama3-70b-8192**: Advanced reasoning
   - **mixtral-8x7b-32768**: Mixture-of-experts

2. **HuggingFace** (Secondary) - Specialized models
   - **mistralai/Mistral-7B-Instruct-v0.1**: Excellent instructions
   - **microsoft/Phi-3-medium-4k-instruct**: Advanced reasoning  
   - **google/gemma-1.1-7b-it**: Safety-focused conversations
   - **HuggingFaceH4/zephyr-7b-beta**: Helpful conversations

3. **Intelligent Fallback System** - Automatic provider switching when APIs unavailable

### API Key Setup
```bash
# Required environment variables
GROQ_API_KEY=gsk_your_groq_api_key_here
HUGGINGFACE_API_KEY=hf_your_huggingface_token_here

# Optional (for future expansion)
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
```

### Enhanced AI Service Architecture
- `app/services/ai_service_enhanced.py` - Multi-provider AI processing with intelligent routing
- `app/api/endpoints/ai_enhanced.py` - Enhanced API endpoints with model selection
- **Endpoints**: `/sentiment`, `/insights`, `/summarize` with optional model parameter
- **Features**: Automatic fallbacks, model-specific optimizations, comprehensive error handling

### Request Format
```json
{
  "text": "Your journal entry text here",
  "task_type": "sentiment|insights|summarize",
  "model": "groq-llama3-8b|hf-mistral-7b|auto" // optional
}
```

### Response Format
```json
{
  "result": "AI-generated analysis",
  "task_type": "sentiment",
  "confidence": 0.85,
  "metadata": {
    "model": "groq-llama3-8b",
    "provider": "groq",
    "word_count": 42,
    "timestamp": "2025-07-23T20:00:00"
  }
}
```

## Common Development Tasks

### Adding New AI Features
1. Update `ai_service_enhanced.py` with new analysis method
2. Add endpoint in `ai_enhanced.py`
3. Update frontend `App.js` to call new endpoint
4. Test with curl or frontend interface

### Database Changes
1. Update models in `app/models/`
2. Create migration in `backend/migrations/`
3. Run migration: `uv run alembic upgrade head`

### Frontend UI Updates
1. Edit `App.js` for component changes
2. Update styles in StyleSheet.create()
3. Test in Expo Go app or web browser

## Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
```bash
# Backend
uv sync
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Frontend (build for production)
npx expo build:web
```

## Testing and Validation

### Comprehensive Testing Tools Available
1. **`quick_hf_test.py`** - Quick CLI validation of all HuggingFace models
2. **`test_hf_models.html`** - Browser-based testing interface (open in browser)
3. **`diagnose_hf_api.py`** - Detailed API diagnostics and debugging

### Running Tests
```bash
# Quick validation of all models
python quick_hf_test.py

# Detailed model testing
python test_hf_models.py

# Open browser testing interface
python -m http.server 8080
# Then open: http://localhost:8080/test_hf_models.html

# API health check
curl https://ai-journal-backend-production.up.railway.app/health
```

### Testing for Boilerplate Responses
The testing tools automatically detect boilerplate responses by checking for phrases like:
- "I don't have access"
- "I cannot analyze"
- "Based on the general"
- And other fallback indicators

## Troubleshooting

### Common Issues
1. **Import errors**: Check virtual environment activation with `uv` or standard Python
2. **API key not found**: Verify GROQ_API_KEY and HUGGINGFACE_API_KEY in Railway environment
3. **Port conflicts**: Use different ports (8000, 8082, etc.)
4. **Dependency conflicts**: Use `uv pip install --force-reinstall`
5. **Railway deployment issues**: Check logs in Railway dashboard

### Debugging AI Services
```bash
# Check AI service status
curl https://ai-journal-backend-production.up.railway.app/health

# Test specific endpoints
curl -X POST https://ai-journal-backend-production.up.railway.app/api/ai/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text":"test","task_type":"sentiment"}'

# View Railway logs
# Go to Railway dashboard → project → deployments → logs

# Test specific endpoints
curl -X POST localhost:8000/api/ai/sentiment -d '{"text":"test"}'
```

## Code Style and Standards

### Python (Backend)
- Use Black for formatting: `uv run black .`
- Use flake8 for linting: `uv run flake8`
- Type hints preferred: `def process_text(text: str) -> Dict[str, Any]:`

### JavaScript (Frontend)
- Use ES6+ features
- Functional components with hooks
- Consistent styling with StyleSheet.create()

## Security Considerations
- Never commit API keys to version control
- Use environment variables for sensitive data
- Implement proper CORS settings for production
- Validate all user inputs in API endpoints

## Performance Optimization
- Use UV for faster Python package management
- Implement caching for AI responses
- Optimize React Native rendering with useMemo/useCallback
- Use background tasks for long-running AI operations

## Next Steps and Roadmap
1. Real AI integration (API keys setup) ✅
2. Enhanced UI/UX improvements ✅
3. Vector database integration
4. User authentication system
5. Cloud deployment (AWS/Vercel)
6. Mobile app store deployment
7. Analytics and monitoring
8. Premium features and monetization

---

**Note**: This project is part of the "Build 10 AI-Powered Mobile Apps" portfolio. UV is recommended for Python package management due to its speed and reliability over traditional pip/conda workflows.
