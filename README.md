# Instagram Multi-Account Management Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-blue.svg)](https://typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, enterprise-grade platform for centralized Instagram account management with advanced post scheduling, analytics, and automation capabilities. Built with modern technologies and designed for scalability, security, and performance.

## ✨ Key Features

- **🔗 Multi-Account Management**: Connect and manage unlimited Instagram accounts
- **📅 Advanced Scheduling**: Automated posting for Feed, Stories, and Reels with timezone support
- **📁 Media Management**: Secure upload system with automatic optimization and organization
- **📊 Analytics & Insights**: Comprehensive metrics, engagement tracking, and performance analytics
- **⚡ Automation Engine**: Celery-powered background workers for scheduled tasks and synchronization
- **🔐 Admin Dashboard**: Secure, role-based administrative interface
- **🔌 Instagram API Integration**: Full Meta Graph API integration with OAuth2 authentication
- **🎯 Content Optimization**: AI-powered hashtag suggestions and optimal posting times
- **📈 Performance Tracking**: Real-time engagement metrics and ROI analysis

## 🛠️ Technology Stack

### Backend Architecture
- **FastAPI** - High-performance async Python web framework
- **PostgreSQL** - Enterprise-grade relational database
- **SQLAlchemy** - Advanced Python ORM with async support
- **Alembic** - Database migration management
- **Celery + Redis** - Distributed task queue for background processing
- **OAuth2 + JWT** - Secure authentication and authorization
- **Pydantic** - Data validation and serialization

### Frontend Stack
- **React 18** - Modern component-based UI library
- **TypeScript** - Type-safe JavaScript development
- **Vite** - Lightning-fast build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible component library
- **React Query** - Powerful data synchronization for React
- **React Router** - Declarative routing

### DevOps & Infrastructure
- **Docker** - Containerized deployment with multi-stage builds
- **Docker Compose** - Multi-container orchestration
- **Nginx** - High-performance reverse proxy and static file server
- **Redis** - In-memory data structure store for caching and message brokering
- **GitHub Actions** - CI/CD pipeline automation

## 📁 Project Architecture

```
instagram-manager/
├── backend/                    # FastAPI Application
│   ├── app/
│   │   ├── api/               # API Endpoints
│   │   │   └── endpoints/     # Route handlers
│   │   ├── core/              # Core configurations
│   │   │   ├── config.py      # Settings management
│   │   │   ├── database.py    # Database connection
│   │   │   └── security.py    # Authentication logic
│   │   ├── models/            # SQLAlchemy Models
│   │   ├── schemas/           # Pydantic Schemas
│   │   ├── services/          # Business Logic Layer
│   │   └── workers/           # Celery Background Tasks
│   ├── alembic/               # Database Migrations
│   ├── tests/                 # Backend Test Suite
│   ├── Dockerfile             # Backend Container
│   └── requirements.txt       # Python Dependencies
├── frontend/                   # React Application
│   ├── src/
│   │   ├── components/        # Reusable UI Components
│   │   ├── contexts/          # React Context Providers
│   │   ├── hooks/             # Custom React Hooks
│   │   ├── lib/               # Utilities & API Client
│   │   ├── pages/             # Application Pages
│   │   └── types/             # TypeScript Definitions
│   ├── public/                # Static Assets
│   ├── tests/                 # Frontend Test Suite
│   ├── Dockerfile             # Frontend Container
│   └── package.json           # Node.js Dependencies
├── nginx/                      # Reverse Proxy Configuration
│   ├── nginx.conf             # Nginx Configuration
│   └── ssl/                   # SSL Certificates
├── docs/                       # Documentation
├── scripts/                    # Deployment Scripts
├── docker-compose.yml          # Service Orchestration
├── docker-compose.prod.yml     # Production Configuration
└── .env.example               # Environment Template
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Meta Developer Account (for Instagram API)
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/instagram-manager.git
cd instagram-manager
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Configure your environment variables:
# - META_APP_ID and META_APP_SECRET (from Meta Developer Console)
# - DATABASE_URL and secure passwords
# - SECRET_KEY for JWT (generate with: openssl rand -hex 32)
# - ADMIN_EMAIL and ADMIN_PASSWORD
```

### 3. Launch Services
```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Access Points
- **Frontend Dashboard**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Backend API**: http://localhost:8080/api/v1
- **Admin Panel**: http://localhost:3000/admin

### 5. Default Admin Credentials
- **Email**: admin@instadmin.com
- **Password**: admin123
- ⚠️ **Important**: Change these credentials in production!

### 6. Instagram API Setup
1. Visit [Meta Developers](https://developers.facebook.com/)
2. Create new app with "Instagram Basic Display" product
3. Configure redirect URI: `https://yourdomain.com/api/v1/instagram/auth/callback`
4. Copy App ID and App Secret to your `.env` file

