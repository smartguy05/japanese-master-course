# System Architecture - Nihongo Master

## Architecture Overview

Nihongo Master is a modern, cloud-ready Japanese learning platform built on a three-tier architecture with AI service integration.

```
┌─────────────────────────────────────────────────────────────┐
│                        End Users                             │
│            (Web Browsers, PWA, Mobile Devices)              │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Nginx Reverse Proxy                      │
│                  (SSL Termination, Static Files)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Frontend   │   │   Backend    │   │    Media     │
│  (Next.js)   │   │  (FastAPI)   │   │   Storage    │
│  React App   │   │  Python API  │   │    (S3)      │
└──────┬───────┘   └──────┬───────┘   └──────────────┘
       │                  │
       │                  ├─────────┐
       │                  │         │
       ▼                  ▼         ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Browser    │   │  PostgreSQL  │   │    Redis     │
│   Storage    │   │   Database   │   │    Cache     │
└──────────────┘   └──────────────┘   └──────────────┘
                            │
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Claude     │   │   Whisper    │   │  Google TTS  │
│  (Anthrop.)  │   │   (OpenAI)   │   │   (Google)   │
│ Conversation │   │  Speech-to-  │   │  Text-to-    │
│              │   │     Text     │   │   Speech     │
└──────────────┘   └──────────────┘   └──────────────┘
```

---

## System Components

### 1. Frontend Layer (Next.js 14)

**Technology:** React 18, TypeScript, Tailwind CSS, shadcn/ui

**Responsibilities:**
- User interface rendering (Server & Client Components)
- Client-side state management (Zustand)
- Form validation and user input handling
- Real-time conversation UI
- Progressive Web App functionality
- Offline capability for flashcard review

**Key Components:**
```
frontend/
├── app/                        # Next.js App Router
│   ├── (auth)/                # Authentication group
│   │   ├── login/
│   │   └── signup/
│   ├── dashboard/             # Main dashboard
│   ├── lessons/               # Lesson browser
│   │   └── [id]/             # Individual lesson
│   ├── practice/              # Practice modes
│   │   ├── flashcards/
│   │   ├── speaking/
│   │   └── listening/
│   ├── conversation/          # AI conversation
│   └── settings/              # User settings
│
├── components/
│   ├── ui/                    # shadcn/ui components
│   ├── flashcard/             # Flashcard components
│   │   ├── FlashcardDeck.tsx
│   │   ├── FlashcardCard.tsx
│   │   └── AnswerButtons.tsx
│   ├── conversation/          # Chat interface
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   └── ConversationHistory.tsx
│   ├── progress/              # Progress tracking
│   │   ├── StreakDisplay.tsx
│   │   ├── LevelProgress.tsx
│   │   └── StatsChart.tsx
│   └── lesson/                # Lesson components
│
├── hooks/                     # Custom React hooks
│   ├── useAuth.ts
│   ├── useSRS.ts
│   ├── useConversation.ts
│   └── useSpeech.ts
│
├── services/                  # API clients
│   ├── api/
│   │   ├── auth.ts
│   │   ├── flashcards.ts
│   │   ├── conversation.ts
│   │   └── progress.ts
│   └── storage/               # Browser storage
│
└── lib/                       # Utilities
    ├── srs-client.ts          # Client-side SRS logic
    ├── audio.ts               # Audio handling
    └── validation.ts          # Form validation
```

**Data Flow:**
1. User interacts with UI (Server or Client Component)
2. Client Component triggers API call via service layer
3. React Query manages request state and caching
4. Response updates component via state management
5. UI re-renders with new data

---

### 2. Backend Layer (FastAPI)

**Technology:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Alembic

**Responsibilities:**
- RESTful API endpoints
- Business logic execution
- Database operations (CRUD)
- Authentication & authorization
- AI service orchestration
- Content generation
- SRS algorithm execution

