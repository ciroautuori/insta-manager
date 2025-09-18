"""Add database indexes for performance optimization

Revision ID: 002_add_indexes
Revises: 001_initial_migration
Create Date: 2024-12-18 13:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_indexes'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes."""
    
    # Analytics table indexes
    op.create_index('idx_analytics_account_date', 'analytics', ['account_id', 'date'])
    op.create_index('idx_analytics_date', 'analytics', ['date'])
    
    # Posts table indexes
    op.create_index('idx_posts_account_status', 'posts', ['account_id', 'status'])
    op.create_index('idx_posts_created_at', 'posts', ['created_at'])
    op.create_index('idx_posts_instagram_id', 'posts', ['instagram_post_id'])
    
    # Scheduled posts table indexes
    op.create_index('idx_scheduled_posts_account_status', 'scheduled_posts', ['account_id', 'status'])
    op.create_index('idx_scheduled_posts_scheduled_for', 'scheduled_posts', ['scheduled_for'])
    op.create_index('idx_scheduled_posts_status_scheduled', 'scheduled_posts', ['status', 'scheduled_for'])
    
    # Instagram accounts table indexes
    op.create_index('idx_instagram_accounts_active', 'instagram_accounts', ['is_active'])
    op.create_index('idx_instagram_accounts_username', 'instagram_accounts', ['username'])
    op.create_index('idx_instagram_accounts_instagram_user_id', 'instagram_accounts', ['instagram_user_id'])
    
    # Media table indexes
    op.create_index('idx_media_account_type', 'media', ['account_id', 'media_type'])
    op.create_index('idx_media_created_at', 'media', ['created_at'])
    
    # Admin table indexes
    op.create_index('idx_admin_email', 'admin', ['email'])
    op.create_index('idx_admin_active', 'admin', ['is_active'])


def downgrade() -> None:
    """Remove performance indexes."""
    
    # Drop all indexes
    op.drop_index('idx_analytics_account_date', table_name='analytics')
    op.drop_index('idx_analytics_date', table_name='analytics')
    
    op.drop_index('idx_posts_account_status', table_name='posts')
    op.drop_index('idx_posts_created_at', table_name='posts')
    op.drop_index('idx_posts_instagram_id', table_name='posts')
    
    op.drop_index('idx_scheduled_posts_account_status', table_name='scheduled_posts')
    op.drop_index('idx_scheduled_posts_scheduled_for', table_name='scheduled_posts')
    op.drop_index('idx_scheduled_posts_status_scheduled', table_name='scheduled_posts')
    
    op.drop_index('idx_instagram_accounts_active', table_name='instagram_accounts')
    op.drop_index('idx_instagram_accounts_username', table_name='instagram_accounts')
    op.drop_index('idx_instagram_accounts_instagram_user_id', table_name='instagram_accounts')
    
    op.drop_index('idx_media_account_type', table_name='media')
    op.drop_index('idx_media_created_at', table_name='media')
    
    op.drop_index('idx_admin_email', table_name='admin')
    op.drop_index('idx_admin_active', table_name='admin')
