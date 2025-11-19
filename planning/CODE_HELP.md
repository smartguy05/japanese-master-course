# Developer Guide - Nihongo Master

## Purpose

This document provides comprehensive technical guidance for developers and AI coding assistants (Claude Code, GitHub Copilot, Cursor, etc.) working on the Nihongo Master Japanese learning platform.

---

## 🚨 CRITICAL: TEST-DRIVEN DEVELOPMENT IS MANDATORY 🚨

**BEFORE writing ANY implementation code, you MUST:**

1. ✅ Write a failing test that describes the desired behavior
2. ✅ Run the test suite to confirm the new test fails  
3. ✅ Document the test in your commit/PR description

**THEN and ONLY THEN:**

4. ✅ Write the minimum code to make the test pass
5. ✅ Verify all tests pass
6. ✅ Refactor if needed while keeping tests green

**NO EXCEPTIONS. NO SHORTCUTS. NO "I'LL ADD TESTS LATER."**

---

## Quick Start for AI Assistants

### When Starting a New Task

1. **Understand the requirement** - Read the task description carefully
2. **Write the test FIRST** - Even before looking at implementation files
3. **Run tests to see failure** - Confirm RED state
4. **Implement minimum code** - Get to GREEN state
5. **Refactor** - Improve while staying GREEN
6. **Commit with test** - Tests and implementation together

### Test-First Example: Adding SRS Feature

**WRONG Approach:**
```python
# ❌ DON'T DO THIS - Writing implementation first
def calculate_next_review_date(card, answer_quality):
    # Implementation code...
    pass

# Writing test after (or worse, not at all)
def test_calculate_next_review_date():
    pass
```

**CORRECT Approach:**
```python
# ✅ DO THIS - Write test FIRST
def test_calculate_next_review_date_for_correct_answer():
    """GIVEN a card with 2 previous correct reviews
    WHEN user answers correctly (quality >= 3)
    THEN next review should be scheduled 6 days from now"""
    # Arrange
    card = Card(
        interval_days=3,
        correct_count=2,
        last_review=datetime.now()
    )
    
    # Act
    next_date = calculate_next_review_date(card, answer_quality=4)
    
    # Assert
    expected_date = datetime.now() + timedelta(days=6)
    assert next_date.date() == expected_date.date()

# Run test - it FAILS (function doesn't exist)
# NOW write the implementation
def calculate_next_review_date(card, answer_quality):
    if answer_quality >= 3:
        new_interval = int(card.interval_days * 2.0)
        return datetime.now() + timedelta(days=new_interval)
    else:
        return datetime.now() + timedelta(days=1)

# Run test again - it PASSES
# Refactor if needed
```

---

## Project Structure

```
nihongo-master/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/v1/            # API routes (versioned)
│   │   ├── core/              # Core business logic
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # External service integrations
│   │   ├── db/                # Database configuration
│   │   └── main.py            # FastAPI app entry point
│   └── tests/                 # Test files (mirrors app/ structure)
│
├── frontend/                  # Next.js 14 frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router (pages)
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utility functions
│   │   ├── services/          # API client services
│   │   └── __tests__/         # Test files
│   └── public/                # Static assets
│
├── content/                   # Content database (JSON/YAML)
│   ├── lessons/               # Lesson content by JLPT level
│   ├── prompts/               # AI prompt templates
│   └── grammar/               # Grammar explanations
│
├── docker/                    # Docker configuration
└── docs/                      # Project documentation
```

---

## Development Environment Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (for production deployment)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests (ALWAYS before committing)
pytest
pytest --cov=app --cov-report=html
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Setup environment variables
cp .env.local.example .env.local
# Edit .env.local with API URLs

# Start development server
npm run dev  # Runs on http://localhost:3000

# Run tests (ALWAYS before committing)
npm test
npm run test:coverage
npm run test:e2e
```

### Running Full Stack with Docker

```bash
# From project root
docker compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

## Testing Strategy

### Test Pyramid

