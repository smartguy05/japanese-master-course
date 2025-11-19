# Technical Architecture & System Design
## Nihongo Sensei - AI-Powered Japanese Learning Platform

**Version:** 1.0.0  
**Last Updated:** 2025-11-19  
**Status:** Design Phase  

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Data Architecture](#data-architecture)
6. [AI Integration Architecture](#ai-integration-architecture)
7. [Frontend Architecture](#frontend-architecture)
8. [Backend Architecture](#backend-architecture)
9. [Infrastructure Architecture](#infrastructure-architecture)
10. [Security Architecture](#security-architecture)
11. [Performance Architecture](#performance-architecture)
12. [Testing Architecture](#testing-architecture)

---

## System Overview

### Purpose
Nihongo Sensei is a comprehensive, self-hosted AI-powered Japanese learning platform designed to take learners from complete beginner (JLPT N5) to professional proficiency (JLPT N2-N3) with emphasis on business communication in Japan.

### Key Objectives
- **Educational Excellence:** Proven learning methodologies (SRS, active recall, multi-modal learning)
- **AI-Powered Personalization:** Adaptive conversation practice with intelligent corrections
- **Self-Hosted Architecture:** Complete control over data and infrastructure
- **Engagement:** Gamification and progress tracking to maintain motivation
- **Accessibility:** PWA support for cross-platform usage (web + Android)

### High-Level Capabilities
1. **Comprehensive Content:** Hiragana, Katakana, 1000+ Kanji, 10,000+ vocabulary, N5-N2 grammar
2. **AI Conversation:** Real-time dialogue with contextual corrections and pronunciation guidance
3. **Speech Integration:** Speech-to-text (learner speaking) and text-to-speech (listening practice)
4. **Spaced Repetition System:** Proven SM-2 algorithm for optimal memory retention
5. **Progress Tracking:** Detailed analytics, streaks, achievements, proficiency levels
6. **Content Generation:** AI-assisted lesson creation with human curation capability

---

## Architecture Principles

### 1. Test-Driven Development (TDD)
- **All code written with tests first** - No exceptions
- Minimum 85% code coverage, 90%+ for critical learning logic
- Integration tests for all API endpoints
- E2E tests for critical user journeys

### 2. Separation of Concerns
- **Backend:** Pure API, no business logic in routes
- **Frontend:** Presentation layer, minimal business logic
- **Services:** Encapsulated business logic with clear interfaces
- **Data:** Clean separation between models, schemas, and database

### 3. API-First Design
- Backend exposes RESTful API
- Frontend consumes API exclusively
- OpenAPI (Swagger) documentation auto-generated
- Versioned API for future compatibility

### 4. Stateless Services
- Backend API is stateless (session data in Redis)
- Horizontal scalability potential
- Easy deployment and updates

### 5. Configuration Over Code
- All deployment configuration via environment variables
- No hardcoded credentials or URLs
- Feature flags for gradual rollouts

### 6. Progressive Enhancement
- Core functionality works without JavaScript
- PWA features enhance but don't require
- Graceful degradation for older browsers

### 7. Security First
- Authentication on all protected endpoints
- Input validation at API boundary
- SQL injection protection via ORM
- XSS protection via framework defaults
- HTTPS enforcement in production

### 8. Performance Budget
- API response time <200ms (95th percentile)
- AI conversation response <3 seconds
- Page load time <2 seconds
- Lighthouse score >90

---

## Technology Stack

### Backend Stack

#### Core Framework
- **Python 3.11+**: Modern async support, type hints, performance
- **FastAPI 0.104+**: High-performance async web framework
  - Automatic OpenAPI documentation
  - Built-in validation via Pydantic
  - Native async/await support
  - Dependency injection system

#### Database Layer
- **PostgreSQL 15+**: Primary relational database
  - JSONB for flexible schema (lesson content)
  - Full-text search for Japanese dictionary
  - Robust transaction support
  - Excellent Python ecosystem
  
- **Redis 7+**: In-memory data store
  - Session management
  - SRS scheduling queue
  - API response caching
  - Rate limiting
  - Pub/Sub for real-time features

#### ORM & Data Management
- **SQLAlchemy 2.0**: Async ORM
  - Declarative models
  - Complex query support
  - Relationship management
  
- **Alembic**: Database migrations
  - Version-controlled schema changes
  - Automatic migration generation
  - Safe rollback support

#### Testing Framework
- **pytest**: Main test runner
- **pytest-asyncio**: Async test support
- **pytest-cov**: Coverage reporting
- **httpx**: Async HTTP client for API tests
- **faker**: Test data generation

#### AI Integration
- **anthropic**: Claude API client
- **openai**: Whisper API client
- **google-cloud-texttospeech**: Japanese TTS
- **httpx**: Configurable HTTP client for custom AI endpoints

#### Additional Libraries
- **python-jose**: JWT token handling
- **passlib + bcrypt**: Password hashing
- **python-multipart**: File upload support
- **pydantic-settings**: Configuration management
- **ruff**: Fast Python linter
- **black**: Code formatter
- **mypy**: Static type checker

### Frontend Stack

#### Core Framework
- **Next.js 14+**: React meta-framework
  - App Router (Server Components)
  - Built-in API routes
  - Image optimization
  - Automatic code splitting
  
- **React 18**: UI library
  - Concurrent rendering
  - Automatic batching
  - Suspense for data fetching

- **TypeScript 5+**: Type safety
  - Compile-time error detection
  - Enhanced IDE support
  - Self-documenting code

#### UI Framework
- **Tailwind CSS 3+**: Utility-first styling
  - Responsive design utilities
  - Dark mode support
  - JIT compilation
  
- **shadcn/ui**: Component library
  - Accessible components (ARIA)
  - Radix UI primitives
  - Customizable design tokens

#### State Management
- **TanStack Query v5**: Server state
  - Automatic caching
  - Background refetching
  - Optimistic updates
  - Request deduplication
  
- **Zustand**: Client state
  - Minimal boilerplate
  - TypeScript support
  - DevTools integration

#### Animation & Interactions
- **Framer Motion**: Animations
  - Declarative animations
  - Gesture support
  - Layout animations

#### Forms & Validation
- **React Hook Form**: Form management
  - Minimal re-renders
  - Built-in validation
  - TypeScript support
  
- **Zod**: Schema validation
  - Type-safe validation
  - Composable schemas
  - Error handling

#### PWA Support
- **next-pwa**: PWA plugin
  - Service worker generation
  - Offline support
  - App manifest
  - Install prompts

#### Testing
- **Jest**: Test runner
- **React Testing Library**: Component testing
- **Playwright**: E2E testing
- **MSW (Mock Service Worker)**: API mocking

#### Additional Libraries
- **date-fns**: Date manipulation
- **recharts**: Data visualization
- **react-hot-toast**: Notifications
- **react-icons**: Icon library

### Infrastructure Stack

#### Containerization
- **Docker 24+**: Container runtime
- **Docker Compose**: Multi-container orchestration

#### Web Server
- **Nginx**: Reverse proxy and static file serving
  - SSL/TLS termination
  - Load balancing potential
  - Compression
  - Rate limiting

#### Object Storage (Optional)
- **MinIO**: S3-compatible object storage
  - Audio file storage
  - User-uploaded content
  - Backup storage

#### Monitoring & Logging
- **Prometheus**: Metrics collection (future)
- **Grafana**: Metrics visualization (future)
- **ELK Stack**: Log aggregation (future)

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐         ┌──────────────────┐            │
│  │   Web Browser    │         │   Mobile PWA     │            │
│  │  (Next.js App)   │         │  (Installed)     │            │
│  └────────┬─────────┘         └────────┬─────────┘            │
│           │                            │                        │
│           └────────────┬───────────────┘                       │
│                        │                                        │
└────────────────────────┼────────────────────────────────────────┘
                         │
                         │ HTTPS
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      NGINX LAYER                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  • SSL/TLS Termination                                         │
│  • Static File Serving                                         │
│  • Request Routing                                             │
│  • Rate Limiting                                               │
│  • Compression (gzip/brotli)                                   │
│                                                                 │
└────────────┬───────────────────────────┬────────────────────────┘
             │                           │
             │                           │
     ┌───────▼────────┐         ┌────────▼──────────┐
     │   Frontend     │         │    Backend API    │
     │  (Next.js)     │         │    (FastAPI)      │
     │  SSR/Static    │         │    REST API       │
     └────────────────┘         └────────┬──────────┘
                                         │
                        ┌────────────────┼────────────────┐
                        │                │                │
              ┌─────────▼────┐  ┌────────▼────┐  ┌───────▼────────┐
              │  PostgreSQL  │  │    Redis    │  │  AI Services   │
              │   Database   │  │    Cache    │  │   (External)   │
              │              │  │   Session   │  │                │
              │  • Users     │  │   Queue     │  │  • Claude API  │
              │  • Content   │  │             │  │  • Whisper API │
              │  • Progress  │  │             │  │  • Google TTS  │
              └──────────────┘  └─────────────┘  └────────────────┘
```

### Component Communication Flow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Browser    │      │  Next.js App │      │  FastAPI     │
│              │      │              │      │   Backend    │
└──────┬───────┘      └──────┬───────┘      └──────┬───────┘
       │                     │                     │
       │  1. Request Page    │                     │
       │─────────────────────>                     │
       │                     │                     │
       │  2. SSR/Static HTML │                     │
       │<─────────────────────                     │
       │                     │                     │
       │  3. API Request     │                     │
       │─────────────────────────────────────────> │
       │                     │                     │
       │                     │  4. DB Query        │
       │                     │     ┌────────────┐  │
       │                     │     │ PostgreSQL │  │
       │                     │     └────────────┘  │
       │                     │                     │
       │                     │  5. Cache Check     │
       │                     │     ┌────────────┐  │
       │                     │     │   Redis    │  │
       │                     │     └────────────┘  │
       │                     │                     │
       │  6. JSON Response   │                     │
       │<───────────────────────────────────────── │
       │                     │                     │
       │  7. Update UI       │                     │
       │─────────────────────>                     │
       │                     │                     │
```

### Conversation Flow (AI Integration)

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Browser │     │ FastAPI  │     │  Redis   │     │ Claude   │
│         │     │          │     │  Cache   │     │   API    │
└────┬────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │               │                │                │
     │ User types    │                │                │
     │ Japanese msg  │                │                │
     │───────────────>                │                │
     │               │                │                │
     │               │ Check cache    │                │
     │               │────────────────>                │
     │               │                │                │
     │               │ Cache miss     │                │
     │               │<────────────────                │
     │               │                │                │
     │               │ Build prompt   │                │
     │               │ with context   │                │
     │               │                │                │
     │               │ Call Claude API                 │
     │               │────────────────────────────────>│
     │               │                │                │
     │               │                │  AI processes  │
     │               │                │  & responds    │
     │               │                │                │
     │               │ Response (JSON)                 │
     │               │<────────────────────────────────│
     │               │                │                │
     │               │ Cache response │                │
     │               │────────────────>                │
     │               │                │                │
     │               │ Parse &        │                │
     │               │ extract        │                │
     │               │ corrections    │                │
     │               │                │                │
     │ JSON response │                │                │
     │<───────────────                │                │
     │               │                │                │
     │ Display with  │                │                │
     │ corrections   │                │                │
     │               │                │                │
```

---

## Data Architecture

### Database Schema (PostgreSQL)

#### Core Tables

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    native_language VARCHAR(10) DEFAULT 'en',
    target_proficiency VARCHAR(10) DEFAULT 'N3',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    preferences JSONB DEFAULT '{}'
);

-- User progress table
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    current_level VARCHAR(10) NOT NULL, -- N5, N4, N3, N2
    total_study_time INTEGER DEFAULT 0, -- minutes
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_study_date DATE,
    xp_points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Kanji master table
CREATE TABLE kanji (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    character VARCHAR(10) UNIQUE NOT NULL,
    jlpt_level VARCHAR(10) NOT NULL, -- N5, N4, N3, N2, N1
    frequency_rank INTEGER,
    meanings JSONB NOT NULL, -- ["water", "cold water"]
    on_readings JSONB, -- ["スイ"]
    kun_readings JSONB, -- ["みず"]
    radical VARCHAR(10),
    stroke_count INTEGER,
    grade INTEGER, -- Jouyou grade
    examples JSONB, -- Example words using this kanji
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vocabulary master table
CREATE TABLE vocabulary (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    word VARCHAR(255) NOT NULL,
    reading VARCHAR(255) NOT NULL,
    jlpt_level VARCHAR(10) NOT NULL,
    meanings JSONB NOT NULL,
    part_of_speech VARCHAR(50),
    frequency_rank INTEGER,
    audio_url VARCHAR(500),
    example_sentences JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Grammar points table
CREATE TABLE grammar_points (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    jlpt_level VARCHAR(10) NOT NULL,
    grammar_pattern VARCHAR(255) NOT NULL,
    meaning TEXT NOT NULL,
    formation TEXT NOT NULL,
    examples JSONB NOT NULL,
    notes TEXT,
    common_mistakes JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Lessons table
CREATE TABLE lessons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    lesson_type VARCHAR(50) NOT NULL, -- kanji, vocabulary, grammar, conversation
    jlpt_level VARCHAR(10) NOT NULL,
    order_index INTEGER NOT NULL,
    content JSONB NOT NULL, -- Flexible lesson content
    exercises JSONB, -- Associated exercises
    estimated_duration INTEGER, -- minutes
    prerequisites JSONB, -- Array of prerequisite lesson IDs
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Flashcards (SRS items)
CREATE TABLE flashcards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content_type VARCHAR(50) NOT NULL, -- kanji, vocabulary, grammar
    content_id UUID NOT NULL, -- References kanji, vocabulary, or grammar_points
    
    -- SRS algorithm fields (SM-2)
    ease_factor DECIMAL(3,2) DEFAULT 2.50,
    interval_days INTEGER DEFAULT 0,
    repetitions INTEGER DEFAULT 0,
    last_reviewed TIMESTAMP,
    next_review TIMESTAMP NOT NULL,
    
    -- Performance tracking
    correct_count INTEGER DEFAULT 0,
    incorrect_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, content_type, content_id)
);

-- User review history
CREATE TABLE review_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flashcard_id UUID REFERENCES flashcards(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    quality INTEGER NOT NULL, -- 0-5 rating
    time_spent INTEGER NOT NULL, -- seconds
    reviewed_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_reviews (user_id, reviewed_at)
);

-- Conversation sessions
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    scenario VARCHAR(255), -- e.g., "restaurant", "business_meeting"
    difficulty_level VARCHAR(10),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    corrections_count INTEGER DEFAULT 0,
    duration_seconds INTEGER
);

-- Conversation messages
CREATE TABLE conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL, -- user, assistant
    content TEXT NOT NULL,
    has_correction BOOLEAN DEFAULT FALSE,
    correction_data JSONB, -- Detailed correction information
    created_at TIMESTAMP DEFAULT NOW()
);

-- User achievements
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL, -- streak, mastery, conversation, milestone
    requirement JSONB NOT NULL, -- Conditions to unlock
    badge_icon VARCHAR(255),
    xp_reward INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User unlocked achievements
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, achievement_id)
);
```

#### Indexes for Performance

```sql
-- Flashcard indexes (critical for SRS queries)
CREATE INDEX idx_flashcards_user_next_review 
    ON flashcards(user_id, next_review);
    
CREATE INDEX idx_flashcards_user_content 
    ON flashcards(user_id, content_type, content_id);

-- Review history indexes
CREATE INDEX idx_review_history_user_date 
    ON review_history(user_id, reviewed_at DESC);

-- Conversation indexes
CREATE INDEX idx_conversation_sessions_user 
    ON conversation_sessions(user_id, started_at DESC);
    
CREATE INDEX idx_conversation_messages_session 
    ON conversation_messages(session_id, created_at);

-- Content lookup indexes
CREATE INDEX idx_kanji_level 
    ON kanji(jlpt_level, frequency_rank);
    
CREATE INDEX idx_vocabulary_level 
    ON vocabulary(jlpt_level, frequency_rank);
    
CREATE INDEX idx_lessons_level_order 
    ON lessons(jlpt_level, order_index);
```

### Redis Data Structures

#### Session Management
```
Key: session:{session_id}
Type: Hash
TTL: 24 hours
Fields:
  - user_id
  - email
  - created_at
  - last_activity
```

#### SRS Review Queue
```
Key: srs:queue:{user_id}
Type: Sorted Set
Score: next_review_timestamp
Members: flashcard_id

Used to efficiently retrieve due flashcards
```

#### API Rate Limiting
```
Key: rate_limit:{user_id}:{endpoint}
Type: String (counter)
TTL: 1 hour
```

#### Conversation Context Cache
```
Key: conversation:context:{session_id}
Type: String (JSON)
TTL: 1 hour
Value: Serialized conversation history
```

#### AI Response Cache
```
Key: ai:response:{hash_of_prompt}
Type: String (JSON)
TTL: 24 hours
Value: Cached AI response for identical prompts
```

---

## AI Integration Architecture

### AI Services Overview

The platform integrates with three primary AI services, all configurable via environment variables:

1. **Conversation AI** (Claude Sonnet 4.5)
2. **Speech-to-Text** (OpenAI Whisper)
3. **Text-to-Speech** (Google Cloud TTS)

### Service Abstraction Layer

```python
# app/services/ai/base.py
from abc import ABC, abstractmethod

class ConversationAI(ABC):
    @abstractmethod
    async def get_response(
        self, 
        messages: List[Message], 
        system_prompt: str
    ) -> ConversationResponse:
        pass

class SpeechToText(ABC):
    @abstractmethod
    async def transcribe(
        self, 
        audio_data: bytes, 
        language: str = "ja"
    ) -> TranscriptionResult:
        pass

class TextToSpeech(ABC):
    @abstractmethod
    async def synthesize(
        self, 
        text: str, 
        voice: str, 
        speed: float = 1.0
    ) -> AudioBytes:
        pass
```

### Conversation AI Implementation

```python
# app/services/ai/conversation.py
from anthropic import AsyncAnthropic

class ClaudeConversationAI(ConversationAI):
    def __init__(self, api_key: str, model: str, base_url: str):
        self.client = AsyncAnthropic(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
    
    async def get_response(
        self, 
        messages: List[Message],
        system_prompt: str
    ) -> ConversationResponse:
        """
        Get conversation response with corrections.
        
        Returns:
            ConversationResponse with:
            - response: Japanese text response
            - correction: Optional correction with explanation
            - encouragement: Positive feedback
        """
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[m.to_dict() for m in messages],
            max_tokens=1000
        )
        
        return self._parse_response(response.content[0].text)
```

### Prompt Engineering Strategy

All prompts are stored in versioned template files for:
- Version control and tracking
- A/B testing capabilities
- Easy updates without code changes
- Regression testing

**Prompt Categories:**

1. **Conversation Prompts** (`prompts/conversation_prompts.py`)
   - General conversation
   - Scenario-based dialogue (restaurant, business, travel)
   - Proficiency-adjusted responses

2. **Correction Prompts** (`prompts/correction_prompts.py`)
   - Grammar error identification
   - Particle usage corrections
   - Politeness level guidance
   - Natural phrasing suggestions

3. **Content Generation Prompts** (`prompts/content_generation_prompts.py`)
   - Lesson creation
   - Example sentence generation
   - Grammar explanations
   - Cultural context notes

### Example: Conversation Correction Prompt

```python
# backend/app/prompts/correction_prompts.py

CONVERSATION_CORRECTION_SYSTEM_PROMPT = """
You are a patient and encouraging Japanese language tutor helping a student practice conversation.

Student Context:
- Current Proficiency: {proficiency_level}
- Learning Goal: Business communication in Japan
- Native Language: {native_language}

Your Role:
1. Respond naturally in Japanese to continue the conversation
2. Gently correct errors without discouraging the student
3. Focus on 1-2 key issues per message (avoid overwhelming)
4. Provide brief explanations in {native_language}
5. Encourage and acknowledge effort

Response Format:
<response>Your natural Japanese response here</response>
<correction>
If there are errors:
- What they said: [original]
- Better way: [corrected]
- Why: [brief explanation in {native_language}]
</correction>
<encouragement>Brief positive feedback in {native_language}</encouragement>

Guidelines:
- Prioritize communication over perfection at early levels
- For N5/N4: Focus on basic grammar and essential particles
- For N3/N2: Address nuance, formality, and natural expression
- Always be constructive and supportive
"""

CONVERSATION_USER_PROMPT_TEMPLATE = """
Previous conversation context:
{conversation_history}

Student's current message: {user_message}

Please respond naturally while providing helpful corrections if needed.
"""
```

### Content Generation Prompt Examples

```python
# backend/app/prompts/content_generation_prompts.py

LESSON_GENERATION_PROMPT = """
Generate a complete {lesson_type} lesson for JLPT {jlpt_level} level.

Requirements:
1. Title: Clear and descriptive
2. Learning Objectives: 3-5 specific, measurable goals
3. Content Structure:
   - Introduction (context and motivation)
   - Core Teaching (explanations with examples)
   - Practice Exercises (5-10 interactive exercises)
   - Summary (key takeaways)
4. Estimated Duration: Realistic time estimate
5. Prerequisites: Required prior knowledge

Focus Areas for {jlpt_level}:
{level_specific_guidance}

Output Format (JSON):
{{
  "title": "Lesson title in English",
  "title_ja": "レッスンタイトル",
  "objectives": ["objective 1", "objective 2", ...],
  "introduction": {{
    "text": "Introduction text",
    "text_ja": "日本語の紹介"
  }},
  "content": [
    {{
      "type": "explanation|example|note",
      "text": "Content in English",
      "text_ja": "日本語のコンテンツ",
      "audio_text": "Text for TTS generation"
    }}
  ],
  "exercises": [
    {{
      "type": "multiple_choice|fill_blank|translation",
      "question": "Question text",
      "question_ja": "質問",
      "options": ["option1", "option2", ...],
      "correct_answer": "correct answer",
      "explanation": "Why this is correct"
    }}
  ],
  "summary": "Key takeaways",
  "estimated_minutes": 20
}}

Generate comprehensive, pedagogically sound content that builds on previous lessons.
"""

EXAMPLE_SENTENCE_GENERATION_PROMPT = """
Generate {count} example sentences demonstrating the usage of: {target_word}

Requirements:
1. Natural, conversational Japanese
2. Appropriate for {jlpt_level} learners
3. Diverse contexts (daily life, work, social situations)
4. Progressive difficulty (simple → complex)
5. Include translations and notes

Output Format (JSON):
{{
  "sentences": [
    {{
      "japanese": "Example sentence in Japanese",
      "reading": "ふりがな付きの文",
      "romaji": "Romaji version",
      "translation": "English translation",
      "context": "Brief context note",
      "audio_text": "Sentence for TTS"
    }}
  ]
}}

Focus on practical, real-world usage that helps learners understand when and how to use this word.
"""

GRAMMAR_EXPLANATION_PROMPT = """
Create a comprehensive explanation for the grammar point: {grammar_pattern}

Target Level: {jlpt_level}

Structure:
1. Pattern Definition
   - Japanese: {grammar_pattern}
   - Meaning: Clear explanation
   - Formation: How to construct it

2. Usage Rules
   - When to use (contexts)
   - When NOT to use (common mistakes)
   - Formality level

3. Examples (5-7 examples)
   - Simple sentences
   - Complex sentences
   - Common collocations

4. Comparison with Similar Patterns
   - How it differs from {similar_pattern_1}
   - How it differs from {similar_pattern_2}

5. Common Mistakes
   - What learners typically get wrong
   - How to avoid these mistakes

6. Cultural Notes (if applicable)
   - Any cultural context needed
   - Usage in business vs. casual settings

Output as structured JSON with separate fields for English and Japanese content.
Ensure explanations are clear, concise, and pedagogically effective.
"""
```

### AI Service Configuration

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Conversation AI
    CONVERSATION_AI_PROVIDER: str = "anthropic"
    ANTHROPIC_API_KEY: str
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com"
    
    # Speech-to-Text
    STT_PROVIDER: str = "openai"
    OPENAI_API_KEY: str
    OPENAI_STT_MODEL: str = "whisper-1"
    OPENAI_BASE_URL: str = "https://api.openai.com"
    
    # Text-to-Speech
    TTS_PROVIDER: str = "google"
    GOOGLE_CLOUD_TTS_KEY: str
    GOOGLE_TTS_VOICE: str = "ja-JP-Neural2-B"
    GOOGLE_TTS_BASE_URL: str = "https://texttospeech.googleapis.com"
    
    # AI Behavior
    CONVERSATION_MAX_CONTEXT: int = 20  # messages
    CONVERSATION_CACHE_TTL: int = 3600  # seconds
    AI_RESPONSE_TIMEOUT: int = 30  # seconds
    
    # Rate Limiting
    AI_CALLS_PER_USER_PER_HOUR: int = 100
    
    class Config:
        env_file = ".env"
```

---

## Frontend Architecture

### Next.js App Router Structure

```
frontend/app/
├── (auth)/                    # Auth layout group
│   ├── login/
│   │   └── page.tsx
│   └── register/
│       └── page.tsx
├── (dashboard)/              # Authenticated layout group
│   ├── layout.tsx            # Shared dashboard layout
│   ├── page.tsx              # Dashboard home
│   ├── lessons/
│   │   ├── page.tsx          # Lesson list
│   │   ├── [id]/
│   │   │   └── page.tsx      # Individual lesson
│   │   └── practice/
│   │       └── page.tsx      # Practice session
│   ├── conversation/
│   │   ├── page.tsx          # Conversation home
│   │   └── [sessionId]/
│   │       └── page.tsx      # Active conversation
│   ├── progress/
│   │   └── page.tsx          # Progress dashboard
│   ├── flashcards/
│   │   └── page.tsx          # SRS review
│   └── settings/
│       └── page.tsx          # User settings
├── api/                      # API routes (minimal, proxy to backend)
│   └── auth/
│       └── [...nextauth].ts
├── layout.tsx                # Root layout
├── page.tsx                  # Landing page
└── globals.css              # Global styles
```

### Component Architecture

**Component Hierarchy:**

```
components/
├── ui/                       # shadcn/ui base components
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── input.tsx
│   └── ...
├── layout/
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── Footer.tsx
│   └── DashboardLayout.tsx
├── flashcards/
│   ├── FlashCard.tsx         # Single flashcard display
│   ├── FlashCardDeck.tsx     # Deck manager
│   ├── ReviewControls.tsx    # Rating buttons
│   └── ProgressRing.tsx      # Visual progress indicator
├── conversation/
│   ├── ConversationInterface.tsx  # Main chat UI
│   ├── MessageBubble.tsx          # Single message
│   ├── CorrectionDisplay.tsx      # Show corrections
│   ├── SpeechInput.tsx            # Mic input
│   └── ScenarioSelector.tsx       # Choose conversation topic
├── progress/
│   ├── StreakDisplay.tsx
│   ├── LevelProgress.tsx
│   ├── StudyTimeChart.tsx
│   └── AchievementGrid.tsx
└── lessons/
    ├── LessonCard.tsx
    ├── ExerciseRenderer.tsx   # Dynamic exercise display
    ├── KanjiDisplay.tsx
    └── VocabularyCard.tsx
```

### State Management Strategy

**Server State (TanStack Query):**
- All data from backend API
- Automatic caching and revalidation
- Optimistic updates for better UX

```typescript
// hooks/useFlashcards.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useFlashcards() {
  const queryClient = useQueryClient();
  
  // Fetch due flashcards
  const { data: dueCards, isLoading } = useQuery({
    queryKey: ['flashcards', 'due'],
    queryFn: () => api.get('/api/flashcards/due'),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
  
  // Record review
  const reviewMutation = useMutation({
    mutationFn: (review: ReviewData) => 
      api.post('/api/flashcards/review', review),
    onMutate: async (review) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['flashcards', 'due'] });
      const previous = queryClient.getQueryData(['flashcards', 'due']);
      
      queryClient.setQueryData(['flashcards', 'due'], (old: Card[]) =>
        old.filter(card => card.id !== review.cardId)
      );
      
      return { previous };
    },
    onError: (err, review, context) => {
      // Rollback on error
      queryClient.setQueryData(['flashcards', 'due'], context.previous);
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['flashcards'] });
    },
  });
  
  return { dueCards, isLoading, reviewMutation };
}
```

**Client State (Zustand):**
- UI state (modals, menus, theme)
- Temporary form data
- User preferences

```typescript
// stores/uiStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  audioEnabled: boolean;
  toggleTheme: () => void;
  toggleSidebar: () => void;
  toggleAudio: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      theme: 'light',
      sidebarOpen: true,
      audioEnabled: true,
      toggleTheme: () => set((state) => ({ 
        theme: state.theme === 'light' ? 'dark' : 'light' 
      })),
      toggleSidebar: () => set((state) => ({ 
        sidebarOpen: !state.sidebarOpen 
      })),
      toggleAudio: () => set((state) => ({ 
        audioEnabled: !state.audioEnabled 
      })),
    }),
    {
      name: 'ui-storage',
    }
  )
);
```

### PWA Configuration

```javascript
// next.config.js
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/api\./,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'api-cache',
        expiration: {
          maxEntries: 50,
          maxAgeSeconds: 5 * 60, // 5 minutes
        },
      },
    },
    {
      urlPattern: /\.(?:jpg|jpeg|png|gif|svg|webp)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'image-cache',
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 30 * 24 * 60 * 60, // 30 days
        },
      },
    },
  ],
});

