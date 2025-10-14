#!/bin/bash

echo "🚀 Démarrage du frontend React..."
cd ecommerce-front

# Vérifier si Node.js est installé
if ! command -v node &> /dev/null; then
    echo "❌ Node.js n'est pas installé. Veuillez installer Node.js 16+"
    exit 1
fi

# Installer les dépendances si package.json existe
if [ -f "package.json" ]; then
    echo "📦 Installation des dépendances Node.js..."
    npm install
fi

# Démarrer le serveur de développement Vite
echo "🌐 Serveur frontend démarré sur http://localhost:5173"
npm run dev