```
           /\
          /  \    E2E Tests (5%)
         /    \   - Critical user journeys
        /------\  
       /        \ Integration Tests (20%)
      /          \ - API endpoints
     /            \- Component integration
    /--------------\
   /                \ Unit Tests (75%)
  /                  \ - Business logic
 /____________________\- Utilities
                        - Components
```

### Backend Testing (pytest)

**Test Organization:**
```
tests/
├── unit/                      # Pure logic tests
│   ├── test_srs_algorithm.py
│   ├── test_conversation.py
│   └── test_utils.py
├── integration/               # Database + service tests
│   ├── test_database.py
│   └── test_ai_services.py
├── api/                       # API endpoint tests
│   ├── test_auth.py
│   ├── test_flashcards.py
│   └── test_conversation.py
├── conftest.py                # Shared fixtures
└── factories.py               # Test data factories
```

**Running Tests:**
```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_srs_algorithm.py -v

# Specific test function
pytest tests/unit/test_srs_algorithm.py::test_calculates_interval -v

# Tests matching pattern
pytest -k "conversation" -v

# With coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Last failed tests only
pytest --lf

# Stop on first failure
pytest -x
```

**Test Fixtures (conftest.py):**
```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db.base import Base

@pytest.fixture
async def db_session():
    """Provide clean database session for each test"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def mock_claude_api(monkeypatch):
    """Mock Anthropic Claude API calls"""
    async def mock_generate(*args, **kwargs):
        return "こんにちは！元気ですか？"
    
    monkeypatch.setattr(
        "app.services.claude.ClaudeClient.generate",
        mock_generate
    )
    return mock_generate
```

**Test Data Factories:**
```python
# tests/factories.py
from datetime import datetime, timedelta
from app.models import Card, User

def create_user(**overrides):
    """Create test user with sensible defaults"""
    defaults = {
        "email": "test@example.com",
        "username": "testuser",
        "japanese_level": "n5"
    }
    defaults.update(overrides)
    return User(**defaults)

def create_card(**overrides):
    """Create test flashcard"""
    defaults = {
        "japanese": "こんにちは",
        "romanji": "konnichiwa",
        "english": "hello",
        "interval_days": 1,
        "next_review": datetime.now(),
        "correct_count": 0
    }
    defaults.update(overrides)
    return Card(**defaults)
```

### Frontend Testing (Vitest + React Testing Library)

**Test Organization:**
```
src/__tests__/
├── unit/                      # Component unit tests
│   ├── Flashcard.test.tsx
│   ├── ProgressBar.test.tsx
│   └── hooks/
│       └── useSRS.test.ts
├── integration/               # Multi-component tests
│   ├── ConversationFlow.test.tsx
│   └── StudySession.test.tsx
└── e2e/                       # End-to-end tests (Playwright)
    ├── auth.spec.ts
    ├── conversation.spec.ts
    └── study-flow.spec.ts
```

**Running Tests:**
```bash
# All tests
npm test

# Watch mode
npm test -- --watch

# Specific file
npm test -- Flashcard.test.tsx

# With coverage
npm run test:coverage

# E2E tests
npm run test:e2e

# E2E with UI
npm run test:e2e -- --ui
```

**Component Testing Example:**
```typescript
// components/Flashcard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Flashcard } from './Flashcard';

describe('Flashcard', () => {
  it('displays Japanese text on initial render', () => {
    const card = {
      id: '1',
      japanese: 'こんにちは',
      english: 'Hello',
      romanji: 'konnichiwa'
    };
    
    render(<Flashcard card={card} />);
    
    expect(screen.getByText('こんにちは')).toBeInTheDocument();
    expect(screen.queryByText('Hello')).not.toBeInTheDocument();
  });
  
  it('flips to show English when clicked', () => {
    const card = {
      id: '1',
      japanese: 'こんにちは',
      english: 'Hello',
      romanji: 'konnichiwa'
    };
    
    render(<Flashcard card={card} />);
    
    const cardElement = screen.getByTestId('flashcard');
    fireEvent.click(cardElement);
    
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.queryByText('こんにちは')).not.toBeInTheDocument();
  });
  
  it('calls onAnswer when answer button clicked', () => {
    const mockOnAnswer = vi.fn();
    const card = { id: '1', japanese: 'こんにちは', english: 'Hello' };
    
    render(<Flashcard card={card} onAnswer={mockOnAnswer} />);
    
    fireEvent.click(screen.getByTestId('flashcard')); // Flip to back
    fireEvent.click(screen.getByText('I knew it!'));
    
    expect(mockOnAnswer).toHaveBeenCalledWith('correct');
  });
});
```

