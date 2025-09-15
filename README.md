# Instagram Multi-Account Dashboard

Dashboard privato per la gestione centralizzata di più account Instagram con funzionalità di programmazione post, analytics e automazione.

## 🚀 Caratteristiche

- **Gestione Multi-Account**: Connetti e gestisci più account Instagram
- **Programmazione Post**: Scheduling automatico per Feed, Stories e Reels
- **Upload Media**: Sistema sicuro per caricare e organizzare contenuti multimediali
- **Analytics**: Metriche dettagliate e insights per ogni account
- **Automazione**: Worker Celery per task programmati e sincronizzazione
- **Dashboard Admin**: Interfaccia sicura solo per amministratori
- **API Instagram**: Integrazione completa con Meta Graph API

## 🛠️ Stack Tecnologico

### Backend
- **FastAPI** - API REST moderna e veloce
- **PostgreSQL** - Database relazionale robusto
- **SQLAlchemy** - ORM Python avanzato
- **Alembic** - Gestione migrazioni database
- **Celery + Redis** - Task queue per automazione
- **OAuth2 + JWT** - Autenticazione sicura

### Frontend
- **React + TypeScript** - UI moderna e type-safe
- **Vite** - Build tool veloce
- **TailwindCSS** - Styling utility-first
- **shadcn/ui** - Componenti UI eleganti
- **React Query** - Gestione stato server

### Deployment
- **Docker** - Containerizzazione completa
- **Nginx** - Reverse proxy e servizio file statici
- **Redis** - Cache e message broker

## 📁 Struttura Progetto

```
instadmin/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoint API
│   │   ├── core/           # Configurazioni base
│   │   ├── models/         # Modelli SQLAlchemy
│   │   ├── schemas/        # Schemi Pydantic
│   │   ├── workers/        # Task Celery
│   │   └── services/       # Business logic
│   ├── alembic/            # Migrazioni DB
│   ├── Dockerfile          # Container backend
│   └── requirements.txt    # Dipendenze Python
├── frontend/               # App React
│   ├── src/
│   │   ├── components/     # Componenti UI
│   │   ├── contexts/       # Context React
│   │   ├── pages/          # Pagine principali
│   │   └── lib/            # Utility e API client
│   ├── Dockerfile          # Container frontend
│   └── package.json        # Dipendenze Node
├── nginx/                  # Configurazione proxy
│   └── nginx.conf          # Configurazione Nginx
├── docker-compose.yml      # Orchestrazione servizi
└── .env.example           # Template variabili ambiente
```

## ⚡ Quick Start

### Prerequisiti
- Docker & Docker Compose
- Account Meta Developer (per Instagram API)

### 1. Clona il Repository
```bash
git clone <repository-url>
cd instadmin
```

### 2. Configura Ambiente
```bash
# Copia e personalizza le variabili ambiente
cp .env.example .env

# Modifica .env con le tue configurazioni:
# - META_APP_ID e META_APP_SECRET
# - DATABASE_URL e password sicure
# - SECRET_KEY univoca per JWT
# - ADMIN_EMAIL e ADMIN_PASSWORD
```

### 3. Avvia i Servizi
```bash
# Build e avvio completo
docker-compose up -d

# Verifica status
docker-compose ps

# Visualizza logs
docker-compose logs -f backend
```

### 4. Accesso Dashboard
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentazione API**: http://localhost:8000/docs

### 5. Login Admin
- Email: admin@instadmin.com (o quello configurato)
- Password: admin123 (CAMBIARE in produzione!)

## 🔧 Configurazione

### Setup Account Meta Developer

