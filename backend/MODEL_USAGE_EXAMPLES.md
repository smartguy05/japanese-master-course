# Database Model Usage Examples

## SQLAlchemy Model Usage Patterns

This guide provides practical examples for working with the Nihongo Sensei database models using SQLAlchemy async ORM.

---

## Basic CRUD Operations

### Creating Records

#### Create a New User
```python
from app.models import User
from app.database import AsyncSessionLocal
from datetime import datetime
import uuid

async def create_user(email: str, password: str, full_name: str):
    """Create a new user with default settings."""
    async with AsyncSessionLocal() as session:
        user = User(
            email=email,
            hashed_password=hash_password(password),  # Use proper hashing
            full_name=full_name,
            native_language="en",
            target_proficiency="N3",
            preferences={
                "theme": "light",
                "daily_goal": 30,
                "notifications": True
            }
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

# Usage
user = await create_user("john@example.com", "securepass123", "John Doe")
print(f"Created user: {user.id}")
```

#### Create User with Progress
```python
from app.models import User, UserProgress

async def create_user_with_progress(email: str, password: str, full_name: str):
    """Create user and initialize progress tracking."""
    async with AsyncSessionLocal() as session:
        # Create user
        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name
        )
        session.add(user)
        await session.flush()  # Get user.id without committing

        # Create progress record
        progress = UserProgress(
            user_id=user.id,
            current_level="N5",
            total_study_time=0,
            current_streak=0,
            longest_streak=0,
            xp_points=0
        )
        session.add(progress)
        await session.commit()

        await session.refresh(user)
        await session.refresh(progress)
        return user, progress
```

#### Add Content (Kanji, Vocabulary, Grammar)
```python
from app.models import Kanji, Vocabulary, GrammarPoint

async def add_kanji(character: str, level: str):
    """Add a new kanji to the database."""
    async with AsyncSessionLocal() as session:
        kanji = Kanji(
            character=character,
            jlpt_level=level,
            frequency_rank=100,
            meanings=["water", "aqua"],
            on_readings=["スイ"],
            kun_readings=["みず"],
            radical="氵",
            stroke_count=4,
            grade=1,
            examples=[
                {"word": "水曜日", "reading": "すいようび", "meaning": "Wednesday"},
                {"word": "水族館", "reading": "すいぞくかん", "meaning": "aquarium"}
            ]
        )
        session.add(kanji)
        await session.commit()
        await session.refresh(kanji)
        return kanji

# Add vocabulary
async def add_vocabulary():
    async with AsyncSessionLocal() as session:
        vocab = Vocabulary(
            word="学校",
            reading="がっこう",
            jlpt_level="N5",
            meanings=["school"],
            part_of_speech="noun",
            frequency_rank=250,
            example_sentences=[
                {
                    "japanese": "学校に行きます。",
                    "reading": "がっこうにいきます。",
                    "english": "I go to school."
                }
            ]
        )
        session.add(vocab)
        await session.commit()
        return vocab
```

---

## Reading Records

### Query Users
```python
from sqlalchemy import select
from app.models import User

async def get_user_by_email(email: str):
    """Find user by email address."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

async def get_active_users():
    """Get all active users."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.is_active == True)
        )
        return result.scalars().all()

async def get_user_with_progress(user_id: uuid.UUID):
    """Get user with their progress (eager loading)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.progress))
        )
        return result.scalar_one_or_none()
```

### Query Content
```python
from app.models import Kanji, Vocabulary, Lesson

async def get_n5_kanji():
    """Get all N5 kanji ordered by frequency."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Kanji)
            .where(Kanji.jlpt_level == "N5")
            .order_by(Kanji.frequency_rank)
        )
        return result.scalars().all()

async def get_vocabulary_by_level(level: str, limit: int = 20):
    """Get vocabulary for a specific JLPT level."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Vocabulary)
            .where(Vocabulary.jlpt_level == level)
            .order_by(Vocabulary.frequency_rank)
            .limit(limit)
        )
        return result.scalars().all()

async def get_published_lessons(level: str):
    """Get published lessons for a JLPT level."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Lesson)
            .where(
                Lesson.jlpt_level == level,
                Lesson.is_published == True
            )
            .order_by(Lesson.order_index)
        )
        return result.scalars().all()
```

---

## SRS (Spaced Repetition System)

