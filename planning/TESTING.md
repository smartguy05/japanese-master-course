# Testing Strategy - Nihongo Master

## Testing Philosophy

**"Tests first, always. No exceptions."**

Nihongo Master follows a strict Test-Driven Development (TDD) approach for all code. This document outlines our testing strategy, requirements, and best practices.

---

## 🚨 MANDATORY TDD WORKFLOW 🚨

### The Sacred Red-Green-Refactor Cycle

```
1. RED:    Write a failing test
2. GREEN:  Write minimum code to pass
3. REFACTOR: Improve code while staying green
4. REPEAT: Continue for next feature
```

**This is not negotiable.** Every line of production code must be justified by a failing test first.

---

## Test Coverage Requirements

### Minimum Coverage Targets

| Component | Target | Critical Paths |
|-----------|--------|----------------|
| Backend Overall | 90% | 100% |
| Core Business Logic | 100% | N/A |
| API Endpoints | 95% | 100% |
| Database Models | 90% | N/A |
| Frontend Overall | 85% | 95% |
| React Components | 90% | 95% |
| Custom Hooks | 95% | 100% |
| API Services | 90% | 100% |

**Critical Paths Include:**
- SRS algorithm (business-critical)
- Authentication & authorization
- Data persistence (user progress)
- AI service integration
- Payment processing (if added)

### Coverage Enforcement

**Pre-commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running tests..."
cd backend && pytest --cov=app --cov-fail-under=90 || exit 1
cd ../frontend && npm test -- --coverage --coverageThreshold='{"global":{"statements":85}}' || exit 1

echo "✅ All tests passed with sufficient coverage"
```

**CI/CD Gate:**
- Pull requests require 100% test pass rate
- Coverage must not decrease from target branch
- Failed builds block merges

---

## Test Pyramid Structure

```
           /\
          /  \    E2E Tests (5%)
         /    \   ~50 tests
        /------\   Critical user journeys
       /        \  
      /          \ Integration Tests (20%)
     /            \ ~200 tests
    /              \ API + Database + Services
   /----------------\
  /                  \ Unit Tests (75%)
 /____________________\ ~750 tests
                        Pure logic + Components
```

### Test Distribution by Phase

**Phase 1 (MVP):**
- Unit tests: ~150
- Integration tests: ~40
- E2E tests: ~10
- **Total: ~200 tests**

**Phase 5 (Complete):**
- Unit tests: ~750
- Integration tests: ~200
- E2E tests: ~50
- **Total: ~1000 tests**

---

## Backend Testing (Python/pytest)

### Test Organization

```
backend/tests/
├── unit/                          # Pure logic, no external dependencies
│   ├── test_srs_algorithm.py     # SRS calculation logic
│   ├── test_conversation_logic.py
│   ├── test_validators.py
│   └── test_utils.py
│
├── integration/                   # Multiple components working together
│   ├── test_database.py          # Database operations
│   ├── test_ai_services.py       # AI service integration (mocked)
│   ├── test_redis_cache.py
│   └── test_content_loading.py
│
├── api/                           # HTTP endpoint testing
│   ├── test_auth.py              # Authentication endpoints
│   ├── test_flashcards.py
│   ├── test_conversation.py
│   ├── test_lessons.py
│   ├── test_progress.py
│   └── test_speech.py
│
├── conftest.py                    # Shared pytest fixtures
├── factories.py                   # Test data factories
└── fixtures/                      # Test data files
    ├── sample_lessons.json
    └── test_audio.wav
```

### Unit Test Examples

**Testing SRS Algorithm (Pure Logic):**

```python
# tests/unit/test_srs_algorithm.py
import pytest
from datetime import datetime, timedelta
from app.core.srs import calculate_next_interval, calculate_ease_factor

