import pytest
from fastapi.testclient import TestClient
from app.models.admin import Admin
from app.core.security import get_password_hash, verify_password


class TestAuthentication:
    """Test authentication endpoints and security."""

    def test_admin_registration(self, client, db_session):
        """Test admin user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newadmin@example.com",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newadmin@example.com"
        assert "id" in data

    def test_admin_login_success(self, client, admin_user):
        """Test successful admin login."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_user.email,
                "password": "testpassword123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_admin_login_invalid_credentials(self, client, admin_user):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": admin_user.email,
                "password": "wrongpassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_admin_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anypassword"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 401

    def test_get_current_admin(self, client, auth_headers):
        """Test getting current admin profile."""
        response = client.get("/api/v1/admin/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data

    def test_unauthorized_access(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/v1/admin/me")
        assert response.status_code == 401

    def test_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/admin/me", headers=headers)
        assert response.status_code == 401

    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)

    def test_duplicate_admin_registration(self, client, admin_user):
        """Test registering admin with existing email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": admin_user.email,
                "password": "newpassword123"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
