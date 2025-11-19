"""
Achievement models for gamification.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Achievement(Base):
    """
    Achievement definition model.

    Attributes:
        id: Unique identifier (UUID)
        title: Achievement title
        description: Achievement description
        category: Achievement category (streak, lessons, kanji, etc.)
        requirement: Requirements to unlock (JSONB)
        badge_icon: Icon identifier or URL
        xp_reward: XP points awarded
    """

    __tablename__ = "achievements"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Achievement Data
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    # Requirements (JSONB for flexibility)
    requirement: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )

    # Reward
    badge_icon: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    xp_reward: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Relationships
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        back_populates="achievement",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of Achievement."""
        return f"<Achievement(title='{self.title}', category='{self.category}')>"


class UserAchievement(Base):
    """
    User-specific achievement unlock record.

    Attributes:
        id: Unique identifier (UUID)
        user_id: Foreign key to User
        achievement_id: Foreign key to Achievement
        unlocked_at: Timestamp when achievement was unlocked
    """

    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Timestamp
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(back_populates="user_achievements")

    def __repr__(self) -> str:
        """String representation of UserAchievement."""
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"
