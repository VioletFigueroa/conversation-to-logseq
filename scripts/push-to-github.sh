#!/bin/bash
# Push to GitHub - conversation-to-logseq repository
# This script will push the repository to GitHub

set -e

REPO_DIR="/home/violetf/Games2/Nextcloud/Documents/Development/Github/conversation-to-logseq"
GITHUB_USERNAME="VioletFigueroa"
REPO_NAME="conversation-to-logseq"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  CONVERSATION-TO-LOGSEQ - GITHUB PUSH SCRIPT               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd "$REPO_DIR"

echo "✓ Repository directory: $REPO_DIR"
echo "✓ GitHub username: $GITHUB_USERNAME"
echo "✓ Repository name: $REPO_NAME"
echo ""

# Verify git status
echo "📋 Checking git status..."
git status --porcelain

if [ -n "$(git status --porcelain)" ]; then
    echo "❌ ERROR: Uncommitted changes detected!"
    echo "Please commit all changes before pushing."
    exit 1
fi

echo "✅ All changes committed"
echo ""

# Verify remote doesn't exist
echo "🔗 Checking for existing remote..."
if git remote get-url origin 2>/dev/null; then
    echo "⚠️  Remote 'origin' already exists:"
    git remote get-url origin
    echo ""
    read -p "Use existing remote? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing remote..."
        git remote remove origin
    fi
else
    echo "✅ No existing remote"
fi

# Add remote if not present
if ! git remote get-url origin 2>/dev/null; then
    echo ""
    echo "📌 Adding GitHub remote..."
    REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    git remote add origin "$REMOTE_URL"
    echo "✅ Remote added: $REMOTE_URL"
fi

echo ""
echo "🔑 Git configuration:"
git config --local user.name
git config --local user.email

echo ""
echo "📊 Repository statistics:"
echo "   Commits: $(git rev-list --all --count)"
echo "   Tags: $(git tag --list | wc -l)"
echo "   Branches: $(git branch --list | wc -l)"

echo ""
echo "📦 Latest commits:"
git log --oneline -3

echo ""
echo "🏷️  Tags:"
git tag -l

echo ""
echo "════════════════════════════════════════════════════════════"
echo "Ready to push to GitHub!"
echo "════════════════════════════════════════════════════════════"
echo ""

read -p "Continue with push? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Push cancelled."
    exit 0
fi

echo ""
echo "🚀 Pushing to GitHub..."
echo ""

# Ensure main branch is default
git branch -M main

# Push main branch
echo "Pushing main branch..."
git push -u origin main
echo "✅ Main branch pushed"
echo ""

# Push tags
echo "Pushing tags..."
git push --tags origin
echo "✅ Tags pushed"
echo ""

# Verify push
echo "🔍 Verifying push..."
if git ls-remote --get-url origin | grep -q "repository not found"; then
    echo "⚠️  Warning: Repository may not exist on GitHub yet"
    echo "Create it at: https://github.com/new"
else
    echo "✅ Remote repository verified"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "✨ PUSH COMPLETE!"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "Next steps:"
echo "1. Go to repository settings"
echo "2. Add topics: logseq, knowledge-management, perplexity, etc."
echo "3. Enable discussions for community questions"
echo ""
