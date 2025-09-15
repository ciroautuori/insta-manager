# Dockerfile per Frontend React
# Multi-stage build per ottimizzare le dimensioni dell'immagine

# Stage 1: Build
FROM node:18-alpine as build

# Installa dipendenze di sistema per compilazione
RUN apk add --no-cache python3 make g++ && ln -sf python3 /usr/bin/python

WORKDIR /app

# Copia package files
COPY package*.json ./

# Installa tutte le dipendenze (incluse dev per il build)
RUN npm ci

# Copia codice sorgente
COPY . .

# Build dell'app React per produzione
RUN npm run build

# Stage 2: Production with Nginx
FROM nginx:alpine

# Copia build files da stage precedente
COPY --from=build /app/dist /usr/share/nginx/html

# Copia configurazione Nginx personalizzata
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Espone porta 80
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost || exit 1

# Avvia Nginx
CMD ["nginx", "-g", "daemon off;"]
