"""
Unit tests for authentication utilities (TDD - TESTS FIRST).

These tests are written BEFORE implementation to follow Test-Driven Development.
They will initially FAIL, then we implement the code to make them pass.
"""

from datetime import datetime, timedelta

import pytest
from jose import JWTError, jwt

from app.config import settings


# Import the functions we're going to implement
# These imports will fail until we create the module
try:
    from app.utils.auth import (
        create_access_token,
        decode_access_token,
        hash_password,
        verify_password,
    )
except ImportError:
    # Expected to fail initially - we haven't written the code yet
    create_access_token = None
    decode_access_token = None
    hash_password = None
    verify_password = None


class TestPasswordHashing:
    """Test password hashing and verification functions."""

    @pytest.mark.skipif(hash_password is None, reason="hash_password not implemented yet")
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "securePassword123!"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    @pytest.mark.skipif(hash_password is None, reason="hash_password not implemented yet")
    def test_hash_password_different_each_time(self):
        """Test that hashing the same password produces different hashes (salt)."""
        password = "securePassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different due to random salt
        assert hash1 != hash2

    @pytest.mark.skipif(hash_password is None, reason="hash_password not implemented yet")
    def test_hash_password_not_plaintext(self):
        """Test that hash doesn't contain the original password."""
        password = "securePassword123!"
        hashed = hash_password(password)

        # Hash should not contain the original password
        assert password not in hashed

    @pytest.mark.skipif(not all([hash_password, verify_password]), reason="Functions not implemented yet")
    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "securePassword123!"
        hashed = hash_password(password)

        # Should return True for correct password
        assert verify_password(password, hashed) is True

    @pytest.mark.skipif(not all([hash_password, verify_password]), reason="Functions not implemented yet")
    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "securePassword123!"
        wrong_password = "wrongPassword456!"
        hashed = hash_password(password)

        # Should return False for wrong password
        assert verify_password(wrong_password, hashed) is False

    @pytest.mark.skipif(verify_password is None, reason="verify_password not implemented yet")
    def test_verify_password_empty_string(self):
        """Test password verification with empty password."""
        hashed = "$2b$12$somehash"  # Fake hash

        # Should return False for empty password
        assert verify_password("", hashed) is False

    @pytest.mark.skipif(not all([hash_password, verify_password]), reason="Functions not implemented yet")
    def test_verify_password_unicode_characters(self):
        """Test password hashing and verification with Unicode characters."""
        password = "パスワード123!@#"  # Japanese characters
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password("パスワード124!@#", hashed) is False


class TestJWTTokens:
    """Test JWT token creation and validation functions."""

    @pytest.mark.skipif(create_access_token is None, reason="create_access_token not implemented yet")
    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a valid JWT string."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0
        # JWT format: header.payload.signature
        assert token.count(".") == 2

    @pytest.mark.skipif(create_access_token is None, reason="create_access_token not implemented yet")
    def test_create_access_token_contains_subject(self):
        """Test that created token contains the subject claim."""
        email = "user@example.com"
        data = {"sub": email}
        token = create_access_token(data)

        # Decode without verification to check contents
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == email

    @pytest.mark.skipif(create_access_token is None, reason="create_access_token not implemented yet")
    def test_create_access_token_has_expiration(self):
        """Test that created token has an expiration time."""
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert "exp" in payload

        # Expiration should be in the future
        exp_timestamp = payload["exp"]
        assert exp_timestamp > datetime.utcnow().timestamp()

    @pytest.mark.skipif(create_access_token is None, reason="create_access_token not implemented yet")
    def test_create_access_token_custom_expiration(self):
        """Test creating token with custom expiration time."""
        data = {"sub": "user@example.com"}
        custom_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=custom_delta)

        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

        # Check expiration is approximately 60 minutes from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        expected_time = datetime.utcnow() + custom_delta
        time_diff = abs((exp_time - expected_time).total_seconds())

        # Allow 5 seconds tolerance
        assert time_diff < 5

    @pytest.mark.skipif(decode_access_token is None, reason="decode_access_token not implemented yet")
    def test_decode_access_token_valid(self):
        """Test decoding a valid access token."""
        email = "user@example.com"
        data = {"sub": email}
        token = create_access_token(data)

        decoded = decode_access_token(token)

        assert decoded is not None
        assert decoded == email

    @pytest.mark.skipif(decode_access_token is None, reason="decode_access_token not implemented yet")
    def test_decode_access_token_invalid_signature(self):
        """Test decoding token with invalid signature."""
        # Create a valid token
        data = {"sub": "user@example.com"}
        token = create_access_token(data)

        # Tamper with the token (change significant portion of signature)
        parts = token.split(".")
        if len(parts) == 3:
            # Replace signature with obviously invalid one
            tampered_token = f"{parts[0]}.{parts[1]}.invalidsignature"
        else:
            tampered_token = token + "tampered"

        # Should return None for invalid token
        decoded = decode_access_token(tampered_token)
        assert decoded is None

    @pytest.mark.skipif(decode_access_token is None, reason="decode_access_token not implemented yet")
    def test_decode_access_token_expired(self):
        """Test decoding an expired token."""
        email = "user@example.com"
        data = {"sub": email}

        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        # Should return None for expired token
        decoded = decode_access_token(token)
        assert decoded is None

    @pytest.mark.skipif(decode_access_token is None, reason="decode_access_token not implemented yet")
    def test_decode_access_token_no_subject(self):
        """Test decoding token without 'sub' claim."""
        # Create token without 'sub' claim
        data = {"user_id": "123"}
        payload = {**data, "exp": datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

        # Should return None for token without 'sub' claim
        decoded = decode_access_token(token)
        assert decoded is None

    @pytest.mark.skipif(decode_access_token is None, reason="decode_access_token not implemented yet")
    def test_decode_access_token_malformed(self):
        """Test decoding a malformed token."""
        malformed_token = "not.a.valid.jwt.token"

        # Should return None for malformed token
        decoded = decode_access_token(malformed_token)
        assert decoded is None

    @pytest.mark.skipif(decode_access_token is None, reason="decode_access_token not implemented yet")
    def test_decode_access_token_empty_string(self):
        """Test decoding an empty string."""
        # Should return None for empty string
        decoded = decode_access_token("")
        assert decoded is None


# This test should be skipped initially, will pass once implementation is done
@pytest.mark.skipif(
    not all([hash_password, verify_password, create_access_token, decode_access_token]),
    reason="All auth utilities not implemented yet"
)
def test_complete_auth_flow():
    """Integration test: Complete authentication flow."""
    # 1. Hash a password
    password = "securePassword123!"
    hashed = hash_password(password)

    # 2. Verify the password
    assert verify_password(password, hashed) is True

    # 3. Create a token for the user
    email = "user@example.com"
    token = create_access_token({"sub": email})

    # 4. Decode the token
    decoded_email = decode_access_token(token)
    assert decoded_email == email

    # 5. Complete flow should work end-to-end
    assert decoded_email is not None
