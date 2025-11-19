# Troubleshooting Guide

Common issues and solutions for Nihongo Sensei.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Docker Problems](#docker-problems)
- [Database Issues](#database-issues)
- [API and Backend](#api-and-backend)
- [Frontend Issues](#frontend-issues)
- [Build Errors](#build-errors)
- [Test Failures](#test-failures)
- [Performance Issues](#performance-issues)
- [Browser Compatibility](#browser-compatibility)
- [Getting Help](#getting-help)

## Installation Issues

### Python Version Mismatch

**Problem:** `python: command not found` or wrong Python version

**Solution:**

```bash
# Check Python version
python --version  # Should be 3.11+

# If wrong version, use python3
python3 --version

# Create alias (add to .bashrc or .zshrc)
alias python=python3

# Or use pyenv to manage versions
pyenv install 3.11.0
pyenv global 3.11.0
```

### Node.js Version Mismatch

**Problem:** `npm` version errors or build failures

**Solution:**

```bash
# Check Node version
node --version  # Should be 18+

# Use nvm to install correct version
nvm install 18
nvm use 18
nvm alias default 18
```

### Virtual Environment Issues

**Problem:** `pip install` fails or installs in wrong location

**Solution:**

```bash
# Ensure virtual environment is activated
which python  # Should show venv/bin/python

# If not activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Recreate virtual environment if corrupted
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependency Installation Failures

**Problem:** Package installation fails

**Solution:**

```bash
# Update pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install with verbose output to see errors
pip install -r requirements.txt -v

# Try installing problematic package separately
pip install package-name

# On Linux, may need system dependencies
sudo apt-get install python3-dev postgresql-dev
```

## Docker Problems

### Docker Compose Not Found

**Problem:** `docker-compose: command not found`

**Solution:**

```bash
# Install Docker Compose
sudo apt-get install docker-compose

# Or use Docker Compose V2 (plugin)
docker compose version

# Use 'docker compose' instead of 'docker-compose'
```

### Permission Denied

**Problem:** `permission denied while trying to connect to Docker daemon`

**Solution:**

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or
newgrp docker

# Test
docker ps
```

### Container Won't Start

**Problem:** PostgreSQL or Redis container fails to start

**Solution:**

```bash
# Check container logs
docker-compose logs postgres
docker-compose logs redis

# Remove and recreate containers
docker-compose down
docker-compose up -d

# Remove volumes if needed (WARNING: deletes data)
docker-compose down -v
docker-compose up -d
```

### Port Already in Use

**Problem:** `port is already allocated`

**Solution:**

```bash
# Find process using port
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

## Database Issues

### Cannot Connect to Database

**Problem:** `could not connect to server: Connection refused`

**Solution:**

```bash
# Check if PostgreSQL is running
docker-compose ps postgres
# or
sudo systemctl status postgresql

# Check connection settings in .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Test connection
psql $DATABASE_URL

# Restart database
docker-compose restart postgres
```

### Migration Failures

**Problem:** `alembic upgrade head` fails

**Solution:**

```bash
# Check current migration status
alembic current

# View migration history
alembic history

# Downgrade to specific version
alembic downgrade <revision>

# Upgrade step by step
alembic upgrade +1

# If corrupted, reset (development only!)
alembic downgrade base
alembic upgrade head

# Check for migration conflicts
alembic heads  # Should show one head
```

### Permission Denied on Database

**Problem:** `permission denied for database`

**Solution:**

```bash
# Grant permissions
psql -U postgres

postgres=# GRANT ALL PRIVILEGES ON DATABASE nihongo_sensei TO your_user;
postgres=# \q

# Or recreate database with correct owner
dropdb nihongo_sensei
createdb nihongo_sensei -O your_user
```

### Database Locked

**Problem:** `database is locked` (SQLite) or connection pool exhausted

**Solution:**

```bash
# For PostgreSQL, increase pool size in config
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Check active connections
psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Terminate idle connections
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';"
```

## API and Backend

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:**

```bash
# Ensure in backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Verify installation
pip list | grep fastapi

# Reinstall if needed
pip install -r requirements.txt

# Run from correct directory
uvicorn app.main:app --reload
```

### Anthropic API Errors

**Problem:** `AuthenticationError` or `RateLimitError`

**Solution:**

```bash
# Check API key in .env
echo $ANTHROPIC_API_KEY

# Verify key is valid
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"

# Check API usage limits
# Visit: https://console.anthropic.com/

# Use environment variable
export ANTHROPIC_API_KEY=your-key-here
```

### Redis Connection Errors

**Problem:** `Error connecting to Redis`

**Solution:**

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli ping
# Should return: PONG

# Check Redis URL in .env
REDIS_URL=redis://localhost:6379/0

# Restart Redis
docker-compose restart redis

# Clear Redis cache if corrupted
redis-cli FLUSHALL
```

### CORS Errors

**Problem:** `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**

```bash
# Check CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Ensure frontend URL is included
# Restart backend after changing
```

### 500 Internal Server Error

**Problem:** Generic server error

**Solution:**

```bash
# Check backend logs
uvicorn app.main:app --reload --log-level debug

# Check application logs
tail -f logs/app.log

# Enable debug mode in .env (development only)
DEBUG=true

# Check database connection
# Check environment variables
# Review recent code changes
```

## Frontend Issues

### Module Not Found

**Problem:** `Module not found: Can't resolve '@/components/...'`

**Solution:**

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
npm install

# Check tsconfig.json paths are correct
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

### Hydration Errors

**Problem:** `Text content does not match server-rendered HTML`

**Solution:**

```typescript
// Use dynamic import with ssr: false
const ClientComponent = dynamic(
  () => import('./ClientComponent'),
  { ssr: false }
);

// Or use useEffect for client-only code
useEffect(() => {
  // Client-only code here
}, []);

// Don't use browser APIs during render
// Use localStorage in useEffect, not directly
```

### API Connection Refused

**Problem:** Frontend can't connect to backend

**Solution:**

```bash
# Check NEXT_PUBLIC_API_URL in .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# Ensure backend is running
curl http://localhost:8000/health

# Check browser console for actual error
# Check CORS settings in backend
```

### TypeScript Errors

**Problem:** Type errors in development

**Solution:**

```bash
# Run type check
npm run type-check

# Regenerate types
npx tsc --noEmit

# Check tsconfig.json is correct
# Install missing @types packages
npm install --save-dev @types/node @types/react

# Clear TypeScript cache
rm -rf .next
```

## Build Errors

### Backend Build Fails

**Problem:** Docker build or deployment fails

**Solution:**

```bash
# Check requirements.txt for incompatible versions
pip check

# Build with verbose output
docker build -t backend --progress=plain .

# Check Dockerfile syntax
# Ensure all dependencies are in requirements.txt

# Test locally first
pip install -r requirements.txt
pytest
```

### Frontend Build Fails

**Problem:** `npm run build` fails

**Solution:**

```bash
# Clear cache
rm -rf .next node_modules

# Reinstall dependencies
npm install

# Build with verbose output
npm run build --verbose

# Check for:
# - TypeScript errors
# - Missing environment variables
# - Import errors

# Fix TypeScript errors
npm run type-check

# Check all ENV vars are prefixed NEXT_PUBLIC_
```

### Out of Memory During Build

**Problem:** Build process runs out of memory

**Solution:**

```bash
# Increase Node memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build

# Or in package.json
{
  "scripts": {
    "build": "NODE_OPTIONS='--max-old-space-size=4096' next build"
  }
}
```

## Test Failures

### Tests Won't Run

**Problem:** `pytest: command not found` or `npm test` fails

**Solution:**

```bash
# Backend
source venv/bin/activate
pip install pytest pytest-asyncio pytest-cov

# Frontend
npm install --save-dev jest @testing-library/react

# Run tests
pytest -v
npm test
```

### Database Tests Fail

**Problem:** Tests fail with database errors

**Solution:**

```bash
# Ensure test database is separate
DATABASE_URL_TEST=postgresql+asyncpg://user:pass@localhost:5432/test_db

# Create test database
createdb test_nihongo_sensei

# Check fixtures in conftest.py
# Ensure database is cleaned between tests
```

### Async Tests Fail

**Problem:** `RuntimeError: This event loop is already running`

**Solution:**

```python
# Use pytest-asyncio properly
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None

# Install pytest-asyncio
pip install pytest-asyncio

# Configure in pytest.ini
[pytest]
asyncio_mode = auto
```

### Mock Failures

**Problem:** Mocks not working as expected

**Solution:**

```python
# Use unittest.mock properly
from unittest.mock import Mock, patch, AsyncMock

# For async functions, use AsyncMock
mock_service = AsyncMock()
mock_service.get_data.return_value = {"key": "value"}

# Patch in the right location
# Patch where it's used, not where it's defined
@patch('app.api.auth.get_current_user')
def test_endpoint(mock_get_user):
    # Test code
```

## Performance Issues

### Slow API Responses

**Problem:** API endpoints are slow

**Solution:**

```bash
# Enable query logging
SQL_ECHO=true

# Check for N+1 queries
# Use joinedload() in SQLAlchemy

# Add database indexes
# Check slow query log

# Enable Redis caching
# Profile with py-spy or cProfile
```

### Slow Frontend Loading

**Problem:** Frontend takes long to load

**Solution:**

```typescript
// Use dynamic imports for large components
const HeavyComponent = dynamic(() => import('./Heavy'));

// Optimize images
import Image from 'next/image';

// Enable SWC minification
// next.config.js
module.exports = {
  swcMinify: true
};

// Analyze bundle size
npm run build
npm run analyze
```

### High Memory Usage

**Problem:** Application using too much memory

**Solution:**

```bash
# Backend: Check for memory leaks
# Use memory profiler
pip install memory-profiler
python -m memory_profiler app/main.py

# Frontend: Check bundle size
npm run build
# Review .next/analyze output

# Reduce pool sizes
DB_POOL_SIZE=10
REDIS_POOL_SIZE=5
```

## Browser Compatibility

### Works in Chrome but not Firefox

**Problem:** Browser-specific issues

**Solution:**

```javascript
// Check for browser-specific code
// Use feature detection, not browser detection

// Test in multiple browsers
// Use Autoprefixer for CSS
// Check Can I Use for feature support
```

### Japanese IME Not Working

**Problem:** Can't type Japanese in input fields

**Solution:**

```typescript
// Ensure input handles composition events
<input
  onCompositionStart={handleCompositionStart}
  onCompositionUpdate={handleCompositionUpdate}
  onCompositionEnd={handleCompositionEnd}
/>

// Don't preventDefault on composition events
// Don't interfere with IME input
```

## Getting Help

### Before Asking for Help

1. **Check this guide** - Your issue may be listed
2. **Search existing issues** - On GitHub
3. **Enable debug logging** - Get detailed error messages
4. **Check environment** - Verify all env vars are set
5. **Test in isolation** - Minimal reproduction case

### Reporting Bugs

Include:
- Operating system and version
- Python/Node.js versions
- Full error message and stack trace
- Steps to reproduce
- Expected vs actual behavior
- Relevant configuration files
- Screenshots if UI issue

### Getting Support

- **GitHub Issues** - Bug reports and technical issues
- **GitHub Discussions** - Questions and help
- **Documentation** - Check all docs first
- **Stack Overflow** - Tag with `nihongo-sensei`

### Useful Debugging Commands

```bash
# System info
python --version
node --version
docker --version
docker-compose --version

# Check services
docker-compose ps
systemctl status postgresql
systemctl status redis

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
journalctl -u postgresql -f

# Test connections
curl http://localhost:8000/health
redis-cli ping
psql -U postgres -c "SELECT version();"

# Check environment
env | grep -E 'ANTHROPIC|DATABASE|REDIS'

# Disk space
df -h

# Memory usage
free -h
```

---

**If all else fails, please open an issue on GitHub with full details!**

---

**Last Updated:** 2025-11-19
