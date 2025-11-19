#!/bin/bash
set -e

# =============================================================================
# Nihongo Sensei - Backup Script
# =============================================================================
# This script creates backups of PostgreSQL and Redis data
# Usage: ./scripts/backup.sh
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
BACKUP_DIR="$PROJECT_ROOT/backups"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Timestamp for backup files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║           Nihongo Sensei - Backup Script                     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Backup directory: $BACKUP_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

cd "$PROJECT_ROOT/docker"

# =============================================================================
# Check if services are running
# =============================================================================

if ! docker-compose ps postgres | grep -q "Up"; then
    echo "❌ PostgreSQL is not running"
    echo "Start services with: docker-compose up -d"
    exit 1
fi

# =============================================================================
# Backup PostgreSQL Database
# =============================================================================

echo "💾 Backing up PostgreSQL database..."

# Get database credentials from .env
source "$PROJECT_ROOT/.env"

POSTGRES_BACKUP_FILE="$BACKUP_DIR/postgres_backup_${TIMESTAMP}.sql"

# Create database dump
docker-compose exec -T postgres pg_dump \
    -U "${POSTGRES_USER:-postgres}" \
    -d "${POSTGRES_DB:-nihongo_sensei}" \
    > "$POSTGRES_BACKUP_FILE"

# Compress backup
echo "Compressing PostgreSQL backup..."
gzip "$POSTGRES_BACKUP_FILE"
POSTGRES_BACKUP_FILE="${POSTGRES_BACKUP_FILE}.gz"

echo "✅ PostgreSQL backup created: $POSTGRES_BACKUP_FILE"
echo "   Size: $(du -h "$POSTGRES_BACKUP_FILE" | cut -f1)"

# =============================================================================
# Backup Redis Data
# =============================================================================

echo ""
echo "💾 Backing up Redis data..."

REDIS_BACKUP_FILE="$BACKUP_DIR/redis_backup_${TIMESTAMP}.rdb"

# Trigger Redis save
docker-compose exec -T redis redis-cli SAVE

# Copy Redis dump file
docker cp nihongo-redis:/data/dump.rdb "$REDIS_BACKUP_FILE"

# Compress backup
echo "Compressing Redis backup..."
gzip "$REDIS_BACKUP_FILE"
REDIS_BACKUP_FILE="${REDIS_BACKUP_FILE}.gz"

echo "✅ Redis backup created: $REDIS_BACKUP_FILE"
echo "   Size: $(du -h "$REDIS_BACKUP_FILE" | cut -f1)"

# =============================================================================
# Cleanup Old Backups
# =============================================================================

echo ""
echo "🧹 Cleaning up old backups..."

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "postgres_backup_*.sql.gz" -type f -mtime +7 -delete
find "$BACKUP_DIR" -name "redis_backup_*.rdb.gz" -type f -mtime +7 -delete

BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" | wc -l)
echo "✅ Cleanup complete. Total backups: $BACKUP_COUNT"

# =============================================================================
# Backup Summary
# =============================================================================

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║               ✅ Backup Complete!                             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "📦 Backup files:"
echo "   PostgreSQL: $POSTGRES_BACKUP_FILE"
echo "   Redis:      $REDIS_BACKUP_FILE"
echo ""
echo "📋 Restore instructions:"
echo ""
echo "PostgreSQL:"
echo "  gunzip -c $POSTGRES_BACKUP_FILE | \\"
echo "    docker-compose exec -T postgres psql -U postgres -d nihongo_sensei"
echo ""
echo "Redis:"
echo "  gunzip -c $REDIS_BACKUP_FILE > dump.rdb"
echo "  docker cp dump.rdb nihongo-redis:/data/dump.rdb"
echo "  docker-compose restart redis"
echo ""
echo "💡 Tip: Consider copying backups to external storage or cloud backup service"
echo ""
echo "Backup completed at: $(date)"
