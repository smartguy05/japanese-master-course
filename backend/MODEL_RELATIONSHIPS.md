# Database Model Relationships

## Entity Relationship Diagram (Text Format)

```
┌─────────────────┐
│      USER       │
│  (Core Entity)  │
└────────┬────────┘
         │
         ├──────────────────────┐
         │                      │
         │ 1:1                  │ 1:N
         ▼                      ▼
┌─────────────────┐    ┌──────────────────┐
│  USER_PROGRESS  │    │   FLASHCARD      │
│                 │    │  (SRS System)    │
│ - current_level │    │ - content_type   │
│ - total_time    │    │ - content_id     │
│ - streak        │    │ - ease_factor    │
│ - xp_points     │    │ - next_review    │
└─────────────────┘    └────────┬─────────┘
                                │
                                │ 1:N
                                ▼
         ┌──────────────────────────────────┐
         │       REVIEW_HISTORY             │
         │  (Tracks each review session)    │
         │ - quality (0-5)                  │
         │ - time_spent                     │
         │ - reviewed_at                    │
         └──────────────────────────────────┘

         ┌────────────────┐
         │      USER      │
         └────────┬───────┘
                  │
                  │ 1:N
                  ▼
         ┌──────────────────────┐
         │ CONVERSATION_SESSION │
         │ - scenario           │
         │ - difficulty_level   │
         │ - started_at         │
         │ - message_count      │
         └────────┬─────────────┘
                  │
                  │ 1:N
                  ▼
         ┌──────────────────────┐
         │ CONVERSATION_MESSAGE │
         │ - role               │
         │ - content            │
         │ - has_correction     │
         │ - correction_data    │
         └──────────────────────┘

         ┌────────────────┐
         │      USER      │
         └────────┬───────┘
                  │
                  │ N:N (through USER_ACHIEVEMENT)
                  ▼
         ┌──────────────────┐     ┌───────────────────┐
         │  ACHIEVEMENT     │◄────│ USER_ACHIEVEMENT  │
         │ - title          │     │ - unlocked_at     │
         │ - category       │     └───────────────────┘
         │ - requirement    │
         │ - xp_reward      │
         └──────────────────┘

┌──────────────────────────────────────────────┐
│          CONTENT TABLES                      │
│          (No FK to User)                     │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────┐  ┌────────────┐  ┌──────────┐│
│  │  KANJI   │  │ VOCABULARY │  │ GRAMMAR  ││
│  │          │  │            │  │  POINT   ││
│  │ - char   │  │ - word     │  │ - pattern││
│  │ - level  │  │ - reading  │  │ - meaning││
│  │ - meaning│  │ - meaning  │  │ - examples││
│  │ - reading│  │ - examples │  └──────────┘│
│  └──────────┘  └────────────┘              │
│                                              │
│  ┌─────────────────────────────────┐        │
│  │          LESSON                 │        │
│  │ - title                         │        │
│  │ - lesson_type                   │        │
│  │ - content (JSONB)               │        │
│  │ - exercises (JSONB)             │        │
│  └─────────────────────────────────┘        │
└──────────────────────────────────────────────┘
```

## Relationship Details

### User-Centric Relationships

#### User → UserProgress (1:1)
```sql
User.id (PK) ←→ UserProgress.user_id (FK, UNIQUE)
```
- Each user has exactly one progress record
- Tracks overall learning statistics
- Cascade delete: Progress deleted when user deleted

#### User → Flashcard (1:N)
```sql
User.id (PK) ←→ Flashcard.user_id (FK)
```
- Each user can have many flashcards
- Flashcards reference content via (content_type, content_id)
- Cascade delete: All flashcards deleted when user deleted

#### User → ReviewHistory (1:N)
```sql
User.id (PK) ←→ ReviewHistory.user_id (FK)
```
- Tracks every review session
- Links to specific flashcard
- Cascade delete: History deleted when user deleted

#### User → ConversationSession (1:N)
```sql
User.id (PK) ←→ ConversationSession.user_id (FK)
```
- Multiple conversation practice sessions per user
- Each session can have multiple messages
- Cascade delete: Sessions deleted when user deleted

#### User → Achievement (N:N)
```sql
User.id ←→ UserAchievement.user_id ←→ Achievement.id
```
- Many-to-many through UserAchievement join table
- Unique constraint: (user_id, achievement_id)
- Cascade delete: User achievements deleted when user deleted

### Nested Relationships

#### Flashcard → ReviewHistory (1:N)
```sql
Flashcard.id (PK) ←→ ReviewHistory.flashcard_id (FK)
```
- Each flashcard has many review records
- Tracks quality ratings for SRS algorithm
- Cascade delete: Reviews deleted when flashcard deleted

#### ConversationSession → ConversationMessage (1:N)
```sql
ConversationSession.id (PK) ←→ ConversationMessage.session_id (FK)
```
- Messages ordered by created_at
- Alternating user/assistant roles
- Cascade delete: Messages deleted when session deleted

#### Achievement → UserAchievement (1:N)
```sql
Achievement.id (PK) ←→ UserAchievement.achievement_id (FK)
```
- Tracks which users unlocked which achievements
- Timestamped with unlocked_at
- Cascade delete: User achievements deleted when achievement deleted

### Content Relationships

Content tables (Kanji, Vocabulary, GrammarPoint, Lesson) are **independent**:
- No foreign keys to User
- Shared across all users
- Referenced by Flashcards via UUID