**Hook Testing Example:**
```typescript
// hooks/useSRS.test.ts
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useSRS } from './useSRS';

describe('useSRS', () => {
  it('initializes with due cards', async () => {
    const { result } = renderHook(() => useSRS());
    
    await act(async () => {
      await result.current.fetchDueCards();
    });
    
    expect(result.current.dueCards.length).toBeGreaterThan(0);
    expect(result.current.isLoading).toBe(false);
  });
  
  it('updates next review date when card answered correctly', async () => {
    const { result } = renderHook(() => useSRS());
    
    await act(async () => {
      await result.current.answerCard('card-123', 'correct');
    });
    
    const card = result.current.dueCards.find(c => c.id === 'card-123');
    expect(card).toBeUndefined(); // Card removed from due list
  });
});
```

---

## Common Development Tasks

### Creating a New API Endpoint

**1. Write the test FIRST:**
```python
# tests/api/test_flashcards.py
async def test_create_flashcard_returns_201(client, db_session):
    """GIVEN valid flashcard data
    WHEN POST /api/v1/flashcards
    THEN should return 201 with created flashcard"""
    
    flashcard_data = {
        "japanese": "ありがとう",
        "romanji": "arigatou",
        "english": "thank you"
    }
    
    response = await client.post("/api/v1/flashcards", json=flashcard_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["japanese"] == "ありがとう"
    assert "id" in data
```

**2. Run test - see it FAIL:**
```bash
pytest tests/api/test_flashcards.py::test_create_flashcard_returns_201 -v
# FAILED - Route not found
```

**3. Implement the endpoint:**
```python
# app/api/v1/flashcards.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.flashcard import FlashcardCreate, FlashcardResponse
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/flashcards", tags=["flashcards"])

@router.post("/", response_model=FlashcardResponse, status_code=201)
async def create_flashcard(
    flashcard: FlashcardCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new flashcard"""
    new_card = Card(**flashcard.model_dump())
    db.add(new_card)
    await db.commit()
    await db.refresh(new_card)
    return new_card
```

**4. Run test again - it PASSES:**
```bash
pytest tests/api/test_flashcards.py::test_create_flashcard_returns_201 -v
# PASSED ✓
```

**5. Refactor if needed, tests stay green**

---

### Adding a New React Component

**1. Write the test FIRST:**
```typescript
// components/ProgressBar.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ProgressBar } from './ProgressBar';

describe('ProgressBar', () => {
  it('displays correct percentage', () => {
    render(<ProgressBar current={30} total={100} />);
    expect(screen.getByText('30%')).toBeInTheDocument();
  });
  
  it('shows visual progress bar filled to percentage', () => {
    render(<ProgressBar current={75} total={100} />);
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toHaveStyle({ width: '75%' });
  });
});
```

**2. Run test - see it FAIL:**
```bash
npm test -- ProgressBar.test.tsx
# FAILED - Module not found
```

**3. Implement the component:**
```typescript
// components/ProgressBar.tsx
interface ProgressBarProps {
  current: number;
  total: number;
}

export function ProgressBar({ current, total }: ProgressBarProps) {
  const percentage = Math.round((current / total) * 100);
  
  return (
    <div className="w-full bg-gray-200 rounded-full h-4">
      <div 
        role="progressbar"
        aria-valuenow={percentage}
        aria-valuemin={0}
        aria-valuemax={100}
        className="bg-blue-600 h-4 rounded-full transition-all"
        style={{ width: `${percentage}%` }}
      >
        <span className="text-xs text-white font-semibold px-2">
          {percentage}%
        </span>
      </div>
    </div>
  );
}
```

**4. Run test - it PASSES**
**5. Refactor styling, add animations, etc.**

