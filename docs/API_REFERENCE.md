# API Reference

Complete API documentation for Nihongo Sensei backend.

**Base URL:** `http://localhost:8000` (development)
**API Version:** v1
**Documentation:** http://localhost:8000/docs (Swagger UI)

## Table of Contents

- [Authentication](#authentication)
- [Lessons](#lessons)
- [Flashcards](#flashcards)
- [Conversation](#conversation)
- [Progress](#progress)
- [Health & Monitoring](#health--monitoring)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Pagination](#pagination)

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### POST /api/auth/register

Register a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "username": "learner123",
  "password": "SecurePass123!",
  "native_language": "en",
  "target_jlpt_level": "N3"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "learner123",
  "native_language": "en",
  "target_jlpt_level": "N3",
  "created_at": "2025-11-19T12:00:00Z"
}
```

**Errors:**
- `400` - Invalid input (email format, weak password)
- `409` - Email or username already exists

---

### POST /api/auth/login

Authenticate and receive JWT token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "learner123"
  }
}
```

**Errors:**
- `400` - Missing credentials
- `401` - Invalid credentials
- `429` - Too many login attempts

---

### GET /api/auth/me

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "learner123",
  "native_language": "en",
  "target_jlpt_level": "N3",
  "created_at": "2025-11-19T12:00:00Z",
  "study_streak": 7,
  "total_reviews": 342
}
```

**Errors:**
- `401` - Invalid or expired token

---

### PUT /api/auth/me

Update user profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "username": "newusername",
  "native_language": "en",
  "target_jlpt_level": "N2"
}
```

**Response (200 OK):**

```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "newusername",
  "native_language": "en",
  "target_jlpt_level": "N2",
  "updated_at": "2025-11-19T12:30:00Z"
}
```

**Errors:**
- `400` - Invalid input
- `401` - Unauthorized
- `409` - Username already taken

---

## Lessons

### GET /api/lessons

Retrieve list of lessons.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| level | string | No | Filter by JLPT level (N5, N4, N3, N2, N1) |
| category | string | No | Filter by category (grammar, vocabulary, kanji) |
| limit | integer | No | Results per page (default: 20, max: 100) |
| offset | integer | No | Pagination offset (default: 0) |

**Example Request:**

```
GET /api/lessons?level=N5&category=grammar&limit=10&offset=0
```

**Response (200 OK):**

```json
{
  "total": 45,
  "limit": 10,
  "offset": 0,
  "items": [
    {
      "id": "hiragana-01",
      "title": "Hiragana Basics",
      "description": "Introduction to hiragana characters",
      "level": "N5",
      "category": "writing",
      "order_index": 1,
      "estimated_duration_minutes": 30,
      "is_completed": false,
      "created_at": "2025-11-19T10:00:00Z"
    }
  ]
}
```

**Errors:**
- `400` - Invalid query parameters
- `401` - Unauthorized

---

### GET /api/lessons/{lesson_id}

Get detailed information about a specific lesson.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "id": "hiragana-01",
  "title": "Hiragana Basics",
  "description": "Introduction to hiragana characters",
  "level": "N5",
  "category": "writing",
  "content": {
    "introduction": "Hiragana is one of the basic Japanese writing systems...",
    "sections": [
      {
        "title": "Basic Characters",
        "content": "Let's start with あ、い、う、え、お...",
        "exercises": [
          {
            "type": "matching",
            "question": "Match the hiragana to romaji",
            "options": ["あ", "い", "う"],
            "answers": ["a", "i", "u"]
          }
        ]
      }
    ]
  },
  "vocabulary": [
    {
      "word": "ありがとう",
      "reading": "arigatou",
      "meaning": "thank you",
      "part_of_speech": "expression"
    }
  ],
  "grammar_points": [],
  "kanji": [],
  "flashcard_count": 15,
  "estimated_duration_minutes": 30,
  "prerequisites": [],
  "next_lessons": ["hiragana-02"]
}
```

**Errors:**
- `401` - Unauthorized
- `404` - Lesson not found

---

### POST /api/lessons

Create a new lesson (admin only).

**Headers:**
```
Authorization: Bearer <admin_token>
```

**Request Body:**

```json
{
  "id": "custom-lesson-01",
  "title": "Custom Lesson",
  "description": "A custom lesson",
  "level": "N5",
  "category": "grammar",
  "content": { /* lesson content */ },
  "order_index": 100
}
```

**Response (201 Created):**

```json
{
  "id": "custom-lesson-01",
  "title": "Custom Lesson",
  "created_at": "2025-11-19T13:00:00Z"
}
```

**Errors:**
- `400` - Invalid lesson data
- `401` - Unauthorized
- `403` - Forbidden (not admin)
- `409` - Lesson ID already exists

---

## Flashcards

### GET /api/flashcards/due

Get flashcards due for review.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Max cards to return (default: 20) |
| card_type | string | No | Filter by type (vocabulary, kanji, grammar) |

**Response (200 OK):**

```json
{
  "total_due": 15,
  "cards": [
    {
      "id": 1234,
      "front": "水",
      "back": "water",
      "readings": ["みず", "すい"],
      "card_type": "kanji",
      "srs_level": 3,
      "ease_factor": 2.5,
      "interval_days": 7,
      "next_review": "2025-11-19T14:00:00Z",
      "total_reviews": 5,
      "correct_reviews": 4
    }
  ]
}
```

**Errors:**
- `401` - Unauthorized

---

### POST /api/flashcards/review

Submit a flashcard review.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "card_id": 1234,
  "quality": 4,
  "time_spent_seconds": 8
}
```

**Quality Scale:**
- `0` - Complete blackout
- `1` - Incorrect, but familiar
- `2` - Incorrect, but easy to recall
- `3` - Correct, but difficult
- `4` - Correct, with hesitation
- `5` - Perfect recall

**Response (200 OK):**

```json
{
  "card_id": 1234,
  "quality": 4,
  "new_interval_days": 14,
  "new_ease_factor": 2.6,
  "next_review": "2025-12-03T14:00:00Z",
  "srs_level": 4,
  "review_recorded_at": "2025-11-19T14:05:00Z"
}
```

**Errors:**
- `400` - Invalid quality value
- `401` - Unauthorized
- `404` - Card not found

---

### GET /api/flashcards/stats

Get study statistics.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "total_cards": 342,
  "cards_due_today": 15,
  "cards_learned": 298,
  "cards_learning": 32,
  "cards_mature": 12,
  "study_streak_days": 7,
  "total_reviews_today": 25,
  "estimated_review_time_minutes": 12,
  "accuracy_rate": 0.87,
  "average_ease_factor": 2.45
}
```

**Errors:**
- `401` - Unauthorized

---

### POST /api/flashcards

Create a custom flashcard.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "front": "日本語",
  "back": "Japanese language",
  "readings": ["にほんご"],
  "card_type": "vocabulary",
  "notes": "Personal note",
  "tags": ["language", "basic"]
}
```

**Response (201 Created):**

```json
{
  "id": 5678,
  "front": "日本語",
  "back": "Japanese language",
  "readings": ["にほんご"],
  "card_type": "vocabulary",
  "created_at": "2025-11-19T14:10:00Z",
  "next_review": "2025-11-19T14:10:00Z"
}
```

**Errors:**
- `400` - Invalid card data
- `401` - Unauthorized

---

## Conversation

### POST /api/conversation/message

Send a message to the AI conversation partner.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "message": "こんにちは！元気ですか？",
  "context": {
    "scenario": "casual",
    "difficulty": "beginner"
  }
}
```

**Response (200 OK):**

```json
{
  "id": "msg_123456",
  "user_message": "こんにちは！元気ですか？",
  "ai_response": "こんにちは！元気です、ありがとう。あなたは？",
  "corrections": [
    {
      "original": "元気ですか",
      "suggestion": "お元気ですか",
      "explanation": "Use お before 元気 for politeness",
      "severity": "minor"
    }
  ],
  "vocabulary_notes": [
    {
      "word": "元気",
      "reading": "げんき",
      "meaning": "healthy, energetic",
      "usage_note": "Common greeting expression"
    }
  ],
  "timestamp": "2025-11-19T14:15:00Z"
}
```

**Errors:**
- `400` - Invalid message format
- `401` - Unauthorized
- `429` - Rate limit exceeded

---

### GET /api/conversation/history

Retrieve conversation history.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| limit | integer | No | Messages to return (default: 50) |
| offset | integer | No | Pagination offset |

**Response (200 OK):**

```json
{
  "total": 125,
  "messages": [
    {
      "id": "msg_123456",
      "user_message": "こんにちは！",
      "ai_response": "こんにちは！元気です。",
      "corrections_count": 0,
      "timestamp": "2025-11-19T14:15:00Z"
    }
  ]
}
```

**Errors:**
- `401` - Unauthorized

---

### DELETE /api/conversation/history

Clear conversation history.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (204 No Content)**

**Errors:**
- `401` - Unauthorized

---

## Health & Monitoring

### GET /health

Health check endpoint (no authentication required).

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "Nihongo Sensei API",
  "version": "0.1.0",
  "timestamp": "2025-11-19T14:20:00Z",
  "database": "connected",
  "redis": "connected"
}
```

---

### GET /

Root API information (no authentication required).

**Response (200 OK):**

```json
{
  "message": "Welcome to Nihongo Sensei API",
  "version": "0.1.0",
  "docs": "/docs"
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    },
    "timestamp": "2025-11-19T14:25:00Z"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 204 | No Content | Success, no response body |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource already exists |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily down |

### Common Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `AUTHENTICATION_ERROR` | Invalid credentials |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `CONFLICT` | Resource already exists |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `INTERNAL_ERROR` | Server error |

---

## Rate Limiting

API requests are rate-limited to prevent abuse.

**Limits:**
- **Authentication endpoints:** 5 requests per minute
- **Conversation endpoints:** 20 requests per minute
- **Other endpoints:** 100 requests per minute

**Rate Limit Headers:**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1637338800
```

**Rate Limit Exceeded Response (429):**

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again later.",
    "retry_after_seconds": 45
  }
}
```

---

## Pagination

List endpoints support pagination via `limit` and `offset` parameters.

**Parameters:**

| Parameter | Type | Default | Max |
|-----------|------|---------|-----|
| limit | integer | 20 | 100 |
| offset | integer | 0 | - |

**Response Format:**

```json
{
  "total": 150,
  "limit": 20,
  "offset": 0,
  "items": [/* ... */]
}
```

**Pagination Links:**

Calculate next page:
```
GET /api/lessons?limit=20&offset=20
```

---

## Filtering and Sorting

### Filtering

Many endpoints support filtering via query parameters:

```
GET /api/lessons?level=N5&category=grammar
GET /api/flashcards/due?card_type=kanji
```

### Sorting

Some endpoints support sorting:

```
GET /api/lessons?sort_by=order_index&order=asc
GET /api/conversation/history?sort_by=timestamp&order=desc
```

---

## Webhooks (Planned)

Webhook support for external integrations planned for v0.3.0.

---

## Versioning

API version is included in all responses:

```json
{
  "version": "0.1.0",
  // ...
}
```

Future versions will use URL versioning:
```
/api/v2/lessons
```

---

## SDKs and Client Libraries

Official client libraries planned:
- Python SDK (v0.2.0)
- JavaScript/TypeScript SDK (v0.2.0)

---

## Interactive Documentation

For interactive API exploration:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

**Last Updated:** 2025-11-19
**API Version:** 0.1.0
