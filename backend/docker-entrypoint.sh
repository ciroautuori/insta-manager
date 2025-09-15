#!/bin/bash
set -e

# Funzione di log
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Avvio backend FastAPI..."

# Attendi che PostgreSQL sia pronto
log "Attendo connessione PostgreSQL..."
while ! pg_isready -h postgres -p 5432 -U postgres; do
    log "PostgreSQL non ancora pronto, attendo..."
    sleep 2
done
log "PostgreSQL pronto!"

# Attendi che Redis sia pronto
log "Attendo connessione Redis..."
while ! redis-cli -h redis -p 6379 -a redis_password ping; do
    log "Redis non ancora pronto, attendo..."
    sleep 2
done
log "Redis pronto!"

# Esegui migrazioni database
log "Esecuzione migrazioni Alembic..."
cd /app
alembic upgrade head

# Crea admin utente se non esiste
log "Creazione admin utente..."
python -c "
from app.core.database import get_session
from app.models.admin import Admin
from app.core.security import get_password_hash
from app.core.config import settings

def create_admin():
    session = get_session()
    try:
        # Verifica se admin esiste già
        existing_admin = session.query(Admin).filter_by(email=settings.ADMIN_EMAIL).first()
        if not existing_admin:
            admin = Admin(
                email=settings.ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                full_name='Administrator',
                is_active=True,
                is_superuser=True
            )
            session.add(admin)
            session.commit()
            print('Admin utente creato con successo')
        else:
            print('Admin utente già esistente')
    finally:
        session.close()

create_admin()
"

log "Inizializzazione completata. Avvio applicazione..."

# Avvia l'applicazione con i parametri passati
exec "$@"
