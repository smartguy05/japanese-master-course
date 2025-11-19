"""
Pytest configuration and fixtures for backend tests.
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.models.kanji import Kanji
from app.models.flashcard import Flashcard
from app.utils.auth import hash_password, create_access_token


# Use a test database URL
TEST_DATABASE_URL = settings.database_url.replace(
    settings.postgres_db, f"{settings.postgres_db}_test"
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.

    Yields:
        AsyncSession: Test database session

    Example:
        async def test_user_creation(db_session):
            user = User(email="test@example.com")
            db_session.add(user)
            await db_session.commit()
            assert user.id is not None
    """
    async_session = sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an async HTTP client for testing API endpoints.
    Overrides the database dependency to use the test database.

    Yields:
        AsyncClient: HTTPX async client for making test requests

    Example:
        async def test_endpoint(client):
            response = await client.get("/api/health")
            assert response.status_code == 200
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """Override get_db to use test database session."""
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def test_password() -> str:
    """Return a valid test password."""
    return "TestPassword123!@#"


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_password: str) -> User:
    """
    Create a test user in the database.

    Args:
        db_session: Database session
        test_password: Plain text password for the test user

    Returns:
        User: Created test user

    Example:
        async def test_with_user(test_user):
            assert test_user.email == "test@example.com"
            assert test_user.is_active is True
    """
    user = User(
        email="test@example.com",
        hashed_password=hash_password(test_password),
        full_name="Test User",
        is_active=True,
        native_language="en",
        target_proficiency="N3"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest.fixture
def test_user_id(test_user: User) -> str:
    """Get test user ID as string."""
    return str(test_user.id)


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient,
    test_user: User
) -> AsyncGenerator[AsyncClient, None]:
    """
    Create an authenticated async HTTP client.

    Args:
        client: Base HTTP client
        test_user: Test user

    Yields:
        AsyncClient: Authenticated HTTP client with Bearer token

    Example:
        async def test_protected_endpoint(authenticated_client):
            response = await authenticated_client.get("/api/protected")
            assert response.status_code == 200
    """
    # Create access token
    token = create_access_token({"sub": test_user.email})

    # Add authorization header
    client.headers["Authorization"] = f"Bearer {token}"

    yield client

    # Clean up
    del client.headers["Authorization"]


@pytest_asyncio.fixture
async def test_kanji(db_session: AsyncSession) -> Kanji:
    """
    Create a test kanji character.

    Returns:
        Kanji: Created test kanji
    """
    from datetime import datetime
    from uuid import uuid4

    kanji = Kanji(
        id=uuid4(),
        character="水",
        jlpt_level="N5",
        meanings=["water"],
        on_readings=["スイ"],
        kun_readings=["みず"],
        radical="水",
        stroke_count=4,
        grade=1,
        frequency_rank=365,
        examples=[
            {"word": "水曜日", "reading": "すいようび", "meaning": "Wednesday"},
            {"word": "水", "reading": "みず", "meaning": "water"}
        ]
    )
    db_session.add(kanji)
    await db_session.commit()
    await db_session.refresh(kanji)

    return kanji


@pytest_asyncio.fixture
async def test_kanji_list(db_session: AsyncSession) -> list[Kanji]:
    """
    Create a list of test kanji characters.

    Returns:
        list[Kanji]: List of 30 test kanji
    """
    from datetime import datetime
    from uuid import uuid4

    kanji_data = [
        ("水", "water", ["スイ"], ["みず"], 4, 1),
        ("火", "fire", ["カ"], ["ひ"], 4, 1),
        ("木", "tree", ["ボク", "モク"], ["き"], 4, 1),
        ("金", "gold", ["キン"], ["かね"], 8, 1),
        ("土", "earth", ["ド", "ト"], ["つち"], 3, 1),
        ("日", "sun", ["ニチ", "ジツ"], ["ひ"], 4, 1),
        ("月", "moon", ["ゲツ", "ガツ"], ["つき"], 4, 1),
        ("人", "person", ["ジン", "ニン"], ["ひと"], 2, 1),
        ("山", "mountain", ["サン"], ["やま"], 3, 1),
        ("川", "river", ["セン"], ["かわ"], 3, 1),
    ]

    kanji_list = []
    for char, meaning, on, kun, strokes, grade in kanji_data * 3:  # Repeat to get 30
        kanji = Kanji(
            id=uuid4(),
            character=char,
            jlpt_level="N5",
            meanings=[meaning],
            on_readings=on,
            kun_readings=kun,
            stroke_count=strokes,
            grade=grade,
            frequency_rank=100
        )
        db_session.add(kanji)
        kanji_list.append(kanji)

    await db_session.commit()

    return kanji_list


@pytest_asyncio.fixture
async def test_flashcard(
    db_session: AsyncSession,
    test_user: User,
    test_kanji: Kanji
) -> Flashcard:
    """
    Create a test flashcard.

    Returns:
        Flashcard: Created test flashcard
    """
    from datetime import datetime

    flashcard = Flashcard(
        user_id=test_user.id,
        content_type="kanji",
        content_id=test_kanji.id,
        ease_factor=2.5,
        interval_days=0,
        repetitions=0,
        next_review=datetime.utcnow(),
        correct_count=0,
        incorrect_count=0
    )
    db_session.add(flashcard)
    await db_session.commit()
    await db_session.refresh(flashcard)

    return flashcard


@pytest_asyncio.fixture
async def other_user(db_session: AsyncSession, test_password: str) -> User:
    """Create another test user for testing permissions."""
    from uuid import uuid4

    user = User(
        id=uuid4(),
        email="other@example.com",
        hashed_password=hash_password(test_password),
        full_name="Other User",
        is_active=True,
        native_language="en",
        target_proficiency="N3"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def other_user_flashcard(
    db_session: AsyncSession,
    other_user: User,
    test_kanji: Kanji
) -> Flashcard:
    """Create a flashcard for the other user."""
    from datetime import datetime

    flashcard = Flashcard(
        user_id=other_user.id,
        content_type="kanji",
        content_id=test_kanji.id,
        ease_factor=2.5,
        interval_days=0,
        repetitions=0,
        next_review=datetime.utcnow()
    )
    db_session.add(flashcard)
    await db_session.commit()
    await db_session.refresh(flashcard)

    return flashcard