module.exports = withPWA({
  reactStrictMode: true,
  // other Next.js config
});
```

```json
// public/manifest.json
{
  "name": "Nihongo Sensei - Japanese Learning",
  "short_name": "Nihongo Sensei",
  "description": "AI-powered Japanese language learning platform",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3B82F6",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/home.png",
      "sizes": "1280x720",
      "type": "image/png"
    }
  ]
}
```

---

## Backend Architecture

### FastAPI Application Structure

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.api import auth, lessons, conversation, flashcards, progress, speech
from app.database import engine
from app.config import settings

app = FastAPI(
    title="Nihongo Sensei API",
    description="AI-powered Japanese learning platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(auth.router)
app.include_router(lessons.router)
app.include_router(conversation.router)
app.include_router(flashcards.router)
app.include_router(progress.router)
app.include_router(speech.router)

@app.on_event("startup")
async def startup():
    # Initialize database connection pool
    # Load initial data if needed
    pass

@app.on_event("shutdown")
async def shutdown():
    # Clean up resources
    pass

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Dependency Injection Pattern

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validate JWT token and return current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
```

### Service Layer Example

```python
# app/services/srs_service.py
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.flashcard import Flashcard, ReviewHistory
from app.schemas.flashcard import ReviewRequest, ReviewResponse

class SRSService:
    """
    Spaced Repetition System implementation using SM-2 algorithm.
    
    Quality ratings (0-5):
    0: Complete blackout
    1: Incorrect with correct answer recognizable
    2: Incorrect but correct answer remembered
    3: Correct but difficult
    4: Correct with hesitation
    5: Perfect recall
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_due_cards(
        self, 
        user_id: str, 
        limit: int = 20
    ) -> List[Flashcard]:
        """Retrieve flashcards due for review."""
        query = (
            select(Flashcard)
            .where(
                Flashcard.user_id == user_id,
                Flashcard.next_review <= datetime.utcnow()
            )
            .order_by(Flashcard.next_review)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def record_review(
        self, 
        flashcard_id: str,
        user_id: str,
        quality: int,
        time_spent: int
    ) -> ReviewResponse:
        """
        Record a review and update SRS parameters.
        
        SM-2 Algorithm:
        - EF' = EF + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        - If quality >= 3: interval = interval * EF
        - If quality < 3: reset to day 1
        """
        # Get flashcard
        flashcard = await self.db.get(Flashcard, flashcard_id)
        if flashcard.user_id != user_id:
            raise ValueError("Unauthorized access to flashcard")
        
        # Update performance tracking
        if quality >= 3:
            flashcard.correct_count += 1
        else:
            flashcard.incorrect_count += 1
        
        # Calculate new ease factor
        old_ef = flashcard.ease_factor
        new_ef = old_ef + (
            0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        )
        # Clamp EF between 1.3 and 2.5
        flashcard.ease_factor = max(1.3, min(2.5, new_ef))
        
        # Calculate new interval
        if quality >= 3:
            # Correct answer - increase interval
            if flashcard.repetitions == 0:
                flashcard.interval_days = 1
            elif flashcard.repetitions == 1:
                flashcard.interval_days = 6
            else:
                flashcard.interval_days = int(
                    flashcard.interval_days * flashcard.ease_factor
                )
            flashcard.repetitions += 1
        else:
            # Incorrect answer - reset
            flashcard.repetitions = 0
            flashcard.interval_days = 1
        
        # Update review timestamps
        flashcard.last_reviewed = datetime.utcnow()
        flashcard.next_review = (
            datetime.utcnow() + timedelta(days=flashcard.interval_days)
        )
        
        # Save review history
        history = ReviewHistory(
            flashcard_id=flashcard_id,
            user_id=user_id,
            quality=quality,
            time_spent=time_spent
        )
        self.db.add(history)
        
        await self.db.commit()
        await self.db.refresh(flashcard)
        
        return ReviewResponse(
            flashcard_id=flashcard_id,
            next_review=flashcard.next_review,
            interval_days=flashcard.interval_days,
            ease_factor=flashcard.ease_factor
        )
```