class TestSRSAlgorithm:
    """Test suite for Spaced Repetition System algorithm"""
    
    def test_first_correct_answer_returns_1_day(self):
        """GIVEN a new card (0 correct reviews)
        WHEN answered correctly
        THEN next interval should be 1 day"""
        interval = calculate_next_interval(
            current_interval=0,
            correct_count=0,
            answer_quality=4,
            ease_factor=2.5
        )
        assert interval == 1
    
    def test_second_correct_answer_returns_3_days(self):
        """GIVEN a card with 1 correct review
        WHEN answered correctly again
        THEN next interval should be 3 days"""
        interval = calculate_next_interval(
            current_interval=1,
            correct_count=1,
            answer_quality=4,
            ease_factor=2.5
        )
        assert interval == 3
    
    def test_incorrect_answer_resets_interval_to_1(self):
        """GIVEN any card
        WHEN answered incorrectly
        THEN interval should reset to 1 day"""
        interval = calculate_next_interval(
            current_interval=30,
            correct_count=10,
            answer_quality=1,
            ease_factor=2.5
        )
        assert interval == 1
    
    @pytest.mark.parametrize("current,quality,expected", [
        (1, 5, 3),   # Easy: 1 * 2.5 = 2.5 → 3
        (3, 5, 8),   # Easy: 3 * 2.5 = 7.5 → 8
        (10, 5, 25), # Easy: 10 * 2.5 = 25
    ])
    def test_easy_answer_multiplies_by_2_5(self, current, quality, expected):
        """GIVEN various intervals
        WHEN answered as 'easy' (quality 5)
        THEN should multiply by 2.5"""
        interval = calculate_next_interval(
            current_interval=current,
            correct_count=5,
            answer_quality=quality,
            ease_factor=2.5
        )
        assert interval == expected
    
    def test_ease_factor_decreases_after_difficult_answer(self):
        """GIVEN a card with default ease factor (2.5)
        WHEN answered as 'hard' (quality 2)
        THEN ease factor should decrease"""
        new_ease = calculate_ease_factor(
            current_ease=2.5,
            answer_quality=2
        )
        assert new_ease < 2.5
        assert new_ease >= 1.3  # Minimum ease factor
    
    def test_ease_factor_increases_after_easy_answer(self):
        """GIVEN a card with default ease factor
        WHEN answered as 'easy' (quality 5)
        THEN ease factor should increase"""
        new_ease = calculate_ease_factor(
            current_ease=2.5,
            answer_quality=5
        )
        assert new_ease > 2.5
```

**Testing Input Validation:**

```python
# tests/unit/test_validators.py
import pytest
from app.core.validators import validate_japanese_text, validate_email

class TestValidators:
    def test_validates_japanese_hiragana(self):
        """GIVEN valid hiragana text
        WHEN validating
        THEN should return True"""
        assert validate_japanese_text("こんにちは") is True
    
    def test_validates_japanese_katakana(self):
        """GIVEN valid katakana text
        WHEN validating
        THEN should return True"""
        assert validate_japanese_text("コンピューター") is True
    
    def test_validates_japanese_kanji(self):
        """GIVEN text with kanji
        WHEN validating
        THEN should return True"""
        assert validate_japanese_text("日本語") is True
    
    def test_rejects_only_english(self):
        """GIVEN only English text
        WHEN validating as Japanese
        THEN should return False"""
        assert validate_japanese_text("hello") is False
    
    @pytest.mark.parametrize("email,expected", [
        ("valid@example.com", True),
        ("user+tag@domain.co.uk", True),
        ("invalid.com", False),
        ("@example.com", False),
        ("user@", False),
    ])
    def test_email_validation(self, email, expected):
        """Test email validation with various formats"""
        assert validate_email(email) == expected
```

### Integration Test Examples

**Testing Database Operations:**

```python
# tests/integration/test_database.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Card
from app.services.flashcard import FlashcardService

@pytest.mark.asyncio
class TestDatabaseOperations:
    async def test_create_user_persists_to_database(self, db_session: AsyncSession):
        """GIVEN valid user data
        WHEN creating a user
        THEN user should be persisted and retrievable"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password"
        )
        
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
    
    async def test_create_card_with_user_relationship(self, db_session: AsyncSession):
        """GIVEN a user exists
        WHEN creating a card for that user
        THEN card should have correct user relationship"""
        # Create user
        user = User(email="test@example.com", username="testuser")
        db_session.add(user)
        await db_session.commit()
        
        # Create card
        card = Card(
            user_id=user.id,
            japanese="こんにちは",
            romanji="konnichiwa",
            english="hello"
        )
        db_session.add(card)
        await db_session.commit()
        await db_session.refresh(card)
        
        assert card.user_id == user.id
        assert card.user.email == "test@example.com"
    
    async def test_cascade_delete_removes_user_cards(self, db_session: AsyncSession):
        """GIVEN a user with cards
        WHEN deleting the user
        THEN all user's cards should be deleted"""
        # Create user with cards
        user = User(email="test@example.com", username="testuser")
        db_session.add(user)
        await db_session.commit()
        
        card1 = Card(user_id=user.id, japanese="test1", english="test1")
        card2 = Card(user_id=user.id, japanese="test2", english="test2")
        db_session.add_all([card1, card2])
        await db_session.commit()
        
        # Delete user
        await db_session.delete(user)
        await db_session.commit()
        
        # Check cards are gone
        result = await db_session.execute(
            select(Card).where(Card.user_id == user.id)
        )
        assert result.scalars().all() == []