## ⚙️ Configuration

### Meta Developer Account Setup

1. Navigate to [Meta Developers Console](https://developers.facebook.com/)
2. Create a new application
3. Add "Instagram Basic Display" product
4. Configure OAuth redirect URI: `https://yourdomain.com/api/v1/instagram/auth/callback`
5. Copy App ID and App Secret to your environment configuration
6. Add test users for development
7. Submit for app review when ready for production

### Environment Variables

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:secure_password@postgres:5432/instagram_manager
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Meta Instagram API (Required)
META_APP_ID=your_meta_app_id
META_APP_SECRET=your_meta_app_secret
META_REDIRECT_URI=https://yourdomain.com/api/v1/instagram/auth/callback
META_API_VERSION=v18.0

# JWT Security
SECRET_KEY=your_256_bit_secret_key_generate_with_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Initial Admin User
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=secure_admin_password_change_in_production
ADMIN_FULL_NAME=System Administrator

# Redis & Celery Configuration
REDIS_URL=redis://:redis_password@redis:6379/0
CELERY_BROKER_URL=redis://:redis_password@redis:6379/1
CELERY_RESULT_BACKEND=redis://:redis_password@redis:6379/2
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json

# Media Storage
MEDIA_STORAGE_PATH=/app/media
PUBLIC_MEDIA_BASE_URL=https://yourdomain.com/media
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,webp,gif,mp4,mov,avi
IMAGE_QUALITY=85
THUMBNAIL_SIZE=300

# Rate Limiting & Security
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_LOGIN_ATTEMPTS=5
INSTAGRAM_API_RATE_LIMIT=200
CORS_ORIGINS=["https://yourdomain.com", "http://localhost:3000"]
ALLOWED_HOSTS=["yourdomain.com", "localhost"]

# Application Settings
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
TIMEZONE=UTC

# Monitoring & Analytics
SENTRY_DSN=your_sentry_dsn_for_error_tracking
GOOGLE_ANALYTICS_ID=your_ga_tracking_id
```

## 🚀 Production Deployment

### Docker Compose Production

```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Scale services as needed
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3
```

### SSL/TLS Setup

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Option A: Let's Encrypt (Recommended)
certbot certonly --webroot -w /var/www/certbot -d yourdomain.com

# Option B: Custom certificates
# Place your certificates in nginx/ssl/
# - fullchain.pem
# - privkey.pem
```

### Environment Security Checklist

- [ ] Change default admin credentials
- [ ] Generate secure SECRET_KEY (256-bit)
- [ ] Use strong database passwords
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Enable firewall rules
- [ ] Configure backup strategy
- [ ] Set up monitoring and logging

### Performance Optimization

```bash
# Database optimization
# Add to docker-compose.prod.yml
postgres:
  command: |
    postgres
    -c shared_preload_libraries=pg_stat_statements
    -c max_connections=200
    -c shared_buffers=256MB
    -c effective_cache_size=1GB

# Redis optimization
redis:
  command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```
### Database Backup & Recovery

```bash
# Automated daily backup
docker-compose exec postgres pg_dump -U postgres instagram_manager > backup_$(date +%F).sql

# Restore from backup
docker-compose exec -T postgres psql -U postgres instagram_manager < backup_2024-01-15.sql

# Backup with compression
docker-compose exec postgres pg_dump -U postgres instagram_manager | gzip > backup_$(date +%F).sql.gz
```

### Monitoring & Health Checks

```bash
# Check service health
docker-compose ps
docker-compose logs --tail=50 backend

# Monitor resource usage
docker stats

# Database performance
docker-compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"
```
## 📊 API Documentation

### API Endpoints Overview

- **Base URL (Development)**: http://localhost:8000/api/v1
- **Base URL (Production)**: https://yourdomain.com/api/v1
- **Interactive Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Authentication Flow

```bash
# Admin login
curl -X POST "https://yourdomain.com/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@yourdomain.com&password=secure_password"

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}

# Use token in subsequent requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://yourdomain.com/api/v1/admin/me
```

### Core API Endpoints

| Endpoint | Method | Description |
|----------|--------|--------------|
| `/auth/login` | POST | Admin authentication |
| `/admin/me` | GET | Current admin profile |
| `/instagram/accounts` | GET | List connected accounts |
| `/instagram/auth/url` | GET | Get OAuth authorization URL |
| `/posts` | GET/POST | Manage Instagram posts |
| `/scheduled` | GET/POST | Manage scheduled posts |
| `/media/upload` | POST | Upload media files |
| `/dashboard/stats` | GET | Dashboard statistics |
| `/analytics` | GET | Account analytics |

### Instagram Integration Examples

```bash
# Get Instagram OAuth URL
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://yourdomain.com/api/v1/instagram/auth/url

# List connected accounts
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://yourdomain.com/api/v1/instagram/accounts

# Get account details
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://yourdomain.com/api/v1/instagram/accounts/1

# Sync account data
curl -X POST -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://yourdomain.com/api/v1/instagram/accounts/1/sync

# Upload media
curl -X POST -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@image.jpg" \
  -F "alt_text=Beautiful sunset" \
  https://yourdomain.com/api/v1/media/upload

# Schedule a post
curl -X POST -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "caption": "Check out this amazing content!",
    "media_files": ["media/image.jpg"],
    "scheduled_for": "2024-12-25T10:00:00Z"
  }' \
  https://yourdomain.com/api/v1/scheduled

# Dashboard statistics
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://yourdomain.com/api/v1/dashboard/stats
```

## 📚 API Documentation

### Documentazione Interattiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoint Principali

#### Autenticazione
```bash
# Login admin (OAuth2PasswordRequestForm)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@instadmin.com&password=admin123"

# Response: {"access_token": "eyJ...", "token_type": "bearer"}
```

#### Instagram Account Management  
```bash
# Ottieni URL autorizzazione Instagram
curl -X GET "http://localhost:8000/api/v1/instagram/auth/url" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Callback dopo autorizzazione
curl -X POST "http://localhost:8000/api/v1/instagram/auth/callback" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "INSTAGRAM_AUTH_CODE", "state": "STATE_VALUE"}'

# Lista account connessi
curl -X GET "http://localhost:8000/api/v1/instagram/accounts" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Post Management
```bash
# Crea nuovo post
curl -X POST "http://localhost:8000/api/v1/posts" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "post_type": "feed",
    "caption": "Il mio primo post!",
    "media_files": [1]
  }'