---

## Infrastructure Architecture

### Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: nihongo_postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - nihongo_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: nihongo_redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - nihongo_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: nihongo_backend
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://redis:6379
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GOOGLE_CLOUD_TTS_KEY: ${GOOGLE_CLOUD_TTS_KEY}
    volumes:
      - ./backend/app:/app/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - nihongo_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        NEXT_PUBLIC_API_URL: http://backend:8000
    container_name: nihongo_frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - nihongo_network
    environment:
      NODE_ENV: production

  nginx:
    image: nginx:alpine
    container_name: nihongo_nginx
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
    networks:
      - nihongo_network

volumes:
  postgres_data:
  redis_data:

networks:
  nihongo_network:
    driver: bridge
```

### Nginx Configuration

```nginx
# docker/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=general_limit:10m rate=50r/s;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    server {
        listen 80;
        server_name _;
        
        # Redirect HTTP to HTTPS in production
        # return 301 https://$host$request_uri;
        
        # Development: allow HTTP
        client_max_body_size 10M;
        
        # Frontend routes
        location / {
            limit_req zone=general_limit burst=20 nodelay;
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
        
        # Backend API routes
        location /api/ {
            limit_req zone=api_limit burst=5 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers (if needed)
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }
        
        # API docs
        location /docs {
            proxy_pass http://backend/docs;
            proxy_set_header Host $host;
        }
        
        # Health check
        location /health {
            access_log off;
            proxy_pass http://backend/health;
        }
    }
    
    # HTTPS configuration (production)
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers HIGH:!aNULL:!MD5;
    #     
    #     # ... rest of configuration
    # }
}
```

---

## Security Architecture

### Authentication Flow

```
┌─────────┐                    ┌──────────┐                    ┌──────────┐
│ Browser │                    │ Backend  │                    │ Database │
└────┬────┘                    └────┬─────┘                    └────┬─────┘
     │                              │                                │
     │ 1. POST /api/auth/register   │                                │
     │  { email, password }         │                                │
     │─────────────────────────────>│                                │
     │                              │                                │
     │                              │ 2. Hash password (bcrypt)      │
     │                              │                                │
     │                              │ 3. CREATE user                 │
     │                              │───────────────────────────────>│
     │                              │                                │
     │                              │ 4. User created                │
     │                              │<───────────────────────────────│
     │                              │                                │
     │ 5. { user_id, message }      │                                │
     │<─────────────────────────────│                                │
     │                              │                                │
     │ 6. POST /api/auth/login      │                                │
     │  { email, password }         │                                │
     │─────────────────────────────>│                                │
     │                              │                                │
     │                              │ 7. SELECT user WHERE email     │
     │                              │───────────────────────────────>│
     │                              │                                │
     │                              │ 8. User record                 │
     │                              │<───────────────────────────────│
     │                              │                                │
     │                              │ 9. Verify password (bcrypt)    │
     │                              │                                │
     │                              │ 10. Generate JWT token         │
     │                              │     (user_id, exp: 30 min)     │
     │                              │                                │
     │                              │ 11. Store session in Redis     │
     │                              │     TTL: 24 hours              │
     │                              │                                │
     │ 12. { access_token, user }   │                                │
     │<─────────────────────────────│                                │
     │                              │                                │
     │ 13. Store token (localStorage│                                │
     │     or secure cookie)        │                                │
     │                              │                                │
     │ 14. GET /api/lessons (with   │                                │
     │     Authorization: Bearer    │                                │
     │     <token>)                 │                                │
     │─────────────────────────────>│                                │
     │                              │                                │
     │                              │ 15. Validate JWT signature     │
     │                              │                                │
     │                              │ 16. Check session in Redis     │
     │                              │                                │
     │                              │ 17. Return protected resource  │
     │                              │                                │
     │ 18. { lessons: [...] }       │                                │
     │<─────────────────────────────│                                │
     │                              │                                │
