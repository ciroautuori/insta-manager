import httpx
import json
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.instagram_account import InstagramAccount
from app.models.post import Post
from app.models.media import Media
from app.core.security import RateLimitManager

class InstagramService:
    """Servizio per interazione con Meta Graph API"""
    
    def __init__(self):
        self.base_url = settings.META_GRAPH_API_URL
        self.app_id = settings.META_APP_ID
        self.app_secret = settings.META_APP_SECRET
        self.redirect_uri = settings.META_REDIRECT_URI
    
    def get_authorization_url(self, state: str) -> str:
        """Genera URL per autorizzazione Instagram"""
        params = {
            'client_id': self.app_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'instagram_basic,instagram_content_publish,instagram_manage_insights',
            'response_type': 'code',
            'state': state
        }
        return f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Scambia codice autorizzazione con access token"""
        async with httpx.AsyncClient() as client:
            data = {
                'client_id': self.app_id,
                'client_secret': self.app_secret,
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
                'code': code
            }
            
            response = await client.post(
                'https://api.instagram.com/oauth/access_token',
                data=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore scambio token: {response.text}")
            
            return response.json()
    
    async def get_long_lived_token(self, access_token: str) -> Dict[str, Any]:
        """Converte short-lived token in long-lived token"""
        async with httpx.AsyncClient() as client:
            params = {
                'grant_type': 'ig_exchange_token',
                'client_secret': self.app_secret,
                'access_token': access_token
            }
            
            response = await client.get(
                f"{self.base_url}/oauth/access_token",
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore long-lived token: {response.text}")
            
            return response.json()
    
    async def refresh_access_token(self, access_token: str) -> Dict[str, Any]:
        """Rinnova access token"""
        async with httpx.AsyncClient() as client:
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': access_token
            }
            
            response = await client.get(
                f"{self.base_url}/refresh_access_token",
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore refresh token: {response.text}")
            
            return response.json()
    
    async def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Ottieni profilo utente Instagram"""
        async with httpx.AsyncClient() as client:
            params = {
                'fields': 'id,username,account_type,media_count,followers_count,follows_count',
                'access_token': access_token
            }
            
            response = await client.get(
                f"{self.base_url}/me",
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore profilo utente: {response.text}")
            
            return response.json()
    
    async def upload_media(self, access_token: str, media_url: str, media_type: str = "IMAGE") -> str:
        """Upload media su Instagram"""
        async with httpx.AsyncClient() as client:
            data = {
                'image_url' if media_type == "IMAGE" else 'video_url': media_url,
                'access_token': access_token
            }
            
            response = await client.post(
                f"{self.base_url}/me/media",
                data=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore upload media: {response.text}")
            
            result = response.json()
            return result['id']
    
    async def publish_media(self, access_token: str, creation_id: str, caption: str = None) -> str:
        """Pubblica media su Instagram"""
        async with httpx.AsyncClient() as client:
            data = {
                'creation_id': creation_id,
                'access_token': access_token
            }
            
            if caption:
                data['caption'] = caption
            
            response = await client.post(
                f"{self.base_url}/me/media_publish",
                data=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore pubblicazione: {response.text}")
            
            result = response.json()
            return result['id']
    
    async def create_post(
        self, 
        access_token: str, 
        media_urls: List[str], 
        caption: str = None,
        location_id: str = None
    ) -> str:
        """Crea e pubblica post completo"""
        
        # Upload media
        media_ids = []
        for media_url in media_urls:
            media_id = await self.upload_media(access_token, media_url)
            media_ids.append(media_id)
        
        # Se singolo media, pubblica direttamente
        if len(media_ids) == 1:
            return await self.publish_media(access_token, media_ids[0], caption)
        
        # Se carousel, crea container
        return await self.create_carousel_post(access_token, media_ids, caption, location_id)
    
    def create_post_sync(
        self,
        access_token: str,
        media_urls: List[str],
        caption: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> str:
        """Wrapper sincrono per create_post da usare nei worker Celery."""
        try:
            # Prova con asyncio.run se non c'è un loop attivo
            return asyncio.run(self.create_post(access_token, media_urls, caption, location_id))
        except RuntimeError:
            # Se un event loop è già in esecuzione, usa un loop dedicato
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(self.create_post(access_token, media_urls, caption, location_id))
            finally:
                asyncio.set_event_loop(None)
                loop.close()
    
    async def create_carousel_post(
        self,
        access_token: str,
        media_ids: List[str],
        caption: str = None,
        location_id: str = None
    ) -> str:
        """Crea post carousel"""
        async with httpx.AsyncClient() as client:
            data = {
                'media_type': 'CAROUSEL',
                'children': ','.join(media_ids),
                'access_token': access_token
            }
            
            if caption:
                data['caption'] = caption
            if location_id:
                data['location_id'] = location_id
            
            # Crea container carousel
            response = await client.post(
                f"{self.base_url}/me/media",
                data=data
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore creazione carousel: {response.text}")
            
            container_id = response.json()['id']
            
            # Pubblica carousel
            return await self.publish_media(access_token, container_id)

    def get_media_insights_sync(self, access_token: str, media_id: str) -> Dict[str, Any]:
        """Wrapper sincrono per get_media_insights."""
        try:
            return asyncio.run(self.get_media_insights(access_token, media_id))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(self.get_media_insights(access_token, media_id))
            finally:
                asyncio.set_event_loop(None)
                loop.close()

    def get_account_insights_sync(
        self,
        access_token: str,
        period: str = "day",
        since: datetime = None,
        until: datetime = None
    ) -> Dict[str, Any]:
        """Wrapper sincrono per get_account_insights."""
        try:
            return asyncio.run(self.get_account_insights(access_token, period, since, until))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(self.get_account_insights(access_token, period, since, until))
            finally:
                asyncio.set_event_loop(None)
                loop.close()
    
    async def get_media_insights(self, access_token: str, media_id: str) -> Dict[str, Any]:
        """Ottieni insights per media"""
        async with httpx.AsyncClient() as client:
            params = {
                'metric': 'impressions,reach,likes,comments,shares,saved',
                'access_token': access_token
            }
            
            response = await client.get(
                f"{self.base_url}/{media_id}/insights",
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore insights media: {response.text}")
            
            return response.json()
    
    async def get_account_insights(
        self,
        access_token: str,
        period: str = "day",
        since: datetime = None,
        until: datetime = None
    ) -> Dict[str, Any]:
        """Ottieni insights account"""
        async with httpx.AsyncClient() as client:
            params = {
                'metric': 'impressions,reach,profile_views,website_clicks',
                'period': period,
                'access_token': access_token
            }
            
            if since:
                params['since'] = int(since.timestamp())
            if until:
                params['until'] = int(until.timestamp())
            
            response = await client.get(
                f"{self.base_url}/me/insights",
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore insights account: {response.text}")
            
            return response.json()
    
    async def get_user_media(self, access_token: str, limit: int = 25) -> Dict[str, Any]:
        """Ottieni media utente"""
        async with httpx.AsyncClient() as client:
            params = {
                'fields': 'id,media_type,media_url,permalink,thumbnail_url,timestamp,caption',
                'limit': limit,
                'access_token': access_token
            }
            
            response = await client.get(
                f"{self.base_url}/me/media",
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Errore media utente: {response.text}")
            
            return response.json()
    
    def validate_token(self, access_token: str) -> bool:
        """Valida token Instagram"""
        try:
            # Tenta una chiamata semplice per verificare il token
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.get_user_profile(access_token))
            return bool(result.get('id'))
        except Exception:
            return False
    
    async def sync_account_data(self, db: Session, account: InstagramAccount) -> InstagramAccount:
        """Sincronizza dati account con Instagram"""
        if not RateLimitManager.check_instagram_api_limit(account.id):
            raise Exception("Limite API Instagram raggiunto")
        
        try:
            # Ottieni dati profilo aggiornati
            profile_data = await self.get_user_profile(account.access_token)
            
            # Aggiorna account
            account.followers_count = profile_data.get('followers_count', 0)
            account.following_count = profile_data.get('follows_count', 0)
            account.posts_count = profile_data.get('media_count', 0)
            account.is_business_account = profile_data.get('account_type') == 'BUSINESS'
            account.last_sync = datetime.utcnow()
            
            db.commit()
            
            # Incrementa contatore API usage
            RateLimitManager.increment_api_usage(account.id)
            
            return account
            
        except Exception as e:
            raise Exception(f"Errore sincronizzazione account: {str(e)}")

# Istanza globale del servizio
instagram_service = InstagramService()
