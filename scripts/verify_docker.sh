#!/bin/bash
set -e

# =============================================================================
# Nihongo Sensei - Docker Configuration Verification Script
# =============================================================================
# This script verifies the Docker configuration is correct
# Usage: ./scripts/verify_docker.sh
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║     Nihongo Sensei - Docker Configuration Verification       ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

ERRORS=0
WARNINGS=0

# =============================================================================
# Check Docker Files Exist
# =============================================================================

echo "📋 Checking Docker configuration files..."
echo ""

FILES=(
    "docker/docker-compose.yml"
    "docker/docker-compose.override.yml"
    "docker/Dockerfile.backend"
    "docker/Dockerfile.frontend"
    "docker/nginx.conf"
    "docker/entrypoint.backend.sh"
    ".env.example"
    ".dockerignore"
)

for file in "${FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        ((ERRORS++))
    fi
done

echo ""

# =============================================================================
# Check Script Files
# =============================================================================

echo "📋 Checking deployment scripts..."
echo ""

SCRIPTS=(
    "scripts/setup.sh"
    "scripts/deploy.sh"
    "scripts/backup.sh"
    "scripts/test_all.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$PROJECT_ROOT/$script" ]; then
        if [ -x "$PROJECT_ROOT/$script" ]; then
            echo "✅ $script (executable)"
        else
            echo "⚠️  $script (not executable)"
            ((WARNINGS++))
        fi
    else
        echo "❌ $script (missing)"
        ((ERRORS++))
    fi
done

echo ""

# =============================================================================
# Check Environment Configuration
# =============================================================================

echo "📋 Checking environment configuration..."
echo ""

if [ -f "$PROJECT_ROOT/.env.example" ]; then
    echo "✅ .env.example exists"

    # Check for required variables in .env.example
    REQUIRED_VARS=(
        "POSTGRES_PASSWORD"
        "SECRET_KEY"
        "ANTHROPIC_API_KEY"
        "OPENAI_API_KEY"
        "GOOGLE_CLOUD_TTS_KEY"
    )

    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$var=" "$PROJECT_ROOT/.env.example"; then
            echo "  ✅ $var defined in .env.example"
        else
            echo "  ❌ $var missing in .env.example"
            ((ERRORS++))
        fi
    done
else
    echo "❌ .env.example missing"
    ((ERRORS++))
fi

echo ""

if [ -f "$PROJECT_ROOT/.env" ]; then
    echo "✅ .env file exists"

    # Check for placeholder values
    if grep -q "CHANGE_ME" "$PROJECT_ROOT/.env"; then
        echo "  ⚠️  .env contains CHANGE_ME placeholders"
        ((WARNINGS++))
    fi

    if grep -q "XXXXX" "$PROJECT_ROOT/.env"; then
        echo "  ⚠️  .env contains XXXXX placeholders"
        ((WARNINGS++))
    fi
else
    echo "⚠️  .env file not found (will be created during setup)"
    ((WARNINGS++))
fi

echo ""

# =============================================================================
# Check Docker Compose Syntax
# =============================================================================

echo "📋 Checking Docker Compose syntax..."
echo ""

cd "$PROJECT_ROOT/docker"

if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
    if docker-compose config > /dev/null 2>&1 || docker compose config > /dev/null 2>&1; then
        echo "✅ docker-compose.yml syntax is valid"
    else
        echo "❌ docker-compose.yml has syntax errors"
        ((ERRORS++))
    fi
else
    echo "⚠️  Docker Compose not installed (cannot verify syntax)"
    ((WARNINGS++))
fi

echo ""

# =============================================================================
# Check Dockerfile Syntax
# =============================================================================

echo "📋 Checking Dockerfile syntax..."
echo ""

if command -v docker &> /dev/null; then
    # Check backend Dockerfile
    if docker build -f "$PROJECT_ROOT/docker/Dockerfile.backend" --target base "$PROJECT_ROOT" -t test-backend:verify > /dev/null 2>&1; then
        echo "✅ Dockerfile.backend syntax is valid"
        docker rmi test-backend:verify > /dev/null 2>&1 || true
    else
        echo "⚠️  Dockerfile.backend may have syntax issues (unable to verify base stage)"
        ((WARNINGS++))
    fi

    # Note: Frontend Dockerfile requires npm dependencies, skip build test
    echo "ℹ️  Dockerfile.frontend (skipping build test)"
else
    echo "⚠️  Docker not installed (cannot verify Dockerfile syntax)"
    ((WARNINGS++))
fi

echo ""

# =============================================================================
# Check Nginx Configuration
# =============================================================================

echo "📋 Checking Nginx configuration..."
echo ""

if [ -f "$PROJECT_ROOT/docker/nginx.conf" ]; then
    # Basic syntax check
    if grep -q "upstream backend" "$PROJECT_ROOT/docker/nginx.conf" && \
       grep -q "upstream frontend" "$PROJECT_ROOT/docker/nginx.conf" && \
       grep -q "location /api" "$PROJECT_ROOT/docker/nginx.conf"; then
        echo "✅ nginx.conf appears valid"
    else
        echo "⚠️  nginx.conf may be incomplete"
        ((WARNINGS++))
    fi
else
    echo "❌ nginx.conf missing"
    ((ERRORS++))
fi

echo ""

# =============================================================================
# Check Documentation
# =============================================================================

echo "📋 Checking documentation..."
echo ""

DOCS=(
    "docs/DEPLOYMENT.md"
    "docker/README.md"
    "CLAUDE.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$PROJECT_ROOT/$doc" ]; then
        echo "✅ $doc"
    else
        echo "⚠️  $doc (missing)"
        ((WARNINGS++))
    fi
done

echo ""

# =============================================================================
# Summary
# =============================================================================

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                   Verification Summary                        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "🎉 All checks passed! Docker configuration is ready."
    echo ""
    echo "Next steps:"
    echo "1. Copy .env.example to .env: cp .env.example .env"
    echo "2. Edit .env with your API keys: nano .env"
    echo "3. Run setup script: ./scripts/setup.sh"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Verification completed with $WARNINGS warning(s)"
    echo ""
    echo "Docker configuration is mostly ready, but review warnings above."
    exit 0
else
    echo "❌ Verification failed with $ERRORS error(s) and $WARNINGS warning(s)"
    echo ""
    echo "Please fix the errors above before deploying."
    exit 1
fi