1. Vai su [Meta Developers](https://developers.facebook.com/)
2. Crea una nuova app con prodotto "Instagram Basic Display"
3. Configura redirect URI: `https://tuodominio.com/auth/instagram/callback`
4. Copia App ID e App Secret nel file `.env`

### Variabili Ambiente Principali
```env
# Database PostgreSQL
DATABASE_URL=postgresql://postgres:postgres_password@postgres:5432/instadmin

# Meta Instagram API (OBBLIGATORIE)
META_APP_ID=your_instagram_app_id
META_APP_SECRET=your_instagram_app_secret
META_REDIRECT_URI=https://yourdomain.com/auth/instagram/callback

# Sicurezza JWT
SECRET_KEY=your_super_secret_jwt_key_256_bits_minimum
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin iniziale
ADMIN_EMAIL=admin@instadmin.com
ADMIN_PASSWORD=your_secure_admin_password
ADMIN_FULL_NAME=Administrator

# Redis/Celery per task queue
REDIS_URL=redis://:redis_password@redis:6379/0
CELERY_BROKER_URL=redis://:redis_password@redis:6379/1
CELERY_RESULT_BACKEND=redis://:redis_password@redis:6379/2

# Media storage
MEDIA_UPLOAD_PATH=/app/media
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=jpg,jpeg,png,gif,mp4,mov

# Rate limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_INSTAGRAM_API=200

# CORS
FRONTEND_URL=http://localhost:3000
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🚀 Deploy Produzione

### 1. Setup SSL/TLS
```bash
# Crea directory certificati
mkdir -p nginx/ssl

# Opzione A: Let's Encrypt (raccomandato)
certbot certonly --webroot -w /var/www/certbot -d yourdomain.com

# Opzione B: Certificati custom
# Copia i tuoi certificati in:
# nginx/ssl/cert.pem
# nginx/ssl/key.pem
```

### 2. Configurazione Sicurezza
```bash
# Crea .env per produzione
cp .env.example .env.prod

# IMPORTANTE: Modifica TUTTE le password di default
# - Genera SECRET_KEY sicura: openssl rand -hex 32
# - Password PostgreSQL e Redis uniche
# - Admin password robusta
# - Configura domini corretti per CORS
```

### 3. Deploy
```bash
# Usa file env produzione
docker-compose --env-file .env.prod up -d

# Verifica servizi attivi
docker-compose ps

# Monitora logs
docker-compose logs -f
```

### 4. Configurazione Server
```bash
# Firewall - apri solo porte necessarie
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable

# Configura backup automatico
crontab -e
# Aggiungi: 0 2 * * * /path/to/backup-script.sh
```

### Backup & Manutenzione
```bash
# Script backup database
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U postgres instadmin > "backup_${DATE}.sql"
gzip "backup_${DATE}.sql"

# Backup volumi Docker
docker run --rm -v instadmin_postgres_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/postgres_data_${DATE}.tar.gz /data

# Rotazione logs
docker-compose exec backend find /app/logs -name "*.log" -mtime +30 -delete

# Aggiornamento servizi
docker-compose pull
docker-compose up -d --force-recreate

# Pulizia immagini vecchie
docker image prune -f
```

## 🔑 Funzionalità Principali

### 1. Gestione Account Instagram
- **Connessione OAuth2**: Flow sicuro per autorizzazione account
- **Sincronizzazione automatica**: Profile info, follower count, media count
- **Refresh token**: Rinnovo automatico autorizzazioni Instagram  
- **Multi-account**: Gestione illimitata account da singola dashboard
- **Permessi granulari**: Controllo accessi per ogni account

### 2. Programmazione Contenuti  
- **Editor avanzato**: Preview in tempo reale per tutti i formati
- **Scheduling flessibile**: Data/ora specifica o ricorrente
- **Multi-formato**: Support completo per Feed, Stories, Reels
- **Retry automatico**: Sistema intelligente per riprovare pubblicazioni fallite
- **Calendario visuale**: Vista mensile con drag & drop
- **Bulk operations**: Programmazione multipla simultanea

### 3. Gestione Media
- **Upload sicuro**: Validazione formato e dimensione
- **Organizzazione**: Tag, categorie, ricerca avanzata  
- **Ottimizzazione**: Resize automatico per Instagram
- **Anteprima**: Preview immediato per tutti i formati
- **Storage scalabile**: Supporto cloud storage (AWS S3, etc.)

### 4. Analytics & Insights
- **Metriche real-time**: Like, commenti, reach, impressioni
- **Grafici interattivi**: Trend temporali e confronti
- **Report personalizzati**: Export PDF/Excel con KPI
- **Analisi hashtag**: Performance e suggerimenti
- **Competitor analysis**: Benchmark con account simili
- **ROI tracking**: Conversioni e engagement rate

### 5. Automazione Avanzata
- **Celery workers**: Task distribuiti per performance
- **Coda prioritaria**: Gestione intelligente pubblicazioni
- **Retry logic**: Sistema resiliente per errori temporanei
- **Monitoring**: Health check e alerting automatico
- **Maintenance**: Pulizia automatica dati obsoleti

## 🛡️ Sicurezza

### Misure Implementate
- **Autenticazione JWT**: Token sicuri con refresh automatico
- **Rate limiting**: Protezione DDoS e abuso API  
- **CORS policy**: Controllo rigoroso domini autorizzati
- **Input validation**: Sanitizzazione completa dati utente
- **SQL injection**: Protezione via ORM parametrizzato
- **XSS protection**: Headers sicurezza e CSP policy
- **HTTPS enforcement**: Redirect automatico HTTP->HTTPS
- **Secrets management**: Variabili ambiente crittografate

### Checklist Sicurezza Produzione
```bash
# 1. Password e chiavi
□ SECRET_KEY generata casualmente (min 256 bit)
□ Password database e Redis uniche e robuste  
□ Admin password diversa da default
□ Certificati SSL validi e aggiornati

# 2. Configurazione
□ DEBUG=false in produzione
□ CORS limitato a domini autorizzati
□ Rate limiting attivo
□ Logging completo abilitato

# 3. Infrastruttura  
□ Firewall configurato (solo 80, 443, 22)
□ Backup automatici attivi
□ Monitoring e alerting configurato
□ Updates automatici di sicurezza

# 4. Applicazione
□ Dipendenze aggiornate
□ Vulnerabilità scannate
□ Access logs monitorati
□ Database accesso limitato
```

## 📚 API Documentation

### Documentazione Interattiva
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc  
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Endpoint Principali

#### Autenticazione
```bash
# Login admin
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@instladmin.com", "password": "admin123"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}
```

#### Instagram Account Management  
```bash
# Ottieni URL autorizzazione Instagram
curl -X GET "http://localhost:8000/instagram/auth-url" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Callback dopo autorizzazione
curl -X POST "http://localhost:8000/instagram/callback" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "INSTAGRAM_AUTH_CODE", "state": "STATE_VALUE"}'

