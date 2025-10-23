#!/bin/bash

# Script de démarrage avec variables d'environnement forcées
echo "🚀 Démarrage de l'e-commerce avec configuration forcée..."

# Aller dans le répertoire backend
cd ecommerce-backend

# Activer l'environnement virtuel
source venv/bin/activate

# Forcer les variables d'environnement
export DATABASE_URL="postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce"
export SECRET_KEY="dev_secret_key_change_in_production"
export DEBUG="True"
export CORS_ORIGINS="http://localhost:5173,http://localhost:3000"

echo "📊 Variables d'environnement:"
echo "  DATABASE_URL: $DATABASE_URL"
echo "  SECRET_KEY: $SECRET_KEY"
echo "  DEBUG: $DEBUG"

# Test de connexion à la base de données
echo "🔍 Test de connexion à PostgreSQL..."
python -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce'
from database.database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT version()')
    print('✅ Connexion PostgreSQL OK:', result.fetchone()[0])
"

if [ $? -eq 0 ]; then
    echo "✅ Base de données accessible"
else
    echo "❌ Problème de connexion à la base de données"
    exit 1
fi

# Démarrer l'API
echo "🌐 Démarrage de l'API sur http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "=" * 50

# Utiliser api_postgres_direct.py qui semble plus simple
uvicorn api_postgres_direct:app --host 0.0.0.0 --port 8000 --reload
