#!/bin/bash

# Script de démarrage du serveur e-commerce

echo "🚀 Démarrage du serveur e-commerce..."

# Aller dans le répertoire backend
cd ecommerce-backend

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier que l'environnement virtuel est activé
echo "🐍 Python utilisé: $(which python)"
echo "📦 SQLAlchemy version: $(python -c 'import sqlalchemy; print(sqlalchemy.__version__)')"

# Démarrer le serveur
echo "📡 Démarrage de l'API sur http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "=" * 50

python run_api.py