```

**Testing AI Service Integration (Mocked):**

```python
# tests/integration/test_ai_services.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.conversation import ConversationService

@pytest.mark.asyncio
class TestAIServiceIntegration:
    async def test_conversation_service_calls_claude_api(self, mock_claude_client):
        """GIVEN a conversation service
        WHEN generating a response
        THEN should call Claude API with correct parameters"""
        mock_claude_client.messages.create = AsyncMock(
            return_value={"content": [{"text": "こんにちは！"}]}
        )
        
        service = ConversationService(claude_client=mock_claude_client)
        response = await service.generate_response(
            user_message="Hello",
            user_level="n5",
            conversation_history=[]
        )
        
        assert response == "こんにちは！"
        mock_claude_client.messages.create.assert_called_once()
    
    async def test_conversation_service_handles_api_timeout(self):
        """GIVEN Claude API times out
        WHEN generating response
        THEN should raise appropriate error"""
        mock_client = AsyncMock()
        mock_client.messages.create.side_effect = TimeoutError()
        
        service = ConversationService(claude_client=mock_client)
        
        with pytest.raises(AIServiceError, match="timeout"):
            await service.generate_response("Hello", "n5", [])
    
    async def test_conversation_service_retries_on_rate_limit(self):
        """GIVEN Claude API returns rate limit error
        WHEN generating response
        THEN should retry with exponential backoff"""
        mock_client = AsyncMock()
        mock_client.messages.create.side_effect = [
            RateLimitError("Too many requests"),
            {"content": [{"text": "Success!"}]}
        ]
        
        service = ConversationService(claude_client=mock_client)
        response = await service.generate_response("Hello", "n5", [])
        
        assert response == "Success!"
        assert mock_client.messages.create.call_count == 2
```

### API Endpoint Testing

```python
# tests/api/test_flashcards.py
import pytest
from httpx import AsyncClient
from app.models import User, Card

