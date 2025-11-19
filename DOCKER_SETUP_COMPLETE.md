# Docker Compose Setup - Complete ✅

Complete Docker Compose setup and deployment configuration for Nihongo Sensei has been created successfully!

## 📦 What Was Created

### Docker Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| **docker-compose.yml** | Production Docker Compose config | `/docker/docker-compose.yml` |
| **docker-compose.override.yml** | Development overrides (hot reload) | `/docker/docker-compose.override.yml` |
| **Dockerfile.backend** | Multi-stage Python/FastAPI build | `/docker/Dockerfile.backend` |
| **Dockerfile.frontend** | Multi-stage Next.js build | `/docker/Dockerfile.frontend` |
| **nginx.conf** | Reverse proxy configuration | `/docker/nginx.conf` |
| **entrypoint.backend.sh** | Backend startup script | `/docker/entrypoint.backend.sh` |
| **.dockerignore** | Docker build exclusions | `/.dockerignore` |

### Deployment Scripts

All scripts are executable and located in `/scripts/`:

| Script | Purpose | Usage |
|--------|---------|-------|
| **setup.sh** | One-command setup | `./scripts/setup.sh` |
| **deploy.sh** | Deploy/update application | `./scripts/deploy.sh [--production]` |
| **backup.sh** | Backup database and Redis | `./scripts/backup.sh` |
| **test_all.sh** | Run all tests with coverage | `./scripts/test_all.sh [--verbose]` |
| **verify_docker.sh** | Verify Docker configuration | `./scripts/verify_docker.sh` |

### Environment Configuration

| File | Purpose | Location |
|------|---------|----------|
| **.env.example** | Environment template | `/.env.example` |
| **.env** | Active configuration | `/.env` (created from template) |

### Documentation

| File | Purpose | Location |
|------|---------|----------|
| **DEPLOYMENT.md** | Complete deployment guide | `/docs/DEPLOYMENT.md` |
| **docker/README.md** | Docker-specific guide | `/docker/README.md` |

### CI/CD Pipeline

| File | Purpose | Location |
|------|---------|----------|
| **ci.yml** | GitHub Actions workflow | `/.github/workflows/ci.yml` |

## 🚀 Quick Start Guide

### 1. Initial Setup (One Command)

```bash
cd /home/user/japanese-master-course
./scripts/setup.sh
```

This will:
- ✅ Check prerequisites (Docker, Docker Compose)
- ✅ Create `.env` file from template
- ✅ Build all Docker images
- ✅ Initialize PostgreSQL database
- ✅ Run Alembic migrations
- ✅ Start all services
- ✅ Verify health checks

### 2. Manual Setup (Step-by-Step)

```bash
# 1. Configure environment
cp .env.example .env
nano .env  # Add your API keys

# 2. Generate secrets
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" >> .env

# 3. Build and start services
cd docker
docker-compose up -d

# 4. Check status
docker-compose ps
```

### 3. Access Application

Once running, access:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Nginx**: http://localhost:80

## 🏗️ Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Nginx (Port 80/443)                      │
│              Reverse Proxy & Rate Limiting                  │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
    ┌──────────▼─────────┐        ┌──────────▼─────────┐
    │   Frontend (3000)  │        │   Backend (8000)   │
    │   Next.js (React)  │        │   FastAPI (Python) │
    │   - UI Components  │        │   - REST API       │
    │   - PWA Support    │        │   - AI Integration │
    └────────────────────┘        └──────────┬─────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
               ┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼──────┐
               │  PostgreSQL 15  │  │    Redis 7      │  │  AI Services │
               │   - User Data   │  │  - Cache        │  │   - Claude   │
               │   - Lessons     │  │  - Sessions     │  │   - Whisper  │
               │   - Progress    │  │  - SRS Queue    │  │   - Google   │
               └─────────────────┘  └─────────────────┘  └──────────────┘
```

## 🔧 Common Commands

### Service Management

```bash
cd /home/user/japanese-master-course/docker

# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Check service status
docker-compose ps

# Execute command in container
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d nihongo_sensei
```

### Development Workflow

```bash
# Development mode (with hot reload)
cd docker
docker-compose up -d

# Watch logs
docker-compose logs -f backend frontend

# Run tests
cd /home/user/japanese-master-course
./scripts/test_all.sh

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Production Deployment

```bash
# Deploy with automated checks
./scripts/deploy.sh --production

# Manual deployment
cd docker
docker-compose -f docker-compose.yml build --no-cache
docker-compose -f docker-compose.yml up -d
```

### Backup & Restore

```bash
# Create backup
./scripts/backup.sh

# Backups are stored in: /backups/

# Restore PostgreSQL
gunzip -c backups/postgres_backup_20241119_120000.sql.gz | \
  docker-compose exec -T postgres psql -U postgres -d nihongo_sensei

# Restore Redis
gunzip -c backups/redis_backup_20241119_120000.rdb.gz > dump.rdb
docker cp dump.rdb nihongo-redis:/data/dump.rdb
docker-compose restart redis
```

## 📋 Environment Variables

### Required Configuration

Edit `.env` file with these required values:

```env
# Generate with: openssl rand -hex 32
SECRET_KEY=your_64_character_hex_string

# Strong database password
POSTGRES_PASSWORD=your_secure_password

# AI API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
GOOGLE_CLOUD_TTS_KEY=...
```

### Optional Configuration

