// Production configuration for AI Journal Summarizer
const config = {
  // Railway backend URL
  API_BASE_URL: 'https://ai-journal-backend-production.up.railway.app',
  
  // API endpoints
  endpoints: {
    health: '/health',
    sentiment: '/api/ai/sentiment',
    insights: '/api/ai/insights',
    summarize: '/api/ai/summarize'
  },
  
  // App settings
  app: {
    name: 'AI Journal Summarizer',
    version: '1.0.0',
    platform: 'web'
  }
};

export default config;
