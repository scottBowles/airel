Backend API for https://airel.vip

## 🐳 Docker Deployment (Coolify)

**New!** This repository now includes optimized Docker configuration for Coolify deployment:

- **Quick Deploy**: See [COOLIFY_QUICK_DEPLOY.md](docs/COOLIFY_QUICK_DEPLOY.md) for fast setup
- **Complete Guide**: See [COOLIFY_DEPLOYMENT.md](docs/COOLIFY_DEPLOYMENT.md) for detailed instructions
- **Environment Setup**: Copy [.env.template](.env.template) for configuration

The Docker setup includes:
- ✅ Production-ready Django app with Gunicorn
- ✅ Celery workers for background tasks
- ✅ Redis message broker
- ✅ FFmpeg for audio processing
- ✅ Health checks and monitoring
- ✅ Security best practices (non-root user)

## Celery with Redis Background Tasks

This application now supports background task processing using Celery with Redis for improved performance, especially for audio transcription operations.

### Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Start Redis**: `brew install redis && brew services start redis` (Mac) or `docker-compose up -d redis` (Docker)
3. **Test setup**: `python manage.py test_celery`
4. **Start worker**: `celery -A website worker --loglevel=info`

### Documentation

- **🐳 Docker/Coolify Deployment**: [COOLIFY_DEPLOYMENT.md](docs/COOLIFY_DEPLOYMENT.md) | [Quick Deploy](docs/COOLIFY_QUICK_DEPLOY.md)
- **Local Development**: [CELERY_LOCAL_DEVELOPMENT.md](docs/CELERY_LOCAL_DEVELOPMENT.md)
- **Production Setup**: [CELERY_PRODUCTION.md](docs/CELERY_PRODUCTION.md)

### Background Tasks Available

- Audio transcription processing
- Session log generation  
- Cleanup of temporary files
- Health checks