---

### Implementing SRS Algorithm Logic

**1. Write tests FIRST (multiple test cases):**
```python
# tests/unit/test_srs_algorithm.py
import pytest
from datetime import datetime, timedelta
from app.core.srs import calculate_next_interval, calculate_next_review

def test_first_review_correct_returns_1_day():
    """GIVEN a new card answered correctly
    WHEN calculating next interval
    THEN should return 1 day"""
    assert calculate_next_interval(
        current_interval=0,
        correct_count=0,
        answer_quality=4
    ) == 1

def test_second_review_correct_returns_3_days():
    """GIVEN a card reviewed once, answered correctly again
    WHEN calculating next interval  
    THEN should return 3 days"""
    assert calculate_next_interval(
        current_interval=1,
        correct_count=1,
        answer_quality=4
    ) == 3

def test_third_review_correct_returns_6_days():
    """GIVEN a card reviewed twice, answered correctly again
    WHEN calculating next interval
    THEN should return 6 days"""
    assert calculate_next_interval(
        current_interval=3,
        correct_count=2,
        answer_quality=4
    ) == 6

def test_incorrect_answer_resets_to_1_day():
    """GIVEN any card answered incorrectly
    WHEN calculating next interval
    THEN should reset to 1 day"""
    assert calculate_next_interval(
        current_interval=10,
        correct_count=5,
        answer_quality=1
    ) == 1

def test_easy_answer_multiplies_by_2_5():
    """GIVEN easy answer (quality 5)
    WHEN calculating next interval
    THEN should multiply current interval by 2.5"""
    assert calculate_next_interval(
        current_interval=4,
        correct_count=3,
        answer_quality=5
    ) == 10  # 4 * 2.5
```

**2. Run tests - all FAIL**

**3. Implement algorithm:**
```python
# app/core/srs.py
def calculate_next_interval(
    current_interval: int,
    correct_count: int,
    answer_quality: int
) -> int:
    """Calculate next review interval using SuperMemo SM-2 algorithm
    
    Args:
        current_interval: Current interval in days (0 for new cards)
        correct_count: Number of times answered correctly in a row
        answer_quality: Quality of answer (1=wrong, 3=hard, 4=good, 5=easy)
        
    Returns:
        Next interval in days
    """
    # Wrong answer - reset
    if answer_quality < 3:
        return 1
    
    # First review
    if correct_count == 0:
        return 1
    
    # Second review
    if correct_count == 1:
        return 3
    
    # Subsequent reviews
    multiplier = 2.5 if answer_quality == 5 else 2.0
    return int(current_interval * multiplier)

def calculate_next_review(
    last_review: datetime,
    interval_days: int
) -> datetime:
    """Calculate next review datetime"""
    return last_review + timedelta(days=interval_days)
```

**4. Run tests - all PASS**
**5. Refactor, add edge cases, optimize**

---

## Database Patterns

### Creating Models

**1. Write migration test FIRST:**
```python
# tests/test_migrations.py
def test_card_model_has_required_fields(db_session):
    """GIVEN Card model
    WHEN creating a card
    THEN should have all required fields"""
    card = Card(
        japanese="テスト",
        english="test",
        romanji="tesuto"
    )
    assert card.japanese is not None
    assert card.interval_days == 1  # Default value
```

**2. Create SQLAlchemy model:**
```python
# app/models/card.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class Card(Base):
    __tablename__ = "cards"
    
    id = Column(Integer, primary_key=True, index=True)
    japanese = Column(String, nullable=False)
    english = Column(String, nullable=False)
    romanji = Column(String, nullable=False)
    
    # SRS fields
    interval_days = Column(Integer, default=1, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)
    next_review = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_review = Column(DateTime)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="cards")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**3. Create Pydantic schemas:**
```python
# app/schemas/card.py
from pydantic import BaseModel, Field
from datetime import datetime

class CardBase(BaseModel):
    japanese: str = Field(..., min_length=1, max_length=200)
    english: str = Field(..., min_length=1, max_length=200)
    romanji: str = Field(..., min_length=1, max_length=200)

class CardCreate(CardBase):
    pass