### Create and Review Flashcards
```python
from app.models import Flashcard, ReviewHistory
from datetime import datetime, timedelta

async def create_flashcard(user_id: uuid.UUID, content_type: str, content_id: uuid.UUID):
    """Create a new flashcard for a user."""
    async with AsyncSessionLocal() as session:
        flashcard = Flashcard(
            user_id=user_id,
            content_type=content_type,  # 'kanji', 'vocabulary', 'grammar'
            content_id=content_id,
            ease_factor=2.50,  # SM-2 default
            interval_days=0,
            repetitions=0,
            next_review=datetime.utcnow()  # Due immediately
        )
        session.add(flashcard)
        await session.commit()
        await session.refresh(flashcard)
        return flashcard

async def get_due_flashcards(user_id: uuid.UUID, limit: int = 20):
    """Get flashcards due for review."""
    async with AsyncSessionLocal() as session:
        now = datetime.utcnow()
        result = await session.execute(
            select(Flashcard)
            .where(
                Flashcard.user_id == user_id,
                Flashcard.next_review <= now
            )
            .order_by(Flashcard.next_review)
            .limit(limit)
        )
        return result.scalars().all()

async def review_flashcard(flashcard_id: uuid.UUID, quality: int, time_spent: int):
    """
    Record a flashcard review with quality rating.

    Quality (SM-2 algorithm):
    - 0: Complete blackout
    - 1: Incorrect, but recognized
    - 2: Incorrect, but easy to recall
    - 3: Correct, but difficult
    - 4: Correct, with hesitation
    - 5: Perfect recall
    """
    async with AsyncSessionLocal() as session:
        # Get flashcard
        result = await session.execute(
            select(Flashcard).where(Flashcard.id == flashcard_id)
        )
        flashcard = result.scalar_one()

        # Update flashcard statistics
        if quality >= 3:
            flashcard.correct_count += 1
        else:
            flashcard.incorrect_count += 1

        # Calculate next review (SM-2 algorithm - simplified)
        if quality < 3:
            # Failed - reset
            flashcard.repetitions = 0
            flashcard.interval_days = 0
            flashcard.next_review = datetime.utcnow() + timedelta(minutes=10)
        else:
            # Passed - increase interval
            flashcard.repetitions += 1

            if flashcard.repetitions == 1:
                flashcard.interval_days = 1
            elif flashcard.repetitions == 2:
                flashcard.interval_days = 6
            else:
                flashcard.interval_days = int(
                    flashcard.interval_days * flashcard.ease_factor
                )

            flashcard.next_review = datetime.utcnow() + timedelta(
                days=flashcard.interval_days
            )

            # Update ease factor
            ease_change = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
            flashcard.ease_factor = max(1.3, flashcard.ease_factor + ease_change)

        flashcard.last_reviewed = datetime.utcnow()

        # Create review history record
        review = ReviewHistory(
            flashcard_id=flashcard_id,
            user_id=flashcard.user_id,
            quality=quality,
            time_spent=time_spent,
            reviewed_at=datetime.utcnow()
        )
        session.add(review)

        await session.commit()
        return flashcard

# Usage
due_cards = await get_due_flashcards(user.id, limit=10)
for card in due_cards:
    # User reviews card, provides quality rating
    await review_flashcard(card.id, quality=4, time_spent=12)
```

---

## Conversation Practice

### Start and Track Conversations
```python
from app.models import ConversationSession, ConversationMessage

async def start_conversation(user_id: uuid.UUID, scenario: str, level: str):
    """Start a new conversation practice session."""
    async with AsyncSessionLocal() as session:
        conv_session = ConversationSession(
            user_id=user_id,
            scenario=scenario,  # e.g., "restaurant", "business_meeting"
            difficulty_level=level,
            started_at=datetime.utcnow()
        )
        session.add(conv_session)
        await session.commit()
        await session.refresh(conv_session)
        return conv_session

async def add_message(
    session_id: uuid.UUID,
    role: str,
    content: str,
    has_correction: bool = False,
    correction_data: dict = None
):
    """Add a message to the conversation."""
    async with AsyncSessionLocal() as session:
        message = ConversationMessage(
            session_id=session_id,
            role=role,  # 'user' or 'assistant'
            content=content,
            has_correction=has_correction,
            correction_data=correction_data,
            created_at=datetime.utcnow()
        )
        session.add(message)

        # Update session message count
        result = await session.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        conv_session = result.scalar_one()
        conv_session.message_count += 1

        if has_correction:
            conv_session.corrections_count += 1

        await session.commit()
        await session.refresh(message)
        return message

async def end_conversation(session_id: uuid.UUID):
    """End a conversation session."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ConversationSession).where(ConversationSession.id == session_id)
        )
        conv_session = result.scalar_one()

        conv_session.ended_at = datetime.utcnow()
        conv_session.duration_seconds = int(
            (conv_session.ended_at - conv_session.started_at).total_seconds()
        )

        await session.commit()
        return conv_session

# Usage example
session = await start_conversation(user.id, "restaurant", "N5")
await add_message(session.id, "user", "すみません、メニューをください。")
await add_message(
    session.id,
    "assistant",
    "はい、どうぞ。",
    has_correction=True,
    correction_data={
        "original": "すみません、メニューをください。",
        "suggestion": "すみません、メニューをお願いします。",
        "explanation": "「お願いします」is more polite in formal settings."
    }
)
await end_conversation(session.id)
```