**API Structure:**
```
backend/app/
├── api/v1/                    # API version 1
│   ├── auth.py               # Authentication endpoints
│   │   POST /login
│   │   POST /register
│   │   POST /logout
│   │   GET /me
│   │
│   ├── flashcards.py         # Flashcard CRUD
│   │   GET /flashcards
│   │   POST /flashcards
│   │   GET /flashcards/{id}
│   │   PUT /flashcards/{id}
│   │   DELETE /flashcards/{id}
│   │   GET /flashcards/due
│   │
│   ├── conversation.py       # AI conversation
│   │   POST /conversation/message
│   │   GET /conversation/history
│   │   POST /conversation/correction
│   │
│   ├── lessons.py            # Lesson management
│   │   GET /lessons
│   │   GET /lessons/{id}
│   │   POST /lessons/{id}/complete
│   │
│   ├── progress.py           # User progress
│   │   GET /progress/stats
│   │   GET /progress/streak
│   │   GET /progress/history
│   │
│   └── speech.py             # Speech processing
│       POST /speech/recognize
│       POST /speech/synthesize
│       POST /speech/score-pronunciation
│
├── core/                      # Core business logic
│   ├── srs.py                # Spaced Repetition System
│   ├── conversation.py       # Conversation engine
│   ├── content_gen.py        # AI content generation
│   └── speech.py             # Speech processing
│
├── models/                    # SQLAlchemy models
│   ├── user.py
│   ├── card.py
│   ├── lesson.py
│   ├── progress.py
│   └── conversation.py
│
├── schemas/                   # Pydantic schemas
│   ├── user.py
│   ├── card.py
│   ├── lesson.py
│   └── conversation.py
│
├── services/                  # External services
│   ├── claude.py             # Anthropic API client
│   ├── whisper.py            # OpenAI Whisper client
│   ├── tts.py                # Google TTS client
│   └── content.py            # Content database
│
├── db/                        # Database config
│   ├── base.py
│   ├── session.py
│   └── init_db.py
│
└── main.py                    # Application entry
```

**API Request Flow:**
```
Client Request
    ↓
Nginx (HTTPS, routing)
    ↓
FastAPI Router (route matching)
    ↓
Dependency Injection (auth, db session)
    ↓
Route Handler (validation via Pydantic)
    ↓
Service Layer (business logic)
    ↓
Database / AI Service
    ↓
Response (Pydantic serialization)
    ↓
Client
```

---

### 3. Database Layer (PostgreSQL)

**Schema Design:**

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    japanese_level VARCHAR(10) DEFAULT 'n5',  -- n5, n4, n3, n2
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Flashcards table
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    -- Content
    japanese TEXT NOT NULL,
    romanji TEXT NOT NULL,
    english TEXT NOT NULL,
    kanji TEXT,
    part_of_speech VARCHAR(50),
    jlpt_level VARCHAR(10),
    
    -- SRS fields
    interval_days INTEGER DEFAULT 1,
    correct_count INTEGER DEFAULT 0,
    incorrect_count INTEGER DEFAULT 0,
    ease_factor FLOAT DEFAULT 2.5,
    next_review TIMESTAMP NOT NULL,
    last_review TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_next_review (user_id, next_review),
    INDEX idx_user_level (user_id, jlpt_level)
);

-- Lessons table
CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    jlpt_level VARCHAR(10) NOT NULL,
    topic VARCHAR(100),
    content JSONB NOT NULL,  -- Flexible lesson structure
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_level (jlpt_level)
);

-- User lesson progress
CREATE TABLE user_lesson_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    lesson_id INTEGER REFERENCES lessons(id) ON DELETE CASCADE,
    
    completed BOOLEAN DEFAULT FALSE,
    score FLOAT,
    completed_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, lesson_id),
    INDEX idx_user_completed (user_id, completed)
);

-- Conversation history
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    correction TEXT,
    topic VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_created (user_id, created_at DESC)
);

-- Daily progress tracking
CREATE TABLE daily_stats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    
    cards_reviewed INTEGER DEFAULT 0,
    cards_correct INTEGER DEFAULT 0,
    conversations_held INTEGER DEFAULT 0,
    study_minutes INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, date),
    INDEX idx_user_date (user_id, date DESC)
);
```

**Database Relationships:**
```
users (1) ─────────── (many) cards
users (1) ─────────── (many) user_lesson_progress
users (1) ─────────── (many) conversations
users (1) ─────────── (many) daily_stats

lessons (1) ────────── (many) user_lesson_progress
```

---

### 4. Caching Layer (Redis)

**Use Cases:**
1. **Session Management** - JWT refresh tokens, user sessions
2. **SRS Scheduling** - Pre-calculated review queues
3. **API Response Caching** - Frequently accessed data
4. **Rate Limiting** - Per-user request throttling
5. **Temporary Data** - Conversation context, in-progress exercises

**Key Patterns:**
```python
# Session storage
redis.setex(f"session:{user_id}", 3600, session_data)

# SRS queue (sorted set by next_review timestamp)
redis.zadd(f"review_queue:{user_id}", {card_id: next_review_timestamp})

# API response cache
redis.setex(f"lessons:n5", 3600, json.dumps(lessons))

# Rate limiting
redis.incr(f"rate_limit:{user_id}:{endpoint}")
redis.expire(f"rate_limit:{user_id}:{endpoint}", 60)

# Conversation context (temporary)
redis.setex(f"conversation:{user_id}", 1800, json.dumps(history))
```

---

### 5. AI Services Integration

#### Anthropic Claude (Conversation)

**Purpose:** Natural language conversation, error correction, content generation

**Integration Pattern:**
```python
from anthropic import AsyncAnthropic

