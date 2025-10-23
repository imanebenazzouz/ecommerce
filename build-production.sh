#!/bin/bash

# Script de build pour la production
echo "🚀 Construction de l'application ecommerce pour la production..."

# Variables
BACKEND_DIR="ecommerce-backend"
FRONTEND_DIR="ecommerce-front"
BUILD_DIR="production-build"

# Créer le dossier de build
echo "📁 Création du dossier de build..."
mkdir -p $BUILD_DIR

# Build du backend
echo "🔧 Construction du backend..."
cd $BACKEND_DIR

# Installer les dépendances
echo "📦 Installation des dépendances backend..."
pip install -r requirements.txt
pip install sqlalchemy psycopg2-binary alembic gunicorn

# Créer les tables de base de données
echo "🗄️ Création des tables de base de données..."
python -c "from database.database import create_tables; create_tables()"

# Migrer les données si nécessaire
echo "🔄 Migration des données..."
python scripts/migrate_to_postgres.py

# Copier les fichiers du backend
echo "📋 Copie des fichiers backend..."
cp -r . ../$BUILD_DIR/backend/
cp config.env.production ../$BUILD_DIR/backend/.env

cd ..

# Build du frontend
echo "🎨 Construction du frontend..."
cd $FRONTEND_DIR

# Installer les dépendances
echo "📦 Installation des dépendances frontend..."
npm install

# Build de production
echo "🏗️ Build de production du frontend..."
npm run build

# Copier les fichiers du frontend
echo "📋 Copie des fichiers frontend..."
cp -r dist ../$BUILD_DIR/frontend/

cd ..

# Créer les fichiers de configuration de production
echo "⚙️ Création des fichiers de configuration..."

# Docker Compose pour la production
cat > $BUILD_DIR/docker-compose.prod.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    container_name: ecommerce_postgres_prod
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: ecommerce
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - ecommerce_network

  redis:
    image: redis:7-alpine
    container_name: ecommerce_redis_prod
    restart: unless-stopped
    networks:
      - ecommerce_network

  backend:
    build: ./backend
    container_name: ecommerce_backend_prod
    environment:
      - DATABASE_URL=postgresql://ecommerce:${POSTGRES_PASSWORD}@postgres:5432/ecommerce
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    restart: unless-stopped
    networks:
      - ecommerce_network

  frontend:
    image: nginx:alpine
    container_name: ecommerce_frontend_prod
    volumes:
      - ./frontend:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - ecommerce_network

volumes:
  postgres_data:

networks:
  ecommerce_network:
    driver: bridge
EOF

# Configuration Nginx
cat > $BUILD_DIR/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    # Configuration pour le frontend
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        root /usr/share/nginx/html;
        index index.html;
        
        # Gestion des routes SPA
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # API proxy vers le backend
        location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Configuration pour les fichiers statiques
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
EOF

# Dockerfile pour le backend
cat > $BUILD_DIR/backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install sqlalchemy psycopg2-binary alembic gunicorn

# Copier le code
COPY . .

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["gunicorn", "api:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
EOF

# Script de déploiement
cat > $BUILD_DIR/deploy.sh << 'EOF'
#!/bin/bash

echo "🚀 Déploiement de l'application ecommerce..."

# Charger les variables d'environnement
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
else
    echo "❌ Fichier .env non trouvé!"
    exit 1
fi

# Démarrer les services
echo "🐳 Démarrage des services Docker..."
docker-compose -f docker-compose.prod.yml up -d

# Attendre que PostgreSQL soit prêt
echo "⏳ Attente de PostgreSQL..."
sleep 10

# Exécuter les migrations
echo "🔄 Exécution des migrations..."
docker-compose -f docker-compose.prod.yml exec backend python scripts/migrate_to_postgres.py

echo "✅ Déploiement terminé!"
echo "🌐 Frontend: http://localhost"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
EOF

chmod +x $BUILD_DIR/deploy.sh

# Fichier .env d'exemple
cat > $BUILD_DIR/.env.example << 'EOF'
# Configuration de production
POSTGRES_PASSWORD=your_secure_password_here
SECRET_KEY=your_super_secret_key_here
DOMAIN=yourdomain.com
EOF

echo "✅ Build de production terminé!"
echo "📁 Dossier de build: $BUILD_DIR"
echo "🚀 Pour déployer: cd $BUILD_DIR && ./deploy.sh"
