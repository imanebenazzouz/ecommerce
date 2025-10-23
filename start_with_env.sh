#!/bin/bash

# Script de démarrage avec variables d'environnement
echo "🚀 Démarrage de l'e-commerce avec variables d'environnement..."

# Aller dans le répertoire backend
cd ecommerce-backend

# Activer l'environnement virtuel
source venv/bin/activate

# Définir les variables d'environnement
export DATABASE_URL="postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce"
export SECRET_KEY="dev_secret_key_change_in_production"
export DEBUG="True"
export CORS_ORIGINS="http://localhost:5173,http://localhost:3000"

echo "📊 Variables d'environnement définies:"
echo "  DATABASE_URL: $DATABASE_URL"
echo "  SECRET_KEY: $SECRET_KEY"
echo "  DEBUG: $DEBUG"
echo "  CORS_ORIGINS: $CORS_ORIGINS"

# Démarrer l'API
echo "🌐 Démarrage de l'API sur http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "=" * 50

uvicorn api_unified:app --host 0.0.0.0 --port 8000 --reload
