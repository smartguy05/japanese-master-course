"""
Integration tests for authentication API endpoints (TDD - TESTS FIRST).

These tests are written BEFORE implementation to follow Test-Driven Development.
They will initially FAIL, then we implement the endpoints to make them pass.
"""

import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.utils.auth import create_access_token, hash_password


class TestRegisterEndpoint:
    """Test user registration endpoint: POST /api/auth/register"""

    @pytest.mark.asyncio
    async def test_register_success(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test successful user registration."""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!@#",
            "full_name": "New User"
        }

        # Act
        response = await client.post("/api/auth/register", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] is True
        assert "hashed_password" not in data  # Should not expose password
        assert "password" not in data

        # Verify user exists in database
        result = await db_session.execute(
            select(User).where(User.email == user_data["email"])
        )
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == user_data["email"]

    @pytest.mark.asyncio
    async def test_register_duplicate_email(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test registration with duplicate email fails."""
        # Arrange
        user_data = {
            "email": test_user.email,  # Use existing user's email
            "password": "SecurePass123!@#",
            "full_name": "Duplicate User"
        }

        # Act
        response = await client.post("/api/auth/register", json=user_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already registered" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email format."""
        # Arrange
        user_data = {
            "email": "not-an-email",
            "password": "SecurePass123!@#",
            "full_name": "Invalid Email"
        }

        # Act
        response = await client.post("/api/auth/register", json=user_data)

        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password fails validation."""
        # Arrange
        weak_passwords = [
            "short",  # Too short
            "NoDigitsHere!@#",  # No digits
            "nouppercasehere123!",  # No uppercase
            "NOLOWERCASEHERE123!",  # No lowercase
            "NoSpecialChars123",  # No special characters
        ]

        for weak_password in weak_passwords:
            user_data = {
                "email": f"test{weak_password}@example.com",
                "password": weak_password,
                "full_name": "Test User"
            }

            # Act
            response = await client.post("/api/auth/register", json=user_data)

            # Assert
            assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        """Test registration with missing required fields."""
        # Arrange
        incomplete_data = {
            "email": "test@example.com"
            # Missing password and full_name
        }

        # Act
        response = await client.post("/api/auth/register", json=incomplete_data)

        # Assert
        assert response.status_code == 422  # Validation error


class TestLoginEndpoint:
    """Test user login endpoint: POST /api/auth/login"""

    @pytest.mark.asyncio
    async def test_login_success(
        self,
        client: AsyncClient,
        test_user: User,
        test_password: str
    ):
        """Test successful login."""
        # Arrange
        login_data = {
            "email": test_user.email,
            "password": test_password
        }

        # Act
        response = await client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test login with incorrect password."""
        # Arrange
        login_data = {
            "email": test_user.email,
            "password": "WrongPassword123!@#"
        }

        # Act
        response = await client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "incorrect" in data["detail"].lower() or "invalid" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user."""
        # Arrange
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!@#"
        }

        # Act
        response = await client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test login with inactive user account."""
        # Arrange - Create inactive user
        inactive_user = User(
            email="inactive@example.com",
            hashed_password=hash_password("SecurePass123!@#"),
            full_name="Inactive User",
            is_active=False
        )
        db_session.add(inactive_user)
        await db_session.commit()

        login_data = {
            "email": inactive_user.email,
            "password": "SecurePass123!@#"
        }

        # Act
        response = await client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "inactive" in data["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_updates_last_login(
        self,
        client: AsyncClient,
        test_user: User,
        test_password: str,
        db_session: AsyncSession
    ):
        """Test that successful login updates last_login timestamp."""
        # Arrange
        initial_last_login = test_user.last_login
        login_data = {
            "email": test_user.email,
            "password": test_password
        }

        # Act
        response = await client.post("/api/auth/login", json=login_data)
        await db_session.refresh(test_user)

        # Assert
        assert response.status_code == 200
        assert test_user.last_login is not None
        if initial_last_login:
            assert test_user.last_login > initial_last_login


class TestGetCurrentUserEndpoint:
    """Test get current user endpoint: GET /api/auth/me"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test retrieving current user with valid token."""
        # Arrange
        token = create_access_token({"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        # Act
        response = await client.get("/api/auth/me", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()

        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "id" in data
        assert "hashed_password" not in data

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test accessing /me without authentication token."""
        # Act
        response = await client.get("/api/auth/me")

        # Assert
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test accessing /me with invalid token."""
        # Arrange
        headers = {"Authorization": "Bearer invalid.token.here"}

        # Act
        response = await client.get("/api/auth/me", headers=headers)

        # Assert
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_expired_token(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test accessing /me with expired token."""
        # Arrange
        expired_token = create_access_token(
            {"sub": test_user.email},
            expires_delta=timedelta(seconds=-1)
        )
        headers = {"Authorization": f"Bearer {expired_token}"}

        # Act
        response = await client.get("/api/auth/me", headers=headers)

        # Assert
        assert response.status_code == 401


class TestLogoutEndpoint:
    """Test logout endpoint: POST /api/auth/logout"""

    @pytest.mark.asyncio
    async def test_logout_success(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test successful logout."""
        # Arrange
        token = create_access_token({"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        # Act
        response = await client.post("/api/auth/logout", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "logged out" in data["message"].lower() or "success" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_logout_no_token(self, client: AsyncClient):
        """Test logout without authentication token."""
        # Act
        response = await client.post("/api/auth/logout")

        # Assert
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_logout_invalidates_token(
        self,
        client: AsyncClient,
        test_user: User
    ):
        """Test that logout invalidates the token for subsequent requests."""
        # Arrange
        token = create_access_token({"sub": test_user.email})
        headers = {"Authorization": f"Bearer {token}"}

        # Act
        logout_response = await client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200

        # Try to use the same token after logout
        me_response = await client.get("/api/auth/me", headers=headers)

        # Assert
        # Token should be invalidated (stored in Redis blacklist)
        assert me_response.status_code == 401


class TestAuthIntegration:
    """End-to-end integration tests for complete auth flow."""

    @pytest.mark.asyncio
    async def test_complete_auth_flow(
        self,
        client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test complete authentication flow: register -> login -> access protected route -> logout."""
        # 1. Register a new user
        user_data = {
            "email": "flowtest@example.com",
            "password": "FlowTest123!@#",
            "full_name": "Flow Test User"
        }
        register_response = await client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201

        # 2. Login with the new user
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        login_response = await client.post("/api/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Access protected route with token
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["email"] == user_data["email"]

        # 4. Logout
        logout_response = await client.post("/api/auth/logout", headers=headers)
        assert logout_response.status_code == 200

        # 5. Verify token is invalidated after logout
        me_after_logout = await client.get("/api/auth/me", headers=headers)
        assert me_after_logout.status_code == 401
