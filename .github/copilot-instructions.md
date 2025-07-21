# GitHub Copilot Instructions for AI Journal Summarizer

## Project Overview
This is an AI-powered journal summarizer mobile app built with React Native (Expo) frontend and FastAPI backend, featuring multiple AI analysis capabilities including sentiment analysis, text summarization, and personal insights.

## Architecture
- **Frontend**: React Native + Expo (~49.0.0)
- **Backend**: FastAPI + Python 3.8+
- **AI Services**: LangChain + Multiple providers (Groq, OpenAI, HuggingFace)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Containerization**: Docker + Docker Compose
- **Package Management**: UV (Python), npm (Node.js)

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

### Current AI Providers
1. **Groq** (Primary) - Fast inference with Llama models
2. **HuggingFace** - Backup/alternative models
3. **OpenAI** - Premium option (optional)
4. **Fallback Service** - Intelligent responses when APIs unavailable

### API Key Setup
```bash
# Required environment variables
GROQ_API_KEY=gsk_your_groq_api_key_here
HUGGINGFACE_API_KEY=hf_your_huggingface_token_here

# Optional
OPENAI_API_KEY=sk-your_openai_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here
```

### Getting API Keys
- **Groq**: https://console.groq.com/ (Free tier available)
- **HuggingFace**: https://huggingface.co/settings/tokens (Free)
- **OpenAI**: https://platform.openai.com/api-keys (Paid after free tier)

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

## Troubleshooting

### Common Issues
1. **Import errors**: Check virtual environment activation
2. **API key not found**: Verify .env file location and format
3. **Port conflicts**: Use different ports (8000, 8082, etc.)
4. **Dependency conflicts**: Use `uv pip install --force-reinstall`

### Debugging AI Services
```bash
# Check AI service status
curl http://localhost:8000/api/ai/health

# View backend logs
uv run python backend/main.py  # Check console output

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