```

### Security Measures

1. **Password Security**
   - Bcrypt hashing with salt
   - Minimum password requirements (12+ chars, complexity)
   - No password stored in plaintext anywhere

2. **Token Security**
   - JWT tokens with short expiration (30 minutes)
   - Refresh token mechanism (24 hours)
   - Token blacklist on logout (Redis)

3. **API Security**
   - Rate limiting per user/IP
   - Input validation on all endpoints (Pydantic)
   - SQL injection prevention (ORM, parameterized queries)
   - XSS prevention (React escaping, CSP headers)

4. **Database Security**
   - Encrypted connections (SSL)
   - Principle of least privilege (app user limited permissions)
   - Regular backups
   - No direct database exposure

5. **Infrastructure Security**
   - HTTPS enforcement in production
   - Docker container isolation
   - No hardcoded secrets (environment variables)
   - Security headers (HSTS, CSP, X-Frame-Options)

---

## Performance Architecture

### Caching Strategy

**Multi-Layer Caching:**

1. **Browser Cache** (Frontend)
   - Static assets (CSS, JS, images): 1 year
   - PWA service worker: Offline content

2. **CDN Cache** (Future - Production)
   - Static assets globally distributed
   - Reduced latency for users

3. **Application Cache** (Redis)
   - API responses: 5-60 minutes depending on data
   - Session data: 24 hours
   - AI responses: 24 hours (expensive to regenerate)

4. **Database Query Cache** (PostgreSQL)
   - Prepared statement caching
   - Connection pooling

**Cache Invalidation Strategy:**
- Time-based expiration (TTL)
- Event-based invalidation (user updates trigger clear)
- Cache tags for related data groups

### Database Optimization

1. **Indexes** (See Data Architecture section)
   - Strategic indexes on frequently queried columns
   - Composite indexes for common query patterns
   - Periodic index maintenance

2. **Query Optimization**
   - Use EXPLAIN ANALYZE for slow queries
   - Avoid N+1 queries (eager loading with SQLAlchemy)
   - Pagination for large result sets

3. **Connection Pooling**
   ```python
   # SQLAlchemy connection pool
   engine = create_async_engine(
       DATABASE_URL,
       pool_size=10,          # Base connection pool
       max_overflow=20,        # Additional connections when needed
       pool_pre_ping=True,     # Verify connections before use
       pool_recycle=3600       # Recycle connections after 1 hour
   )
   ```

### API Performance

**Response Time Budget:**
- Simple GET: <50ms
- Complex queries: <200ms
- AI conversation: <3s
- Speech transcription: <5s

**Optimization Techniques:**
1. **Async/Await** - Non-blocking I/O
2. **Background Tasks** - Offload heavy work (FastAPI BackgroundTasks)
3. **Compression** - Gzip for responses >1KB
4. **Pagination** - Limit result set size
5. **Field Selection** - Return only requested fields

---

## Testing Architecture

### Test Pyramid

```
               /\
              /  \
            /  E2E \          < 5% - Full user journeys
           /--------\
          /          \
         / Integration\       < 25% - API + DB + Services
        /--------------\
       /                \
      /   Unit Tests     \    < 70% - Functions, utilities, logic
     /--------------------\