```env
# Application
ENVIRONMENT=production          # development | staging | production
LOG_LEVEL=INFO                 # DEBUG | INFO | WARNING | ERROR

# CORS (comma-separated)
CORS_ORIGINS=https://your-domain.com

# Redis password (recommended for production)
REDIS_PASSWORD=your_redis_password

# Service ports (if defaults conflict)
BACKEND_PORT=8000
FRONTEND_PORT=3000
POSTGRES_PORT=5432
REDIS_PORT=6379
```

## 🔍 Health Checks

### Manual Health Checks

```bash
# Overall health
curl http://localhost:80/health

# Backend API
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# Database
docker-compose exec postgres pg_isready -U postgres

# Redis
docker-compose exec redis redis-cli ping
```

### Automated Health Checks

All services include Docker health checks:

```bash
# View health status
docker-compose ps

# Inspect health details
docker inspect nihongo-backend --format='{{.State.Health.Status}}'
```

## 🧪 Testing

### Run All Tests

```bash
./scripts/test_all.sh
```

This runs:
- ✅ Backend tests (pytest)
- ✅ Frontend tests (Jest)
- ✅ Coverage reports
- ✅ Coverage threshold checks (85%)

### Run Tests in Docker

```bash
# Backend tests
docker-compose exec backend pytest tests/ --cov=app

# Frontend tests
docker-compose exec frontend npm test
```

## 🔐 Security Considerations

### Production Checklist

- [ ] Use strong, unique passwords for all services
- [ ] Enable SSL/TLS certificates (Let's Encrypt)
- [ ] Set CORS origins to specific domains (not *)
- [ ] Enable Redis password authentication
- [ ] Keep Docker images updated
- [ ] Enable firewall (ufw, iptables)
- [ ] Use secrets management for API keys
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Enable rate limiting (configured in nginx.conf)

### SSL Certificate Setup

For production with SSL:

1. Get certificate:
```bash
sudo certbot certonly --standalone -d your-domain.com
```

2. Update `docker/nginx.conf`:
```nginx
# Uncomment HTTPS server block
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    # ...
}
```

3. Mount certificates in `docker-compose.yml`:
```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

## 📊 Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Service-specific stats
docker stats nihongo-backend nihongo-frontend
```

### Database Monitoring

```bash
# PostgreSQL connections
docker-compose exec postgres psql -U postgres -d nihongo_sensei -c \
  "SELECT count(*) FROM pg_stat_activity;"

# Database size
docker-compose exec postgres psql -U postgres -d nihongo_sensei -c \
  "SELECT pg_size_pretty(pg_database_size('nihongo_sensei'));"
```

### Redis Monitoring

```bash
# Redis info
docker-compose exec redis redis-cli info

# Current connections
docker-compose exec redis redis-cli client list

# Memory usage
docker-compose exec redis redis-cli info memory
```

## 🐛 Troubleshooting

### Services Won't Start

1. **Check logs:**
   ```bash
   docker-compose logs
   ```

2. **Port conflicts:**
   ```bash
   sudo lsof -i :80
   sudo lsof -i :8000
   sudo lsof -i :3000
   ```

3. **Disk space:**
   ```bash
   df -h
   docker system prune -a
   ```

### Database Connection Errors

```bash
# Verify database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U postgres -d nihongo_sensei -c "SELECT 1"

# Reset database (⚠️ deletes all data)
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

### Frontend Can't Connect to Backend

1. Check `NEXT_PUBLIC_API_URL` in `.env`
2. Verify `CORS_ORIGINS` includes frontend URL
3. Test nginx configuration:
   ```bash
   docker-compose exec nginx nginx -t
   ```

### Container Keeps Restarting

```bash
# View exit code and error
docker-compose ps
docker-compose logs [service-name]

# Check health status
docker inspect nihongo-backend --format='{{.State.Health}}'
```

## 📚 Additional Resources

### Documentation

- **Full Deployment Guide**: `/docs/DEPLOYMENT.md`
- **Docker README**: `/docker/README.md`
- **Project Guide**: `/CLAUDE.md`

### External Documentation

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/docs/)

## 🎯 Next Steps

1. **Review Configuration**
   ```bash
   ./scripts/verify_docker.sh
   ```

2. **Configure API Keys**
   ```bash
   nano .env
   # Add your ANTHROPIC_API_KEY, OPENAI_API_KEY, GOOGLE_CLOUD_TTS_KEY
   ```

3. **Start Application**
   ```bash
   ./scripts/setup.sh
   ```

4. **Verify Installation**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000/docs
   - Health: http://localhost:80/health

5. **Run Tests**
   ```bash
   ./scripts/test_all.sh
   ```

6. **Set Up Backups**
   ```bash
   # Add to crontab for daily backups
   crontab -e
   # Add: 0 2 * * * /path/to/scripts/backup.sh
   ```

## ✅ Verification Checklist

Run through this checklist to ensure everything is working:

- [ ] All Docker configuration files created
- [ ] All deployment scripts created and executable
- [ ] Environment configuration file created
- [ ] Documentation complete
- [ ] CI/CD pipeline configured
- [ ] Docker Compose syntax valid
- [ ] All services start successfully
- [ ] Health checks pass
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Database migrations run successfully
- [ ] Tests pass (./scripts/test_all.sh)
- [ ] Backups working (./scripts/backup.sh)

## 🎉 Success!

Your Docker Compose setup is complete and ready to use!

The Nihongo Sensei application is now fully containerized and can be deployed anywhere Docker runs.

**Total Files Created:** 13
- 7 Docker configuration files
- 5 deployment scripts
- 1 CI/CD workflow

**Project Root:** `/home/user/japanese-master-course`

---

**Created:** 2025-11-19
**Status:** ✅ Complete and Ready for Deployment
