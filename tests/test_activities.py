"""
Comprehensive tests for Mergington High School API endpoints
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Verify all 9 activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert "Basketball Team" in data
        assert "Tennis Club" in data
        assert "Drama Club" in data
        assert "Art Studio" in data
        assert "Debate Team" in data
        assert "Science Club" in data
    
    def test_get_activities_structure(self, client, reset_activities):
        """Verify each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_activities_participants_initialized(self, client, reset_activities):
        """Verify participants are pre-populated correctly"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        
        assert len(data["Basketball Team"]["participants"]) == 1
        assert "james@mergington.edu" in data["Basketball Team"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_valid_returns_200(self, client, reset_activities):
        """Verify valid signup returns 200"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Verify participant is added to activity"""
        email = "newstudent@mergington.edu"
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 3
    
    def test_signup_duplicate_returns_400(self, client, reset_activities):
        """Verify duplicate signup returns 400 with appropriate error"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_duplicate_does_not_add_duplicate(self, client, reset_activities):
        """Verify duplicate signup doesn't add member twice"""
        initial_count = len(
            client.get("/activities").json()["Chess Club"]["participants"]
        )
        
        # Try to signup duplicate
        client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        
        # Verify count unchanged
        final_count = len(
            client.get("/activities").json()["Chess Club"]["participants"]
        )
        assert initial_count == final_count
    
    def test_signup_activity_not_found_returns_404(self, client, reset_activities):
        """Verify signup to non-existent activity returns 404"""
        response = client.post(
            "/activities/Fictional Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_multiple_students_different_activities(self, client, reset_activities):
        """Verify multiple students can sign up for different activities"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email1}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email1 in activities["Chess Club"]["participants"]
        assert email2 in activities["Programming Class"]["participants"]
    
    def test_signup_same_student_different_activities(self, client, reset_activities):
        """Verify same student can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]
    
    def test_signup_missing_email_parameter(self, client, reset_activities):
        """Verify missing email parameter returns error"""
        response = client.post(
            "/activities/Chess Club/signup"
        )
        # FastAPI returns 422 for missing required parameter
        assert response.status_code == 422
    
    def test_signup_empty_email_parameter(self, client, reset_activities):
        """Verify empty email parameter is still added"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": ""}
        )
        # Empty string is technically valid per the current implementation
        assert response.status_code == 200
        
        activities = client.get("/activities").json()
        assert "" in activities["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_valid_returns_200(self, client, reset_activities):
        """Verify valid unregister returns 200"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Verify participant is removed from activity"""
        email = "michael@mergington.edu"
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1
    
    def test_unregister_not_signed_up_returns_400(self, client, reset_activities):
        """Verify unregistering non-signed-up student returns 400"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notstudent@mergington.edu"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()
    
    def test_unregister_activity_not_found_returns_404(self, client, reset_activities):
        """Verify unregister from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Fictional Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Verify student can re-signup after unregistering"""
        email = "testuser@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Signup again
        response3 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_unregister_doesnt_affect_other_participants(self, client, reset_activities):
        """Verify unregistering one participant doesn't affect others"""
        response_before = client.get("/activities")
        count_before = len(response_before.json()["Chess Club"]["participants"])
        
        # Unregister one student
        client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        
        response_after = client.get("/activities")
        participants_after = response_after.json()["Chess Club"]["participants"]
        
        assert len(participants_after) == count_before - 1
        assert "michael@mergington.edu" not in participants_after
        # Verify other participant remains
        assert "daniel@mergington.edu" in participants_after
    
    def test_unregister_missing_email_parameter(self, client, reset_activities):
        """Verify missing email parameter returns error"""
        response = client.delete(
            "/activities/Chess Club/unregister"
        )
        # FastAPI returns 422 for missing required parameter
        assert response.status_code == 422
    
    def test_unregister_multiple_students_from_same_activity(self, client, reset_activities):
        """Verify multiple students can be unregistered from same activity"""
        # Initial participants: michael, daniel
        response1 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        response2 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "daniel@mergington.edu"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert len(activities["Chess Club"]["participants"]) == 0


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirect_status(self, client):
        """Verify root endpoint returns redirect status"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code in [307, 302]  # Temporary or permanent redirect
    
    def test_root_redirects_to_static_index(self, client):
        """Verify root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert "/static/index.html" in response.headers.get("location", "")


class TestIntegration:
    """Integration tests combining multiple endpoints"""
    
    def test_full_signup_unregister_workflow(self, client, reset_activities):
        """Test complete signup and unregister workflow"""
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_participants = set(
            initial_response.json()[activity]["participants"]
        )
        
        # Signup
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        assert email in after_signup.json()[activity]["participants"]
        assert len(after_signup.json()[activity]["participants"]) == len(
            initial_participants
        ) + 1
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister restored to initial state
        final_response = client.get("/activities")
        assert email not in final_response.json()[activity]["participants"]
        assert (
            set(final_response.json()[activity]["participants"]) ==
            initial_participants
        )
    
    def test_multiple_activities_signup_and_unregister(self, client, reset_activities):
        """Test managing signups across multiple activities"""
        email = "multiactivity@mergington.edu"
        activities_list = ["Chess Club", "Programming Class", "Drama Club"]
        
        # Sign up for multiple activities
        for activity in activities_list:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all signups
        activities = client.get("/activities").json()
        for activity in activities_list:
            assert email in activities[activity]["participants"]
        
        # Unregister from one activity
        client.delete(
            f"/activities/{activities_list[0]}/unregister",
            params={"email": email}
        )
        
        # Verify unregister only affects target activity
        activities = client.get("/activities").json()
        assert email not in activities[activities_list[0]]["participants"]
        assert email in activities[activities_list[1]]["participants"]
        assert email in activities[activities_list[2]]["participants"]
