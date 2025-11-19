# 🇯🇵 Nihongo Sensei - AI-Powered Japanese Learning Platform

## Project Overview

**Nihongo Sensei** is a comprehensive, self-hosted AI-powered Japanese learning platform designed to take learners from complete beginner (N5) to professional proficiency (N2-N3) with focus on business communication in Japan. The platform combines multiple teaching methodologies including conversational AI, speech recognition, gamification, and spaced repetition to create an engaging and effective learning experience.

**Target User:** Anthony - preparing for relocation to Japan and employment at a Japanese company, requiring practical business-level Japanese proficiency.

**Key Success Metrics:**
- Achieve JLPT N3 proficiency within 12 months of daily use
- Enable comfortable business communication in Japanese
- Maintain 80%+ 7-day retention rate through engagement
- Self-hostable with minimal infrastructure requirements

---

## 🚨 MANDATORY TEST-DRIVEN DEVELOPMENT (TDD) REQUIREMENTS 🚨

**THIS IS NOT OPTIONAL - TDD IS REQUIRED FOR ALL CODE IN THIS PROJECT**

### The Non-Negotiable Workflow

```
CRITICAL REQUIREMENT: TESTS MUST BE WRITTEN BEFORE IMPLEMENTATION

1. ✅ Write the test FIRST (RED phase)
2. ✅ Run the test and watch it FAIL
3. ✅ Write MINIMUM code to make test pass (GREEN phase)
4. ✅ Refactor while keeping tests green (REFACTOR phase)
5. ✅ Commit with test evidence
6. 🔁 Repeat

NO CODE SHOULD BE WRITTEN WITHOUT A FAILING TEST FIRST.
```

### TDD Violations (These Are Forbidden)