# Lista account connessi
curl -X GET "http://localhost:8000/instagram/accounts" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Post Management
```bash
# Crea nuovo post
curl -X POST "http://localhost:8000/posts/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "post_type": "feed", 
    "content": "Il mio primo post!",
    "media_files": ["image1.jpg"],
    "hashtags": ["test", "instladmin"]
  }'

# Programma post
curl -X POST "http://localhost:8000/scheduled/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "post_type": "feed",
    "content": "Post programmato!",
    "media_files": ["image1.jpg"],
    "scheduled_time": "2024-12-25T10:00:00Z"
  }'
```

#### Analytics
```bash
# Analytics account
curl -X GET "http://localhost:8000/analytics/account/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Analytics post specifico  
curl -X GET "http://localhost:8000/analytics/post/123" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Dashboard stats
curl -X GET "http://localhost:8000/dashboard/stats" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Rate Limits
- **API generale**: 60 richieste/minuto per IP
- **Login endpoint**: 5 tentativi/minuto per IP
- **Instagram API**: 200 richieste/ora (limite Meta)

## 🧪 Testing & Development

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
```

4. **Coding Standards**
   - **Backend**: Segui PEP 8, usa black per formatting
   - **Frontend**: ESLint + Prettier configurati  
   - **Commit**: Conventional Commits format
   - **Tests**: Coverage minima 80%

5. **Pull Request**
   - Descrizione dettagliata delle modifiche
   - Screenshot per UI changes
   - Test copertura completa
   - Documentazione aggiornata

### Roadmap Sviluppo

#### v2.0 - Prossimi Features
- [ ] **Multi-tenant**: Supporto più organizzazioni
- [ ] **Advanced scheduling**: Timezone e ricorrenza  
- [ ] **AI content**: Suggerimenti automatici hashtag
- [ ] **Team collaboration**: Workflow approvazione post
- [ ] **White label**: Personalizzazione brand
- [ ] **Mobile app**: App nativa iOS/Android
- [ ] **Integrations**: Zapier, IFTTT connectors

#### v2.1 - Analytics Avanzate
- [ ] **A/B testing**: Test automatici post variants
- [ ] **Predictive analytics**: ML per optimal posting times
- [ ] **Competitor tracking**: Monitoraggio automatico
- [ ] **ROI calculator**: Tracking conversioni e revenue
- [ ] **Custom reports**: Report builder drag & drop

## 📄 Licenza

Distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori informazioni.

## 🆘 Supporto

### Risoluzione Problemi

#### Problemi Comuni

**1. Instagram API non funziona**
```bash
# Verifica configurazione Meta App
echo $META_APP_ID $META_APP_SECRET

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