---

## Progress Tracking

### Update User Progress
```python
from app.models import UserProgress
from datetime import date

async def update_study_session(user_id: uuid.UUID, minutes: int, xp_earned: int):
    """Update user progress after a study session."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        progress = result.scalar_one()

        # Update study time
        progress.total_study_time += minutes

        # Update streak
        today = date.today()
        if progress.last_study_date == today:
            # Already studied today, no streak change
            pass
        elif progress.last_study_date == date.today() - timedelta(days=1):
            # Studied yesterday, increment streak
            progress.current_streak += 1
            progress.longest_streak = max(
                progress.longest_streak,
                progress.current_streak
            )
        else:
            # Streak broken, restart
            progress.current_streak = 1

        progress.last_study_date = today

        # Add XP
        progress.xp_points += xp_earned

        # Check for level up (example logic)
        if progress.xp_points >= 1000 and progress.current_level == "N5":
            progress.current_level = "N4"

        progress.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(progress)
        return progress

# Usage
progress = await update_study_session(user.id, minutes=25, xp_earned=50)
print(f"Streak: {progress.current_streak} days, XP: {progress.xp_points}")
```

---

## Achievements

### Check and Unlock Achievements
```python
from app.models import Achievement, UserAchievement

async def create_achievement(title: str, category: str, requirement: dict, xp: int):
    """Create an achievement definition."""
    async with AsyncSessionLocal() as session:
        achievement = Achievement(
            title=title,
            description=f"Achievement: {title}",
            category=category,
            requirement=requirement,
            badge_icon=f"badge_{category}.svg",
            xp_reward=xp
        )
        session.add(achievement)
        await session.commit()
        await session.refresh(achievement)
        return achievement

async def check_and_unlock_achievement(user_id: uuid.UUID, achievement_id: uuid.UUID):
    """Unlock an achievement for a user if requirements met."""
    async with AsyncSessionLocal() as session:
        # Check if already unlocked
        result = await session.execute(
            select(UserAchievement)
            .where(
                UserAchievement.user_id == user_id,
                UserAchievement.achievement_id == achievement_id
            )
        )
        if result.scalar_one_or_none():
            return None  # Already unlocked

        # Get achievement
        result = await session.execute(
            select(Achievement).where(Achievement.id == achievement_id)
        )
        achievement = result.scalar_one()

        # TODO: Check requirements (depends on achievement type)
        requirements_met = True  # Placeholder

        if requirements_met:
            # Unlock achievement
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement_id,
                unlocked_at=datetime.utcnow()
            )
            session.add(user_achievement)

            # Award XP
            result = await session.execute(
                select(UserProgress).where(UserProgress.user_id == user_id)
            )
            progress = result.scalar_one()
            progress.xp_points += achievement.xp_reward

            await session.commit()
            await session.refresh(user_achievement)
            return user_achievement

        return None

async def get_user_achievements(user_id: uuid.UUID):
    """Get all achievements unlocked by a user."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Achievement)
            .join(UserAchievement)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.unlocked_at.desc())
        )
        return result.scalars().all()
```

---

## Complex Queries

### Analytics Queries
```python
from sqlalchemy import func, desc

async def get_user_statistics(user_id: uuid.UUID):
    """Get comprehensive user statistics."""
    async with AsyncSessionLocal() as session:
        # Get progress
        progress_result = await session.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        progress = progress_result.scalar_one()

        # Count flashcards by status
        total_cards = await session.scalar(
            select(func.count(Flashcard.id)).where(Flashcard.user_id == user_id)
        )

        due_cards = await session.scalar(
            select(func.count(Flashcard.id))
            .where(
                Flashcard.user_id == user_id,
                Flashcard.next_review <= datetime.utcnow()
            )
        )

        # Get review statistics
        total_reviews = await session.scalar(
            select(func.count(ReviewHistory.id))
            .where(ReviewHistory.user_id == user_id)
        )

        avg_quality = await session.scalar(
            select(func.avg(ReviewHistory.quality))
            .where(ReviewHistory.user_id == user_id)
        )

        # Get conversation statistics
        total_conversations = await session.scalar(
            select(func.count(ConversationSession.id))
            .where(ConversationSession.user_id == user_id)
        )

        return {
            "level": progress.current_level,
            "xp": progress.xp_points,
            "study_time": progress.total_study_time,
            "current_streak": progress.current_streak,
            "longest_streak": progress.longest_streak,
            "total_flashcards": total_cards,
            "due_flashcards": due_cards,
            "total_reviews": total_reviews,
            "avg_quality": float(avg_quality) if avg_quality else 0,
            "total_conversations": total_conversations
        }

async def get_top_learners(limit: int = 10):
    """Get top learners by XP."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User, UserProgress)
            .join(UserProgress)
            .order_by(desc(UserProgress.xp_points))
            .limit(limit)
        )
        return result.all()
```

