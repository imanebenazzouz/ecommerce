# 🚀 Guide de mise en production - Ecommerce

## 📋 Prérequis

### Serveur de production
- **OS**: Ubuntu 20.04+ ou CentOS 8+
- **RAM**: Minimum 2GB (recommandé 4GB+)
- **CPU**: 2 cœurs minimum
- **Stockage**: 20GB minimum
- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+

### Logiciels requis
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose git curl

# CentOS/RHEL
sudo yum install -y docker docker-compose git curl
```

## 🗄️ Configuration de la base de données

### 1. Installation PostgreSQL

#### Option A: Avec Docker (Recommandé)
```bash
# Créer un réseau Docker
docker network create ecommerce_network

# Démarrer PostgreSQL
docker run -d \
  --name ecommerce-postgres \
  --network ecommerce_network \
  -e POSTGRES_DB=ecommerce \
  -e POSTGRES_USER=ecommerce \
  -e POSTGRES_PASSWORD=your_secure_password \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine
```

#### Option B: Installation native
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql postgresql-server
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 2. Configuration de la base de données
```sql
-- Se connecter à PostgreSQL
sudo -u postgres psql

-- Créer la base de données
CREATE DATABASE ecommerce;
CREATE USER ecommerce WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce TO ecommerce;
\q
```

## 🔧 Configuration du backend

### 1. Installation des dépendances
```bash
cd ecommerce-backend

# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
pip install sqlalchemy psycopg2-binary alembic gunicorn
```

### 2. Configuration des variables d'environnement
```bash
# Copier le fichier de configuration
cp config.env.production .env

# Éditer les variables
nano .env
```

Variables importantes à configurer:
```env
DATABASE_URL=postgresql://ecommerce:your_secure_password@localhost:5432/ecommerce
SECRET_KEY=your_super_secret_key_here_change_this_in_production
DEBUG=False
PRODUCTION_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Migration des données
```bash
# Créer les tables
python -c "from database.database import create_tables; create_tables()"

# Migrer les données existantes
python scripts/migrate_to_postgres.py
```

## 🎨 Configuration du frontend

### 1. Installation des dépendances
```bash
cd ecommerce-front

# Installer les dépendances
npm install

# Build de production
npm run build
```

### 2. Configuration des variables d'environnement
```bash
# Copier le fichier de configuration
cp config.env.production .env.production

# Éditer les variables
nano .env.production
```

## 🐳 Déploiement avec Docker

### 1. Construction de l'image
```bash
# Depuis la racine du projet
./build-production.sh
```

### 2. Configuration du déploiement
```bash
cd production-build

# Copier et configurer les variables d'environnement
cp .env.example .env
nano .env
```

### 3. Déploiement
```bash
# Démarrer tous les services
./deploy.sh
```

## 🌐 Configuration du serveur web

### 1. Installation Nginx
```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 2. Configuration Nginx
```bash
# Créer la configuration
sudo nano /etc/nginx/sites-available/ecommerce
```

Configuration Nginx:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Frontend
    location / {
        root /path/to/ecommerce/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Activation du site
```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/

# Tester la configuration
sudo nginx -t

# Redémarrer Nginx
sudo systemctl restart nginx
```

## 🔒 Configuration SSL (HTTPS)

### 1. Installation Certbot
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### 2. Obtenir le certificat SSL
```bash
# Obtenir le certificat
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Renouvellement automatique
sudo crontab -e
# Ajouter: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring et logs

### 1. Configuration des logs
```bash
# Logs du backend
tail -f /var/log/ecommerce/backend.log

# Logs de Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 2. Monitoring de la base de données
```bash
# Se connecter à PostgreSQL
psql -h localhost -U ecommerce -d ecommerce

# Vérifier les tables
\dt

# Vérifier les données
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
```

## 🔄 Sauvegarde et maintenance

### 1. Sauvegarde de la base de données
```bash
# Créer un script de sauvegarde
nano /home/backup_db.sh
```

Script de sauvegarde:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/backups"
DB_NAME="ecommerce"

# Créer le dossier de sauvegarde
mkdir -p $BACKUP_DIR

# Sauvegarde de la base de données
pg_dump -h localhost -U ecommerce $DB_NAME > $BACKUP_DIR/ecommerce_$DATE.sql

# Compresser la sauvegarde
gzip $BACKUP_DIR/ecommerce_$DATE.sql

# Supprimer les sauvegardes anciennes (plus de 7 jours)
find $BACKUP_DIR -name "ecommerce_*.sql.gz" -mtime +7 -delete

echo "Sauvegarde terminée: $BACKUP_DIR/ecommerce_$DATE.sql.gz"
```

### 2. Automatisation des sauvegardes
```bash
# Rendre le script exécutable
chmod +x /home/backup_db.sh

# Ajouter à la crontab
crontab -e
# Ajouter: 0 2 * * * /home/backup_db.sh
```

## 🚨 Dépannage

### Problèmes courants

#### 1. Erreur de connexion à la base de données
```bash
# Vérifier que PostgreSQL est démarré
sudo systemctl status postgresql

# Vérifier la connexion
psql -h localhost -U ecommerce -d ecommerce
```

#### 2. Erreur CORS
- Vérifier que `PRODUCTION_ORIGINS` est correctement configuré
- Vérifier que le domaine est dans la liste des origines autorisées

#### 3. Erreur 502 Bad Gateway
- Vérifier que le backend est démarré sur le port 8000
- Vérifier la configuration Nginx

#### 4. Problème de permissions
```bash
# Vérifier les permissions des fichiers
ls -la /path/to/ecommerce/

# Corriger les permissions si nécessaire
sudo chown -R www-data:www-data /path/to/ecommerce/
```

## 📈 Optimisation des performances

### 1. Configuration PostgreSQL
```sql
-- Se connecter à PostgreSQL
sudo -u postgres psql

-- Optimiser la configuration
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Redémarrer PostgreSQL
sudo systemctl restart postgresql
```

### 2. Configuration Nginx
```nginx
# Ajouter dans la configuration Nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

# Cache pour les fichiers statiques
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## ✅ Checklist de déploiement

- [ ] Serveur configuré avec Docker et Docker Compose
- [ ] PostgreSQL installé et configuré
- [ ] Base de données créée avec les bonnes permissions
- [ ] Backend configuré avec les variables d'environnement
- [ ] Migration des données effectuée
- [ ] Frontend buildé pour la production
- [ ] Nginx configuré et démarré
- [ ] SSL configuré (HTTPS)
- [ ] Monitoring et logs configurés
- [ ] Sauvegarde automatisée configurée
- [ ] Tests de fonctionnement effectués

## 🎯 URLs de test

Après déploiement, tester ces URLs:
- **Frontend**: https://yourdomain.com
- **API Backend**: https://yourdomain.com/api/
- **Documentation API**: https://yourdomain.com/api/docs
- **Health Check**: https://yourdomain.com/api/

## 📞 Support

En cas de problème:
1. Vérifier les logs: `tail -f /var/log/nginx/error.log`
2. Vérifier le statut des services: `sudo systemctl status nginx postgresql`
3. Tester la connectivité: `curl -I https://yourdomain.com`
4. Vérifier la base de données: `psql -h localhost -U ecommerce -d ecommerce`
