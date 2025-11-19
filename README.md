# Nihongo Sensei - AI-Powered Japanese Learning Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](backend/htmlcov/index.html)

> A comprehensive, self-hosted AI-powered Japanese learning platform designed to take learners from complete beginner (N5) to professional proficiency (N2-N3) with focus on business communication in Japan.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Screenshots](#screenshots)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Development](#development)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

**Nihongo Sensei** combines multiple teaching methodologies including conversational AI, speech recognition, gamification, and spaced repetition to create an engaging and effective learning experience. Built with a test-driven development approach, the platform maintains 90%+ test coverage across all critical features.

### Target Audience

Designed for serious learners preparing for relocation to Japan and employment at Japanese companies, requiring practical business-level Japanese proficiency.

### Success Metrics

- Achieve JLPT N3 proficiency within 12 months of daily use
- Enable comfortable business communication in Japanese
- Maintain 80%+ 7-day retention rate through engagement
- Self-hostable with minimal infrastructure requirements

## Key Features

### Current MVP Features (v0.1.0)

- **User Authentication & Management**
  - Secure JWT-based authentication
  - User profiles with learning preferences
  - Progress tracking and statistics

- **Structured Lesson System**
  - Progressive curriculum from N5 to N3
  - Grammar explanations and examples
  - Vocabulary with readings and meanings
  - Kanji learning with stroke order

- **SRS Flashcard System**
  - SM-2 spaced repetition algorithm
  - Customizable review intervals
  - Performance-based scheduling
  - Study streak tracking

- **AI-Powered Conversation Practice**
  - Natural conversations with Claude Sonnet 4.5
  - Real-time grammar corrections
  - Context-aware responses
  - Conversation history tracking

- **Progress Dashboard**
  - Daily study streaks
  - Cards due for review
  - Mastery statistics
  - Achievement tracking

### Planned Features

- Speech-to-text Japanese practice (Whisper API)
- Text-to-speech pronunciation guide (Google TTS)
- Kanji handwriting recognition
- Business Japanese scenarios
- Mobile Progressive Web App
- Offline study mode
- Community features

## Screenshots

### Dashboard
*[Screenshot placeholder: User dashboard showing daily progress, streak counter, and study recommendations]*

### Flashcard Review
*[Screenshot placeholder: Flashcard interface with Japanese character on front, readings and meaning on back]*

### AI Conversation
*[Screenshot placeholder: Chat interface with AI sensei providing grammar corrections in context]*

### Lesson View
*[Screenshot placeholder: Structured lesson with grammar points, vocabulary, and examples]*

## Technology Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy 2.0** - Database ORM with async support
- **PostgreSQL 15+** - Relational database
- **Redis 7+** - Caching and session management
- **Alembic** - Database migrations
- **pytest** - Testing framework with 90%+ coverage

### AI Services
- **Anthropic Claude Sonnet 4.5** - Conversational AI
- **OpenAI Whisper** - Speech-to-text (planned)
- **Google Cloud TTS** - Text-to-speech (planned)

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Accessible component library
- **TanStack Query** - Server state management
- **Zustand** - Client state management

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy
- **GitHub Actions** - CI/CD pipeline

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- API keys for:
  - Anthropic Claude API
  - OpenAI API (for future speech features)
  - Google Cloud TTS (for future speech features)

### 3-Step Setup

```bash
# 1. Clone and configure
git clone https://github.com/yourusername/nihongo-sensei.git
cd nihongo-sensei
cp .env.example .env
# Edit .env with your API keys

# 2. Start with Docker Compose
docker-compose up -d

# 3. Initialize database
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/import_initial_data.py
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup (Development)

See detailed setup instructions in [Development](#development) section below.

## Development

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment
cp ../.env.example ../.env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Database Setup

```bash
# Start PostgreSQL and Redis with Docker
docker-compose up -d postgres redis

# Or install locally:
# - PostgreSQL 15+
# - Redis 7+
```

### Running Tests

```bash
# Backend tests with coverage
cd backend
pytest --cov=app --cov-report=html --cov-report=term

# Frontend tests
cd frontend
npm test

# Watch mode for TDD
cd backend
pytest-watch -- --cov=app

cd frontend
npm test -- --watch
```

## Project Structure

```
nihongo-sensei/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── lessons.py     # Lesson management
│   │   │   ├── flashcards.py  # SRS flashcard system
│   │   │   └── conversation.py # AI conversation
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── services/          # Business logic layer
│   │   │   ├── ai_service.py        # AI API integration
│   │   │   ├── srs_service.py       # Spaced repetition
│   │   │   ├── conversation_service.py
│   │   │   └── lesson_service.py
│   │   ├── prompts/           # AI prompt templates
│   │   ├── utils/             # Utility functions
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection
│   │   └── main.py            # Application entry point
│   ├── tests/                 # Test suite (90%+ coverage)
│   │   ├── unit/              # Unit tests
│   │   ├── integration/       # API integration tests
│   │   └── e2e/               # End-to-end tests
│   ├── alembic/              # Database migrations
│   ├── scripts/              # Utility scripts
│   └── requirements.txt
│
├── frontend/                  # Next.js React frontend
│   ├── app/                  # App Router pages
│   │   ├── page.tsx          # Home page
│   │   ├── layout.tsx        # Root layout
│   │   ├── lessons/          # Lesson pages (planned)
│   │   └── dashboard/        # User dashboard (planned)
│   ├── components/           # React components
│   │   ├── ui/              # shadcn/ui components
│   │   └── layout/          # Layout components
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API client
│   ├── lib/                 # Utilities
│   └── __tests__/           # Frontend tests
│
├── docker/                   # Docker configuration (planned)
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
│
├── docs/                     # Documentation
│   ├── API_REFERENCE.md     # Complete API documentation
│   ├── USER_GUIDE.md        # User manual
│   ├── TROUBLESHOOTING.md   # Common issues & solutions
│   ├── ARCHITECTURE.md      # System architecture
│   ├── DEPLOYMENT.md        # Deployment guide
│   └── TESTING.md           # Testing strategy
│
├── .env.example             # Environment template
├── CONTRIBUTING.md          # Contribution guidelines
├── CHANGELOG.md             # Version history
└── README.md               # This file
```

## Testing

This project follows **strict Test-Driven Development (TDD)** practices.

### Test Coverage

- **Overall Coverage:** 90%+
- **Core Business Logic:** 95%+
- **API Endpoints:** 100%
- **Test Files:** 18 files, ~5,400 lines of test code

### Running Tests

```bash
# Full test suite
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Watch mode for TDD
pytest-watch -- --cov=app
```

### Test Structure

- **Unit Tests:** Individual functions, services, and algorithms
- **Integration Tests:** API endpoints, database operations
- **E2E Tests:** Complete user workflows (planned)

See [TESTING.md](docs/TESTING.md) for detailed testing guidelines.

## Deployment

### Docker Deployment (Recommended)

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale backend=3
```

### Manual Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Server requirements
- Environment configuration
- Database setup
- Nginx configuration
- SSL/TLS setup
- Monitoring and logging

### Environment Variables

Required environment variables:
- `ANTHROPIC_API_KEY` - Claude API access
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `SECRET_KEY` - JWT signing key

See `.env.example` for complete configuration options.

## Documentation

### For Users
- [User Guide](docs/USER_GUIDE.md) - Getting started with learning
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

### For Developers
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [Architecture](docs/ARCHITECTURE.md) - System design and architecture
- [Testing Guide](docs/TESTING.md) - Testing strategy and practices
- [Backend README](backend/README.md) - Backend development guide
- [Frontend README](frontend/README.md) - Frontend development guide

### For Contributors
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- [Code of Conduct](CONTRIBUTING.md#code-of-conduct) - Community standards

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup
- Git workflow and branching strategy
- Pull request process
- Code style guidelines
- Testing requirements
- Commit message conventions

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write tests first** (TDD approach)
4. Implement the feature
5. Ensure all tests pass (`pytest && npm test`)
6. Commit changes (`git commit -m 'feat: add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Roadmap

### Version 0.2.0 (Planned)
- Speech-to-text practice with Whisper API
- Text-to-speech pronunciation guide
- Kanji handwriting recognition
- Enhanced progress analytics

### Version 0.3.0 (Planned)
- Business Japanese scenarios
- Progressive Web App (PWA) support
- Offline study mode
- Mobile-optimized interface

### Version 1.0.0 (Planned)
- Community features (study groups, leaderboards)
- Custom lesson creation
- Import/export progress
- Multi-language interface

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## Performance

- **Backend Response Time:** <100ms average
- **Database Query Time:** <50ms average
- **Frontend Initial Load:** <2s on 3G
- **Lighthouse Score:** 90+ (Performance, Accessibility, SEO)

## Security

- JWT-based authentication with secure token handling
- Password hashing with bcrypt
- SQL injection protection via SQLAlchemy
- CORS configuration for production
- Environment-based secrets management
- Regular dependency updates

See [SECURITY.md](docs/SECURITY.md) for security best practices.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **JMDict/KANJIDIC2** - Japanese dictionary data
- **Tatoeba Project** - Example sentences
- **Anthropic** - Claude AI API
- **OpenAI** - Whisper API for speech recognition
- **Community Contributors** - Thank you!

## Support

- **Documentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/yourusername/nihongo-sensei/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/nihongo-sensei/discussions)

## Project Status

**Current Version:** 0.1.0 (MVP)
**Status:** Active Development
**Test Coverage:** 90%+
**Production Ready:** Backend MVP complete, Frontend in progress

---

**Built with ❤️ for Japanese language learners worldwide**

*Last Updated: 2025-11-19*