---

## Transaction Examples

### Atomic Operations
```python
async def complete_lesson_atomically(user_id: uuid.UUID, lesson_id: uuid.UUID):
    """Complete a lesson with all updates in a single transaction."""
    async with AsyncSessionLocal() as session:
        try:
            async with session.begin():
                # Get lesson
                lesson_result = await session.execute(
                    select(Lesson).where(Lesson.id == lesson_id)
                )
                lesson = lesson_result.scalar_one()

                # Create flashcards for lesson content
                # (Assuming lesson.content contains kanji/vocab IDs)
                for item_id in lesson.content.get("vocabulary_ids", []):
                    flashcard = Flashcard(
                        user_id=user_id,
                        content_type="vocabulary",
                        content_id=uuid.UUID(item_id),
                        ease_factor=2.50,
                        interval_days=0,
                        repetitions=0,
                        next_review=datetime.utcnow()
                    )
                    session.add(flashcard)

                # Update progress
                progress_result = await session.execute(
                    select(UserProgress).where(UserProgress.user_id == user_id)
                )
                progress = progress_result.scalar_one()
                progress.xp_points += 100  # XP for completing lesson
                progress.total_study_time += lesson.estimated_duration or 30

                # Check for achievements
                # ... achievement logic ...

                # Commit happens automatically when exiting the context
                print(f"Lesson {lesson.title} completed successfully")

        except Exception as e:
            # Rollback happens automatically on exception
            print(f"Error completing lesson: {e}")
            raise
```

---

## Best Practices

### 1. Always Use Async Context Managers
```python
# Good
async with AsyncSessionLocal() as session:
    # Your code here
    await session.commit()

# Bad (resource leak)
session = AsyncSessionLocal()
# ... code ...
await session.commit()
# session never closed!
```

### 2. Use Relationships for Navigation
```python
# Good - use SQLAlchemy relationships
user = await get_user_by_id(user_id)
progress = user.progress  # Access via relationship

# Less efficient - manual join
progress = await session.execute(
    select(UserProgress).where(UserProgress.user_id == user_id)
)
```

### 3. Batch Operations
```python
# Good - batch insert
async with AsyncSessionLocal() as session:
    flashcards = [
        Flashcard(user_id=user_id, content_type="kanji", content_id=kanji_id)
        for kanji_id in kanji_ids
    ]
    session.add_all(flashcards)
    await session.commit()

# Bad - individual inserts in a loop
for kanji_id in kanji_ids:
    async with AsyncSessionLocal() as session:
        flashcard = Flashcard(...)
        session.add(flashcard)
        await session.commit()  # Slow!
```

### 4. Use Indexes Effectively
```python
# Leverages index
await session.execute(
    select(Flashcard)
    .where(Flashcard.user_id == user_id, Flashcard.next_review <= now)
)

# Doesn't leverage index well
await session.execute(
    select(Flashcard)
    .where(func.date(Flashcard.next_review) == date.today())
)
```

---

## Common Pitfalls to Avoid

❌ **Don't forget to commit**
```python
session.add(user)
# Forgot await session.commit() - changes not saved!
```

❌ **Don't use blocking calls**
```python
# Bad - blocking
session.execute(select(User))  # Missing await!

# Good
await session.execute(select(User))
```

❌ **Don't query in loops (N+1 problem)**
```python
# Bad
users = await get_all_users()
for user in users:
    progress = await get_progress(user.id)  # N+1 queries!

# Good - use eager loading
users = await session.execute(
    select(User).options(selectinload(User.progress))
)
```

❌ **Don't leak sessions**
```python
# Bad
def get_session():
    return AsyncSessionLocal()

session = get_session()
# ... never closed!

# Good
async with AsyncSessionLocal() as session:
    # Automatically closed
    pass
```

---

This guide covers the most common usage patterns. For more advanced scenarios, refer to the [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html).
