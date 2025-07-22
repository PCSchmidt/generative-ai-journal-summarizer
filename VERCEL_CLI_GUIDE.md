# Vercel CLI Commands for AI Journal Summarizer

## Quick Setup
```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Link project to existing Vercel project
vercel link

# Set environment variables
vercel env add REACT_NATIVE_API_URL production
# Enter: https://ai-journal-backend-production.up.railway.app
```

## Deployment Commands
```bash
# Deploy to preview (development)
vercel

# Deploy to production
vercel --prod

# Deploy with specific build command
vercel --build-env NODE_ENV=production --prod

# Check deployment status
vercel ls

# View deployment logs
vercel logs [deployment-url]
```

## Project Configuration
```bash
# Set build settings via CLI
vercel project add

# Override build command
vercel --build-env BUILD_COMMAND="npm run vercel-build"

# Set output directory
vercel --build-env OUTPUT_DIRECTORY="dist"
```

## Environment Variables
```bash
# List all environment variables
vercel env ls

# Add environment variable
vercel env add REACT_NATIVE_API_URL

# Remove environment variable
vercel env rm REACT_NATIVE_API_URL

# Pull environment variables to local .env
vercel env pull .env.local
```

## Debugging
```bash
# View project settings
vercel project ls

# Check build logs
vercel logs --follow

# Inspect specific deployment
vercel inspect [deployment-url]
```

## Automation Examples
```bash
# Deploy with all settings in one command
vercel deploy \
  --name ai-journal-summarizer \
  --build-env REACT_NATIVE_API_URL=https://ai-journal-backend-production.up.railway.app \
  --prod

# Deploy and alias to custom domain
vercel deploy --prod && vercel alias
```
