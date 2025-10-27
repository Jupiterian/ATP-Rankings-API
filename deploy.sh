#!/bin/bash
# Quick deployment script for pushing changes to GitHub

echo "🎾 ATP Rankings - GitHub Deployment"
echo "===================================="
echo ""

# Check git status
echo "📋 Checking git status..."
git status
echo ""

# Prompt for commit message
read -p "Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="Add FastAPI web application with deployment files"
fi

# Add all files
echo "📦 Staging files..."
git add .

# Commit
echo "💾 Committing changes..."
git commit -m "$commit_msg"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "Next steps:"
echo "1. Visit https://github.com/Jupiterian/ATP-Rankings-Data-Visualization"
echo "2. Choose a deployment platform from DEPLOYMENT.md"
echo "3. Recommended: Deploy to Render.com (free & easy)"
echo ""