```

### Test Organization

**Backend Tests:**
```
tests/
├── unit/                      # Fast, isolated tests
│   ├── test_srs_algorithm.py
│   ├── test_kanji_utils.py
│   ├── test_auth_utils.py
│   └── test_validators.py
├── integration/               # API + database tests
│   ├── test_api_auth.py
│   ├── test_api_lessons.py
│   ├── test_api_conversation.py
│   └── test_database.py
├── e2e/                       # End-to-end flows
│   ├── test_user_registration.py
│   ├── test_learning_session.py
│   └── test_srs_workflow.py
├── fixtures/                  # Shared test data
│   ├── users.py
│   ├── content.py
│   └── ai_responses.py
└── conftest.py               # Pytest configuration
```

**Frontend Tests:**
```
__tests__/
├── unit/
│   ├── utils/
│   │   ├── srsScheduler.test.ts
│   │   └── japaneseUtils.test.ts
│   └── hooks/
│       ├── useSRS.test.ts
│       └── useConversation.test.ts
├── components/
│   ├── FlashCard.test.tsx
│   ├── ConversationInterface.test.tsx
│   └── ProgressDashboard.test.tsx
└── e2e/
    ├── login.spec.ts
    ├── lesson-flow.spec.ts
    └── conversation.spec.ts