# Programma post
curl -X POST "http://localhost:8000/api/v1/scheduled" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "post_type": "feed",
    "caption": "Post programmato!",
    "media_files": ["image1.jpg"],
    "scheduled_for": "2025-12-25T10:00:00Z"
  }'
```

#### Analytics
```bash
# Analytics account
curl -X GET "http://localhost:8000/api/v1/analytics/account/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Analytics post specifico  
curl -X GET "http://localhost:8000/api/v1/analytics/post/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Dashboard statistics
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://yourdomain.com/api/v1/dashboard/stats
```

## 🧪 Testing & Quality Assurance

### Health Check & Smoke Tests

```bash
# System health check
curl http://localhost:8000/health
# Expected: {"status":"healthy","environment":"production"}

# Authentication test
ACCESS_TOKEN=$(curl -sS -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@instadmin.com&password=admin123" | \
  jq -r .access_token)

# Verify admin profile
curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/api/v1/admin/me

# Test Instagram OAuth URL generation
curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" \
  http://localhost:8000/api/v1/instagram/auth/url

# Dashboard statistics
curl -sS -H "Authorization: Bearer $ACCESS_TOKEN" \
  https://yourdomain.com/api/v1/dashboard/stats
```

### Automated Testing

```bash
# Backend tests
cd backend
python -m pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
npm run test:e2e

# Integration tests
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Performance Testing

```bash
# Load testing with Apache Bench
ab -n 1000 -c 10 https://yourdomain.com/api/v1/health

# Database performance
docker-compose exec postgres psql -U postgres -c "EXPLAIN ANALYZE SELECT * FROM posts LIMIT 100;"
```

### Rate Limits & Security

- **General API**: 60 requests/minute per IP
- **Login endpoint**: 5 attempts/minute per IP  
- **Instagram API**: 200 requests/hour (Meta limit)
- **Media upload**: 10 files/minute per user
- **Account sync**: 1 request/5 minutes per account

## 🔧 Development & Database Management

### Database Migrations with Alembic

```bash
# Create database backup (recommended)
docker-compose exec -T postgres pg_dump -U postgres instagram_manager > backup_$(date +%F_%H%M%S).sql

# Rebuild containers with latest changes
docker-compose build --no-cache backend celery-worker celery-beat
docker-compose up -d

# Generate new migration based on model changes
docker-compose exec backend alembic revision --autogenerate -m "Add new features"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Check migration history
docker-compose exec backend alembic history --verbose

# Rollback to previous migration (if needed)
docker-compose exec backend alembic downgrade -1
```

### Database Schema

The application uses a well-structured PostgreSQL schema with the following key tables:

- **`admins`**: System administrators with role-based access
- **`instagram_accounts`**: Connected Instagram accounts with OAuth tokens
- **`posts`**: Published Instagram posts with engagement metrics
- **`scheduled_posts`**: Queued posts for future publishing
- **`media`**: Uploaded media files with metadata
- **`analytics`**: Performance metrics and insights data

### Local Development Setup

```bash
# Backend development
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
npm install
npm run dev

# Database setup (local)
psql -U postgres -c "CREATE DATABASE instagram_manager;"
alembic upgrade head
```

### Setup Ambiente Sviluppo

#### Backend
```bash
cd backend

# Virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate  # Windows

# Installa dipendenze
pip install -r requirements.txt

# Setup database locale  
export DATABASE_URL="postgresql://postgres:password@localhost:5432/instladmin_dev"

# Migrazione database
alembic upgrade head

# Avvia server dev
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Avvia worker Celery (terminale separato)
celery -A app.workers.celery_app worker --loglevel=info

# Avvia Celery Beat (terminale separato)  
celery -A app.workers.celery_app beat --loglevel=info
```

#### Frontend
```bash
cd frontend

# Installa dipendenze
npm install

# Avvia dev server
npm run dev

# Build produzione
npm run build

# Preview build  
npm run preview
```

### Testing

#### Backend Tests
```bash
cd backend

# Installa test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run tutti i test
pytest

# Test con coverage
pytest --cov=app tests/

# Test specifici
pytest tests/test_auth.py -v
pytest tests/test_instagram.py::test_auth_flow -v
```

#### Frontend Tests  
```bash
cd frontend

# Unit tests
npm run test

# E2E tests
npm run test:e2e

# Coverage
npm run test:coverage
```

### Debugging

#### Backend Debugging
```python
# Aggiungi breakpoint nel codice
import pdb; pdb.set_trace()

# Logging avanzato
import logging
logging.basicConfig(level=logging.DEBUG)

# Monitor database queries
export ECHO_SQL=true
```

#### Docker Debugging
```bash
# Accesso container
docker-compose exec backend bash
docker-compose exec frontend sh

# Logs dettagliati
docker-compose logs -f --tail=100 backend

# Restart servizio singolo
docker-compose restart backend

# Monitor risorse
docker stats
```

## 🤝 Contributi

### Linee Guida

1. **Fork e Clone**
```bash
git clone https://github.com/yourusername/instladmin.git
cd instladmin
```

2. **Setup Development Environment**
```bash
# Copia env per development
cp .env.example .env.dev

# Avvia stack completo
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

3. **Crea Feature Branch**
```bash
git checkout -b feature/amazing-feature
# Check callback URL
# Deve matchare esattamente quello in Meta Developer Console

# Verifica token Instagram
curl -X GET "http://localhost:8000/instagram/accounts" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**2. Container non si avvia**
```bash
# Check logs
docker-compose logs backend

# Verifica porte disponibili
netstat -tulpn | grep :8000

# Rebuild senza cache
docker-compose build --no-cache
docker-compose up -d
```

**3. Database problemi**
```bash
# Reset completo database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

**4. Celery tasks non eseguiti**
```bash
# Verifica worker attivo
docker-compose logs celery-worker

# Monitor coda Redis
docker-compose exec redis redis-cli
> KEYS celery*
> LLEN celery
```

#### Logs e Monitoring
```bash
# Logs tutti i servizi
docker-compose logs -f

# Logs specifico servizio con timestamp
docker-compose logs -f -t backend

# Monitor risorse sistema
docker stats

# Health check
curl http://localhost:8000/health
curl http://localhost:3000/health
```

#### Performance Tuning
```bash
# Backend: Aumenta worker uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Database: Ottimizza PostgreSQL
# Aggiungi in docker-compose.yml postgres:
command: postgres -c shared_buffers=256MB -c max_connections=200

# Redis: Aumenta memoria
command: redis-server --maxmemory 512mb --requirepass redis_password
```

### Canali Supporto
- **GitHub Issues**: Bug report e feature request
- **Discussions**: Domande generali e community
- **Email**: support@instladmin.com (se disponibile)
- **Documentation**: Consulta sempre docs/API prima di chiedere

### Contributi Community
- **Bug fixes**: Sempre benvenuti via PR
- **Feature requests**: Discuti prima nelle Issues
- **Documentation**: Miglioramenti alla docs apprezzati
- **Translations**: Localizzazione in altre lingue
- **Examples**: Tutorial e use cases reali

---

**⚠️ Importante**: Questo è un tool per uso privato/aziendale. Rispetta sempre i Terms of Service di Instagram e Meta. L'uso improprio può portare alla sospensione degli account Instagram.
