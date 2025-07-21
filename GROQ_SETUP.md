# 🔑 Get Your Free Groq API Key

## Quick Setup (2 minutes)

1. **Visit Groq Console**: https://console.groq.com/
2. **Sign Up**: Create a free account (Google/GitHub login available)
3. **Get API Key**: 
   - Go to "API Keys" section
   - Click "Create API Key"
   - Copy the key (starts with `gsk_`)

4. **Add to .env file**:
   ```
   GROQ_API_KEY=gsk_your_actual_key_here
   ```

5. **Restart Backend**:
   ```bash
   # Stop current backend (Ctrl+C)
   # Then restart:
   npm run backend:dev
   ```

## Why Groq?
- ⚡ **Fastest inference**: 100+ tokens/second
- 🆓 **Free tier**: Generous usage limits
- 🧠 **Llama 3**: Latest open-source model
- 🔒 **Privacy focused**: No training on your data

## Test AI Functionality
Once you add the API key and restart:

```bash
curl -X POST http://localhost:8000/api/ai/health
# Should show: "ai_enabled": true

curl -X POST http://localhost:8000/api/ai/sentiment \
  -H "Content-Type: application/json" \
  -d '{"text": "I feel amazing today! Starting my new job and everything is going great."}'
```

## Alternative: Continue with Fallback
The app works fine without API keys using smart fallback responses. Add AI keys when ready for full functionality.
