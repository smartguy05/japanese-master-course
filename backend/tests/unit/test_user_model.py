"""
Unit tests for User model.

Following TDD: These tests are written BEFORE the User model implementation.
"""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select

from app.models.user import User


@pytest.mark.asyncio
async def test_user_creation(db_session):
    """Test creating a user with required fields."""
    # Arrange
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_123",
        full_name="Test User",
        native_language="en",
        target_proficiency="N3",
    )

    # Act
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assert
    assert user.id is not None
    assert isinstance(user.id, uuid.UUID)
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.native_language == "en"
    assert user.target_proficiency == "N3"
    assert user.is_active is True  # Default value
    assert isinstance(user.created_at, datetime)
    assert user.last_login is None  # Not set yet


@pytest.mark.asyncio
async def test_user_email_unique_constraint(db_session):
    """Test that email must be unique."""
    # Arrange
    user1 = User(
        email="duplicate@example.com",
        hashed_password="password1",
        full_name="User One",
    )
    user2 = User(
        email="duplicate@example.com",
        hashed_password="password2",
        full_name="User Two",
    )

    # Act & Assert
    db_session.add(user1)
    await db_session.commit()

    db_session.add(user2)
    with pytest.raises(Exception):  # Should raise IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_user_preferences_jsonb(db_session):
    """Test that preferences field stores JSONB data."""
    # Arrange
    preferences = {
        "theme": "dark",
        "notifications": True,
        "daily_goal": 30,
        "lesson_reminders": ["09:00", "18:00"],
    }
    user = User(
        email="preferences@example.com",
        hashed_password="password",
        full_name="Preferences User",
        preferences=preferences,
    )

    # Act
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assert
    assert user.preferences == preferences
    assert user.preferences["theme"] == "dark"
    assert user.preferences["notifications"] is True
    assert user.preferences["daily_goal"] == 30
    assert user.preferences["lesson_reminders"] == ["09:00", "18:00"]


@pytest.mark.asyncio
async def test_user_defaults(db_session):
    """Test default values for optional fields."""
    # Arrange
    user = User(
        email="defaults@example.com",
        hashed_password="password",
        full_name="Default User",
    )

    # Act
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Assert
    assert user.is_active is True
    assert user.native_language == "en"  # Default
    assert user.target_proficiency == "N3"  # Default
    assert user.preferences == {}  # Default empty dict
    assert user.last_login is None


@pytest.mark.asyncio
async def test_user_query_by_email(db_session):
    """Test querying user by email."""
    # Arrange
    user = User(
        email="query@example.com",
        hashed_password="password",
        full_name="Query User",
    )
    db_session.add(user)
    await db_session.commit()

    # Act
    result = await db_session.execute(
        select(User).where(User.email == "query@example.com")
    )
    found_user = result.scalar_one_or_none()

    # Assert
    assert found_user is not None
    assert found_user.email == "query@example.com"
    assert found_user.full_name == "Query User"


@pytest.mark.asyncio
async def test_user_update_last_login(db_session):
    """Test updating last_login timestamp."""
    # Arrange
    user = User(
        email="login@example.com",
        hashed_password="password",
        full_name="Login User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Act
    login_time = datetime.utcnow()
    user.last_login = login_time
    await db_session.commit()
    await db_session.refresh(user)

    # Assert
    assert user.last_login is not None
    assert isinstance(user.last_login, datetime)


@pytest.mark.asyncio
async def test_user_deactivate(db_session):
    """Test deactivating a user."""
    # Arrange
    user = User(
        email="deactivate@example.com",
        hashed_password="password",
        full_name="Deactivate User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Act
    user.is_active = False
    await db_session.commit()
    await db_session.refresh(user)

    # Assert
    assert user.is_active is False


@pytest.mark.asyncio
async def test_user_representation(db_session):
    """Test string representation of User."""
    # Arrange
    user = User(
        email="repr@example.com",
        hashed_password="password",
        full_name="Repr User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Act
    user_repr = repr(user)

    # Assert
    assert "User" in user_repr
    assert "repr@example.com" in user_repr