class ClaudeService:
    def __init__(self, api_key: str, base_url: str = None):
        self.client = AsyncAnthropic(
            api_key=api_key,
            base_url=base_url or "https://api.anthropic.com"
        )
    
    async def generate_conversation_response(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: list[dict],
        max_tokens: int = 500
    ) -> str:
        messages = self._format_history(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=messages
        )
        
        return response.content[0].text
```

**Error Handling:**
- Timeout: 30 seconds, retry once with exponential backoff
- Rate limit: Queue requests, warn user
- API error: Fallback to cached responses or generic error message

---

#### OpenAI Whisper (Speech-to-Text)

**Purpose:** Convert spoken Japanese to text for pronunciation practice

**Integration Pattern:**
```python
from openai import AsyncOpenAI

class WhisperService:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def transcribe_audio(
        self,
        audio_file: bytes,
        language: str = "ja"
    ) -> dict:
        response = await self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language,
            response_format="verbose_json"
        )
        
        return {
            "text": response.text,
            "confidence": response.segments[0].confidence if response.segments else 0.0
        }
```

**Audio Processing:**
- Max file size: 25 MB
- Supported formats: MP3, M4A, WAV, WEBM
- Pre-processing: Normalize audio levels, remove silence
- Post-processing: Confidence scoring, alternative transcriptions

---

#### Google Cloud TTS (Text-to-Speech)

**Purpose:** Generate natural Japanese speech for listening practice

**Integration Pattern:**
```python
from google.cloud import texttospeech

class TTSService:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
    
    async def synthesize_speech(
        self,
        text: str,
        voice_name: str = "ja-JP-Neural2-B",
        speaking_rate: float = 1.0
    ) -> bytes:
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="ja-JP",
            name=voice_name
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate,
            pitch=0.0
        )
        
        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return response.audio_content
```

**Voice Options:**
- ja-JP-Neural2-B: Male voice (default)
- ja-JP-Neural2-C: Female voice
- ja-JP-Neural2-D: Male voice (alternative)
- Speaking rates: 0.5x (slow), 1.0x (normal), 1.5x (fast)

---

## Data Flow Diagrams

### User Study Session Flow

```
User Opens App
    │
    ├─→ Load Due Cards (Backend API)
    │       │
    │       ├─→ Check Redis Cache
    │       │   ├─→ Cache Hit: Return Cards
    │       │   └─→ Cache Miss: Query Database
    │       │           │
    │       │           └─→ Cache Result in Redis
    │       │
    │       └─→ Return Due Cards to Frontend
    │
    ├─→ Display Flashcard (Frontend)
    │       │
    │       └─→ User Answers (Correct/Incorrect)
    │               │
    │               ├─→ Send Answer to Backend
    │               │       │
    │               │       ├─→ Calculate Next Interval (SRS Algorithm)
    │               │       │
    │               │       ├─→ Update Card in Database
    │               │       │
    │               │       └─→ Update Redis Queue
    │               │
    │               └─→ Show Next Card
    │
    └─→ Complete Session
            │
            └─→ Update Daily Stats (Backend)
                    │
                    └─→ Display Progress Summary (Frontend)
```

### AI Conversation Flow

```
User Types Message
    │
    ├─→ Send to Backend API
    │       │
    │       ├─→ Load Conversation History (Database)
    │       │
    │       ├─→ Build System Prompt (Based on User Level)
    │       │
    │       ├─→ Call Claude API
    │       │       │
    │       │       ├─→ Timeout? Retry Once
    │       │       │
    │       │       └─→ Return AI Response
    │       │
    │       ├─→ Analyze Response for Corrections
    │       │       │
    │       │       └─→ Detect Grammar/Vocabulary Errors
    │       │
    │       ├─→ Save Conversation to Database
    │       │
    │       └─→ Return Response + Corrections
    │
    └─→ Display AI Message (Frontend)
            │
            └─→ Show Corrections (If Any)
```

### Speech Recognition Flow

```
User Speaks Japanese
    │
    ├─→ Record Audio (Frontend)
    │       │
    │       └─→ Convert to Base64 / Upload
    │
    ├─→ Send to Backend API
    │       │
    │       ├─→ Validate Audio Format & Size
    │       │
    │       ├─→ Call Whisper API
    │       │       │
    │       │       └─→ Return Transcription + Confidence
    │       │
    │       ├─→ Compare to Expected Text (If Quiz Mode)
    │       │       │
    │       │       └─→ Calculate Pronunciation Score
    │       │
    │       └─→ Return Transcription + Score
    │
    └─→ Display Results (Frontend)
            │
            ├─→ Show Transcribed Text
            ├─→ Show Score/Feedback
            └─→ Play Correct Pronunciation (TTS)
```

---

## Deployment Architecture

### Docker Compose Stack

```yaml
version: '3.8'