```

### Test Data Management

```python
# tests/fixtures/content.py
import pytest

@pytest.fixture
def sample_kanji():
    """Sample kanji for testing."""
    return {
        "character": "水",
        "meanings": ["water", "cold water"],
        "on_readings": ["スイ"],
        "kun_readings": ["みず"],
        "jlpt_level": "N5",
        "stroke_count": 4
    }

@pytest.fixture
async def test_user(db_session):
    """Create a test user in database."""
    user = User(
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        full_name="Test User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
```

---

## Deployment Considerations

### Production Checklist

- [ ] All environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Backup strategy implemented
- [ ] Monitoring configured
- [ ] Error logging set up
- [ ] Rate limiting configured
- [ ] Security headers enabled
- [ ] CORS properly configured
- [ ] Health check endpoints working

### Scalability Path

**Phase 1: Single Server (MVP)**
- All services on one machine
- Suitable for 100-500 users

**Phase 2: Vertical Scaling**
- Upgrade server resources
- Suitable for 500-2000 users

**Phase 3: Horizontal Scaling** (Future)
- Multiple backend instances behind load balancer
- Separate database server
- Redis cluster
- Suitable for 2000+ users

---

**Document Status:** Complete  
**Next Steps:** Review architecture, approve technical approach, proceed to implementation planning

