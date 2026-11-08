#!/bin/bash

# Docker Configuration Validation Script
# This script validates the Docker setup for Coolify deployment

echo "🐳 Docker Configuration Validation"
echo "=================================="

# Check if required files exist
echo "📋 Checking required files..."
files=(".dockerignore" "Dockerfile" "docker-compose.yml" "requirements.txt" ".env.template")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

# Validate Dockerfile
echo -e "\n📦 Validating Dockerfile..."
if grep -q "FROM python:3.14-slim" Dockerfile; then
    echo "✅ Using Python 3.14 slim base image"
else
    echo "❌ Incorrect base image"
fi

if grep -q "ffmpeg" Dockerfile; then
    echo "✅ FFmpeg dependency included"
else
    echo "❌ FFmpeg dependency missing"
fi

if grep -q "gunicorn" Dockerfile; then
    echo "✅ Production server (Gunicorn) configured"
else
    echo "❌ Production server not configured"
fi

if grep -q "HEALTHCHECK" Dockerfile; then
    echo "✅ Health check configured"
else
    echo "❌ Health check missing"
fi

if grep -q "useradd.*appuser" Dockerfile; then
    echo "✅ Non-root user configured"
else
    echo "❌ Running as root (security risk)"
fi

# Validate docker-compose.yml
echo -e "\n🐋 Validating docker-compose.yml..."
if grep -q "redis:7-alpine" docker-compose.yml; then
    echo "✅ Redis service configured"
else
    echo "❌ Redis service missing"
fi

if grep -q "celery.*worker" docker-compose.yml; then
    echo "✅ Celery worker service configured"
else
    echo "❌ Celery worker service missing"
fi

if grep -q "healthcheck:" docker-compose.yml; then
    echo "✅ Health checks configured"
else
    echo "❌ Health checks missing"
fi

if grep -q "flower" docker-compose.yml; then
    echo "✅ Flower monitoring available"
else
    echo "❌ Flower monitoring missing"
fi

# Validate requirements.txt
echo -e "\n📋 Validating requirements.txt..."
if grep -q "celery==" requirements.txt; then
    echo "✅ Celery dependency present"
else
    echo "❌ Celery dependency missing"
fi

if grep -q "redis==" requirements.txt; then
    echo "✅ Redis dependency present"
else
    echo "❌ Redis dependency missing"
fi

if grep -q "flower==" requirements.txt; then
    echo "✅ Flower dependency present"
else
    echo "❌ Flower dependency missing"
fi

if grep -q "gunicorn==" requirements.txt; then
    echo "✅ Gunicorn dependency present"
else
    echo "❌ Gunicorn dependency missing"
fi

# Check .dockerignore
echo -e "\n🚫 Validating .dockerignore..."
if grep -q ".git" .dockerignore; then
    echo "✅ Git files excluded"
else
    echo "❌ Git files not excluded"
fi

if grep -q "__pycache__" .dockerignore; then
    echo "✅ Python cache excluded"
else
    echo "❌ Python cache not excluded"
fi

if grep -q "node_modules" .dockerignore; then
    echo "✅ Node modules excluded"
else
    echo "❌ Node modules not excluded"
fi

# Check environment template
echo -e "\n🔧 Validating environment template..."
required_vars=("SECRET_KEY" "DATABASE_URL" "CELERY_BROKER_URL" "CELERY_RESULT_BACKEND")
for var in "${required_vars[@]}"; do
    if grep -q "$var" .env.template; then
        echo "✅ $var documented"
    else
        echo "❌ $var missing from template"
    fi
done

# Check documentation
echo -e "\n📚 Validating documentation..."
if [ -f "COOLIFY_DEPLOYMENT.md" ]; then
    echo "✅ Coolify deployment guide exists"
    if grep -q "Docker" COOLIFY_DEPLOYMENT.md; then
        echo "✅ Docker deployment documented"
    else
        echo "❌ Docker deployment not documented"
    fi
else
    echo "❌ Coolify deployment guide missing"
fi

echo -e "\n🎉 Validation complete!"
echo ""
echo "📋 Next Steps for Coolify Deployment:"
echo "1. Copy .env.template to set up environment variables"
echo "2. Deploy Redis service in Coolify"
echo "3. Deploy Django app using Dockerfile"
echo "4. Deploy Celery worker using Dockerfile with custom command"
echo "5. Configure environment variables for all services"
echo ""
echo "📖 See COOLIFY_DEPLOYMENT.md for detailed instructions"