#### Flashcard References Content
```python
# Polymorphic reference
Flashcard.content_type = 'kanji' | 'vocabulary' | 'grammar'
Flashcard.content_id = UUID of the content item

# Example queries
SELECT * FROM flashcards
WHERE user_id = $1
  AND content_type = 'kanji'
  AND content_id = $2;
```

## Cascade Delete Behavior

### Delete User
```sql
DELETE FROM users WHERE id = $1;
```
**Also deletes:**
- UserProgress (1 record)
- All Flashcards for that user
- All ReviewHistory for that user
- All ConversationSessions for that user
- All ConversationMessages for those sessions (nested)
- All UserAchievements for that user

**Does NOT delete:**
- Kanji, Vocabulary, GrammarPoint, Lesson (shared content)
- Achievement definitions

### Delete ConversationSession
```sql
DELETE FROM conversation_sessions WHERE id = $1;
```
**Also deletes:**
- All ConversationMessages for that session

### Delete Flashcard
```sql
DELETE FROM flashcards WHERE id = $1;
```
**Also deletes:**
- All ReviewHistory for that flashcard

## Index Strategy

### User Queries
```sql
-- Find user by email (login)
SELECT * FROM users WHERE email = ?;
-- Uses: ix_users_email (unique)

-- Get user's progress
SELECT * FROM user_progress WHERE user_id = ?;
-- Uses: ix_user_progress_user_id

-- Get due flashcards
SELECT * FROM flashcards
WHERE user_id = ? AND next_review <= NOW()
ORDER BY next_review;
-- Uses: ix_flashcards_user_next_review

-- Get user's conversation history
SELECT * FROM conversation_sessions
WHERE user_id = ?
ORDER BY started_at DESC;
-- Uses: ix_conversation_sessions_user
```

### Content Queries
```sql
-- Get N5 kanji ordered by frequency
SELECT * FROM kanji
WHERE jlpt_level = 'N5'
ORDER BY frequency_rank;
-- Uses: ix_kanji_level

-- Get N4 vocabulary
SELECT * FROM vocabulary
WHERE jlpt_level = 'N4'
ORDER BY frequency_rank;
-- Uses: ix_vocabulary_level

-- Get lessons for N3 in order
SELECT * FROM lessons
WHERE jlpt_level = 'N3'
ORDER BY order_index;
-- Uses: ix_lessons_level_order
```

### Analytics Queries
```sql
-- Get review history for user
SELECT * FROM review_history
WHERE user_id = ?
ORDER BY reviewed_at DESC
LIMIT 100;
-- Uses: ix_review_history_user_date

-- Get achievements by category
SELECT * FROM achievements
WHERE category = 'streak';
-- Uses: ix_achievements_category

-- Get user's unlocked achievements
SELECT a.* FROM achievements a
JOIN user_achievements ua ON ua.achievement_id = a.id
WHERE ua.user_id = ?;
-- Uses: ix_user_achievements_user_id
```

## Data Flow Examples

### New User Registration
```
1. INSERT INTO users (...)
2. INSERT INTO user_progress (user_id = new_user.id, ...)
3. User can start learning
```

### Learning Flow
```
1. User selects N5 Hiragana lesson
2. System creates flashcards:
   - INSERT INTO flashcards (user_id, content_type='kanji', content_id)
3. User reviews flashcard:
   - UPDATE flashcards SET last_reviewed=NOW(), ...
   - INSERT INTO review_history (flashcard_id, quality, ...)
4. Update progress:
   - UPDATE user_progress SET total_study_time += ?, current_streak = ?
```

### Conversation Practice
```
1. User starts conversation:
   - INSERT INTO conversation_sessions (user_id, scenario, ...)
2. Messages exchanged:
   - INSERT INTO conversation_messages (session_id, role='user', ...)
   - INSERT INTO conversation_messages (session_id, role='assistant', ...)
3. Session ends:
   - UPDATE conversation_sessions SET ended_at=NOW(), message_count=?
```

### Achievement Unlock
```
1. System checks requirements:
   - Query user_progress, review_history, etc.
2. If criteria met:
   - INSERT INTO user_achievements (user_id, achievement_id, ...)
   - UPDATE user_progress SET xp_points += ?
```

## Performance Considerations

### Query Patterns
- **Hot path**: Flashcard due reviews (indexed on user_id + next_review)
- **Frequent**: User progress lookups (indexed on user_id)
- **Moderate**: Content browsing (indexed on jlpt_level)
- **Cold**: Historical analytics (indexed on reviewed_at)

### Expected Table Sizes
- Users: 1K - 100K rows
- UserProgress: 1K - 100K rows (1:1 with users)
- Flashcards: 10K - 10M rows (avg 100-1000 per user)
- ReviewHistory: 100K - 100M rows (10+ reviews per flashcard)
- Kanji: ~2,500 rows (fixed, JLPT kanji)
- Vocabulary: ~10K rows (fixed, common words)
- Lessons: 100 - 1K rows (curated content)
- ConversationSessions: 10K - 1M rows
- ConversationMessages: 100K - 10M rows
- Achievements: 50 - 200 rows (fixed)
- UserAchievements: 10K - 1M rows

### Optimization Notes
- JSONB fields indexed with GIN for content searches (future)
- Partition review_history by month if > 10M rows
- Archive old conversation_messages periodically
- Materialized views for user statistics (future optimization)
