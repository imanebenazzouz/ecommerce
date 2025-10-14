#!/bin/bash

echo "🚀 Démarrage du backend FastAPI..."
cd ecommerce-backend

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé. Veuillez installer Python 3.8+"
    exit 1
fi

# Installer les dépendances si requirements.txt existe
if [ -f "requirements.txt" ]; then
    echo "📦 Installation des dépendances Python..."
    pip3 install -r requirements.txt
fi

# Démarrer le serveur FastAPI avec uvicorn
echo "🌐 Serveur API démarré sur http://localhost:8000"
echo "📚 Documentation API disponible sur http://localhost:8000/docs"
python3 -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
