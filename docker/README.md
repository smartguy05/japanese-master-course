# Docker Configuration

This directory contains all Docker-related configuration files for the Nihongo Sensei application.

## Files Overview

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Main production Docker Compose configuration |
| `docker-compose.override.yml` | Development overrides (hot reload, debugging) |
| `Dockerfile.backend` | Multi-stage build for FastAPI backend |
| `Dockerfile.frontend` | Multi-stage build for Next.js frontend |
| `nginx.conf` | Nginx reverse proxy configuration |
| `entrypoint.backend.sh` | Backend startup script (migrations, health checks) |

## Quick Start

### Development Mode

```bash
# Start all services with hot reload
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Mode

```bash
# Build and start services
docker-compose -f docker-compose.yml up -d --build

# View logs
docker-compose -f docker-compose.yml logs -f

# Stop services
docker-compose -f docker-compose.yml down
```

## Service Ports

| Service | Internal Port | External Port | Purpose |
|---------|--------------|---------------|---------|
| Nginx | 80, 443 | 80, 443 | Reverse proxy |
| Frontend | 3000 | 3000 | Next.js UI |
| Backend | 8000 | 8000 | FastAPI API |
| PostgreSQL | 5432 | 5432 | Database |
| Redis | 6379 | 6379 | Cache/Queue |

## Common Commands

### View Service Status
```bash
docker-compose ps
```

### Restart a Service
```bash
docker-compose restart backend
```

### View Logs for Specific Service
```bash
docker-compose logs -f backend
```

### Execute Command in Container
```bash
# Backend shell
docker-compose exec backend bash

# PostgreSQL shell
docker-compose exec postgres psql -U postgres -d nihongo_sensei

# Redis CLI
docker-compose exec redis redis-cli
```

### Run Database Migrations
```bash
docker-compose exec backend alembic upgrade head
```

### Rebuild a Service
```bash
docker-compose up -d --build backend
```

## Development vs Production

### Development (docker-compose.override.yml)

- Volume mounts for hot reload
- Debug ports exposed (5678 for Python debugger)
- Development environment variables
- Non-optimized builds
- Verbose logging

### Production (docker-compose.yml only)

- Optimized multi-stage builds
- Non-root users for security
- Health checks enabled
- Minimal image size
- Production logging

## Environment Variables

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp ../.env.example ../.env
```

Required variables:
- `POSTGRES_PASSWORD` - Database password
- `SECRET_KEY` - JWT secret key
- `ANTHROPIC_API_KEY` - Claude API key
- `OPENAI_API_KEY` - Whisper API key
- `GOOGLE_CLOUD_TTS_KEY` - Google TTS key

## Troubleshooting

### Services won't start

1. Check logs: `docker-compose logs`
2. Check if ports are in use: `sudo lsof -i :80`
3. Verify .env file exists: `ls -la ../.env`

### Database connection errors

1. Wait for database to be ready (can take 10-20 seconds)
2. Check database health: `docker-compose exec postgres pg_isready`
3. Verify DATABASE_URL in logs: `docker-compose logs backend | grep DATABASE_URL`

### Frontend can't connect to backend

1. Check NEXT_PUBLIC_API_URL in .env
2. Verify CORS_ORIGINS includes frontend URL
3. Check nginx configuration: `docker-compose exec nginx nginx -t`

## Clean Up

### Remove all containers and volumes
```bash
docker-compose down -v
```

### Remove all images
```bash
docker-compose down --rmi all
```

### Clean up Docker system
```bash
docker system prune -a --volumes
```

## Health Checks

All services have health checks configured:

```bash
# Check all services
docker-compose ps

# Check specific service health
docker inspect nihongo-backend --format='{{.State.Health.Status}}'
```

## Backup & Restore

### Backup
```bash
../scripts/backup.sh
```

### Restore
```bash
# PostgreSQL
gunzip -c backups/postgres_backup_*.sql.gz | \
  docker-compose exec -T postgres psql -U postgres -d nihongo_sensei

# Redis
gunzip -c backups/redis_backup_*.rdb.gz > dump.rdb
docker cp dump.rdb nihongo-redis:/data/dump.rdb
docker-compose restart redis
```

## Security Notes

1. **Never commit .env file** - Contains secrets
2. **Use strong passwords** - Generate with `openssl rand -hex 32`
3. **Enable SSL in production** - Uncomment HTTPS section in nginx.conf
4. **Restrict network access** - Use firewall rules
5. **Regular updates** - Keep images updated: `docker-compose pull`

## Additional Resources

- [Full Deployment Guide](../docs/DEPLOYMENT.md)
- [Project Documentation](../CLAUDE.md)
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
