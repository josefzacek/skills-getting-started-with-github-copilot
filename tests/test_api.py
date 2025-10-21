"""
Tests for the Mergington High School Activities API.
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestActivitiesAPI:
    """Test class for activities API endpoints."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.client = TestClient(app)
    
    def test_root_redirect(self):
        """Test that root path redirects to static/index.html."""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_get_activities_success(self):
        """Test successful retrieval of activities."""
        response = self.client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check structure of first activity
        first_activity = list(data.values())[0]
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        assert isinstance(first_activity["participants"], list)
    
    def test_signup_for_activity_success(self):
        """Test successful signup for an activity."""
        # Get initial participant count
        initial_response = self.client.get("/activities")
        initial_data = initial_response.json()
        chess_club = initial_data["Chess Club"]
        initial_count = len(chess_club["participants"])
        
        # Sign up new student
        response = self.client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        updated_response = self.client.get("/activities")
        updated_data = updated_response.json()
        updated_chess_club = updated_data["Chess Club"]
        assert len(updated_chess_club["participants"]) == initial_count + 1
        assert "newstudent@mergington.edu" in updated_chess_club["participants"]
    
    def test_signup_for_nonexistent_activity(self):
        """Test signup for non-existent activity returns 404."""
        response = self.client.post(
            "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_registration(self):
        """Test that duplicate registration returns 400."""
        # Try to register existing student
        response = self.client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up"
    
    def test_unregister_from_activity_success(self):
        """Test successful unregistration from an activity."""
        # Get initial participant count
        initial_response = self.client.get("/activities")
        initial_data = initial_response.json()
        chess_club = initial_data["Chess Club"]
        initial_count = len(chess_club["participants"])
        
        # Unregister existing student
        response = self.client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was removed
        updated_response = self.client.get("/activities")
        updated_data = updated_response.json()
        updated_chess_club = updated_data["Chess Club"]
        assert len(updated_chess_club["participants"]) == initial_count - 1
        assert "michael@mergington.edu" not in updated_chess_club["participants"]
    
    def test_unregister_from_nonexistent_activity(self):
        """Test unregister from non-existent activity returns 404."""
        response = self.client.post(
            "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_non_registered_student(self):
        """Test unregister non-registered student returns 400."""
        response = self.client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not registered for this activity"
    
    def test_activity_data_integrity(self):
        """Test that activity data maintains expected structure."""
        response = self.client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        
        for activity_name, activity_data in data.items():
            # Check required fields
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            
            assert "description" in activity_data
            assert isinstance(activity_data["description"], str)
            assert len(activity_data["description"]) > 0
            
            assert "schedule" in activity_data
            assert isinstance(activity_data["schedule"], str)
            assert len(activity_data["schedule"]) > 0
            
            assert "max_participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0
            
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            
            # Check that participants count doesn't exceed max
            assert len(activity_data["participants"]) <= activity_data["max_participants"]
            
            # Check that all participants have valid email format
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant
                assert participant.endswith("@mergington.edu")


class TestActivityBusinessLogic:
    """Test business logic and edge cases."""
    
    def setup_method(self):
        """Setup method run before each test."""
        self.client = TestClient(app)
    
    def test_activity_capacity_limits(self):
        """Test that activities respect participant limits."""
        response = self.client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            current_participants = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            spots_available = max_participants - current_participants
            
            # Verify spots calculation is correct
            assert spots_available >= 0
            assert current_participants <= max_participants
    
    def test_signup_and_unregister_workflow(self):
        """Test complete signup and unregister workflow."""
        test_email = "workflow@mergington.edu"
        activity_name = "Programming Class"
        
        # 1. Get initial state
        initial_response = self.client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = initial_data[activity_name]["participants"].copy()
        
        # 2. Sign up
        signup_response = self.client.post(
            f"/activities/{activity_name}/signup?email={test_email}"
        )
        assert signup_response.status_code == 200
        
        # 3. Verify signup
        after_signup_response = self.client.get("/activities")
        after_signup_data = after_signup_response.json()
        assert test_email in after_signup_data[activity_name]["participants"]
        assert len(after_signup_data[activity_name]["participants"]) == len(initial_participants) + 1
        
        # 4. Unregister
        unregister_response = self.client.post(
            f"/activities/{activity_name}/unregister?email={test_email}"
        )
        assert unregister_response.status_code == 200
        
        # 5. Verify unregister
        after_unregister_response = self.client.get("/activities")
        after_unregister_data = after_unregister_response.json()
        assert test_email not in after_unregister_data[activity_name]["participants"]
        assert after_unregister_data[activity_name]["participants"] == initial_participants
    
    def test_special_characters_in_activity_names(self):
        """Test handling of special characters in activity names."""
        # Test with URL encoding
        response = self.client.post(
            "/activities/Chess%20Club/signup?email=special@mergington.edu"
        )
        # Should work with URL encoded space
        assert response.status_code in [200, 400]  # 400 if already registered
    
    def test_email_validation_patterns(self):
        """Test various email patterns."""
        test_cases = [
            ("valid@mergington.edu", True),
            ("another.student@mergington.edu", True),
            ("student+tag@mergington.edu", True),
        ]
        
        for email, should_work in test_cases:
            response = self.client.post(
                f"/activities/Art Club/signup?email={email}"
            )
            if should_work:
                assert response.status_code in [200, 400]  # 400 if already registered
            # Note: The current API doesn't validate email format,
            # but this test structure allows for future email validation