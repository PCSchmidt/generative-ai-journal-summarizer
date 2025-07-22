#!/bin/bash
# Test Railway AI Journal Summarizer API
RAILWAY_URL="https://ai-journal-backend-production.up.railway.app"

echo "🚀 Testing AI Journal Summarizer API on Railway..."
echo "Base URL: $RAILWAY_URL"
echo ""

echo "1. Testing Health Endpoint..."
curl -s "$RAILWAY_URL/health"
echo ""

echo "2. Testing Root Endpoint..."
curl -s "$RAILWAY_URL/"
echo ""

echo "3. Testing Sentiment Analysis..."
curl -s -X POST "$RAILWAY_URL/api/ai/sentiment" \
  -H "Content-Type: application/json" \
  -d '{"text": "Today was an amazing day! I accomplished so much and feel really happy."}'
echo ""

echo "4. Testing Insights Generation..."
curl -s -X POST "$RAILWAY_URL/api/ai/insights" \
  -H "Content-Type: application/json" \
  -d '{"text": "I have been reflecting on my goals and what makes me truly fulfilled."}'
echo ""

echo "5. Testing Text Summarization..."
curl -s -X POST "$RAILWAY_URL/api/ai/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "Today I went to the park and saw beautiful flowers. The weather was perfect and I spent time reading my favorite book. Later I met with friends for coffee and we had great conversations about our future plans."}'
echo ""

echo "✅ API Testing Complete!"
echo ""
echo "📱 Frontend Configuration:"
echo "Use this Railway URL in your React Native app: $RAILWAY_URL"