services:
  # Reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/nihongo
      - REDIS_URL=redis://redis:6379
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - WHISPER_API_KEY=${WHISPER_API_KEY}
      - GOOGLE_TTS_CREDENTIALS=${GOOGLE_TTS_CREDENTIALS}
    depends_on:
      - postgres
      - redis
    volumes:
      - ./content:/app/content

  # Database
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=nihongo
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Scaling Considerations

**Horizontal Scaling:**
- Frontend: Multiple Next.js instances behind load balancer
- Backend: Multiple FastAPI instances (stateless)
- Database: Read replicas for heavy read workloads
- Redis: Redis Cluster for high availability

**Vertical Scaling:**
- Increase container resources as user base grows
- Expected requirements:
  - 1-100 users: 2GB RAM, 2 CPUs per service
  - 100-1000 users: 4GB RAM, 4 CPUs per service
  - 1000+ users: Consider horizontal scaling

---

## Security Architecture

### Authentication Flow

```
User Login Request
    │
    ├─→ Backend Validates Credentials
    │       │
    │       ├─→ Verify Email & Password Hash (bcrypt)
    │       │
    │       └─→ Generate JWT Tokens
    │               ├─→ Access Token (15 min expiry)
    │               └─→ Refresh Token (7 days expiry)
    │
    ├─→ Store Refresh Token in HTTP-only Cookie
    │
    └─→ Return Access Token to Frontend
            │
            └─→ Store in Memory (Not LocalStorage!)
```

**Protected Route Access:**
```
Client Request with Access Token
    │
    ├─→ Backend Validates JWT Signature
    │       │
    │       ├─→ Valid? Continue to Route Handler
    │       │
    │       └─→ Expired? Return 401
    │               │
    │               └─→ Frontend Uses Refresh Token
    │                       │
    │                       └─→ Get New Access Token
```

### Data Security

**At Rest:**
- User passwords: bcrypt hashing (cost factor 12)
- Sensitive data: AES-256 encryption
- Database: Encrypted volumes (provider-specific)
- Backups: Encrypted before storage

**In Transit:**
- All external communication: HTTPS/TLS 1.3
- Internal services (Docker): Encrypted overlay network (optional)
- API keys: Environment variables, never committed

**API Security:**
- Rate limiting: 100 requests/minute per user
- Input validation: Pydantic schemas on all inputs
- SQL injection prevention: SQLAlchemy ORM (no raw queries)
- XSS prevention: React auto-escaping, Content Security Policy
- CSRF protection: SameSite cookies, CSRF tokens

---

## Performance Optimization

### Caching Strategy

**Layer 1: Browser Cache**
- Static assets: 1 year
- API responses: Conditional (ETag, Last-Modified)
- Service Worker: Offline flashcard data

**Layer 2: Redis Cache**
- User sessions: 1 hour
- Frequently accessed data: 30 minutes
- SRS queues: 5 minutes
- API responses: 10 minutes

**Layer 3: Database Query Optimization**
- Indexes on: user_id, next_review, jlpt_level
- Eager loading with `selectinload()` for relationships
- Connection pooling: 20 connections per backend instance

### Response Time Targets

| Endpoint | Target | Fallback |
|----------|--------|----------|
| Authentication | <100ms | N/A |
| Flashcard fetch | <50ms | Cached cards |
| AI conversation | <3s | "Thinking..." indicator |
| Speech recognition | <2s | "Processing..." |
| TTS synthesis | <1s | Pre-generated audio |

---

## Monitoring & Observability

### Metrics to Track

**Application Metrics:**
- Request rate (requests/second)
- Error rate (errors/total requests)
- Response time (p50, p95, p99)
- Active users (concurrent, daily, monthly)

**Business Metrics:**
- Cards reviewed per user per day
- Conversation quality ratings
- Study streak lengths
- Content completion rates
- AI API costs per user

**Infrastructure Metrics:**
- CPU usage per container
- Memory usage per container
- Database connection pool usage
- Redis memory usage
- Network throughput

### Logging Strategy

**Log Levels:**
- DEBUG: Development only
- INFO: User actions, API calls
- WARNING: Degraded performance, retries
- ERROR: Failed requests, exceptions
- CRITICAL: System failures

**Structured Logging:**
```python
logger.info(
    "conversation_generated",
    user_id=user.id,
    message_length=len(message),
    ai_provider="claude",
    response_time_ms=elapsed_ms
)
```

---

## Future Architecture Considerations

### Planned Enhancements

**Phase 2-3:**
- WebSocket support for real-time AI conversations
- Background job queue (Celery) for content generation
- CDN for static assets and audio files
- Elasticsearch for advanced content search

**Phase 4-5:**
- Microservices separation (AI services, content, user management)
- Event-driven architecture (message queue)
- Multi-region deployment
- Machine learning model deployment (custom pronunciation scoring)

---

**Last Updated:** Initial creation
**Review Cadence:** After major architectural changes