@pytest.mark.asyncio
class TestFlashcardAPI:
    async def test_list_flashcards_requires_authentication(self, client: AsyncClient):
        """GIVEN no authentication
        WHEN listing flashcards
        THEN should return 401"""
        response = await client.get("/api/v1/flashcards")
        assert response.status_code == 401
    
    async def test_list_flashcards_returns_user_cards(
        self,
        client: AsyncClient,
        authenticated_user: User,
        auth_headers: dict
    ):
        """GIVEN authenticated user with cards
        WHEN listing flashcards
        THEN should return only user's cards"""
        response = await client.get(
            "/api/v1/flashcards",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert all(card["user_id"] == authenticated_user.id for card in data)
    
    async def test_create_flashcard_validates_input(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """GIVEN invalid flashcard data
        WHEN creating flashcard
        THEN should return 422 with validation errors"""
        invalid_data = {
            "japanese": "",  # Empty - invalid
            "english": "test"
        }
        
        response = await client.post(
            "/api/v1/flashcards",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422
        assert "japanese" in response.json()["detail"]
    
    async def test_create_flashcard_success(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """GIVEN valid flashcard data
        WHEN creating flashcard
        THEN should return 201 with created card"""
        card_data = {
            "japanese": "ありがとう",
            "romanji": "arigatou",
            "english": "thank you"
        }
        
        response = await client.post(
            "/api/v1/flashcards",
            json=card_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["japanese"] == "ありがとう"
        assert data["english"] == "thank you"
        assert "id" in data
    
    async def test_get_due_cards_returns_only_due_cards(
        self,
        client: AsyncClient,
        authenticated_user: User,
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """GIVEN user with cards (some due, some not)
        WHEN fetching due cards
        THEN should return only cards with next_review <= now"""
        # Create cards with different review dates
        now = datetime.utcnow()
        
        due_card = Card(
            user_id=authenticated_user.id,
            japanese="due",
            english="due",
            next_review=now - timedelta(hours=1)  # Due
        )
        future_card = Card(
            user_id=authenticated_user.id,
            japanese="future",
            english="future",
            next_review=now + timedelta(days=1)  # Not due
        )
        
        db_session.add_all([due_card, future_card])
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/flashcards/due",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        cards = response.json()
        assert len(cards) == 1
        assert cards[0]["japanese"] == "due"
```

---

## Frontend Testing (Vitest + React Testing Library)

### Test Organization

```
frontend/src/__tests__/
├── unit/
│   ├── components/
│   │   ├── Flashcard.test.tsx
│   │   ├── ConversationMessage.test.tsx
│   │   └── ProgressBar.test.tsx
│   ├── hooks/
│   │   ├── useSRS.test.ts
│   │   ├── useAuth.test.ts
│   │   └── useConversation.test.ts
│   └── utils/
│       ├── srs-client.test.ts
│       └── formatters.test.ts
│
├── integration/
│   ├── StudySession.test.tsx
│   ├── ConversationFlow.test.tsx
│   └── LessonCompletion.test.tsx
│
└── e2e/
    ├── auth.spec.ts
    ├── flashcard-study.spec.ts
    ├── conversation.spec.ts
    └── progress-tracking.spec.ts
```

### Component Testing Examples

```typescript
// __tests__/unit/components/Flashcard.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Flashcard } from '@/components/flashcard/Flashcard';

describe('Flashcard', () => {
  const mockCard = {
    id: '1',
    japanese: 'こんにちは',
    romanji: 'konnichiwa',
    english: 'Hello'
  };

  it('displays Japanese text on initial render', () => {
    render(<Flashcard card={mockCard} />);
    
    expect(screen.getByText('こんにちは')).toBeInTheDocument();
    expect(screen.queryByText('Hello')).not.toBeInTheDocument();
  });

  it('flips to show English when clicked', async () => {
    render(<Flashcard card={mockCard} />);
    
    const card = screen.getByTestId('flashcard');
    fireEvent.click(card);
    
    await waitFor(() => {
      expect(screen.getByText('Hello')).toBeInTheDocument();
      expect(screen.queryByText('こんにちは')).not.toBeInTheDocument();
    });
  });

  it('calls onAnswer with correct quality when button clicked', async () => {
    const mockOnAnswer = vi.fn();
    render(<Flashcard card={mockCard} onAnswer={mockOnAnswer} />);
    
    // Flip to back
    fireEvent.click(screen.getByTestId('flashcard'));
    
    // Click "I knew it" button
    await waitFor(() => {
      fireEvent.click(screen.getByText('I knew it!'));
    });
    
    expect(mockOnAnswer).toHaveBeenCalledWith('correct');
  });

  it('displays romanji when Show Romanji is clicked', async () => {
    render(<Flashcard card={mockCard} />);
    
    const showRomanjiButton = screen.getByText('Show Romanji');
    fireEvent.click(showRomanjiButton);
    
    await waitFor(() => {
      expect(screen.getByText('konnichiwa')).toBeInTheDocument();
    });
  });
});
```

### Hook Testing Examples

```typescript
// __tests__/unit/hooks/useSRS.test.ts
import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useSRS } from '@/hooks/useSRS';
import * as api from '@/services/api/flashcards';

vi.mock('@/services/api/flashcards');

describe('useSRS', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches due cards on mount', async () => {
    const mockCards = [
      { id: '1', japanese: 'test1', english: 'test1' },
      { id: '2', japanese: 'test2', english: 'test2' }
    ];
    
    vi.mocked(api.getDueCards).mockResolvedValue(mockCards);
    
    const { result } = renderHook(() => useSRS());
    
    expect(result.current.isLoading).toBe(true);
    
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    
    expect(result.current.dueCards).toEqual(mockCards);
  });

  it('updates card and removes from due list when answered', async () => {
    const mockCards = [
      { id: '1', japanese: 'test1', english: 'test1' },
      { id: '2', japanese: 'test2', english: 'test2' }
    ];
    
    vi.mocked(api.getDueCards).mockResolvedValue(mockCards);
    vi.mocked(api.answerCard).mockResolvedValue({ success: true });
    
    const { result } = renderHook(() => useSRS());
    
    await waitFor(() => {
      expect(result.current.dueCards.length).toBe(2);
    });
    
    // Answer first card
    await act(async () => {
      await result.current.answerCard('1', 'correct');
    });
    
    // Card should be removed from due list
    expect(result.current.dueCards.length).toBe(1);
    expect(result.current.dueCards[0].id).toBe('2');
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(api.getDueCards).mockRejectedValue(
      new Error('API error')
    );
    
    const { result } = renderHook(() => useSRS());
    
    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });
    
    expect(result.current.error).toBeTruthy();
    expect(result.current.dueCards).toEqual([]);
  });
});
```

### E2E Testing Examples (Playwright)

```typescript
// __tests__/e2e/flashcard-study.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Flashcard Study Session', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Wait for redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
  });

  test('complete study session flow', async ({ page }) => {
    // Navigate to study
    await page.click('text=Study Now');
    
    // Wait for flashcard to load
    await expect(page.locator('[data-testid="flashcard"]')).toBeVisible();
    
    // Check front side (Japanese)
    const frontText = await page.locator('[data-testid="flashcard"]').textContent();
    expect(frontText).toMatch(/[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]/); // Japanese characters
    
    // Flip card
    await page.click('[data-testid="flashcard"]');
    await page.waitForTimeout(500); // Animation
    
    // Check back side (English)
    const backText = await page.locator('[data-testid="flashcard"]').textContent();
    expect(backText).toMatch(/^[a-zA-Z\s]+$/); // English characters
    
    // Answer card
    await page.click('text=I knew it!');
    
    // Next card should appear
    await expect(page.locator('[data-testid="flashcard"]')).toBeVisible();
    
    // Complete session (answer 10 cards)
    for (let i = 0; i < 9; i++) {
      await page.click('[data-testid="flashcard"]');
      await page.waitForTimeout(300);
      await page.click('text=I knew it!');
      await page.waitForTimeout(200);
    }
    
    // Session complete screen
    await expect(page.locator('text=Session Complete!')).toBeVisible();
    await expect(page.locator('text=10 cards reviewed')).toBeVisible();
  });

  test('handles incorrect answers', async ({ page }) => {
    await page.goto('/practice/flashcards');
    
    // Answer incorrectly
    await page.click('[data-testid="flashcard"]'); // Flip
    await page.click('text=I forgot');
    
    // Card should be rescheduled for review later in session
    // Complete other cards...
    for (let i = 0; i < 5; i++) {
      await page.click('[data-testid="flashcard"]');
      await page.waitForTimeout(300);
      await page.click('text=I knew it!');
      await page.waitForTimeout(200);
    }
    
    // Incorrect card should appear again
    // (implementation-specific validation)
  });
});
```

---

## Test Data Management

### Fixtures and Factories

**pytest Fixtures (Backend):**

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.db.base import Base
from app.models import User, Card

@pytest.fixture(scope="function")
async def db_session():
    """Provide clean database for each test"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
async def authenticated_user(db_session: AsyncSession):
    """Create and return authenticated test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
        japanese_level="n5"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(authenticated_user: User):
    """Generate authentication headers for API tests"""
    token = create_access_token(user_id=authenticated_user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def sample_cards(db_session: AsyncSession, authenticated_user: User):
    """Create sample flashcards for testing"""
    cards = [
        Card(
            user_id=authenticated_user.id,
            japanese="こんにちは",
            romanji="konnichiwa",
            english="hello",
            next_review=datetime.utcnow() - timedelta(hours=1)
        ),
        Card(
            user_id=authenticated_user.id,
            japanese="ありがとう",
            romanji="arigatou",
            english="thank you",
            next_review=datetime.utcnow() + timedelta(days=1)
        )
    ]
    
    db_session.add_all(cards)
    await db_session.commit()
    return cards
```

