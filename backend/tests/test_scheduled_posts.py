import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.models.scheduled_post import ScheduledPost, SchedulingStatus
from app.models.instagram_account import InstagramAccount
from app.models.post import Post, PostType, PostStatus
from app.workers.publisher import publish_scheduled_post


class TestScheduledPosts:
    """Test scheduled posts functionality."""

    @pytest.fixture
    def instagram_account(self, db_session):
        """Create test Instagram account."""
        account = InstagramAccount(
            instagram_user_id="123456789",
            username="testuser",
            access_token="test_token",
            is_active=True
        )
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)
        return account

    @pytest.fixture
    def scheduled_post(self, db_session, instagram_account):
        """Create test scheduled post."""
        future_time = datetime.utcnow() + timedelta(hours=1)
        post = ScheduledPost(
            account_id=instagram_account.id,
            caption="Test scheduled post",
            media_files=["test_image.jpg"],
            scheduled_for=future_time,
            status=SchedulingStatus.PENDING,
            post_type=PostType.FEED
        )
        db_session.add(post)
        db_session.commit()
        db_session.refresh(post)
        return post

    def test_create_scheduled_post(self, client, auth_headers, instagram_account):
        """Test creating a scheduled post."""
        future_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
        
        response = client.post(
            "/api/v1/scheduled",
            json={
                "account_id": instagram_account.id,
                "caption": "New scheduled post",
                "media_files": ["image1.jpg"],
                "scheduled_for": future_time,
                "post_type": "FEED"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["caption"] == "New scheduled post"
        assert data["status"] == "PENDING"

    def test_get_scheduled_posts(self, client, auth_headers, scheduled_post):
        """Test retrieving scheduled posts."""
        response = client.get("/api/v1/scheduled", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(post["id"] == scheduled_post.id for post in data)

    def test_get_scheduled_post_by_id(self, client, auth_headers, scheduled_post):
        """Test retrieving specific scheduled post."""
        response = client.get(
            f"/api/v1/scheduled/{scheduled_post.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == scheduled_post.id
        assert data["caption"] == scheduled_post.caption

    def test_update_scheduled_post(self, client, auth_headers, scheduled_post):
        """Test updating a scheduled post."""
        new_caption = "Updated caption"
        
        response = client.put(
            f"/api/v1/scheduled/{scheduled_post.id}",
            json={"caption": new_caption},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["caption"] == new_caption

    def test_delete_scheduled_post(self, client, auth_headers, scheduled_post):
        """Test deleting a scheduled post."""
        response = client.delete(
            f"/api/v1/scheduled/{scheduled_post.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify post is deleted
        get_response = client.get(
            f"/api/v1/scheduled/{scheduled_post.id}",
            headers=auth_headers
        )
        assert get_response.status_code == 404

    def test_schedule_past_date_validation(self, client, auth_headers, instagram_account):
        """Test validation for scheduling in the past."""
        past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        
        response = client.post(
            "/api/v1/scheduled",
            json={
                "account_id": instagram_account.id,
                "caption": "Past scheduled post",
                "media_files": ["image1.jpg"],
                "scheduled_for": past_time,
                "post_type": "FEED"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "future" in response.json()["detail"].lower()

    def test_schedule_without_media_validation(self, client, auth_headers, instagram_account):
        """Test validation for posts without media."""
        future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        
        response = client.post(
            "/api/v1/scheduled",
            json={
                "account_id": instagram_account.id,
                "caption": "Post without media",
                "media_files": [],
                "scheduled_for": future_time,
                "post_type": "FEED"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "media" in response.json()["detail"].lower()

    @patch('app.workers.publisher.instagram_service.create_post_sync')
    def test_publish_scheduled_post_success(self, mock_create_post, db_session, scheduled_post):
        """Test successful scheduled post publishing."""
        mock_create_post.return_value = {
            "id": "published_post_123",
            "permalink": "https://instagram.com/p/test"
        }
        
        # Execute the Celery task directly
        result = publish_scheduled_post(scheduled_post.id)
        
        assert result["status"] == "success"
        
        # Verify database updates
        db_session.refresh(scheduled_post)
        assert scheduled_post.status == SchedulingStatus.PUBLISHED
        assert scheduled_post.published_at is not None

    @patch('app.workers.publisher.instagram_service.create_post_sync')
    def test_publish_scheduled_post_failure(self, mock_create_post, db_session, scheduled_post):
        """Test failed scheduled post publishing."""
        mock_create_post.side_effect = Exception("Instagram API error")
        
        # Execute the Celery task directly
        result = publish_scheduled_post(scheduled_post.id)
        
        assert result["status"] == "error"
        
        # Verify database updates
        db_session.refresh(scheduled_post)
        assert scheduled_post.status == SchedulingStatus.FAILED
        assert scheduled_post.error_message is not None

    def test_bulk_schedule_posts(self, client, auth_headers, instagram_account):
        """Test bulk scheduling multiple posts."""
        posts_data = []
        for i in range(3):
            future_time = (datetime.utcnow() + timedelta(hours=i+1)).isoformat()
            posts_data.append({
                "account_id": instagram_account.id,
                "caption": f"Bulk post {i+1}",
                "media_files": [f"image{i+1}.jpg"],
                "scheduled_for": future_time,
                "post_type": "FEED"
            })
        
        response = client.post(
            "/api/v1/scheduled/bulk",
            json={"posts": posts_data},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data["created"]) == 3

    def test_get_posts_by_status(self, client, auth_headers, scheduled_post):
        """Test filtering posts by status."""
        response = client.get(
            "/api/v1/scheduled?status=PENDING",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(post["status"] == "PENDING" for post in data)

    def test_get_posts_by_account(self, client, auth_headers, scheduled_post):
        """Test filtering posts by account."""
        response = client.get(
            f"/api/v1/scheduled?account_id={scheduled_post.account_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(post["account_id"] == scheduled_post.account_id for post in data)
