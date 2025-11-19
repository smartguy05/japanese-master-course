# Nihongo Sensei - Deployment Guide

Complete guide for deploying and managing the Nihongo Sensei Japanese learning platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Service Architecture](#service-architecture)
- [Environment Configuration](#environment-configuration)
- [Deployment Methods](#deployment-methods)
- [Production Deployment](#production-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)
- [Backup & Restore](#backup--restore)
- [Scaling](#scaling)
- [Security](#security)

---

## Prerequisites

### Required Software

1. **Docker** (version 20.10 or higher)
   ```bash
   # Install on Ubuntu/Debian
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Verify installation
   docker --version
   ```

2. **Docker Compose** (version 2.0 or higher)
   ```bash
   # Docker Compose v2 is included with Docker Desktop
   # For Linux, install Docker Compose plugin
   sudo apt-get update
   sudo apt-get install docker-compose-plugin

   # Verify installation
   docker compose version
   ```

3. **Git**
   ```bash
   sudo apt-get install git
   ```

### API Keys Required

You'll need API keys for the following services:

1. **Anthropic Claude API** (for conversation features)
   - Sign up at: https://console.anthropic.com/
   - Get API key from Account Settings

2. **OpenAI API** (for Whisper speech-to-text)
   - Sign up at: https://platform.openai.com/
   - Create API key from API Keys section

3. **Google Cloud Text-to-Speech** (for Japanese voice)
   - Create project at: https://console.cloud.google.com/
   - Enable Text-to-Speech API
   - Create service account and download key

### System Requirements

**Minimum (Development):**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB

**Recommended (Production):**
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB SSD
- Bandwidth: 100+ Mbps

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-username/nihongo-sensei.git
cd nihongo-sensei
```

### 2. Run One-Command Setup

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script will:
- Check prerequisites
- Create `.env` file from template
- Build Docker images
- Initialize database
- Run migrations
- Start all services

### 3. Configure API Keys

Edit `.env` file and add your API keys:

```bash
nano .env
```

Required configuration:
```env
ANTHROPIC_API_KEY=sk-ant-api03-XXXXX
OPENAI_API_KEY=sk-XXXXX
GOOGLE_CLOUD_TTS_KEY=XXXXX
SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
```

### 4. Restart Services

```bash
cd docker
docker-compose restart
```

### 5. Verify Installation

Open browser and navigate to:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:80/health

---

## Service Architecture

### Docker Services Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Nginx (Port 80/443)                 │
│                     Reverse Proxy & Load Balancer           │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
    ┌──────────▼─────────┐        ┌──────────▼─────────┐
    │   Frontend (3000)  │        │   Backend (8000)   │
    │   Next.js App      │        │   FastAPI Server   │
    └────────────────────┘        └──────────┬─────────┘
                                             │
                        ┌────────────────────┼────────────────────┐
                        │                    │                    │
               ┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼──────┐
               │  PostgreSQL     │  │     Redis       │  │  AI Services │
               │  Database       │  │  Cache/Queue    │  │ Claude/Whisper│
               │  (Port 5432)    │  │  (Port 6379)    │  │   External    │
               └─────────────────┘  └─────────────────┘  └──────────────┘
```

### Service Details

| Service    | Image               | Port  | Purpose                          |
|-----------|---------------------|-------|----------------------------------|
| nginx     | nginx:alpine        | 80    | Reverse proxy, load balancing    |
| frontend  | Custom (Next.js)    | 3000  | React UI, user interface         |
| backend   | Custom (FastAPI)    | 8000  | REST API, business logic         |
| postgres  | postgres:15-alpine  | 5432  | Primary database                 |
| redis     | redis:7-alpine      | 6379  | Cache, sessions, SRS queue       |

### Network Architecture

All services communicate via a Docker bridge network (`nihongo_network`):
- **Internal**: Backend ↔ PostgreSQL, Backend ↔ Redis
- **External**: Nginx → Frontend, Nginx → Backend
- **Public**: User → Nginx (Port 80/443)

---

## Environment Configuration

### Environment Variables Reference

#### Database Configuration

```env
POSTGRES_HOST=postgres          # Hostname (use 'localhost' for external)
POSTGRES_PORT=5432              # PostgreSQL port
POSTGRES_DB=nihongo_sensei      # Database name
POSTGRES_USER=postgres          # Database user
POSTGRES_PASSWORD=<secure>      # Strong password (min 16 chars)
```

#### Redis Configuration

```env
REDIS_HOST=redis                # Hostname
REDIS_PORT=6379                 # Redis port
REDIS_PASSWORD=                 # Optional password (recommended for production)
```

#### Security Settings

```env
# Generate with: openssl rand -hex 32
SECRET_KEY=<64-char-hex-string>

# JWT algorithm (don't change unless you know what you're doing)
ALGORITHM=HS256

# Token expiration in minutes
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### AI Service Configuration

```env
# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-...
AI_CONVERSATION_MODEL=claude-sonnet-4-20250514
AI_CONVERSATION_BASE_URL=https://api.anthropic.com

# OpenAI Whisper
OPENAI_API_KEY=sk-...
AI_STT_MODEL=whisper-1
AI_STT_BASE_URL=https://api.openai.com

# Google Cloud TTS
GOOGLE_CLOUD_TTS_KEY=...
AI_TTS_MODEL=ja-JP-Neural2-B
```

#### Application Settings

```env
ENVIRONMENT=production          # development | staging | production
LOG_LEVEL=INFO                 # DEBUG | INFO | WARNING | ERROR
CORS_ORIGINS=https://your-domain.com  # Comma-separated origins
```

### Alternative AI Providers

#### Using Ollama (Self-Hosted)

```env
AI_CONVERSATION_BASE_URL=http://ollama:11434
AI_CONVERSATION_MODEL=llama3.1:70b
```

#### Using Azure OpenAI

```env
AI_CONVERSATION_BASE_URL=https://your-resource.openai.azure.com
AI_CONVERSATION_MODEL=your-deployment-name
```

---

## Deployment Methods

### Method 1: Development Deployment

For local development with hot reload:

```bash
cd docker
docker-compose up -d
```

This uses `docker-compose.override.yml` which includes:
- Volume mounts for hot reload
- Development environment variables
- Debug ports exposed
- Non-optimized builds

### Method 2: Production Deployment

For production with optimized builds:

```bash
# Build production images
cd docker
docker-compose -f docker-compose.yml build --no-cache

# Start services
docker-compose -f docker-compose.yml up -d
```

### Method 3: Using Deployment Script

Automated deployment with health checks:

```bash
# Development
./scripts/deploy.sh

# Production
./scripts/deploy.sh --production
```

The script handles:
- Pre-deployment checks
- Database backup
- Image building
- Migration execution
- Service restart
- Health verification
- Cleanup

---

## Production Deployment

### 1. Server Setup

#### On Ubuntu/Debian Server

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install nginx (for SSL termination if not using Docker nginx)
sudo apt-get install nginx certbot python3-certbot-nginx
```

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/your-username/nihongo-sensei.git
cd nihongo-sensei

# Create production environment
cp .env.example .env

# Generate secure secrets
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" >> .env
echo "REDIS_PASSWORD=$(openssl rand -hex 16)" >> .env

# Edit with your API keys
nano .env
```

### 3. SSL Certificate Setup

#### Using Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Certificates will be at:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

#### Update Nginx Configuration

Edit `docker/nginx.conf` and uncomment HTTPS section:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # ... rest of configuration
}
```

### 4. Deploy

```bash
./scripts/deploy.sh --production
```

### 5. Set Up Automatic Certificate Renewal

```bash
# Add to crontab
sudo crontab -e

# Add this line
0 0 1 * * certbot renew --post-hook "docker-compose -f /path/to/docker/docker-compose.yml restart nginx"
```

### 6. Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

---

## Monitoring & Maintenance

### Viewing Logs

```bash
# All services
docker-compose -f docker/docker-compose.yml logs -f

# Specific service
docker-compose -f docker/docker-compose.yml logs -f backend

# Last 100 lines
docker-compose -f docker/docker-compose.yml logs --tail=100 backend
```

### Service Status

```bash
# Check running containers
docker-compose -f docker/docker-compose.yml ps

# Check resource usage
docker stats
```

### Health Checks

```bash
# Overall health
curl http://localhost:80/health

# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping
```

### Updating the Application

```bash
# Pull latest code
git pull origin main

# Deploy update
./scripts/deploy.sh --production
```

---

## Troubleshooting

### Services Won't Start

**Check logs:**
```bash
docker-compose logs
```

**Common issues:**
1. Port already in use
   ```bash
   sudo lsof -i :80
   sudo lsof -i :8000
   sudo lsof -i :3000
   ```

2. Insufficient permissions
   ```bash
   sudo chown -R $USER:$USER .
   ```

3. Out of disk space
   ```bash
   df -h
   docker system prune -a
   ```

### Database Connection Errors

**Check PostgreSQL:**
```bash
# Verify container is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U postgres -d nihongo_sensei -c "SELECT 1"
```

**Reset database:**
```bash
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

### Frontend/Backend Communication Issues

**Check CORS settings:**
```env
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
```

**Check nginx configuration:**
```bash
docker-compose exec nginx nginx -t
docker-compose restart nginx
```

### AI Service Errors

**Verify API keys:**
```bash
# Check if keys are set
docker-compose exec backend env | grep API_KEY
```

**Test AI connectivity:**
```bash
# From backend container
docker-compose exec backend python -c "
from app.services.ai_service import AIService
# Test connection
"
```

---

## Backup & Restore

### Automated Backups

```bash
# Manual backup
./scripts/backup.sh

# Set up daily backups with cron
crontab -e

# Add this line (daily at 2 AM)
0 2 * * * /path/to/nihongo-sensei/scripts/backup.sh
```

### Manual Database Backup

```bash
# PostgreSQL backup
docker-compose exec -T postgres pg_dump \
  -U postgres \
  -d nihongo_sensei \
  > backup_$(date +%Y%m%d).sql

# Compress backup
gzip backup_$(date +%Y%m%d).sql
```

### Restore Database

```bash
# From backup file
gunzip -c backup_20241119.sql.gz | \
  docker-compose exec -T postgres psql -U postgres -d nihongo_sensei

# Or restore from script backup
gunzip -c backups/postgres_backup_20241119_120000.sql.gz | \
  docker-compose exec -T postgres psql -U postgres -d nihongo_sensei
```

### Backup to Cloud Storage

**AWS S3 Example:**
```bash
#!/bin/bash
# Add to backup.sh

aws s3 cp backups/ s3://your-bucket/nihongo-backups/ \
  --recursive \
  --exclude "*" \
  --include "*.gz"
```

---

## Scaling

### Horizontal Scaling (Multiple Instances)

**Using Docker Swarm:**

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml nihongo

# Scale backend
docker service scale nihongo_backend=3
```

**Using Kubernetes:**

See `k8s/` directory for Kubernetes manifests (future implementation).

### Vertical Scaling (Resource Limits)

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Database Optimization

**PostgreSQL tuning for production:**

```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Adjust shared buffers (25% of RAM)
ALTER SYSTEM SET shared_buffers = '2GB';

-- Increase work memory
ALTER SYSTEM SET work_mem = '16MB';

-- Reload configuration
SELECT pg_reload_conf();
```

### Redis Optimization

```bash
# Increase maxmemory
docker-compose exec redis redis-cli CONFIG SET maxmemory 2gb
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## Security

### Security Checklist

- [ ] Use strong, unique passwords for all services
- [ ] Enable SSL/TLS certificates
- [ ] Set CORS origins to specific domains (not *)
- [ ] Keep Docker images updated
- [ ] Enable firewall (ufw, iptables)
- [ ] Use secrets management for API keys
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Enable rate limiting
- [ ] Use non-root containers

### Secrets Management

**Using Docker Secrets (Swarm):**

```bash
# Create secret
echo "sk-ant-..." | docker secret create anthropic_key -

# Use in docker-compose.yml
services:
  backend:
    secrets:
      - anthropic_key
```

**Using Environment Files:**

```bash
# Restrict .env permissions
chmod 600 .env

# Add to .gitignore
echo ".env" >> .gitignore
```

### Rate Limiting

Already configured in `nginx.conf`:
- API: 100 requests/minute
- Auth: 10 requests/minute
- Conversation: 30 requests/minute

Adjust in `docker/nginx.conf` as needed.

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-username/nihongo-sensei/issues
- Documentation: https://github.com/your-username/nihongo-sensei/wiki
- Email: support@nihongo-sensei.com

---

**Last Updated:** 2025-11-19
**Version:** 1.0.0
