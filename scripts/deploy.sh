#!/bin/bash
set -e

# =============================================================================
# Nihongo Sensei - Deployment Script
# =============================================================================
# This script deploys or updates the application
# Usage: ./scripts/deploy.sh [--production]
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Parse arguments
PRODUCTION=false
if [[ "$1" == "--production" ]]; then
    PRODUCTION=true
fi

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║         Nihongo Sensei - Deployment Script                   ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

if [ "$PRODUCTION" = true ]; then
    echo "🚨 PRODUCTION DEPLOYMENT MODE"
    echo ""
    read -p "Are you sure you want to deploy to production? (yes/no): " -r
    if [[ ! $REPLY == "yes" ]]; then
        echo "Deployment cancelled."
        exit 0
    fi
fi

# =============================================================================
# Pre-Deployment Checks
# =============================================================================

echo "📋 Running pre-deployment checks..."

# Check if .env exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi
echo "✅ Environment configuration found"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

# Check if services are running
cd "$PROJECT_ROOT/docker"

# =============================================================================
# Backup Database
# =============================================================================

if docker-compose ps postgres | grep -q "Up"; then
    echo ""
    echo "💾 Creating database backup..."
    "$SCRIPT_DIR/backup.sh" || echo "⚠️  Backup failed, continuing anyway..."
fi

# =============================================================================
# Pull Latest Code
# =============================================================================

if [ "$PRODUCTION" = true ]; then
    echo ""
    echo "📥 Pulling latest code from repository..."
    cd "$PROJECT_ROOT"
    git pull origin main || echo "⚠️  Git pull failed, using local code"
fi

# =============================================================================
# Build Images
# =============================================================================

echo ""
echo "🏗️  Building Docker images..."

cd "$PROJECT_ROOT/docker"

if [ "$PRODUCTION" = true ]; then
    # Production build
    docker-compose build --no-cache --pull backend frontend
else
    # Development build
    docker-compose build backend frontend
fi

echo "✅ Images built successfully"

# =============================================================================
# Run Database Migrations
# =============================================================================

echo ""
echo "🔄 Running database migrations..."

# Ensure database is running
docker-compose up -d postgres redis

# Wait for database
echo "Waiting for database..."
sleep 5

# Run migrations
docker-compose run --rm backend alembic upgrade head

echo "✅ Migrations completed"

# =============================================================================
# Restart Services
# =============================================================================

echo ""
echo "🔄 Restarting services..."

# Stop services gracefully
docker-compose down

# Start all services
docker-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 20

# =============================================================================
# Health Checks
# =============================================================================

echo ""
echo "🏥 Running health checks..."

MAX_RETRIES=10
RETRY_DELAY=5

# Check backend
echo "Checking backend..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -f http://localhost:8000/health &> /dev/null; then
        echo "✅ Backend is healthy"
        break
    else
        if [ $i -eq $MAX_RETRIES ]; then
            echo "❌ Backend health check failed after $MAX_RETRIES attempts"
            echo "Check logs: docker-compose logs backend"
            exit 1
        fi
        echo "Attempt $i/$MAX_RETRIES failed, retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
    fi
done

# Check frontend
echo "Checking frontend..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -f http://localhost:3000 &> /dev/null; then
        echo "✅ Frontend is healthy"
        break
    else
        if [ $i -eq $MAX_RETRIES ]; then
            echo "❌ Frontend health check failed after $MAX_RETRIES attempts"
            echo "Check logs: docker-compose logs frontend"
            exit 1
        fi
        echo "Attempt $i/$MAX_RETRIES failed, retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
    fi
done

# Check nginx
echo "Checking nginx..."
if curl -f http://localhost:80/health &> /dev/null; then
    echo "✅ Nginx is healthy"
else
    echo "⚠️  Nginx health check failed"
fi

# =============================================================================
# Post-Deployment Tasks
# =============================================================================

if [ "$PRODUCTION" = true ]; then
    echo ""
    echo "🧹 Cleaning up..."

    # Remove old images
    docker image prune -f

    # Remove old volumes (commented out for safety)
    # docker volume prune -f
fi

# =============================================================================
# Deployment Complete
# =============================================================================

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║            ✅ Deployment Successful!                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 Application URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo ""
echo "📊 Monitor logs with:"
echo "   docker-compose -f docker/docker-compose.yml logs -f"
echo ""
echo "🔧 Manage services:"
echo "   docker-compose -f docker/docker-compose.yml ps"
echo "   docker-compose -f docker/docker-compose.yml restart [service]"
echo ""

# Show running containers
echo "📦 Running containers:"
docker-compose ps

echo ""
echo "Deployment completed at: $(date)"
