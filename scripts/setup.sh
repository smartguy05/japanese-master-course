#!/bin/bash
set -e

# =============================================================================
# Nihongo Sensei - One-Command Setup Script
# =============================================================================
# This script sets up the entire development environment from scratch
# Usage: ./scripts/setup.sh
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   Nihongo Sensei - Japanese Learning Platform Setup          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# =============================================================================
# Check Prerequisites
# =============================================================================

echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✅ Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✅ Docker Compose found"

# =============================================================================
# Environment Configuration
# =============================================================================

echo ""
echo "🔧 Setting up environment configuration..."

if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "Creating .env file from template..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"

    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your API keys"
    echo ""
    echo "Required API keys:"
    echo "  - ANTHROPIC_API_KEY (https://console.anthropic.com/)"
    echo "  - OPENAI_API_KEY (https://platform.openai.com/api-keys)"
    echo "  - GOOGLE_CLOUD_TTS_KEY (https://console.cloud.google.com/)"
    echo ""
    echo "Generate SECRET_KEY with: openssl rand -hex 32"
    echo ""

    read -p "Press Enter after you've configured .env file..."
else
    echo "✅ .env file already exists"
fi

# =============================================================================
# Docker Setup
# =============================================================================

echo ""
echo "🐳 Setting up Docker environment..."

cd "$PROJECT_ROOT/docker"

# Pull base images
echo "Pulling Docker images..."
docker-compose pull postgres redis nginx

# Build application images
echo "Building application images..."
docker-compose build --no-cache

# =============================================================================
# Database Initialization
# =============================================================================

echo ""
echo "💾 Initializing database..."

# Start only database and redis
docker-compose up -d postgres redis

# Wait for services to be healthy
echo "Waiting for database to be ready..."
sleep 10

# Check database health
until docker-compose exec -T postgres pg_isready -U postgres; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# Check Redis health
until docker-compose exec -T redis redis-cli ping; do
    echo "Waiting for Redis..."
    sleep 2
done
echo "✅ Redis is ready"

# =============================================================================
# Run Database Migrations
# =============================================================================

echo ""
echo "🔄 Running database migrations..."

# Start backend temporarily to run migrations
docker-compose run --rm backend alembic upgrade head

echo "✅ Database migrations completed"

# =============================================================================
# Import Sample Data (Optional)
# =============================================================================

echo ""
read -p "Do you want to import sample lesson data? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Importing sample data..."
    docker-compose run --rm backend python -m app.scripts.import_sample_data || echo "Sample data import skipped"
fi

# =============================================================================
# Start All Services
# =============================================================================

echo ""
echo "🚀 Starting all services..."

docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to start..."
sleep 15

# =============================================================================
# Verify Installation
# =============================================================================

echo ""
echo "🔍 Verifying installation..."

# Check backend health
if curl -f http://localhost:8000/health &> /dev/null; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend health check failed"
fi

# Check frontend
if curl -f http://localhost:3000 &> /dev/null; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend health check failed"
fi

# Check nginx
if curl -f http://localhost:80/health &> /dev/null; then
    echo "✅ Nginx is running"
else
    echo "⚠️  Nginx health check failed"
fi

# =============================================================================
# Setup Complete
# =============================================================================

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║              ✅ Setup Complete!                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📱 Application URLs:"
echo "   Frontend:  http://localhost:3000"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Nginx:     http://localhost:80"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs:         docker-compose -f docker/docker-compose.yml logs -f"
echo "   Stop services:     docker-compose -f docker/docker-compose.yml down"
echo "   Restart services:  docker-compose -f docker/docker-compose.yml restart"
echo "   Run tests:         ./scripts/test_all.sh"
echo "   Backup database:   ./scripts/backup.sh"
echo ""
echo "📚 Documentation:"
echo "   Deployment Guide:  docs/DEPLOYMENT.md"
echo "   Project Guide:     CLAUDE.md"
echo ""
echo "Happy learning! 🎌"
