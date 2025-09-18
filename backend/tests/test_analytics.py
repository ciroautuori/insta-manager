import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch
from app.models.analytics import Analytics
from app.models.instagram_account import InstagramAccount


class TestAnalytics:
    """Test analytics functionality."""

    @pytest.fixture
    def instagram_account(self, db_session):
        """Create test Instagram account."""
        account = InstagramAccount(
            instagram_user_id="123456789",
            username="testuser",
            access_token="test_token",
            is_active=True,
            is_business_account=True,
            followers_count=1000,
            following_count=500,
            posts_count=50
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        return account

    @pytest.fixture
    def analytics_data(self, db_session, instagram_account):
        """Create test analytics data."""
        analytics_records = []
        for i in range(7):
            record_date = date.today() - timedelta(days=i)
            analytics = Analytics(
                account_id=instagram_account.id,
                date=record_date,
                followers_count=1000 + i * 10,
                following_count=500,
                posts_count=50 + i,
                total_impressions=5000 + i * 100,
                total_reach=4000 + i * 80,
                profile_views=200 + i * 5,
                website_clicks=50 + i * 2
            )
            analytics_records.append(analytics)
            db_session.add(analytics)
        
        db_session.commit()
        return analytics_records

    def test_get_analytics(self, client, auth_headers, analytics_data):
        """Test retrieving analytics data."""
        response = client.get("/api/v1/analytics/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 7
        assert all("total_impressions" in record for record in data)

    def test_get_analytics_with_filters(self, client, auth_headers, analytics_data, instagram_account):
        """Test retrieving analytics with filters."""
        start_date = (date.today() - timedelta(days=3)).isoformat()
        
        response = client.get(
            f"/api/v1/analytics/?account_id={instagram_account.id}&start_date={start_date}&limit=5",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_get_account_analytics(self, client, auth_headers, analytics_data, instagram_account):
        """Test retrieving analytics for specific account."""
        response = client.get(
            f"/api/v1/analytics/account/{instagram_account.id}?days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 7
        assert all(record["account_id"] == instagram_account.id for record in data)

    def test_get_account_analytics_nonexistent(self, client, auth_headers):
        """Test retrieving analytics for non-existent account."""
        response = client.get("/api/v1/analytics/account/99999", headers=auth_headers)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch('app.services.instagram_service.instagram_service.get_account_insights')
    def test_sync_account_analytics_success(self, mock_get_insights, client, auth_headers, instagram_account):
        """Test successful analytics synchronization."""
        mock_get_insights.return_value = {
            "data": [
                {
                    "end_time": "2024-01-15T00:00:00Z",
                    "values": [
                        {"name": "impressions", "value": 1500},
                        {"name": "reach", "value": 1200},
                        {"name": "profile_views", "value": 300}
                    ]
                }
            ]
        }
        
        response = client.post(
            f"/api/v1/analytics/sync/{instagram_account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()

    def test_sync_analytics_non_business_account(self, client, auth_headers, db_session):
        """Test analytics sync for non-business account."""
        personal_account = InstagramAccount(
            instagram_user_id="987654321",
            username="personaluser",
            access_token="test_token",
            is_active=True,
            is_business_account=False
        )
        db_session.add(personal_account)
        db_session.commit()
        
        response = client.post(
            f"/api/v1/analytics/sync/{personal_account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "business" in response.json()["detail"].lower()

    def test_get_account_insights(self, client, auth_headers, analytics_data, instagram_account):
        """Test retrieving account insights."""
        response = client.get(
            f"/api/v1/analytics/insights/{instagram_account.id}?days=7",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["account_id"] == instagram_account.id
        assert "followers_growth" in data
        assert "engagement_by_post_type" in data
        assert "best_posting_times" in data

    def test_delete_account_analytics(self, client, auth_headers, analytics_data, instagram_account):
        """Test deleting account analytics."""
        response = client.delete(
            f"/api/v1/analytics/account/{instagram_account.id}?confirm=true",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert "deleted" in response.json()["message"].lower()

    def test_delete_analytics_without_confirmation(self, client, auth_headers, instagram_account):
        """Test deleting analytics without confirmation."""
        response = client.delete(
            f"/api/v1/analytics/account/{instagram_account.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "confirm" in response.json()["detail"].lower()

    def test_export_analytics_json(self, client, auth_headers, analytics_data, instagram_account):
        """Test exporting analytics in JSON format."""
        response = client.get(
            f"/api/v1/analytics/export/{instagram_account.id}?format=json",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "account" in data
        assert "analytics" in data
        assert len(data["analytics"]) == 7

    def test_export_analytics_csv(self, client, auth_headers, analytics_data, instagram_account):
        """Test exporting analytics in CSV format."""
        response = client.get(
            f"/api/v1/analytics/export/{instagram_account.id}?format=csv",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]

    def test_export_analytics_with_date_range(self, client, auth_headers, analytics_data, instagram_account):
        """Test exporting analytics with date range."""
        start_date = (date.today() - timedelta(days=3)).isoformat()
        end_date = date.today().isoformat()
        
        response = client.get(
            f"/api/v1/analytics/export/{instagram_account.id}?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["analytics"]) <= 4  # 3 days + today