class CardResponse(CardBase):
    id: int
    interval_days: int
    correct_count: int
    next_review: datetime
    
    class Config:
        from_attributes = True
```

**4. Generate migration:**
```bash
alembic revision --autogenerate -m "Add cards table"
# Review generated migration in alembic/versions/
alembic upgrade head
```

---

## AI Integration Patterns

### Calling Claude API

**1. Write test with mocked API FIRST:**
```python
# tests/integration/test_claude_service.py
async def test_generate_conversation_response(mock_claude_api):
    """GIVEN user message in Japanese
    WHEN generating AI response
    THEN should return appropriate Japanese reply"""
    
    service = ConversationService()
    response = await service.generate_response(
        user_message="今日は天気がいいですね。",
        user_level="n5",
        conversation_history=[]
    )
    
    assert isinstance(response, str)
    assert len(response) > 0
    # Basic validation that it's Japanese text
    assert any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' 
               for char in response)
```

**2. Implement service:**
```python
# app/services/conversation.py
from anthropic import AsyncAnthropic
from app.core.config import settings

class ConversationService:
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
    
    async def generate_response(
        self,
        user_message: str,
        user_level: str,
        conversation_history: list[dict]
    ) -> str:
        """Generate conversation response using Claude
        
        TESTING: This method should be mocked in most tests
        Integration tests verify the actual API contract
        """
        system_prompt = self._build_system_prompt(user_level)
        messages = self._format_conversation(conversation_history, user_message)
        
        response = await self.client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=500,
            system=system_prompt,
            messages=messages
        )
        
        return response.content[0].text
    
    def _build_system_prompt(self, user_level: str) -> str:
        """Build system prompt based on user level"""
        prompts = {
            "n5": "You are a patient Japanese tutor. Use simple Japanese...",
            "n4": "You are a Japanese tutor. Use intermediate Japanese...",
            # etc.
        }
        return prompts.get(user_level, prompts["n5"])
```

**3. Use in API endpoint:**
```python
# app/api/v1/conversation.py
@router.post("/message")
async def send_message(
    message: ConversationMessage,
    current_user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service)
):
    """Send message and get AI response"""
    response_text = await service.generate_response(
        user_message=message.text,
        user_level=current_user.japanese_level,
        conversation_history=await get_user_history(current_user.id)
    )
    
    # Save to database
    await save_conversation(current_user.id, message.text, response_text)
    
    return {"response": response_text}
```

---

## Content Generation with AI

### Prompt Engineering Patterns

**Location:** `content/prompts/lesson_generation.txt`

**Prompt Structure:**
```yaml
name: generate_vocabulary_lesson
version: 1.0
description: Generate vocabulary lesson for specific topic and JLPT level

system_prompt: |
  You are an expert Japanese language instructor creating lesson content.
  
  REQUIREMENTS:
  - All content must be appropriate for {jlpt_level}
  - Include exactly {num_words} vocabulary words
  - Each word must have: kanji (if applicable), hiragana, romanji, English
  - Provide 2 example sentences per word
  - All kanji must include furigana
  
  QUALITY STANDARDS:
  - Natural, conversational Japanese (not textbook stiff)
  - Culturally appropriate examples
  - Practical, useful vocabulary
  - Clear, accurate English translations
  
  OUTPUT FORMAT:
  Return valid JSON matching this schema:
  {
    "topic": "string",
    "level": "n5|n4|n3|n2",
    "vocabulary": [
      {
        "kanji": "string or null",
        "hiragana": "string",
        "romanji": "string",
        "english": "string",
        "part_of_speech": "noun|verb|adjective|adverb|particle",
        "examples": [
          {
            "japanese": "string (with furigana in parentheses)",
            "romanji": "string",
            "english": "string"
          }
        ]
      }
    ]
  }

user_prompt_template: |
  Create a vocabulary lesson on the topic: "{topic}"
  JLPT Level: {jlpt_level}
  Number of words: {num_words}
  
  Focus areas: {focus_areas}
