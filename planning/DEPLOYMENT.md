# Deployment Guide - Nihongo Master

## Overview

This guide covers deploying Nihongo Master using Docker for self-hosted installations, including local development, staging, and production environments.

---

## Quick Start (Local Development)

### Prerequisites

- **Docker** 20.10+ and **Docker Compose** 2.0+
- **Git** for cloning repository
- **API Keys:**
  - Anthropic Claude API key
  - OpenAI API key (for Whisper)
  - Google Cloud credentials (for TTS)

### One-Command Setup

```bash
# Clone repository
git clone https://github.com/yourusername/nihongo-master.git
cd nihongo-master

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or your preferred editor

# Start all services
docker compose up -d

# Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Expected Setup Time:** 5-10 minutes (initial Docker image build)

---

## Environment Configuration

### Environment Variables (.env)

```bash
# ==== Application Settings ====
APP_NAME=Nihongo Master
APP_ENV=development  # development, staging, production
DEBUG=true           # Set to false in production
SECRET_KEY=your-secret-key-here  # Generate with: openssl rand -hex 32

# ==== Database (PostgreSQL) ====
DATABASE_URL=postgresql://nihongo_user:secure_password@postgres:5432/nihongo_db
POSTGRES_USER=nihongo_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=nihongo_db

# ==== Redis Cache ====
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=  # Optional, leave empty for local dev

# ==== AI Services ====
# Anthropic Claude (Conversation)
CLAUDE_API_KEY=sk-ant-api03-your-key-here
CLAUDE_BASE_URL=https://api.anthropic.com  # Optional: override for testing
CLAUDE_MODEL=claude-sonnet-4-20250514

# OpenAI (Whisper Speech-to-Text)
OPENAI_API_KEY=sk-your-openai-key-here
WHISPER_MODEL=whisper-1

# Google Cloud (Text-to-Speech)
GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/google-tts-credentials.json
TTS_VOICE_NAME=ja-JP-Neural2-B
TTS_LANGUAGE_CODE=ja-JP

# ==== Frontend ====
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Nihongo Master

# ==== Security ====
JWT_SECRET_KEY=your-jwt-secret-here  # Generate with: openssl rand -hex 32
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# ==== Email (Optional, for user verification) ====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@nihongomaster.com

# ==== Storage (Optional, for audio files) ====
# Leave empty to use local filesystem
S3_BUCKET_NAME=
S3_ACCESS_KEY=
S3_SECRET_KEY=
S3_REGION=us-east-1
```

### Generating Secrets

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY  
openssl rand -hex 32

# Generate secure database password
openssl rand -base64 32
```

---

## Docker Configuration

### docker-compose.yml (Development)

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: nihongo-postgres
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres-init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - nihongo-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: nihongo-redis
    command: redis-server --appendonly yes ${REDIS_PASSWORD:+--requirepass $REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - nihongo-network

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    container_name: nihongo-backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - CLAUDE_MODEL=${CLAUDE_MODEL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG}
    volumes:
      - ./backend:/app
      - ./content:/app/content
      - ./secrets:/app/secrets:ro
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    networks:
      - nihongo-network

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: development
    container_name: nihongo-frontend
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_APP_NAME=${NEXT_PUBLIC_APP_NAME}
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    ports:
      - "3000:3000"
    depends_on:
      - backend
    command: npm run dev
    networks:
      - nihongo-network

  # Nginx (Production only)
  # Uncomment for production deployment
  # nginx:
  #   image: nginx:alpine
  #   container_name: nihongo-nginx
  #   volumes:
  #     - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
  #     - ./ssl:/etc/nginx/ssl:ro
  #   ports:
  #     - "80:80"
  #     - "443:443"
  #   depends_on:
  #     - backend
  #     - frontend
  #   networks:
  #     - nihongo-network

volumes:
  postgres_data:
  redis_data:

networks:
  nihongo-network:
    driver: bridge
```

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM base as production
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Frontend Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as base

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Development stage
FROM base as development
COPY . .
CMD ["npm", "run", "dev"]

# Builder stage
FROM base as builder
COPY . .
RUN npm run build

# Production stage
FROM node:18-alpine as production
WORKDIR /app

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.js ./

RUN npm ci --only=production

EXPOSE 3000
CMD ["npm", "start"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/api/health || exit 1
```

---

## Production Deployment

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - nihongo-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "--pass", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - nihongo-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: production
    restart: unless-stopped
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=false
    volumes:
      - ./content:/app/content:ro
      - ./secrets:/app/secrets:ro
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    networks:
      - nihongo-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      target: production
    restart: unless-stopped
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
      - NEXT_PUBLIC_APP_NAME=${NEXT_PUBLIC_APP_NAME}
      - NODE_ENV=production
    depends_on:
      - backend
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    networks:
      - nihongo-network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    volumes:
      - ./docker/nginx-prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
      - frontend
    networks:
      - nihongo-network

volumes:
  postgres_data:
  redis_data:
  nginx_logs:

networks:
  nihongo-network:
    driver: bridge
```

### Nginx Production Configuration

```nginx
# docker/nginx-prod.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=conversation_limit:10m rate=2r/s;

    # Backend upstream
    upstream backend {
        server backend:8000 max_fails=3 fail_timeout=30s;
    }

    # Frontend upstream
    upstream frontend {
        server frontend:3000 max_fails=3 fail_timeout=30s;
    }

    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API proxy
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;

            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts for AI requests
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Conversation endpoint (lower rate limit)
        location /api/v1/conversation/ {
            limit_req zone=conversation_limit burst=5 nodelay;

            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Longer timeout for AI processing
            proxy_read_timeout 120s;
        }

        # Frontend proxy
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files (if served by Nginx)
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

---

## Database Management

### Initial Setup

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create initial admin user
docker compose exec backend python scripts/create_admin.py \
  --email admin@example.com \
  --username admin \
  --password secure_password
```

### Backup Strategy

**Automated Daily Backups:**

```bash
# Create backup script: scripts/backup-db.sh
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="nihongo_db_${TIMESTAMP}.sql.gz"

docker compose exec -T postgres pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} | gzip > ${BACKUP_DIR}/${BACKUP_FILE}

