#!/bin/bash
set -e

echo "Starting Nihongo Sensei Backend..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "postgres" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "PostgreSQL is up!"

# Wait for Redis to be ready
echo "Waiting for Redis..."
until redis-cli -h redis -a "$REDIS_PASSWORD" ping; do
  >&2 echo "Redis is unavailable - sleeping"
  sleep 1
done
echo "Redis is up!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Import initial data if needed (only on first run)
if [ "$IMPORT_INITIAL_DATA" = "true" ]; then
    echo "Importing initial dictionary data..."
    python -m app.scripts.import_jmdict || echo "Dictionary import skipped or failed"
fi

# Execute the main command
echo "Starting application..."
exec "$@"