```

**Usage in Code:**
```python
# app/services/content_generation.py
async def generate_vocabulary_lesson(
    topic: str,
    jlpt_level: str,
    num_words: int = 10
) -> dict:
    """Generate vocabulary lesson using AI
    
    TESTING: Mock this in most tests, validate output schema
    """
    prompt_template = load_prompt("generate_vocabulary_lesson")
    
    response = await claude_client.generate(
        system=prompt_template["system_prompt"].format(
            jlpt_level=jlpt_level,
            num_words=num_words
        ),
        user=prompt_template["user_prompt_template"].format(
            topic=topic,
            jlpt_level=jlpt_level,
            num_words=num_words,
            focus_areas="practical conversation"
        )
    )
    
    # Validate output matches schema
    lesson_data = json.loads(response)
    return VocabularyLessonSchema.model_validate(lesson_data)
```

---

## Error Handling Patterns

### Backend Error Handling

```python
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

# Custom exceptions
class CardNotFoundError(Exception):
    pass

class AIServiceError(Exception):
    pass

# Error handlers
@app.exception_handler(CardNotFoundError)
async def card_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Flashcard not found"}
    )

# In route handlers
@router.get("/cards/{card_id}")
async def get_card(card_id: int, db: AsyncSession = Depends(get_db)):
    card = await db.get(Card, card_id)
    if not card:
        raise HTTPException(
            status_code=404,
            detail=f"Card {card_id} not found"
        )
    return card

# Service layer error handling
async def generate_ai_response(message: str) -> str:
    try:
        response = await claude_client.generate(message)
        return response
    except anthropic.RateLimitError:
        raise AIServiceError("Rate limit exceeded. Please try again later.")
    except anthropic.APIError as e:
        raise AIServiceError(f"AI service error: {str(e)}")
```

### Frontend Error Handling

```typescript
// services/api.ts
export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public details?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function fetchWithError<T>(url: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new APIError(
        error.detail || 'Request failed',
        response.status,
        error
      );
    }
    
    return response.json();
  } catch (error) {
    if (error instanceof APIError) throw error;
    throw new APIError('Network error', 0, error);
  }
}

// In components - use error boundaries
export function ConversationPage() {
  const { data, error, isLoading } = useQuery({
    queryKey: ['conversation'],
    queryFn: () => fetchWithError('/api/v1/conversation'),
    retry: 3,
    retryDelay: 1000,
  });
  
  if (error) {
    return <ErrorMessage error={error} />;
  }
  
  // Render component
}
```

---

## Performance Guidelines

### Backend Performance

```python
# Use async/await consistently
async def get_due_cards(user_id: int, db: AsyncSession):
    """Get cards due for review - MUST be async"""
    result = await db.execute(
        select(Card)
        .where(Card.user_id == user_id)
        .where(Card.next_review <= datetime.now())
        .limit(20)
    )
    return result.scalars().all()

# Eager load relationships to avoid N+1 queries
async def get_lessons_with_cards(user_id: int, db: AsyncSession):
    """Eager load related data"""
    result = await db.execute(
        select(Lesson)
        .options(selectinload(Lesson.cards))
        .where(Lesson.user_id == user_id)
    )
    return result.scalars().all()

# Use Redis caching for expensive operations
@cache(expire=3600)  # Cache for 1 hour
async def get_kanji_information(kanji: str) -> dict:
    """Expensive operation - cache results"""
    # Complex processing...
    return result

# Paginate large result sets
async def list_vocabulary(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Vocabulary)
        .offset(skip)
        .limit(min(limit, 100))  # Max 100 items
    )
    return result.scalars().all()
```

### Frontend Performance

```typescript
// Use React Server Components by default
export default async function LessonsPage() {
  const lessons = await getLessons(); // Fetched on server
  return <LessonsList lessons={lessons} />;
}

// Client components only when needed
'use client';
export function InteractiveFlashcard() {
  const [flipped, setFlipped] = useState(false);
  // Interactive logic
}

// Memoize expensive computations
const sortedCards = useMemo(() => {
  return cards.sort((a, b) => a.nextReview - b.nextReview);
}, [cards]);

