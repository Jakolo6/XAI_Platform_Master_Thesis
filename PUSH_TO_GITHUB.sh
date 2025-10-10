#!/bin/bash
# Script to push XAI Platform to GitHub

echo "🚀 Pushing XAI Platform to GitHub..."
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "❌ Error: Not in project root directory"
    exit 1
fi

# Check git status
echo "📋 Checking git status..."
git status

echo ""
echo "⚠️  IMPORTANT: Review the files above"
echo "Make sure NO sensitive files (.env, API keys) are listed!"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Aborted"
    exit 1
fi

# Add all files
echo "📦 Adding files..."
git add .

# Commit
echo "💾 Committing..."
git commit -m "feat: Complete multi-dataset XAI platform with Supabase integration

- Multi-dataset support (3 datasets configured)
- Supabase cloud database integration
- Automated dataset processing pipeline
- Cross-dataset benchmarking
- Modern React frontend with Next.js
- FastAPI backend with async support
- Comprehensive documentation
- Production-ready deployment configuration"

# Check if remote exists
if git remote | grep -q "origin"; then
    echo "📤 Pushing to existing remote..."
    git push origin main
else
    echo ""
    echo "🔗 No remote found. Please add your GitHub repository URL:"
    echo "Example: https://github.com/Jakolo6/XAI_Platform_Master_Thesis.git"
    read -p "Repository URL: " repo_url
    
    git remote add origin "$repo_url"
    git branch -M main
    git push -u origin main
fi

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "🌐 Next steps:"
echo "1. Go to https://app.netlify.com/"
echo "2. Click 'Add new site' → 'Import an existing project'"
echo "3. Connect to GitHub and select your repository"
echo "4. Configure:"
echo "   - Base directory: frontend"
echo "   - Build command: npm run build"
echo "   - Publish directory: frontend/.next"
echo "5. Add environment variable:"
echo "   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1"
echo ""
echo "📚 See DEPLOYMENT_GUIDE.md for detailed instructions"