# Keep only last 30 days of backups
find ${BACKUP_DIR} -name "nihongo_db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}"
```

**Schedule with cron:**

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/nihongo-master/scripts/backup-db.sh >> /var/log/nihongo-backup.log 2>&1
```

**Restore from Backup:**

```bash
# Stop backend
docker compose stop backend

# Restore database
gunzip -c /backups/nihongo_db_20250101_020000.sql.gz | \
  docker compose exec -T postgres psql -U ${POSTGRES_USER} ${POSTGRES_DB}

# Start backend
docker compose start backend
```

---

## CI/CD Pipeline (GitHub Actions)

### .github/workflows/test.yml

```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
      
      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run tests
        working-directory: ./backend
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
          SECRET_KEY: test_secret_key
          JWT_SECRET_KEY: test_jwt_secret
        run: |
          pytest --cov=app --cov-report=xml --cov-report=term-missing
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
          flags: backend

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run tests
        working-directory: ./frontend
        run: npm run test:ci
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./frontend/coverage/coverage-final.json
          flags: frontend

  lint:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      # Backend linting
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install backend linters
        run: |
          pip install black ruff mypy
      
      - name: Run Black
        working-directory: ./backend
        run: black --check .
      
      - name: Run Ruff
        working-directory: ./backend
        run: ruff check .
      
      - name: Run MyPy
        working-directory: ./backend
        run: mypy app
      
      # Frontend linting
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install frontend dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run ESLint
        working-directory: ./frontend
        run: npm run lint
      
      - name: Run TypeScript check
        working-directory: ./frontend
        run: npm run type-check
```

### .github/workflows/deploy.yml

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push backend
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: |
            yourusername/nihongo-backend:latest
            yourusername/nihongo-backend:${{ github.sha }}
          cache-from: type=registry,ref=yourusername/nihongo-backend:latest
          cache-to: type=inline
      
      - name: Build and push frontend
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          push: true
          tags: |
            yourusername/nihongo-frontend:latest
            yourusername/nihongo-frontend:${{ github.sha }}
          cache-from: type=registry,ref=yourusername/nihongo-frontend:latest
          cache-to: type=inline
      
      # Optional: Deploy to your server via SSH
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /opt/nihongo-master
            docker compose pull
            docker compose up -d
            docker compose exec backend alembic upgrade head
```

---

## Monitoring & Logging

### Health Check Endpoints

**Backend Health Check:**
```python
# app/api/v1/health.py
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        
        # Check Redis connection
        redis_client = await get_redis()
        await redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )
```

**Frontend Health Check:**
```typescript
// app/api/health/route.ts
export async function GET() {
  return Response.json({
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
}
```

### Log Aggregation

**Configure Structured Logging:**

```python
# backend/app/core/logging.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure in main.py
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler("/app/logs/app.log"),
        logging.StreamHandler()
    ]
)

for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

---

## Scaling Considerations

### Horizontal Scaling

**Load Balancer Configuration (Nginx Upstream):**

```nginx
upstream backend {
    least_conn;
    server backend-1:8000 max_fails=3 fail_timeout=30s;
    server backend-2:8000 max_fails=3 fail_timeout=30s;
    server backend-3:8000 max_fails=3 fail_timeout=30s;
}

upstream frontend {
    server frontend-1:3000 max_fails=3 fail_timeout=30s;
    server frontend-2:3000 max_fails=3 fail_timeout=30s;
}
```

**Docker Swarm / Kubernetes:**

For production at scale, consider orchestration platforms:

```yaml
# docker-swarm-stack.yml
version: '3.8'

services:
  backend:
    image: yourusername/nihongo-backend:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

---

## Troubleshooting

### Common Issues

**Issue: Container fails to start**
```bash
# Check logs
docker compose logs backend
docker compose logs frontend

# Check health status
docker compose ps

# Restart specific service
docker compose restart backend
```

**Issue: Database connection fails**
```bash
# Check PostgreSQL is running
docker compose ps postgres

# Test connection
docker compose exec postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# Check DATABASE_URL in .env
```

**Issue: Frontend can't reach backend**
```bash
# Check network connectivity
docker compose exec frontend ping backend

# Verify NEXT_PUBLIC_API_URL in .env
# Should be http://backend:8000 for Docker, http://localhost:8000 for host
```

**Issue: High memory usage**
```bash
# Check container stats
docker stats

# Adjust resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

---

## Maintenance

### Updating Dependencies

**Backend:**
```bash
cd backend
pip list --outdated
pip install -U package-name
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend
npm outdated
npm update
npm audit fix
```

### Database Migrations

**Create Migration:**
```bash
docker compose exec backend alembic revision -m "Description"
# Edit migration in alembic/versions/
docker compose exec backend alembic upgrade head
```

**Rollback Migration:**
```bash
docker compose exec backend alembic downgrade -1
```

---

## Security Checklist

Before production deployment:

- [ ] Change all default passwords
- [ ] Generate secure SECRET_KEY and JWT_SECRET_KEY
- [ ] Set DEBUG=false
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall (allow only 80, 443, SSH)
- [ ] Set up automated backups
- [ ] Configure log rotation
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting
- [ ] Review and test disaster recovery procedures

---

**Last Updated:** Initial creation
**Review Cadence:** Before each major deployment
