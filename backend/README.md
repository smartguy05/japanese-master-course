# Nihongo Sensei - Backend API

FastAPI-based backend service for the Nihongo Sensei Japanese learning platform.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Setup](#setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Environment Variables](#environment-variables)
- [Development Workflow](#development-workflow)
- [Code Structure](#code-structure)
- [Services](#services)
- [Testing Strategy](#testing-strategy)

## Overview

The backend provides a RESTful API for:
- User authentication and authorization
- Lesson content management
- SRS flashcard system
- AI-powered conversation practice
- Progress tracking and analytics

**Tech Stack:**
- Python 3.11+
- FastAPI (async web framework)
- SQLAlchemy 2.0 (async ORM)
- PostgreSQL 15+ (database)
- Redis 7+ (caching, sessions)
- Alembic (migrations)
- pytest (testing)

## Architecture

```
┌─────────────────┐
│  FastAPI App    │
├─────────────────┤
│   API Routes    │ ─── Auth, Lessons, Flashcards, Conversation
├─────────────────┤
│   Services      │ ─── Business Logic Layer
├─────────────────┤
│   Models        │ ─── SQLAlchemy ORM
├─────────────────┤
│   Database      │ ─── PostgreSQL + Redis
└─────────────────┘
```

### Key Design Patterns

1. **Dependency Injection** - FastAPI's DI system for services
2. **Repository Pattern** - Data access abstraction
3. **Service Layer** - Business logic separation
4. **Schema Validation** - Pydantic models for data validation
5. **Async/Await** - Non-blocking I/O operations

## Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+
- Redis 7+
- Virtual environment tool (venv, conda, etc.)

### Installation

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Database Setup

```bash
# Option 1: Using Docker
cd ..
docker-compose up -d postgres redis

# Option 2: Local installation
# Install PostgreSQL and Redis locally
# Create database
createdb nihongo_sensei
```

### Environment Configuration

```bash
# Copy example environment file
cp ../.env.example ../.env

# Edit .env with your configuration
nano ../.env
```

**Required variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - JWT signing key (generate with `openssl rand -hex 32`)
- `ANTHROPIC_API_KEY` - Claude API key

See [Environment Variables](#environment-variables) section for complete list.

### Run Migrations

```bash
# Run database migrations
alembic upgrade head

# Create a new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"
```

### Import Initial Data

```bash
# Import Japanese dictionary data (optional but recommended)
python scripts/import_initial_data.py
```

## Running the Application

### Development Server

```bash
# Standard mode
uvicorn app.main:app --reload --port 8000

# With environment variables
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0

# With log level
uvicorn app.main:app --reload --port 8000 --log-level debug
```

**Access points:**
- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### Production Server

```bash
# Using Gunicorn with Uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_srs_algorithm.py -v

# Run specific test category
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m "not slow"     # Exclude slow tests

# Watch mode (for TDD)
pytest-watch -- --cov=app
```

### Test Coverage

Current coverage: **90%+**

View detailed coverage report:
```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Test Structure

```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_srs_algorithm.py      # SRS scheduling logic
│   ├── test_ai_service.py         # AI service (mocked)
│   ├── test_auth_utils.py         # Authentication utilities
│   ├── test_content_utils.py      # Content processing
│   ├── test_conversation_service.py
│   ├── test_lesson_service.py
│   └── test_user_model.py
├── integration/             # Integration tests (DB, API)
│   ├── test_api_auth.py           # Auth endpoints
│   ├── test_api_lessons.py        # Lesson endpoints
│   ├── test_api_flashcards.py     # Flashcard endpoints
│   ├── test_api_conversation.py   # Conversation endpoints
│   └── test_api_health.py         # Health checks
├── e2e/                    # End-to-end tests (planned)
└── conftest.py             # Shared fixtures
```

## API Endpoints

### Authentication

```
POST   /api/auth/register       Register new user
POST   /api/auth/login          Login and get JWT token
GET    /api/auth/me             Get current user info
PUT    /api/auth/me             Update user profile
```

### Lessons

```
GET    /api/lessons            List all lessons
GET    /api/lessons/{id}       Get lesson details
POST   /api/lessons            Create lesson (admin)
PUT    /api/lessons/{id}       Update lesson (admin)
DELETE /api/lessons/{id}       Delete lesson (admin)
```

### Flashcards

```
GET    /api/flashcards/due     Get cards due for review
POST   /api/flashcards/review  Submit card review
GET    /api/flashcards/stats   Get study statistics
POST   /api/flashcards         Create custom flashcard
```

### Conversation

```
POST   /api/conversation/message    Send message to AI
GET    /api/conversation/history    Get conversation history
DELETE /api/conversation/history    Clear conversation history
```

### Health & Monitoring

```
GET    /health                 Health check endpoint
GET    /                       API information
```

For complete API documentation, see:
- Interactive docs: http://localhost:8000/docs
- [API Reference](../docs/API_REFERENCE.md)

## Database Schema

### Core Tables

**users**
- User authentication and profile information
- Study preferences and settings

**lessons**
- Structured lesson content
- Grammar points, vocabulary, kanji
- JLPT level classification

**flashcards**
- Individual flashcard items
- Associated with vocabulary or kanji
- Custom user-created cards

**reviews**
- SRS review history
- Performance tracking
- Next review scheduling

**conversations**
- AI conversation history
- User messages and AI responses
- Grammar corrections

**progress**
- User learning progress
- Study streaks and statistics
- Achievement tracking

### Entity Relationships

```
users (1) ─── (N) reviews
users (1) ─── (N) conversations
users (1) ─── (1) progress
lessons (1) ─── (N) flashcards
flashcards (1) ─── (N) reviews
```

See database models in `app/models/` for complete schema.

## Environment Variables

### Required

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services
ANTHROPIC_API_KEY=sk-ant-...
```

### Optional

```bash
# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=false

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# AI Configuration
AI_CONVERSATION_MODEL=claude-sonnet-4-20250514
AI_CONVERSATION_BASE_URL=https://api.anthropic.com
ENABLE_CONTENT_CACHING=true

# Database Pool
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis
REDIS_POOL_SIZE=10
```

See `../.env.example` for complete list.

## Development Workflow

### Test-Driven Development (TDD)

**This project requires TDD. Write tests first!**

```bash
# 1. Start test watcher
pytest-watch -- --cov=app

# 2. Write failing test
# Edit tests/unit/test_new_feature.py

# 3. Implement minimum code to pass
# Edit app/services/new_feature.py

# 4. See test pass
# 5. Refactor while keeping tests green
```

### Adding a New Feature

1. **Write Test First**
```python
# tests/unit/test_new_feature.py
def test_new_feature():
    result = new_feature()
    assert result == expected_value
```

2. **Run Test (Should Fail)**
```bash
pytest tests/unit/test_new_feature.py
```

3. **Implement Feature**
```python
# app/services/new_feature.py
def new_feature():
    return expected_value
```

4. **Test Passes**
```bash
pytest tests/unit/test_new_feature.py
```

5. **Add Integration Test**
```python
# tests/integration/test_api_new_feature.py
async def test_new_feature_endpoint(client):
    response = await client.get("/api/new-feature")
    assert response.status_code == 200
```

### Database Migrations

```bash
# Create migration after model changes
alembic revision --autogenerate -m "Add new table"

# Review generated migration
nano alembic/versions/xxx_add_new_table.py

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Code Style

```bash
# Format code
black app/ tests/

# Check linting
ruff check app/ tests/

# Type checking
mypy app/

# Run all checks
black . && ruff check . && mypy app/
```

## Code Structure

### Application Entry Point

**app/main.py**
- FastAPI application initialization
- Middleware configuration
- Router registration
- Lifespan events (startup/shutdown)

### API Routes (app/api/)

Each module handles specific domain:
- `auth.py` - Authentication and user management
- `lessons.py` - Lesson content CRUD
- `flashcards.py` - SRS flashcard operations
- `conversation.py` - AI conversation interface

**Pattern:**
```python
from fastapi import APIRouter, Depends
from app.services.example_service import ExampleService

router = APIRouter(prefix="/api/example", tags=["example"])

@router.get("/")
async def get_items(service: ExampleService = Depends()):
    return await service.get_all()
```

### Services (app/services/)

Business logic layer, separated from API routes.

**Key Services:**
- `ai_service.py` - Anthropic Claude API integration
- `srs_service.py` - Spaced repetition scheduling (SM-2 algorithm)
- `conversation_service.py` - Conversation management and correction
- `lesson_service.py` - Lesson content management
- `redis_service.py` - Redis caching and sessions

**Pattern:**
```python
class ExampleService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_item(self, item_id: int):
        # Business logic here
        pass
```

### Models (app/models/)

SQLAlchemy ORM models representing database tables.

**Pattern:**
```python
from sqlalchemy import Column, Integer, String
from app.database import Base

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

### Schemas (app/schemas/)

Pydantic models for request/response validation.

**Pattern:**
```python
from pydantic import BaseModel, Field

class ExampleCreate(BaseModel):
    name: str = Field(..., min_length=1)

class ExampleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
```

### Prompts (app/prompts/)

AI prompt templates for Claude API.

**Pattern:**
```python
CONVERSATION_PROMPT = """
You are a Japanese language tutor...
User: {user_message}
Context: {context}
"""

def build_prompt(user_message: str, context: str) -> str:
    return CONVERSATION_PROMPT.format(
        user_message=user_message,
        context=context
    )
```

## Services

### AI Service

**Purpose:** Integration with Anthropic Claude API

**Key Methods:**
- `chat()` - Send message and get response
- `parse_correction()` - Extract grammar corrections
- `generate_content()` - Generate lesson content

**Testing:** Uses mocked responses for consistent testing

### SRS Service

**Purpose:** Spaced Repetition System (SM-2 algorithm)

**Key Methods:**
- `calculate_next_review()` - Schedule next review
- `update_ease_factor()` - Adjust difficulty based on performance
- `get_due_cards()` - Retrieve cards due for review

**Testing:** 100% coverage with edge case testing

### Conversation Service

**Purpose:** Manage AI conversation sessions

**Key Methods:**
- `send_message()` - Process user message and get AI response
- `get_history()` - Retrieve conversation history
- `clear_history()` - Reset conversation

**Testing:** Integration tests with mocked AI service

### Lesson Service

**Purpose:** Lesson content management

**Key Methods:**
- `get_lesson()` - Retrieve lesson by ID
- `create_lesson()` - Create new lesson
- `list_lessons()` - Get paginated lesson list

**Testing:** Database integration tests

## Testing Strategy

### Unit Tests

**Focus:** Individual functions and services in isolation

**Characteristics:**
- Fast (<10ms per test)
- No external dependencies
- Mocked services and APIs
- 95%+ coverage target

**Example:**
```python
def test_calculate_next_review_good_answer():
    """Test SRS calculation for good answer."""
    result = srs_service.calculate_next_review(
        ease_factor=2.5,
        interval=1,
        quality=4
    )
    assert result.interval > 1
    assert result.ease_factor >= 2.5
```

### Integration Tests

**Focus:** API endpoints with real database

**Characteristics:**
- Medium speed (100-500ms per test)
- Uses test database
- Mocked AI services
- 100% endpoint coverage

**Example:**
```python
@pytest.mark.asyncio
async def test_create_lesson(client, db_session):
    """Test lesson creation endpoint."""
    payload = {"title": "Test Lesson", "level": "N5"}
    response = await client.post("/api/lessons", json=payload)

    assert response.status_code == 201
    assert response.json()["title"] == "Test Lesson"
```

### Test Fixtures

**conftest.py** provides shared fixtures:
- `client` - Test HTTP client
- `db_session` - Test database session
- `mock_ai_service` - Mocked AI responses
- `test_user` - Authenticated test user

## Performance Considerations

### Database Optimization

- Use async SQLAlchemy for non-blocking queries
- Implement connection pooling
- Add database indexes on frequently queried fields
- Use `joinedload()` to prevent N+1 queries

### Caching Strategy

- Redis for session data
- Cache frequent AI prompts responses
- Cache lesson content (infrequent changes)
- Implement cache invalidation on updates

### API Response Times

**Targets:**
- Health check: <10ms
- Simple queries: <50ms
- Complex queries: <200ms
- AI conversations: <2s (external API)

## Troubleshooting

### Common Issues

**Database connection errors:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
psql $DATABASE_URL
```

**Redis connection errors:**
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli -u $REDIS_URL ping
```

**Migration conflicts:**
```bash
# Reset migrations (development only!)
alembic downgrade base
alembic upgrade head
```

**Import errors:**
```bash
# Ensure virtual environment is activated
which python  # Should point to venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

See [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) for more solutions.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

**Key Points:**
- Write tests first (TDD)
- Maintain 90%+ coverage
- Follow code style (black, ruff)
- Update documentation
- Write clear commit messages

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)

---

**Last Updated:** 2025-11-19
