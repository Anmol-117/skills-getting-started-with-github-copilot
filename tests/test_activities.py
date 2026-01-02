import pytest
from fastapi.testclient import TestClient


def test_get_activities(client: TestClient):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]


def test_signup_for_activity(client: TestClient):
    """Test signing up for an activity"""
    # Test successful signup
    response = client.post("/activities/Chess%20Club/signup?email=test@example.com")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "Signed up test@example.com for Chess Club" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_duplicate(client: TestClient):
    """Test signing up for the same activity twice"""
    # First signup
    client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")

    # Second signup should fail
    response = client.post("/activities/Chess%20Club/signup?email=duplicate@example.com")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client: TestClient):
    """Test signing up for a nonexistent activity"""
    response = client.post("/activities/Nonexistent%20Activity/signup?email=test@example.com")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_from_activity(client: TestClient):
    """Test unregistering from an activity"""
    # First signup
    client.post("/activities/Chess%20Club/signup?email=unregister@example.com")

    # Then unregister
    response = client.delete("/activities/Chess%20Club/unregister?email=unregister@example.com")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "Unregistered unregister@example.com from Chess Club" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "unregister@example.com" not in activities["Chess Club"]["participants"]


def test_unregister_not_signed_up(client: TestClient):
    """Test unregistering someone who isn't signed up"""
    response = client.delete("/activities/Chess%20Club/unregister?email=notsignedup@example.com")
    assert response.status_code == 400

    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_unregister_nonexistent_activity(client: TestClient):
    """Test unregistering from a nonexistent activity"""
    response = client.delete("/activities/Nonexistent%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404

    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_root_redirect(client: TestClient):
    """Test root endpoint redirects to static files"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]