import pytest

pytestmark = pytest.mark.asyncio

async def test_register_user(test_client, test_user_data):
    """Test user registration endpoint."""
    response = test_client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]
    assert "id" in data
    assert "password" not in data

async def test_register_duplicate_user(test_client, test_user_data):
    """Test registration with duplicate username/email."""
    # First registration
    response = test_client.post("/auth/register", json=test_user_data)
    assert response.status_code == 200
    
    # Attempt duplicate registration
    response = test_client.post("/auth/register", json=test_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

async def test_login_user(test_client, test_user_data):
    """Test user login endpoint."""
    # Register user first
    test_client.post("/auth/register", json=test_user_data)
    
    # Login
    login_data = {
        "username": test_user_data["username"],
        "password": test_user_data["password"]
    }
    response = test_client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_invalid_credentials(test_client):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    response = test_client.post("/auth/login", json=login_data)
    assert response.status_code == 400
    assert "Incorrect username or password" in response.json()["detail"]

async def test_get_current_user(test_client, test_user_data, auth_headers):
    """Test getting current user profile."""
    # Register user first
    test_client.post("/auth/register", json=test_user_data)
    
    response = test_client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user_data["username"]
    assert data["email"] == test_user_data["email"]

async def test_unauthorized_access(test_client):
    """Test accessing protected endpoint without token."""
    response = test_client.get("/auth/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]
