# TimeAlign DevOps Pipeline Setup Guide

## 🚀 Overview

This guide will help you set up a complete CI/CD pipeline for TimeAlign using GitHub Actions and Emergent platform integration.

## 📋 Prerequisites

- GitHub account
- Access to Emergent platform
- TimeAlign app repository

## 🔧 Step 1: Connect to GitHub

### Option A: Using Emergent UI
1. In Emergent, go to your project settings
2. Click "Connect to GitHub"
3. Authorize Emergent to access your GitHub account
4. Select or create a repository for TimeAlign
5. Push your code to GitHub

### Option B: Manual Git Setup
```bash
# Initialize git repository
cd /app
git init

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/timealign.git

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
.venv/
env/

# Environment variables
.env
*.env.local

# Build outputs
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Test coverage
.coverage
coverage/
*.coverage
EOF

# Commit and push
git add .
git commit -m "Initial commit: TimeAlign with DevOps pipeline"
git branch -M main
git push -u origin main
```

## 🔑 Step 2: Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings > Secrets and variables > Actions):

### Required Secrets:

1. **DEPLOYMENT_TOKEN**
   - Generate a JWT token for API authentication
   - Used by workflows to create deployment records
   ```bash
   # Generate token (run on your server)
   python -c "import jwt; print(jwt.encode({'user_id': 'github-actions', 'service': 'ci'}, 'your-jwt-secret', algorithm='HS256'))"
   ```

2. **MONGO_URL** (for tests)
   ```
   mongodb://localhost:27017
   ```

3. **DB_NAME** (for tests)
   ```
   test_database_ci
   ```

### Optional Secrets (for notifications):
- **SLACK_WEBHOOK** - For Slack notifications
- **DISCORD_WEBHOOK** - For Discord notifications

## 📁 Step 3: Verify Workflow Files

The following GitHub Actions workflows have been created:

### 1. CI Pipeline (`.github/workflows/ci.yml`)
- Runs on every push and PR
- Backend tests (Python/FastAPI)
- Frontend build (React)
- Security scanning

### 2. Deploy to Preview (`.github/workflows/deploy-preview.yml`)
- Triggers on push to `develop` branch
- Deploys to preview environment
- URL: 

### 3. Deploy to Production (`.github/workflows/deploy-production.yml`)
- Triggers on push to `main` branch
- Requires manual approval (GitHub environments)
- Includes health checks and backups

### 4. Test Suite (`.github/workflows/test.yml`)
- Unit tests with coverage
- Integration tests with MongoDB
- E2E tests with Playwright
- Runs daily and on demand

## 🌿 Step 4: Branch Strategy

Set up the following branches:

```bash
# Create develop branch for testing
git checkout -b develop
git push -u origin develop

# Create feature branches as needed
git checkout -b feature/new-feature
```

### Branch Strategy:
- **main** → Production environment
- **develop** → Preview/staging environment  
- **feature/** → Development branches

## 🔐 Step 5: Configure GitHub Environments

1. Go to repository Settings > Environments
2. Create two environments:

### Preview Environment
- Name: `preview`
- URL: 
- Protection rules: None (auto-deploy)

### Production Environment
- Name: `production`
- URL: `https://timealign.app` 
- Protection rules:
  - ✅ Required reviewers (add team members)
  - ✅ Wait timer: 5 minutes
  - ✅ Only allow main branch

## 📊 Step 6: Access DevOps Dashboard

The TimeAlign app now includes a DevOps dashboard:

1. Log in to TimeAlign
2. Navigate to the **DevOps** tab
3. View:
   - Pipeline status
   - Deployment history
   - Recent builds
   - Environment health

## 🔄 Step 7: Workflow Usage

### Deploy to Preview:
```bash
git checkout develop
git add .
git commit -m "feat: add new feature"
git push origin develop
# ✅ Automatically deploys to preview
```

### Deploy to Production:
```bash
# Merge develop to main
git checkout main
git merge develop
git push origin main
# ✅ Triggers production workflow (requires approval)
```

### Run Tests Manually:
```bash
# From GitHub UI:
# Actions > Test Suite > Run workflow
```

## 📈 Step 8: Monitor Pipelines

### On GitHub:
1. Go to Actions tab in your repository
2. View running workflows
3. Check logs and artifacts
4. Review test results

### In TimeAlign Dashboard:
1. Navigate to DevOps tab
2. View real-time pipeline status
3. Check deployment history
4. Monitor environment health

## 🧪 Testing the Pipeline

### Test CI Pipeline:
```bash
# Make a small change
echo "# Test commit" >> README.md
git add README.md
git commit -m "test: trigger CI pipeline"
git push

# Check GitHub Actions tab - CI should run
```

### Test Preview Deployment:
```bash
git checkout develop
echo "console.log('test');" >> frontend/src/App.js
git add .
git commit -m "test: preview deployment"
git push origin develop

# Check:
# 1. GitHub Actions running
# 2. TimeAlign DevOps dashboard
# 3. Preview URL after deployment
```

## 🔧 Customization

### Add Slack Notifications:

Edit `.github/workflows/deploy-production.yml`:

```yaml
- name: Notify Slack
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "✅ Production deployed: ${{ github.sha }}",
        "username": "TimeAlign Bot"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Add More Test Steps:

Edit `.github/workflows/test.yml`:

```yaml
- name: Performance tests
  run: |
    cd backend
    pytest tests/performance/ -v
```

## 📚 Best Practices

1. **Never commit secrets** - Use GitHub Secrets
2. **Protect main branch** - Require PR reviews
3. **Write tests** - Aim for 80%+ coverage
4. **Use semantic commits** - `feat:`, `fix:`, `chore:`
5. **Review before merging** - Use pull requests
6. **Monitor deployments** - Check DevOps dashboard
7. **Backup before deploy** - Production has automatic backups

## 🐛 Troubleshooting

### Workflow fails:
```bash
# View detailed logs on GitHub Actions tab
# Common issues:
# - Missing secrets
# - Incorrect MONGO_URL
# - Test failures
```

### Deployment record not created:
```bash
# Check DEPLOYMENT_TOKEN secret
# Verify API endpoint is accessible
# Check backend logs
```

### Tests fail:
```bash
# Run tests locally first
cd backend
pytest tests/ -v

cd frontend  
yarn test
```

## 📞 Support

For help with:
- **GitHub setup**: Check GitHub documentation
- **Emergent platform**: Use support_agent
- **TimeAlign app**: Review SETUP_GUIDE.md

## 🎯 Next Steps

1. ✅ Connect repository to GitHub
2. ✅ Add GitHub secrets
3. ✅ Configure environments
4. ✅ Test the pipeline
5. ✅ Monitor deployments
6. 🚀 Deploy to production!

---

**Your DevOps pipeline is ready! Happy deploying! 🚀**