**Test Factories (Frontend):**

```typescript
// __tests__/factories/index.ts
import { faker } from '@faker-js/faker';

export const createMockCard = (overrides = {}) => ({
  id: faker.string.uuid(),
  japanese: 'テスト',
  romanji: 'tesuto',
  english: 'test',
  intervalDays: 1,
  correctCount: 0,
  nextReview: new Date().toISOString(),
  ...overrides
});

export const createMockUser = (overrides = {}) => ({
  id: faker.string.uuid(),
  email: faker.internet.email(),
  username: faker.internet.userName(),
  japaneseLevel: 'n5',
  createdAt: new Date().toISOString(),
  ...overrides
});

export const createMockConversation = (overrides = {}) => ({
  id: faker.string.uuid(),
  userMessage: faker.lorem.sentence(),
  aiResponse: faker.lorem.sentence(),
  createdAt: new Date().toISOString(),
  ...overrides
});
```

---

## Mocking Strategies

### External API Mocking

**Claude API Mock:**

```python
# tests/conftest.py
@pytest.fixture
def mock_claude_client(monkeypatch):
    """Mock Anthropic Claude API"""
    class MockClaudeClient:
        async def messages_create(self, **kwargs):
            return {
                "content": [{"text": "こんにちは！元気ですか？"}],
                "usage": {"input_tokens": 10, "output_tokens": 15}
            }
    
    mock_client = MockClaudeClient()
    monkeypatch.setattr(
        "app.services.claude.ClaudeClient",
        lambda *args, **kwargs: mock_client
    )
    return mock_client
```

