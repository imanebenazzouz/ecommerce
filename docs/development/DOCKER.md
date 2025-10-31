# 🐳 Documentation Docker - E-Commerce

**Version:** 2.0  
**Date:** Janvier 2025  
**Status:** ✅ Production Ready

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Architecture Docker](#architecture-docker)
3. [Configuration](#configuration)
4. [Déploiement](#déploiement)
5. [Services](#services)
6. [Monitoring](#monitoring)
7. [Maintenance](#maintenance)
8. [Dépannage](#dépannage)

---

## 🎯 Vue d'Ensemble

L'application e-commerce utilise **Docker Compose** pour orchestrer tous les services nécessaires en production :
- PostgreSQL - Base de données
- Redis - Cache et sessions
- Backend API - FastAPI
- Frontend - React (build statique)
- Nginx - Reverse proxy
- Prometheus - Métriques
- Grafana - Visualisation

### Avantages Docker

✅ **Isolation** - Chaque service dans son conteneur  
✅ **Reproducibilité** - Même environnement partout  
✅ **Scalabilité** - Facile d'ajouter des instances  
✅ **Maintenance** - Mise à jour simplifiée  
✅ **Monitoring** - Intégré avec Prometheus/Grafana

---

## 🏗️ Architecture Docker

### Architecture Globale

```
┌──────────────────────────────────────────────────────────┐
│                      INTERNET                             │
└───────────────────────┬──────────────────────────────────┘
                        │
                        │ HTTPS:443 / HTTP:80
                        │
┌───────────────────────▼──────────────────────────────────┐
│              NGINX (Reverse Proxy)                        │
│                   ecommerce-nginx                         │
│              Ports: 80, 443, 9090, 3001                  │
└───────────────────────┬──────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
┌───────────▼──────────┐  ┌────────▼─────────────┐
│   FRONTEND (React)   │  │  BACKEND (FastAPI)   │
│  ecommerce-frontend  │  │  ecommerce-backend   │
│   Port: 3000:80      │  │   Port: 8000:8000    │
└──────────────────────┘  └──────────┬───────────┘
                                     │
                        ┌────────────┴────────────┐
                        │                         │
            ┌───────────▼────────┐  ┌────────────▼────────┐
            │   POSTGRESQL       │  │   REDIS (Cache)     │
            │  ecommerce-postgres│  │  ecommerce-redis    │
            │   Port: 5432       │  │   Port: 6379        │
            └────────────────────┘  └─────────────────────┘
                        │                         │
            ┌───────────▼────────┐  ┌────────────▼────────┐
            │   PROMETHEUS       │  │   GRAFANA           │
            │  ecommerce-prometheus │ ecommerce-grafana   │
            │   Port: 9090       │  │   Port: 3001        │
            └────────────────────┘  └─────────────────────┘
```

### Réseau Docker

Tous les services sont sur le réseau `ecommerce-network` (bridge).

---

## ⚙️ Configuration

### Fichiers Docker

```
ecommerce/
├── docker-compose.prod.yml    # 🌟 Compose production
├── ecommerce-backend/
│   ├── docker-compose.yml     # Dev (PostgreSQL + Redis)
│   ├── Dockerfile.prod        # Image backend
│   └── docker-entrypoint.sh   # Script d'initialisation
├── ecommerce-front/
│   └── Dockerfile.prod        # Image frontend
└── docker-compose.prod.yml    # Orchestration complète
```

### Variables d'Environnement

Créer un fichier `.env` à la racine :

```env
# Base de données
POSTGRES_PASSWORD=ecommerce_prod_password_2024
POSTGRES_DB=ecommerce
POSTGRES_USER=ecommerce

# Redis
REDIS_PASSWORD=redis_prod_password_2024

# Sécurité
SECRET_KEY=your_super_secret_production_key_change_this
JWT_SECRET_KEY=your_jwt_secret_key_change_this

# Domaine
DOMAIN=localhost

# Grafana
GRAFANA_PASSWORD=admin123
```

### Configuration Nginx

Fichier: `nginx/nginx.conf`

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name localhost;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
        }

        # Prometheus
        location /metrics {
            proxy_pass http://prometheus:9090;
        }
    }
}
```

---

## 🚀 Déploiement

### Déploiement Rapide

Le projet inclut **2 scripts de déploiement** :

#### Option 1: Déploiement Complet

```bash
./deploy.sh
```

**Ce qu'il fait :**
- ✅ Vérifie Docker et Docker Compose
- ✅ Vérifie le fichier `.env` existe
- ✅ Arrête les anciens conteneurs
- ✅ Build les images
- ✅ Démarre tous les services
- ✅ Affiche les logs de démarrage
- ✅ Teste la connectivité API

#### Option 2: Déploiement Simplifié (✅ Recommandé)

```bash
./deploy_simple.sh
```

**Avantages :**
- ⚡ Plus rapide
- 📝 Messages plus clairs
- 🎯 Idéal pour tests rapides
- 🔒 Pas de passwords hardcodés

### Déploiement Manuel

```bash
# 1. Build les images
docker-compose -f docker-compose.prod.yml build

# 2. Démarrer les services
docker-compose -f docker-compose.prod.yml up -d

# 3. Vérifier le statut
docker-compose -f docker-compose.prod.yml ps

# 4. Voir les logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Vérification du Déploiement

```bash
# Santé de l'API
curl http://localhost/api/health

# Frontend
curl http://localhost

# Prometheus
curl http://localhost:9090

# Grafana
curl http://localhost:3001
```

---

## 🐳 Services

### PostgreSQL

**Conteneur:** `ecommerce-postgres-prod`  
**Image:** `postgres:15-alpine`  
**Port:** `5432`  
**Volumes:**
- `postgres_data:/var/lib/postgresql/data`

**Variables:**
- POSTGRES_DB=ecommerce
- POSTGRES_USER=ecommerce
- POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

**Commandes utiles:**

```bash
# Connexion
docker exec -it ecommerce-postgres-prod psql -U ecommerce -d ecommerce

# Backup
docker exec ecommerce-postgres-prod pg_dump -U ecommerce ecommerce > backup.sql

# Restore
docker exec -i ecommerce-postgres-prod psql -U ecommerce ecommerce < backup.sql

# Logs
docker logs -f ecommerce-postgres-prod
```

### Redis

**Conteneur:** `ecommerce-redis-prod`  
**Image:** `redis:7-alpine`  
**Port:** `6379`  
**Volumes:**
- `redis_data:/data`

**Variables:**
- REDIS_PASSWORD=${REDIS_PASSWORD}

**Commandes utiles:**

```bash
# Connexion
docker exec -it ecommerce-redis-prod redis-cli -a ${REDIS_PASSWORD}

# Logs
docker logs -f ecommerce-redis-prod
```

### Backend API

**Conteneur:** `ecommerce-backend-prod`  
**Image:** Build depuis `ecommerce-backend/`  
**Port:** `8000`  
**Démarre après:** PostgreSQL + Redis (health check)

**Variables:**
- DATABASE_URL
- SECRET_KEY
- JWT_SECRET_KEY
- DEBUG=False

**Commandes utiles:**

```bash
# Logs
docker logs -f ecommerce-backend-prod

# Shell
docker exec -it ecommerce-backend-prod sh

# Restart
docker-compose -f docker-compose.prod.yml restart backend
```

### Frontend

**Conteneur:** `ecommerce-frontend-prod`  
**Image:** Build depuis `ecommerce-front/`  
**Port:** `3000:80`  
**Build:** Vite build statique  
**Serveur:** Nginx (interne)

**Variables:**
- VITE_API_URL=https://${DOMAIN}/api

**Commandes utiles:**

```bash
# Logs
docker logs -f ecommerce-frontend-prod

# Rebuild
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### Nginx

**Conteneur:** `ecommerce-nginx-prod`  
**Image:** `nginx:alpine`  
**Ports:** `80, 443`  
**Volumes:**
- `./nginx/nginx.conf:/etc/nginx/nginx.conf`
- `./nginx/conf.d:/etc/nginx/conf.d`
- `./ssl:/etc/nginx/ssl`

**Commandes utiles:**

```bash
# Test config
docker exec ecommerce-nginx-prod nginx -t

# Reload config
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

# Logs
docker logs -f ecommerce-nginx-prod
```

### Prometheus

**Conteneur:** `ecommerce-prometheus`  
**Image:** `prom/prometheus:latest`  
**Port:** `9090`  
**Volumes:**
- `./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml`
- `prometheus_data:/prometheus`

**URL:** http://localhost:9090

### Grafana

**Conteneur:** `ecommerce-grafana`  
**Image:** `grafana/grafana:latest`  
**Port:** `3001:3000`  
**Volumes:**
- `grafana_data:/var/lib/grafana`

**Variables:**
- GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

**URL:** http://localhost:3001  
**Login:** admin / ${GRAFANA_PASSWORD}

---

## 📊 Monitoring

### Prometheus

**Métriques collectées:**
- Requêtes HTTP
- Temps de réponse
- Erreurs 4xx, 5xx
- Utilisation CPU/RAM
- Connexions DB

**Query PromQL:**

```promql
# Requêtes par seconde
rate(http_requests_total[5m])

# Temps de réponse moyen
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# Erreurs
sum(rate(http_requests_total{status=~"5.."}[5m]))
```

### Grafana

**Dashboards pré-configurés:**
- Vue d'ensemble API
- Performances backend
- Santé des services
- Utilisation des ressources

**Créer un dashboard:**
1. Aller sur http://localhost:3001
2. Login admin
3. Créer un nouveau dashboard
4. Ajouter des panels Prometheus

### Monitoring Automatique

Le script `monitor.sh` vérifie :
- Statut des conteneurs
- Utilisation CPU/RAM
- Connectivité (API, Frontend, DB, Redis)
- Logs récents
- Ports ouverts

```bash
./monitor.sh
```

---

## 🔧 Maintenance

### Sauvegarde de la Base de Données

```bash
# Backup complet
docker exec ecommerce-postgres-prod pg_dump -U ecommerce ecommerce > backup_$(date +%Y%m%d).sql

# Backup compressé
docker exec ecommerce-postgres-prod pg_dump -U ecommerce ecommerce | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Restauration

```bash
# Depuis un fichier SQL
docker exec -i ecommerce-postgres-prod psql -U ecommerce ecommerce < backup.sql

# Depuis un fichier compressé
gunzip < backup.sql.gz | docker exec -i ecommerce-postgres-prod psql -U ecommerce ecommerce
```

### Mise à Jour

```bash
# 1. Stopper les services
docker-compose -f docker-compose.prod.yml down

# 2. Mettre à jour le code
git pull

# 3. Rebuild les images
docker-compose -f docker-compose.prod.yml build

# 4. Redémarrer
docker-compose -f docker-compose.prod.yml up -d

# 5. Vérifier
./monitor.sh
```

### Nettoyage

```bash
# Stopper et supprimer les conteneurs
docker-compose -f docker-compose.prod.yml down

# Supprimer les volumes (⚠️ données perdues)
docker-compose -f docker-compose.prod.yml down -v

# Nettoyer les images inutilisées
docker system prune -a

# Nettoyer tout (⚠️ destructif)
docker system prune -a --volumes
```

### Logs

```bash
# Tous les logs
docker-compose -f docker-compose.prod.yml logs -f

# Logs d'un service
docker-compose -f docker-compose.prod.yml logs -f backend

# Dernières 100 lignes
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# Logs depuis il y a 10 minutes
docker-compose -f docker-compose.prod.yml logs --since=10m backend
```

---

## 🔍 Dépannage

### Service ne démarre pas

```bash
# Voir les logs d'erreur
docker-compose -f docker-compose.prod.yml logs service_name

# Vérifier le statut
docker-compose -f docker-compose.prod.yml ps

# Redémarrer
docker-compose -f docker-compose.prod.yml restart service_name
```

### Port déjà utilisé

```bash
# Trouver le processus
lsof -i :8000
lsof -i :5432

# Tuer le processus
kill -9 $(lsof -ti:8000)
```

### Base de données inaccessible

```bash
# Vérifier que PostgreSQL tourne
docker ps | grep postgres

# Vérifier la connexion
docker exec ecommerce-postgres-prod pg_isready -U ecommerce

# Voir les logs
docker logs ecommerce-postgres-prod

# Redémarrer
docker-compose -f docker-compose.prod.yml restart postgres
```

### Backend erreur 500

```bash
# Logs backend
docker logs -f ecommerce-backend-prod

# Connexion DB OK ?
docker exec ecommerce-postgres-prod psql -U ecommerce -d ecommerce -c "SELECT 1"

# Variables d'environnement
docker exec ecommerce-backend-prod env | grep DATABASE
```

### Frontend erreurs CORS

Vérifier que le backend autorise le domaine :
```python
# ecommerce-backend/api.py
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:5173",
    # Votre domaine
]
```

### Mémoire insuffisante

```bash
# Voir l'utilisation
docker stats

# Augmenter les limites dans docker-compose.prod.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### HTTPS ne fonctionne pas

1. Vérifier que les certificats existent dans `ssl/`:
   - `cert.pem`
   - `key.pem`

2. Vérifier la config Nginx:
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
}
```

3. Reload Nginx:
```bash
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## 🚀 Commandes Rapides

```bash
# Démarrage
./deploy_simple.sh

# Statut
docker-compose -f docker-compose.prod.yml ps

# Logs
docker-compose -f docker-compose.prod.yml logs -f

# Monitoring
./monitor.sh

# Arrêt
docker-compose -f docker-compose.prod.yml down

# Redémarrer
docker-compose -f docker-compose.prod.yml restart

# Clean
docker-compose -f docker-compose.prod.yml down -v
docker system prune -a
```

---

## 📚 Ressources

- **Documentation Docker Compose**: https://docs.docker.com/compose
- **Documentation Nginx**: https://nginx.org/en/docs
- **Documentation Prometheus**: https://prometheus.io/docs
- **Documentation Grafana**: https://grafana.com/docs

---

**Docker prêt pour la production !** 🐳🚀

