"""
Integration tests for health check API endpoint.

Following TDD: These tests are written BEFORE the implementation!
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_check_success(client: AsyncClient) -> None:
    """
    Test that health check endpoint returns successful response.

    Given: The application is running
    When: A GET request is made to /health
    Then: Response status code is 200
    And: Response contains status "healthy"
    And: Response contains service name
    And: Response contains version
    """
    # Act
    response = await client.get("/health")

    # Assert
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert data["service"] == "Nihongo Sensei"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_check_response_structure(client: AsyncClient) -> None:
    """
    Test that health check response has correct structure.

    Given: The application is running
    When: A GET request is made to /health
    Then: Response contains all required fields
    And: Fields have correct types
    """
    # Act
    response = await client.get("/health")

    # Assert
    assert response.status_code == 200

    data = response.json()

    # Verify required fields exist
    required_fields = ["status", "service", "version"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

    # Verify field types
    assert isinstance(data["status"], str)
    assert isinstance(data["service"], str)
    assert isinstance(data["version"], str)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_check_contains_timestamp(client: AsyncClient) -> None:
    """
    Test that health check includes a timestamp.

    Given: The application is running
    When: A GET request is made to /health
    Then: Response contains a timestamp field
    And: Timestamp is in ISO format
    """
    # Act
    response = await client.get("/health")

    # Assert
    assert response.status_code == 200

    data = response.json()
    assert "timestamp" in data
    assert isinstance(data["timestamp"], str)

    # Verify timestamp format (basic check for ISO format)
    from datetime import datetime

    try:
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        pytest.fail("Timestamp is not in valid ISO format")
