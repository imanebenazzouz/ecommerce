#!/bin/bash

echo "🚀 Démarrage facile de l'application e-commerce"
echo "=" * 50

# Aller dans le répertoire backend
cd ecommerce-backend

# Activer l'environnement virtuel
echo "🐍 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier que Python est correct
echo "📍 Python utilisé: $(which python)"
echo "📦 SQLAlchemy: $(python -c 'import sqlalchemy; print(sqlalchemy.__version__)' 2>/dev/null || echo 'Non installé')"

# Démarrer l'API
echo "📡 Démarrage de l'API..."
echo "🌐 URL: http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "=" * 50

python run_api.py
