#!/bin/bash
# Vercel CLI Deployment Script for AI Journal Summarizer

echo "🚀 AI Journal Summarizer - Vercel CLI Deployment"
echo "================================================"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Login to Vercel (if not already logged in)
echo "🔐 Checking Vercel authentication..."
vercel whoami || vercel login

# Set up project configuration
echo "⚙️ Configuring project settings..."

# Create vercel project configuration
cat > .vercel/project.json << EOF
{
  "projectId": "",
  "orgId": ""
}
EOF

# Deploy with specific settings
echo "🚀 Deploying to Vercel..."
vercel deploy \
  --build-env REACT_NATIVE_API_URL=https://ai-journal-backend-production.up.railway.app \
  --prod

echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Check deployment URL"
echo "2. Test all AI features"
echo "3. Verify Railway backend connection"
