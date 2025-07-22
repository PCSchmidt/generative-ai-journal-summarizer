#!/bin/bash

# Complete Deployment and Progress Tracking Automation
# Combines deployment with automatic progress updates

set -e

echo "🚀 AI Journal Summarizer - Full Deploy + Progress Tracking"
echo "========================================================"

# Phase 1: Deploy to Vercel
echo "📦 Phase 1: Deploying to Vercel..."
./deploy-vercel.sh

# Phase 2: Test Railway API
echo "🧪 Phase 2: Testing Railway API..."
./test-railway-api.sh

# Phase 3: Update progress tracking
echo "📊 Phase 3: Updating progress tracking..."
./trigger-progress-update.sh

# Phase 4: Trigger parent repo update (if available)
echo "🔄 Phase 4: Triggering parent repository progress update..."

PARENT_REPO_PATH="../roadmap-for-building-generative-ai-apps"

if [ -d "$PARENT_REPO_PATH" ]; then
    echo "✅ Found parent repository, updating progress table..."
    cd "$PARENT_REPO_PATH"
    
    # Check if sync script exists
    if [ -f "scripts/sync-app-progress.sh" ]; then
        echo "🔄 Running parent repo sync script..."
        bash scripts/sync-app-progress.sh
        echo "✅ Parent repository progress updated!"
    else
        echo "⚠️ Parent repo sync script not found"
        echo "   Expected: scripts/sync-app-progress.sh"
    fi
    
    cd - # Return to original directory
else
    echo "⚠️ Parent repository not found at: $PARENT_REPO_PATH"
    echo "   Progress update will only be local"
fi

# Phase 5: GitHub Actions trigger
echo "🤖 Phase 5: Triggering GitHub Actions progress report..."
git add .
git commit -m "🚀 DEPLOY: Full deployment with progress tracking update" || echo "No changes to commit"
git push origin main

echo ""
echo "🎉 Complete Deployment + Progress Tracking Finished!"
echo ""
echo "✅ Vercel frontend deployed"
echo "✅ Railway backend tested"  
echo "✅ Progress metrics updated"
echo "✅ GitHub Actions triggered"
echo ""
echo "🔗 Next Steps:"
echo "1. Verify deployment at Vercel URL"
echo "2. Check parent repo progress table update"
echo "3. Monitor GitHub Actions workflow"
echo "4. Begin next development phase"
