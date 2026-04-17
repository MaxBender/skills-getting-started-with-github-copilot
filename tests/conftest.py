"""
Pytest configuration and fixtures for FastAPI tests.

This module provides reusable fixtures for integration and unit tests,
including a configured TestClient and sample activity data.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture providing a FastAPI TestClient for making requests to the application.
    
    The client uses the application instance with its in-memory activity database.
    Each test receives a fresh client instance.
    
    Yields:
        TestClient: Configured test client for the FastAPI app
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Fixture providing sample activity data for testing.
    
    Contains various activity states for testing different scenarios:
    - Activities with different participant counts
    - Activities at capacity (max_participants reached)
    - Activities with no participants
    
    Returns:
        dict: Sample activities matching the application's in-memory database structure
    """
    return {
        "Test Chess": {
            "description": "Test chess activity",
            "schedule": "Monday 3:00 PM",
            "max_participants": 2,
            "participants": ["alice@test.edu", "bob@test.edu"]  # At capacity
        },
        "Test Programming": {
            "description": "Test programming activity",
            "schedule": "Tuesday 3:00 PM",
            "max_participants": 3,
            "participants": ["charlie@test.edu"]  # One slot available
        },
        "Test Art": {
            "description": "Test art activity",
            "schedule": "Wednesday 3:00 PM",
            "max_participants": 5,
            "participants": []  # No participants
        }
    }