// Debounce user input
const debouncedSearch = useDebouncedCallback(
  (value: string) => setSearchQuery(value),
  300
);

// Lazy load heavy components
const ConversationUI = lazy(() => import('./ConversationUI'));

// Optimize images
<Image
  src="/kanji/kanji-123.png"
  width={100}
  height={100}
  alt="Kanji character"
  loading="lazy"
/>
```

---

## Security Checklist

### Before Committing Code

- [ ] No API keys or secrets in code
- [ ] All user input validated
- [ ] SQL injection prevented (using ORM)
- [ ] XSS prevented (React auto-escapes)
- [ ] Authentication required on protected routes
- [ ] Authorization checked for user-owned resources
- [ ] Rate limiting configured
- [ ] HTTPS enforced in production
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies checked for vulnerabilities

### Security Testing

```python
# Test authentication required
async def test_protected_route_requires_auth(client):
    """GIVEN no authentication
    WHEN accessing protected route
    THEN should return 401"""
    response = await client.get("/api/v1/profile")
    assert response.status_code == 401

# Test authorization for resources
async def test_cannot_access_other_user_cards(client, auth_user):
    """GIVEN authenticated user
    WHEN accessing another user's cards
    THEN should return 403"""
    other_user_card_id = 999
    response = await client.get(f"/api/v1/cards/{other_user_card_id}")
    assert response.status_code == 403

# Test input validation
async def test_rejects_invalid_email(client):
    """GIVEN invalid email format
    WHEN creating user
    THEN should return 422"""
    response = await client.post("/api/v1/users", json={
        "email": "not-an-email",
        "password": "secure123"
    })
    assert response.status_code == 422
```

---

## Git Workflow

### Commit Messages

Follow conventional commits:

```bash
# Good commit messages
git commit -m "feat: add SRS interval calculation"
git commit -m "test: add tests for flashcard API"
git commit -m "fix: correct timezone handling in review dates"
git commit -m "docs: update API documentation"
git commit -m "refactor: extract conversation service"

# Types: feat, fix, docs, test, refactor, style, chore
```

### Pull Request Checklist

Before creating PR:

- [ ] All tests pass (`pytest && npm test`)
- [ ] Test coverage hasn't decreased
- [ ] Code is formatted (`black . && prettier --write .`)
- [ ] Linting passes (`ruff check . && eslint .`)
- [ ] Type checking passes (`mypy app && tsc --noEmit`)
- [ ] No console.log or print statements left
- [ ] Documentation updated if needed
- [ ] Migration created if schema changed
- [ ] CHANGELOG.md updated

---

## Troubleshooting

### Common Issues

**Backend:**

```bash
# Database connection fails
# Check: PostgreSQL is running, .env has correct credentials
docker compose ps postgres

# Alembic migration fails
# Check: No conflicting migrations, database is accessible
alembic current
alembic history

# Tests fail with "event loop is closed"
# Use pytest-asyncio, mark tests with @pytest.mark.asyncio

# Import errors
# Check: Virtual environment activated, dependencies installed
which python
pip list
```

**Frontend:**

```bash
# "Cannot find module" errors
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Type errors in tests
# Check: @testing-library/react types installed
npm install -D @types/testing-library__react

# Build fails
# Check: Environment variables for production build
cat .env.local

# Hydration errors (React)
# Check: No <div> in <p>, consistent server/client rendering
```

---

## Performance Monitoring

### Key Metrics to Track

**Backend:**
- API response times (avg, p95, p99)
- Database query times
- AI API latency
- Error rates
- Memory usage
- Active connections

**Frontend:**
- Time to First Byte (TTFB)
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Time to Interactive (TTI)
- Client-side errors
- Bundle sizes

---

## Additional Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [React Testing Library](https://testing-library.com/react)
- [Anthropic API](https://docs.anthropic.com/)

### Internal Docs
- See `docs/ARCHITECTURE.md` for system design
- See `docs/TESTING.md` for testing strategy
- See `docs/DEPLOYMENT.md` for deployment guide
- See `docs/SECURITY.md` for security guidelines

---

**Remember: Tests first, always. No exceptions.**

**Last Updated:** Initial creation
