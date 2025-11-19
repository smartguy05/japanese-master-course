"""
Conversation API endpoints for AI-powered conversation practice.

This module provides endpoints for:
- Creating conversation sessions
- Sending messages and receiving AI responses
- Retrieving conversation history
- Ending conversation sessions
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.conversation import ConversationMessage
from app.models.user import User
from app.schemas.conversation import (
    AIMessageResponse,
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    CorrectionData,
    MessageCreate,
    MessageResponse,
)
from app.services.ai_service import AIService, AIServiceError, get_ai_service
from app.services.conversation_service import (
    ConversationError,
    ConversationService,
    get_conversation_service,
)

router = APIRouter(prefix="/api/conversation", tags=["conversation"])


@router.post(
    "/sessions",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new conversation session",
    description="Start a new conversation practice session with specified scenario and difficulty",
)
async def create_conversation_session(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """
    Create a new conversation practice session.

    Args:
        data: Session creation data (scenario, difficulty_level)
        current_user: Authenticated user
        db: Database session

    Returns:
        Created conversation session

    Raises:
        HTTPException 400: If scenario or difficulty level is invalid
    """
    try:
        service = get_conversation_service(db)
        session = await service.create_session(
            user_id=current_user.id,
            scenario=data.scenario,
            difficulty_level=data.difficulty_level,
        )

        # Convert to response schema
        return ConversationResponse.model_validate(session)

    except ConversationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation session: {str(e)}",
        )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=AIMessageResponse,
    summary="Send message and get AI response",
    description="Send a user message and receive AI response with corrections",
)
async def send_message(
    session_id: uuid.UUID,
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ai_service: AIService = Depends(get_ai_service),
) -> AIMessageResponse:
    """
    Send a message in a conversation and receive AI response.

    This endpoint:
    1. Saves the user's message
    2. Gets conversation history
    3. Calls AI service for response
    4. Saves AI response with corrections
    5. Returns the AI response

    Args:
        session_id: ID of the conversation session
        message: Message content
        current_user: Authenticated user
        db: Database session
        ai_service: AI service instance

    Returns:
        AI response with corrections and encouragement

    Raises:
        HTTPException 404: If session not found
        HTTPException 403: If user doesn't own the session
        HTTPException 500: If AI service fails
    """
    try:
        conv_service = get_conversation_service(db)

        # Verify session exists and belongs to user
        session = await conv_service.get_session(session_id)
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation",
            )

        # Check if session is already ended
        if session.ended_at is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send messages to ended conversation",
            )

        # Save user message
        user_message = await conv_service.add_message(
            session_id=session_id,
            role="user",
            content=message.content,
            correction_data=None,
        )

        # Get conversation context
        conversation_history = await conv_service.get_conversation_context(
            session_id=session_id,
            max_messages=20,
        )

        # Get AI response
        try:
            ai_response = await ai_service.get_conversation_response(
                user_message=message.content,
                conversation_history=conversation_history,
                user_level=session.difficulty_level,
                scenario=session.scenario,
            )
        except AIServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI service error: {str(e)}",
            )

        # Save AI response message
        correction_dict = None
        if ai_response.correction:
            correction_dict = {
                "original": ai_response.correction.original,
                "corrected": ai_response.correction.corrected,
                "explanation": ai_response.correction.explanation,
            }

        assistant_message = await conv_service.add_message(
            session_id=session_id,
            role="assistant",
            content=ai_response.response,
            correction_data=correction_dict,
        )

        # Build response
        correction_response = None
        if ai_response.correction:
            correction_response = CorrectionData(
                original=ai_response.correction.original,
                corrected=ai_response.correction.corrected,
                explanation=ai_response.correction.explanation,
            )

        return AIMessageResponse(
            response=ai_response.response,
            correction=correction_response,
            encouragement=ai_response.encouragement,
            user_message_id=user_message.id,
            assistant_message_id=assistant_message.id,
        )

    except ConversationError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation session not found",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}",
        )


@router.get(
    "/sessions/{session_id}",
    response_model=ConversationResponse,
    summary="Get conversation session",
    description="Retrieve conversation session with all messages",
)
async def get_conversation_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """
    Get conversation session details with all messages.

    Args:
        session_id: ID of the session
        current_user: Authenticated user
        db: Database session

    Returns:
        Conversation session with messages

    Raises:
        HTTPException 404: If session not found
        HTTPException 403: If user doesn't own the session
    """
    try:
        service = get_conversation_service(db)
        session = await service.get_session(session_id)

        # Verify ownership
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation",
            )

        # Convert messages to response schema
        messages = [MessageResponse.model_validate(msg) for msg in session.messages]

        # Build response
        response = ConversationResponse.model_validate(session)
        response.messages = messages

        return response

    except ConversationError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation session not found",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversation: {str(e)}",
        )


@router.get(
    "/sessions",
    response_model=List[ConversationListResponse],
    summary="List user's conversations",
    description="Get paginated list of user's conversation sessions",
)
async def list_user_conversations(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[ConversationListResponse]:
    """
    List user's conversation sessions.

    Args:
        limit: Maximum number of sessions to return (default: 20)
        offset: Number of sessions to skip (default: 0)
        current_user: Authenticated user
        db: Database session

    Returns:
        List of conversation sessions
    """
    try:
        service = get_conversation_service(db)
        sessions = await service.get_user_sessions(
            user_id=current_user.id,
            limit=min(limit, 100),  # Cap at 100
            offset=offset,
        )

        return [ConversationListResponse.model_validate(session) for session in sessions]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve conversations: {str(e)}",
        )


@router.delete(
    "/sessions/{session_id}",
    response_model=ConversationResponse,
    summary="End conversation session",
    description="End conversation session and calculate final statistics",
)
async def end_conversation_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    """
    End a conversation session.

    Calculates final statistics including:
    - Total duration
    - Message count
    - Corrections count

    Args:
        session_id: ID of the session to end
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated conversation session with final statistics

    Raises:
        HTTPException 404: If session not found
        HTTPException 403: If user doesn't own the session
        HTTPException 400: If session already ended
    """
    try:
        service = get_conversation_service(db)

        # Verify session exists and belongs to user
        session = await service.get_session(session_id)
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this conversation",
            )

        # End session
        ended_session = await service.end_session(session_id)

        return ConversationResponse.model_validate(ended_session)

    except ConversationError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        elif "already ended" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end conversation: {str(e)}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end conversation: {str(e)}",
        )