- ❌ Writing implementation code before tests exist
- ❌ Skipping tests because "it's just a small change"
- ❌ Writing tests after implementation is complete
- ❌ Commenting out failing tests to "fix later"
- ❌ Pushing code without running the full test suite
- ❌ "I'll write tests later" (No, you won't. Write them now.)

### Why This Matters for This Project

1. **AI Integration Complexity:** API calls, prompt engineering, and conversation flows require precise testing to ensure reliability
2. **Educational Correctness:** Grammar corrections, vocabulary teaching, and kanji recognition must be 100% accurate
3. **User Progress Integrity:** SRS scheduling, streak tracking, and progress data cannot have bugs
4. **Multi-Component System:** Frontend, backend, AI services, and databases must integrate flawlessly
5. **Long Development Timeline:** 15-25 months requires disciplined testing to prevent technical debt

### Test Coverage Requirements

- **Minimum Coverage:** 85% overall, 90% for core learning logic
- **Critical Paths:** 100% coverage for SRS algorithms, progress tracking, and AI correction logic
- **API Endpoints:** Every endpoint must have integration tests
- **React Components:** All interactive components must have unit tests
- **AI Prompts:** Regression tests for prompt outputs with sample data

---

## Technology Stack

### Backend (Python 3.11+)
- **FastAPI** - Async web framework for REST API
- **SQLAlchemy 2.0** - ORM with async support
- **Alembic** - Database migrations
- **PostgreSQL 15+** - Primary database
- **Redis 7+** - Caching, session management, SRS queue
- **pytest + pytest-asyncio** - Testing framework
- **httpx** - Async HTTP client for AI API calls
- **python-multipart** - File upload handling
- **python-jose** - JWT token handling
- **passlib + bcrypt** - Password hashing
- **pydantic** - Data validation and settings

### AI Services (Configurable)
- **Primary Conversation:** Anthropic Claude Sonnet 4.5 (default)
- **Speech-to-Text:** OpenAI Whisper API
- **Text-to-Speech:** Google Cloud Text-to-Speech
- **Content Generation:** Claude Sonnet 4.5 with specialized prompts
- **Fallback Support:** Configurable URLs for alternative providers

### Frontend (Next.js 14+ / React 18)
- **Next.js 14** - App Router, Server Components, TypeScript
- **React 18** - UI library with hooks
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Pre-built accessible components
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Framer Motion** - Animations
- **React Hook Form + Zod** - Form validation
- **next-pwa** - Progressive Web App support
- **Jest + React Testing Library** - Frontend testing

### Infrastructure & Deployment
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy, static file serving
- **MinIO** (optional) - S3-compatible object storage for audio files
- **GitHub Actions** - CI/CD pipeline
- **pytest-cov** - Coverage reporting
- **pre-commit** - Git hooks for linting and testing

### Data Sources
- **JMDict/KANJIDIC2** - Japanese dictionary data (open source)
- **Tatoeba** - Example sentences corpus
- **AI-Generated Content** - Custom lessons, grammar explanations, conversation scenarios

---

## 🧪 Test-Driven Development Workflow

### Running Tests

**Backend (Python):**
```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_srs_algorithm.py -v

# Run with specific markers
pytest -m "unit" -v
pytest -m "integration" -v
pytest -m "ai_dependent" -v

# Watch mode for TDD
pytest-watch -- --cov=app
```

**Frontend (Next.js):**
```bash
# Run all tests
npm test

# Run in watch mode (for TDD)
npm test -- --watch

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- ConversationInterface.test.tsx
```

**Pre-commit Hooks:**
```bash
# Install pre-commit hooks (do this once)
pre-commit install

# Run manually before commit
pre-commit run --all-files

# Tests run automatically on git commit
git commit -m "feat: add kanji recognition"
```

### Test Structure

**Backend Tests (`/backend/tests/`):**
```
tests/
├── unit/
│   ├── test_srs_algorithm.py          # SRS scheduling logic
│   ├── test_kanji_service.py          # Kanji data operations
│   ├── test_conversation_service.py   # AI conversation logic
│   └── test_auth.py                   # Authentication logic
├── integration/
│   ├── test_api_lessons.py            # Lesson API endpoints
│   ├── test_api_conversation.py       # Conversation endpoints
│   ├── test_api_progress.py           # Progress tracking endpoints
│   └── test_database.py               # Database operations
├── e2e/
│   ├── test_user_journey.py           # Complete user flows
│   └── test_learning_session.py       # Full learning session
└── conftest.py                        # Pytest fixtures
```

**Frontend Tests (`/frontend/__tests__/`):**
```
__tests__/
├── components/
│   ├── FlashCard.test.tsx
│   ├── ConversationInterface.test.tsx
│   └── ProgressDashboard.test.tsx
├── hooks/
│   ├── useSRS.test.ts
│   └── useConversation.test.ts
├── utils/
│   ├── srsScheduler.test.ts
│   └── japaneseUtils.test.ts
└── integration/
    └── LearningSession.test.tsx
```

### Test-First Examples

**Example 1: Adding Kanji Recognition Feature**

```python
# Step 1: Write the test FIRST (tests/unit/test_kanji_service.py)
def test_recognize_kanji_from_image():
    """Test kanji recognition from uploaded image."""
    # Arrange
    test_image = load_test_image("kanji_水.png")
    expected_kanji = "水"
    expected_readings = ["すい", "みず"]
    
    # Act
    result = kanji_service.recognize_from_image(test_image)
    
    # Assert
    assert result.kanji == expected_kanji
    assert result.readings == expected_readings
    assert result.confidence > 0.8

# Step 2: Run test - it WILL fail (no implementation yet)
# Step 3: Write MINIMUM code to make it pass
# Step 4: Refactor for quality while keeping tests green
```

**Example 2: Adding Conversation Correction Feature**

```typescript
// Step 1: Write the test FIRST (__tests__/utils/correctionParser.test.ts)
describe('correctionParser', () => {
  it('should extract corrections from AI response', () => {
    // Arrange
    const aiResponse = `
      Your sentence was good! However, you said "私は学校に行きました"
      but it's more natural to say "私は学校へ行きました".
      The particle へ is more common for destinations.
    `;
    
    // Act
    const corrections = parseCorrections(aiResponse);
    
    // Assert
    expect(corrections).toHaveLength(1);
    expect(corrections[0].original).toBe('私は学校に行きました');
    expect(corrections[0].corrected).toBe('私は学校へ行きました');
    expect(corrections[0].explanation).toContain('particle へ');
  });
});

// Step 2: Run test - it WILL fail
// Step 3: Implement parseCorrections() to make test pass
// Step 4: Refactor and add more test cases
```

### Quality Gates

**Pre-Commit:**
- All tests must pass
- Linting must pass (ruff, black, eslint, prettier)
- Type checking must pass (mypy, TypeScript)
- No coverage decrease allowed

**Pull Request:**
- All tests must pass in CI
- Coverage must be ≥85% overall
- New code must have ≥90% coverage
- Integration tests must pass
- Code review required

**Deployment:**
- Full test suite passes
- E2E tests pass
- Performance tests pass (if applicable)
- Security scan passes

---

## Project Structure

```
nihongo-sensei/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── kanji.py
│   │   │   ├── vocabulary.py
│   │   │   ├── lesson.py
│   │   │   └── progress.py
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── api/               # API routes
│   │   │   ├── auth.py
│   │   │   ├── lessons.py
│   │   │   ├── conversation.py
│   │   │   ├── speech.py
│   │   │   └── progress.py
│   │   ├── services/          # Business logic
│   │   │   ├── ai_service.py         # AI API integration
│   │   │   ├── srs_service.py        # Spaced repetition
│   │   │   ├── kanji_service.py      # Kanji operations
│   │   │   ├── content_generation.py # AI content generation
│   │   │   └── speech_service.py     # Speech recognition/synthesis
│   │   ├── prompts/           # AI prompt templates
│   │   │   ├── conversation_prompts.py
│   │   │   ├── correction_prompts.py
│   │   │   └── content_generation_prompts.py
│   │   └── utils/
│   ├── tests/                 # All backend tests
│   ├── alembic/              # Database migrations
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/                  # Next.js React frontend
│   ├── app/                  # App Router pages
│   │   ├── page.tsx          # Home page
│   │   ├── lessons/          # Lesson pages
│   │   ├── conversation/     # Conversation interface
│   │   ├── progress/         # Progress dashboard
│   │   └── settings/         # User settings
│   ├── components/           # React components
│   │   ├── flashcards/
│   │   ├── conversation/
│   │   ├── progress/
│   │   └── ui/              # shadcn components
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utilities
│   ├── __tests__/           # Frontend tests
│   ├── public/
│   │   ├── manifest.json    # PWA manifest
│   │   └── sw.js           # Service worker
│   ├── package.json
│   └── next.config.js
├── docker/                   # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── scripts/                  # Utility scripts
│   ├── setup.sh             # One-command setup
│   ├── import_jmdict.py     # Import dictionary data
│   ├── generate_content.py  # AI content generation
│   └── backup.sh            # Database backup
├── docs/                     # Project documentation
│   ├── design.md
│   ├── plan.md
│   ├── tasks.md
│   ├── progress.md
│   ├── goals.md
│   ├── CODE_HELP.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── TESTING.md
│   └── SECURITY.md
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/CD pipeline
├── .env.example             # Environment template
├── .pre-commit-config.yaml  # Pre-commit hooks
└── README.md
```

---

## Development Commands

### Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd nihongo-sensei

# Install pre-commit hooks (CRITICAL - enforces TDD)
pre-commit install

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Testing dependencies

# Frontend setup
cd ../frontend
npm install

# Start databases (Docker)
cd ..
docker-compose up -d postgres redis

# Initialize database
cd backend
alembic upgrade head
python scripts/import_jmdict.py  # Import Japanese dictionary data

# Environment variables
cp .env.example .env
# Edit .env with your API keys:
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY (for Whisper)
# - GOOGLE_CLOUD_TTS_KEY
```

### Development Workflow (TDD)

**ALWAYS START WITH TESTS:**

```bash
# Backend TDD workflow
cd backend

# 1. Start test watcher
pytest-watch -- --cov=app

# 2. Write failing test in tests/
# 3. Implement minimum code to pass
# 4. See test turn green
# 5. Refactor while keeping tests green

# Frontend TDD workflow
cd frontend

# 1. Start test watcher
npm test -- --watch

# 2. Write failing test in __tests__/
# 3. Implement minimum code to pass
# 4. See test turn green
# 5. Refactor while keeping tests green
```

### Running the Application

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Access application:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Testing Commands (Run Before Every Commit)

```bash
# Backend: Full test suite with coverage
cd backend
pytest --cov=app --cov-report=html --cov-report=term-missing
# Coverage report: htmlcov/index.html

# Frontend: Full test suite with coverage
cd frontend
npm test -- --coverage --watchAll=false
# Coverage report: coverage/index.html

# Run all tests (backend + frontend)
./scripts/test_all.sh

# Pre-commit checks (linting, type checking, tests)
pre-commit run --all-files
```

### Database Migrations

```bash
cd backend
source venv/bin/activate

# Create migration after model changes
alembic revision --autogenerate -m "Add kanji proficiency tracking"

# BEFORE applying migration:
# 1. Write test for migration in tests/test_migrations.py
# 2. Verify test fails
# 3. Apply migration
alembic upgrade head

# 4. Verify test passes
pytest tests/test_migrations.py -v

# Rollback migration
alembic downgrade -1
```

### Content Generation

```bash
# Generate N5 lesson content using AI
cd backend
python scripts/generate_content.py --level N5 --type grammar

# Generate conversation scenarios
python scripts/generate_content.py --type conversation --scenarios business

# Generate test data for development
python scripts/generate_test_data.py
```

---

## Code Patterns & Standards

### Backend Patterns

**1. API Endpoint Structure (with tests first)**

```python
# tests/integration/test_api_lessons.py - WRITE THIS FIRST
@pytest.mark.asyncio
async def test_get_lesson_success(client, authenticated_user):
    """Test successful lesson retrieval."""
    # Arrange
    lesson_id = "hiragana-01"
    
    # Act
    response = await client.get(f"/api/lessons/{lesson_id}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lesson_id
    assert "content" in data
    assert "exercises" in data

# app/api/lessons.py - IMPLEMENT AFTER TEST EXISTS
from fastapi import APIRouter, Depends, HTTPException
from app.services.lesson_service import LessonService
from app.schemas.lesson import LessonResponse

router = APIRouter(prefix="/api/lessons", tags=["lessons"])

@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(
    lesson_id: str,
    service: LessonService = Depends()
):
    """Retrieve a lesson by ID."""
    lesson = await service.get_lesson(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
```

**2. Service Layer Pattern (business logic)**

```python
# tests/unit/test_srs_service.py - WRITE THIS FIRST
def test_calculate_next_review_correct_answer():
    """Test SRS scheduling for correct answers."""
    # Arrange
    card = FlashCard(
        ease_factor=2.5,
        interval_days=1,
        repetitions=0
    )
    
    # Act
    next_review = srs_service.calculate_next_review(
        card=card,
        quality=4  # Good answer
    )
    
    # Assert
    assert next_review.interval_days > card.interval_days
    assert next_review.ease_factor >= 2.5
    assert next_review.repetitions == 1

# app/services/srs_service.py - IMPLEMENT AFTER TEST
class SRSService:
    """Spaced Repetition System implementation (SM-2 algorithm)."""
    
    def calculate_next_review(
        self,
        card: FlashCard,
        quality: int  # 0-5 rating
    ) -> NextReview:
        """Calculate next review date based on answer quality."""
        # SM-2 algorithm implementation
        # ... implementation details
        return NextReview(...)
```

**3. AI Service Integration (with mocking for tests)**

```python
# tests/unit/test_ai_service.py - WRITE THIS FIRST
@pytest.mark.asyncio
async def test_conversation_response_correction(mock_anthropic_client):
    """Test AI conversation with grammar correction."""
    # Arrange
    user_input = "私は学校に行きました"  # Using に instead of へ
    mock_anthropic_client.messages.create.return_value = Mock(
        content=[Mock(text="Good effort! However, with destinations...")]
    )
    
    # Act
    response = await ai_service.get_conversation_response(
        user_input=user_input,
        conversation_history=[]
    )
    
    # Assert
    assert "correction" in response
    assert response["correction"]["explanation"]
    mock_anthropic_client.messages.create.assert_called_once()

# app/services/ai_service.py - IMPLEMENT AFTER TEST
class AIService:
    def __init__(self, api_key: str, model: str):
        self.client = Anthropic(api_key=api_key)
        self.model = model
    
    async def get_conversation_response(
        self,
        user_input: str,
        conversation_history: List[Message]
    ) -> ConversationResponse:
        """Get AI response with potential corrections."""
        # Use structured prompts from prompts/conversation_prompts.py
        prompt = build_conversation_prompt(user_input, conversation_history)
        
        response = await self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        return parse_conversation_response(response.content[0].text)
```

### Frontend Patterns

**1. React Component Structure (with tests first)**

```typescript
// __tests__/components/FlashCard.test.tsx - WRITE THIS FIRST
import { render, screen, fireEvent } from '@testing-library/react';
import { FlashCard } from '@/components/flashcards/FlashCard';

describe('FlashCard', () => {
  it('should reveal answer when card is flipped', () => {
    // Arrange
    const card = {
      front: '水',
      back: 'みず (water)',
      readings: ['すい', 'みず']
    };
    
    render(<FlashCard card={card} />);
    
    // Act
    const cardElement = screen.getByTestId('flashcard');
    fireEvent.click(cardElement);
    
    // Assert
    expect(screen.getByText('みず (water)')).toBeInTheDocument();
    expect(screen.getByText('すい')).toBeInTheDocument();
  });
});

// components/flashcards/FlashCard.tsx - IMPLEMENT AFTER TEST
'use client';
import { useState } from 'react';
import { Card } from '@/components/ui/card';

interface FlashCardProps {
  card: {
    front: string;
    back: string;
    readings: string[];
  };
}

export function FlashCard({ card }: FlashCardProps) {
  const [isFlipped, setIsFlipped] = useState(false);
  
  return (
    <Card 
      data-testid="flashcard"
      onClick={() => setIsFlipped(!isFlipped)}
      className="cursor-pointer"
    >
      {!isFlipped ? (
        <div className="text-6xl">{card.front}</div>
      ) : (
        <div>
          <div className="text-3xl">{card.back}</div>
          <div className="text-sm">
            {card.readings.map(r => <span key={r}>{r}</span>)}
          </div>
        </div>
      )}
    </Card>
  );
}
```

**2. Custom Hooks (with tests first)**

```typescript
// __tests__/hooks/useSRS.test.ts - WRITE THIS FIRST
import { renderHook, act } from '@testing-library/react';
import { useSRS } from '@/hooks/useSRS';

describe('useSRS', () => {
  it('should schedule next review based on answer quality', () => {
    // Arrange
    const { result } = renderHook(() => useSRS());
    const card = { id: '1', interval: 1, easeFactor: 2.5 };
    
    // Act
    act(() => {
      result.current.recordAnswer(card, 4); // Good answer
    });
    
    // Assert
    const nextReview = result.current.getNextReview(card.id);
    expect(nextReview.interval).toBeGreaterThan(1);
    expect(nextReview.easeFactor).toBeGreaterThanOrEqual(2.5);
  });
});

// hooks/useSRS.ts - IMPLEMENT AFTER TEST
export function useSRS() {
  // SRS implementation
  const recordAnswer = (card: Card, quality: number) => {
    // Calculate next review using SM-2 algorithm
  };
  
  return { recordAnswer, getNextReview };
}
```

### AI Prompt Engineering

**Located in:** `backend/app/prompts/`

All prompts are version-controlled, tested, and documented. Each prompt has:
1. Clear purpose and expected output
2. Example inputs and outputs
3. Regression tests to catch prompt drift

**Example: Conversation Correction Prompt**

```python
# backend/app/prompts/correction_prompts.py

CONVERSATION_CORRECTION_PROMPT = """
You are a patient Japanese language tutor helping a student practice conversation.
The student is at {proficiency_level} level and is learning Japanese for business communication.

Student's message: {user_input}

Your task:
1. Respond naturally to continue the conversation in Japanese
2. If there are grammar, vocabulary, or usage errors, gently correct them
3. Provide brief explanations for corrections in English
4. Encourage the student and maintain a positive tone
5. Keep corrections focused on one or two key issues, not overwhelming

Format your response as:
<response>Your conversational response in Japanese</response>
<correction>If applicable, explain the correction in English</correction>
<encouragement>Brief positive feedback</encouragement>

Context: {conversation_context}
"""

# tests/unit/test_correction_prompts.py - REGRESSION TESTS
def test_correction_prompt_identifies_particle_error():
    """Test that prompt catches に vs へ particle errors."""
    # Test with known error patterns
    result = apply_prompt(
        CONVERSATION_CORRECTION_PROMPT,
        user_input="私は学校に行きました",
        proficiency_level="N5"
    )
    
    assert "へ" in result["correction"]  # Should suggest へ for destination
    assert "に" in result["correction"]  # Should reference the error
```

---

## Environment Configuration

### Required Environment Variables

```bash
# API Keys (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-...           # Claude API for conversation
OPENAI_API_KEY=sk-...                  # Whisper API for speech-to-text
GOOGLE_CLOUD_TTS_KEY=...               # Google TTS for Japanese speech

# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nihongo_sensei
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=your-secret-key-here        # Generate with: openssl rand -hex 32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration (Customizable)
AI_CONVERSATION_MODEL=claude-sonnet-4-20250514
AI_CONVERSATION_BASE_URL=https://api.anthropic.com
AI_STT_MODEL=whisper-1
AI_STT_BASE_URL=https://api.openai.com
AI_TTS_MODEL=ja-JP-Neural2-B
AI_TTS_BASE_URL=https://texttospeech.googleapis.com

# Application Settings
ENVIRONMENT=development  # development, staging, production
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Content Generation
CONTENT_GENERATION_MODEL=claude-sonnet-4-20250514
ENABLE_CONTENT_CACHING=true
```

### Customizing AI Providers

Users can point to different AI providers by changing base URLs and models:

```bash
# Use Azure OpenAI instead
AI_CONVERSATION_BASE_URL=https://your-resource.openai.azure.com
AI_CONVERSATION_MODEL=your-deployment-name

# Use local Ollama for conversation
AI_CONVERSATION_BASE_URL=http://localhost:11434
AI_CONVERSATION_MODEL=llama3.1:70b
```

---

## Gotchas & Important Notes

### Critical Development Rules

1. **TESTS BEFORE CODE** - No exceptions. If you're not writing a test, you're doing it wrong.

2. **AI API Costs** - Every conversation costs money. Implement caching and rate limiting early:
   ```python
   # Cache common responses
   @cache(expire=3600)
   async def get_grammar_explanation(grammar_point: str):
       # Expensive AI call
   ```

3. **Japanese Text Encoding** - Always use UTF-8. Test with actual Japanese characters:
   ```python
   # Good test
   def test_kanji_storage():
       kanji = "日本語"
       # Actually test with real Japanese, not romanji
   ```

4. **SRS Algorithm Precision** - The spaced repetition algorithm is the heart of learning effectiveness. Test extensively:
   - Test with edge cases (perfect score, terrible score)
   - Test with long intervals (30+ days)
   - Test ease factor boundaries (1.3 to 2.5)

5. **Conversation Context Limits** - Claude has context limits. Implement conversation summarization:
   ```python
   # After 20 messages, summarize context
   if len(conversation_history) > 20:
       context_summary = await summarize_context(conversation_history)
   ```

6. **Speech Recognition Latency** - Whisper API can take 2-5 seconds. Provide user feedback:
   ```typescript
   // Show processing state immediately
   setProcessingState('transcribing');
   const result = await transcribeAudio(audioBlob);
   ```

7. **PWA Offline Support** - Cache essential resources but not AI responses:
   ```javascript
   // Service worker: Cache UI, not dynamic AI content
   const CACHE_STATIC = ['/', '/styles.css', '/flashcards'];
   const NO_CACHE = ['/api/conversation', '/api/speech'];
   ```

8. **Database Migration Safety** - ALWAYS test migrations with production-like data:
   ```bash
   # Create test database with realistic data size
   python scripts/create_test_db.py --users 1000 --cards 50000
   # Test migration
   alembic upgrade head
   # Verify data integrity
   pytest tests/test_migrations.py
   ```

9. **Kanji Stroke Order** - If implementing handwriting recognition, stroke order matters:
   ```python
   # Test stroke order validation
   def test_stroke_order_validation():
       strokes = [Stroke(...), Stroke(...)]
       is_valid = validate_stroke_order("水", strokes)
       assert is_valid
   ```

10. **Japanese IME Testing** - Test with actual Japanese IME input, not copy-paste:
    ```typescript
    // Test with composition events
    fireEvent.compositionStart(input);
    fireEvent.compositionUpdate(input, { data: 'みず' });
    fireEvent.compositionEnd(input, { data: '水' });
    ```

### Common Pitfalls to Avoid

- **Skipping Tests for "Simple" Features** - Simple features become complex. Test everything.
- **Over-Engineering Before MVP** - Build the simplest thing that works, with tests.
- **Ignoring Mobile Performance** - Test on actual low-end Android devices.
- **Not Planning for Scale** - Even self-hosted needs to handle 100+ users efficiently.
- **Assuming AI Consistency** - AI responses vary. Test with multiple runs.
- **Forgetting Accessibility** - Japanese learners may have diverse needs. Test with screen readers.

---

## Testing Best Practices for This Project

### Unit Tests
- **Focus:** Individual functions, utilities, algorithms
- **Speed:** Fast (<10ms per test)
- **Isolation:** No external dependencies (mock everything)
- **Coverage:** Aim for 100% of business logic

```python
# Example: SRS algorithm unit test
def test_ease_factor_decrease_on_poor_quality():
    """Ease factor decreases for quality < 3."""
    initial_ease = 2.5
    result = calculate_ease_factor(initial_ease, quality=2)
    assert result < 2.5
```

### Integration Tests
- **Focus:** API endpoints, database operations, service integration
- **Speed:** Medium (100-500ms per test)
- **Dependencies:** Real database (test DB), mocked AI APIs
- **Coverage:** All API endpoints, critical flows

```python
# Example: API integration test
@pytest.mark.asyncio
async def test_create_lesson_endpoint(client, db_session):
    """Test lesson creation with database."""
    payload = {"title": "Hiragana Basics", "level": "N5"}
    response = await client.post("/api/lessons", json=payload)
    assert response.status_code == 201
    
    # Verify in database
    lesson = await db_session.execute(
        select(Lesson).where(Lesson.title == "Hiragana Basics")
    )
    assert lesson.scalar_one() is not None
```

### End-to-End Tests
- **Focus:** Complete user journeys
- **Speed:** Slow (seconds per test)
- **Dependencies:** Full system running
- **Coverage:** Critical paths only (login → lesson → practice → progress)

```python
# Example: E2E user journey
@pytest.mark.e2e
async def test_complete_learning_session(browser):
    """Test complete learning session from login to completion."""
    # Login
    await browser.goto("http://localhost:3000/login")
    await browser.fill("#email", "test@example.com")
    await browser.fill("#password", "password123")
    await browser.click("button[type=submit]")
    
    # Start lesson
    await browser.goto("http://localhost:3000/lessons/hiragana-01")
    await browser.click("[data-testid=start-lesson]")
    
    # Complete flashcards
    for _ in range(5):
        await browser.click("[data-testid=show-answer]")
        await browser.click("[data-testid=rate-good]")
    
    # Verify progress updated
    await browser.goto("http://localhost:3000/progress")
    assert await browser.locator("text=Hiragana Basics").is_visible()
```

### AI Service Tests (Mocking Strategy)

```python
# Mock AI responses for consistent testing
@pytest.fixture
def mock_anthropic_response():
    return {
        "content": [{
            "text": "<response>それはいいですね！</response>"
                   "<correction>Use 'は' instead of 'が' here</correction>"
        }]
    }

def test_conversation_parsing(mock_anthropic_response):
    """Test parsing of AI conversation response."""
    result = parse_ai_response(mock_anthropic_response)
    assert result.response == "それはいいですね！"
    assert "は" in result.correction
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt
      
      - name: Run linting
        run: |
          ruff check backend/app
          black --check backend/app
      
      - name: Run tests with coverage
        run: |
          pytest backend/tests --cov=backend/app --cov-fail-under=85
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
        working-directory: frontend
      
      - name: Run linting
        run: npm run lint
        working-directory: frontend
      
      - name: Run tests with coverage
        run: npm test -- --coverage --watchAll=false
        working-directory: frontend
      
      - name: Check coverage threshold
        run: npm run test:coverage-check
        working-directory: frontend
```

---

## Quick Reference

### First-Time Setup Checklist

- [ ] Clone repository
- [ ] Install pre-commit hooks: `pre-commit install`
- [ ] Set up Python virtual environment
- [ ] Install backend dependencies
- [ ] Install frontend dependencies
- [ ] Start Docker containers (Postgres, Redis)
- [ ] Copy `.env.example` to `.env` and configure
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Import dictionary data: `python scripts/import_jmdict.py`
- [ ] **RUN ALL TESTS** to verify setup: `pytest && npm test`

### Daily Development Checklist

- [ ] Pull latest changes: `git pull`
- [ ] Activate virtual environment
- [ ] Start test watchers (backend and frontend)
- [ ] **WRITE FAILING TEST** for new feature
- [ ] Implement minimum code to pass
- [ ] See test turn green
- [ ] Refactor while keeping tests green
- [ ] Run full test suite before commit
- [ ] Push changes (pre-commit hooks will run)

### Before Every Commit

- [ ] All tests pass: `pytest && npm test`
- [ ] Coverage hasn't decreased: Check coverage reports
- [ ] Linting passes: `ruff check && npm run lint`
- [ ] Type checking passes: `mypy && npm run type-check`
- [ ] No commented-out code or debug statements
- [ ] Commit message follows convention: `feat:`, `fix:`, `test:`, etc.

### Before Every Pull Request

- [ ] Branch is up to date with main
- [ ] All CI checks pass on GitHub
- [ ] New code has ≥90% test coverage
- [ ] Integration tests pass
- [ ] No security vulnerabilities: `safety check && npm audit`
- [ ] Documentation updated if needed
- [ ] CHANGELOG.md updated

---

## Learning Resources

### For Developers

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Next.js Documentation:** https://nextjs.org/docs
- **Anthropic API Documentation:** https://docs.anthropic.com/
- **SuperMemo SM-2 Algorithm:** https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
- **Japanese NLP Resources:** JMDict, KANJIDIC2, Tatoeba

### For Japanese Language Learning

- **JLPT Levels:** https://www.jlpt.jp/e/about/levelsummary.html
- **Kanji Database:** https://www.kanjidatabase.com/
- **Grammar Resources:** https://guidetojapanese.org/
- **Business Japanese:** https://www.nhk.or.jp/lesson/en/

---

## Summary: TDD Culture for This Project

This is a **test-driven project**. That means:

1. **Tests are not an afterthought** - They are the first thought
2. **Tests are not optional** - They are mandatory
3. **Tests are not separate** - They are integral to development
4. **Tests are not someone else's job** - They are your job

**If you write code without tests, you are not contributing to this project correctly.**

The 15-25 month timeline assumes disciplined TDD from day one. Cutting corners on testing will not save time - it will cost time through bugs, rework, and technical debt.

Write tests. Make them pass. Refactor. Repeat. 🔄

---

**Last Updated:** 2025-11-19
**Project Status:** Pre-Development (Documentation Phase)
**Next Steps:** Review all documentation, approve technical approach, begin Phase 1 implementation