**Frontend API Mocking (MSW):**

```typescript
// __tests__/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/v1/flashcards/due', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: '1',
          japanese: 'こんにちは',
          english: 'hello'
        }
      ])
    );
  }),
  
  rest.post('/api/v1/conversation/message', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        response: 'それはいいですね！',
        correction: null
      })
    );
  })
];
```

---

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements-dev.txt
      
      - name: Run tests with coverage
        run: |
          cd backend
          pytest --cov=app --cov-report=xml --cov-fail-under=90
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Run tests with coverage
        run: |
          cd frontend
          npm run test:ci
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Testing Best Practices

### DO ✅

1. **Write tests first** - Red-Green-Refactor
2. **Test behavior, not implementation** - Focus on what, not how
3. **Use descriptive test names** - `test_user_cannot_access_other_users_cards`
4. **Arrange-Act-Assert pattern** - Clear test structure
5. **Test edge cases** - Empty strings, null values, max limits
6. **Mock external dependencies** - Don't call real APIs in tests
7. **Keep tests fast** - Unit tests < 10ms, integration < 100ms
8. **Use fixtures/factories** - DRY test data creation
9. **Test error cases** - Not just happy paths
10. **Maintain test independence** - Tests shouldn't depend on each other

### DON'T ❌

1. **Skip writing tests** - "I'll add them later" = never
2. **Test implementation details** - Internal state, private methods
3. **Write brittle tests** - Breaking on formatting changes
4. **Ignore flaky tests** - Fix or remove them
5. **Test too much in one test** - One assertion per test (when possible)
6. **Commit commented-out tests** - Delete or fix them
7. **Use production data in tests** - Always use mocks/fixtures
8. **Skip CI checks** - "Works on my machine" isn't enough
9. **Write slow tests** - Optimize or move to integration suite
10. **Duplicate test logic** - Use shared fixtures/utilities

---

## Test Reporting

### Coverage Reports

**Backend (pytest-cov):**
```bash
pytest --cov=app --cov-report=html --cov-report=term-missing

# View report
open htmlcov/index.html
```

**Frontend (Vitest):**
```bash
npm run test:coverage

# View report
open coverage/index.html
```

### Quality Metrics

Track these metrics:
- **Test count** - Total number of tests
- **Coverage %** - Line and branch coverage
- **Test duration** - Total time to run suite
- **Flakiness rate** - % of tests that fail intermittently
- **Skipped tests** - Should be 0

---

## Troubleshooting Tests

### Common Issues

**Tests pass locally but fail in CI:**
- Environment differences (timezone, filesystem)
- Missing dependencies
- Timing issues (use `waitFor` in frontend tests)

**Flaky tests:**
- Add proper `await` for async operations
- Use deterministic test data (no random values)
- Clear state between tests

**Slow tests:**
- Profile with `pytest --durations=10`
- Move slow tests to integration suite
- Optimize database operations

---

**Last Updated:** Initial creation
**Review Cadence:** After each phase completion
