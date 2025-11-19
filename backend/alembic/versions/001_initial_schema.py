"""Initial schema with all models

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-11-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables."""

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.Text(), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('native_language', sa.String(10), nullable=False, server_default='en'),
        sa.Column('target_proficiency', sa.String(10), nullable=False, server_default='N3'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('preferences', postgresql.JSONB(), nullable=False, server_default='{}'),
    )
    op.create_index('ix_users_id', 'users', ['id'])

    # User Progress table
    op.create_table(
        'user_progress',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('current_level', sa.String(), nullable=False, server_default='N5'),
        sa.Column('total_study_time', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_study_date', sa.Date(), nullable=True),
        sa.Column('xp_points', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_user_progress_id', 'user_progress', ['id'])
    op.create_index('ix_user_progress_user_id', 'user_progress', ['user_id'])

    # Kanji table
    op.create_table(
        'kanji',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('character', sa.String(1), nullable=False, unique=True),
        sa.Column('jlpt_level', sa.String(10), nullable=False),
        sa.Column('frequency_rank', sa.Integer(), nullable=True),
        sa.Column('meanings', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('on_readings', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('kun_readings', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('radical', sa.String(10), nullable=True),
        sa.Column('stroke_count', sa.Integer(), nullable=True),
        sa.Column('grade', sa.Integer(), nullable=True),
        sa.Column('examples', postgresql.JSONB(), nullable=False, server_default='[]'),
    )
    op.create_index('ix_kanji_id', 'kanji', ['id'])
    op.create_index('ix_kanji_character', 'kanji', ['character'])
    op.create_index('ix_kanji_level', 'kanji', ['jlpt_level', 'frequency_rank'])

    # Vocabulary table
    op.create_table(
        'vocabulary',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('word', sa.String(100), nullable=False),
        sa.Column('reading', sa.String(100), nullable=False),
        sa.Column('jlpt_level', sa.String(10), nullable=False),
        sa.Column('meanings', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('part_of_speech', sa.String(50), nullable=False),
        sa.Column('frequency_rank', sa.Integer(), nullable=True),
        sa.Column('audio_url', sa.String(500), nullable=True),
        sa.Column('example_sentences', postgresql.JSONB(), nullable=False, server_default='[]'),
    )
    op.create_index('ix_vocabulary_id', 'vocabulary', ['id'])
    op.create_index('ix_vocabulary_word', 'vocabulary', ['word'])
    op.create_index('ix_vocabulary_level', 'vocabulary', ['jlpt_level', 'frequency_rank'])

    # Grammar Points table
    op.create_table(
        'grammar_points',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('jlpt_level', sa.String(10), nullable=False),
        sa.Column('grammar_pattern', sa.String(200), nullable=False),
        sa.Column('meaning', sa.Text(), nullable=False),
        sa.Column('formation', sa.Text(), nullable=False),
        sa.Column('examples', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('common_mistakes', postgresql.JSONB(), nullable=False, server_default='[]'),
    )
    op.create_index('ix_grammar_points_id', 'grammar_points', ['id'])
    op.create_index('ix_grammar_points_pattern', 'grammar_points', ['grammar_pattern'])
    op.create_index('ix_grammar_points_level', 'grammar_points', ['jlpt_level'])

    # Lessons table
    op.create_table(
        'lessons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('lesson_type', sa.String(50), nullable=False),
        sa.Column('jlpt_level', sa.String(10), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('content', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('exercises', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('prerequisites', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_index('ix_lessons_id', 'lessons', ['id'])
    op.create_index('ix_lessons_type', 'lessons', ['lesson_type'])
    op.create_index('ix_lessons_level_order', 'lessons', ['jlpt_level', 'order_index'])

    # Flashcards table
    op.create_table(
        'flashcards',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_type', sa.String(50), nullable=False),
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ease_factor', sa.Float(), nullable=False, server_default='2.5'),
        sa.Column('interval_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('repetitions', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_reviewed', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_review', sa.DateTime(timezone=True), nullable=False),
        sa.Column('correct_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('incorrect_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_flashcards_id', 'flashcards', ['id'])
    op.create_index('ix_flashcards_user_id', 'flashcards', ['user_id'])
    op.create_index('ix_flashcards_user_next_review', 'flashcards', ['user_id', 'next_review'])
    op.create_index('ix_flashcards_user_content', 'flashcards', ['user_id', 'content_type', 'content_id'])

    # Review History table
    op.create_table(
        'review_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('flashcard_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quality', sa.Integer(), nullable=False),
        sa.Column('time_spent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['flashcard_id'], ['flashcards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_review_history_id', 'review_history', ['id'])
    op.create_index('ix_review_history_flashcard_id', 'review_history', ['flashcard_id'])
    op.create_index('ix_review_history_user_date', 'review_history', ['user_id', sa.text('reviewed_at DESC')])

    # Conversation Sessions table
    op.create_table(
        'conversation_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('scenario', sa.String(100), nullable=False),
        sa.Column('difficulty_level', sa.String(10), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('corrections_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duration_seconds', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_conversation_sessions_id', 'conversation_sessions', ['id'])
    op.create_index('ix_conversation_sessions_user', 'conversation_sessions', ['user_id', sa.text('started_at DESC')])

    # Conversation Messages table
    op.create_table(
        'conversation_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('has_correction', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('correction_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['conversation_sessions.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_conversation_messages_id', 'conversation_messages', ['id'])
    op.create_index('ix_conversation_messages_session_id', 'conversation_messages', ['session_id'])

    # Achievements table
    op.create_table(
        'achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('requirement', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('badge_icon', sa.String(255), nullable=False),
        sa.Column('xp_reward', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_achievements_id', 'achievements', ['id'])
    op.create_index('ix_achievements_category', 'achievements', ['category'])

    # User Achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )
    op.create_index('ix_user_achievements_id', 'user_achievements', ['id'])
    op.create_index('ix_user_achievements_user_id', 'user_achievements', ['user_id'])
    op.create_index('ix_user_achievements_achievement_id', 'user_achievements', ['achievement_id'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('conversation_messages')
    op.drop_table('conversation_sessions')
    op.drop_table('review_history')
    op.drop_table('flashcards')
    op.drop_table('lessons')
    op.drop_table('grammar_points')
    op.drop_table('vocabulary')
    op.drop_table('kanji')
    op.drop_table('user_progress')
    op.drop_table('users')
