"""
Integration and unit tests for FastAPI application endpoints.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the code being tested (make API call)
- Assert: Verify the results match expectations
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


class TestRootEndpoint:
    """Tests for the GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """
        Test that GET / redirects to /static/index.html
        
        AAA Pattern:
        - Arrange: TestClient is ready (from fixture)
        - Act: Send GET request to /
        - Assert: Verify redirect response and location header
        """
        # Arrange
        # (client fixture already initialized)
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all activities as JSON
        
        AAA Pattern:
        - Arrange: TestClient is ready
        - Act: Send GET request to /activities
        - Assert: Verify response structure and content
        """
        # Arrange
        # (client fixture already initialized)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Verify activity structure
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_includes_predefined_activities(self, client):
        """
        Test that GET /activities includes expected predefined activities
        
        AAA Pattern:
        - Arrange: TestClient is ready
        - Act: Send GET request to /activities
        - Assert: Verify specific activities exist
        """
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name in expected_activities:
            assert activity_name in activities


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success_for_available_activity(self, client):
        """
        Test successful signup for an available activity
        
        AAA Pattern:
        - Arrange: Set up valid activity and email
        - Act: POST signup request
        - Assert: Verify participant added and success message returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        
        # Verify participant was added
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        assert email in verify_data[activity_name]["participants"]
    
    def test_signup_fails_for_nonexistent_activity(self, client):
        """
        Test signup fails with 404 when activity doesn't exist
        
        AAA Pattern:
        - Arrange: Use non-existent activity name
        - Act: POST signup request
        - Assert: Verify 404 error response
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_fails_for_duplicate_email(self, client):
        """
        Test signup fails with 400 when student already signed up
        
        AAA Pattern:
        - Arrange: Get existing participant from an activity
        - Act: Try to sign up same email again
        - Assert: Verify 400 error response
        """
        # Arrange
        activity_name = "Chess Club"
        # Get existing participants
        get_response = client.get("/activities")
        existing_email = get_response.json()[activity_name]["participants"][0]
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_succeeds_before_reaching_capacity(self, client):
        """
        Test signup succeeds when activity has available slots
        
        AAA Pattern:
        - Arrange: Find activity with available capacity
        - Act: Sign up student for that activity
        - Assert: Verify successful signup
        """
        # Arrange
        # Programming Class has max 20, should have available slots
        activity_name = "Programming Class"
        email = "capacity@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success_removes_participant(self, client):
        """
        Test successful unregister removes participant from activity
        
        AAA Pattern:
        - Arrange: First signup a student, then set up unregister
        - Act: POST unregister request
        - Assert: Verify participant removed and success message returned
        """
        # Arrange
        activity_name = "Programming Class"
        email = "unreg_student@mergington.edu"
        
        # First, sign up the student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        
        # Verify participant was removed
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        assert email not in verify_data[activity_name]["participants"]
    
    def test_unregister_fails_for_nonexistent_activity(self, client):
        """
        Test unregister fails with 404 when activity doesn't exist
        
        AAA Pattern:
        - Arrange: Use non-existent activity name
        - Act: POST unregister request
        - Assert: Verify 404 error response
        """
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_unregister_fails_for_nonparticipant(self, client):
        """
        Test unregister fails with 404 when participant not in activity
        
        AAA Pattern:
        - Arrange: Use valid activity but non-participant email
        - Act: POST unregister request
        - Assert: Verify 404 error response
        """
        # Arrange
        activity_name = "Debate Club"
        email = "nonparticipant@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestSignupUnregisterFlow:
    """Integration tests for signup and unregister flow"""
    
    def test_signup_then_unregister_flow(self, client):
        """
        Test complete flow: signup then unregister
        
        AAA Pattern:
        - Arrange: Set up activity and email
        - Act: Sign up, then unregister
        - Assert: Verify participant added then removed
        """
        # Arrange
        activity_name = "Tennis Club"
        email = "flow_test@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert signup
        assert signup_response.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]
        
        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert unregister
        assert unregister_response.status_code == 200
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]
    
    def test_multiple_signups_and_unregisters(self, client):
        """
        Test multiple students signing up and unregistering
        
        AAA Pattern:
        - Arrange: Set up multiple emails and activity
        - Act: Sign up multiple students, then unregister one
        - Assert: Verify correct participants list
        """
        # Arrange
        activity_name = "Art Studio"
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        # Act - Sign up all students
        for email in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Assert all signed up
        activities = client.get("/activities").json()
        for email in students:
            assert email in activities[activity_name]["participants"]
        
        # Act - Unregister one student
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": students[0]}
        )
        assert unregister_response.status_code == 200
        
        # Assert one removed, others remain
        activities = client.get("/activities").json()
        assert students[0] not in activities[activity_name]["participants"]
        assert students[1] in activities[activity_name]["participants"]
        assert students[2] in activities[activity_name]["participants"]
