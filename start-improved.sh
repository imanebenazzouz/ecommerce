#!/bin/bash

# Script de démarrage amélioré pour l'application e-commerce avec CSS moderne

echo "🚀 Démarrage de l'application e-commerce avec design moderne..."
echo "=================================================="

# Vérifier si les dossiers existent
if [ ! -d "ecommerce-backend" ]; then
    echo "❌ Erreur: Le dossier ecommerce-backend n'existe pas"
    exit 1
fi

if [ ! -d "ecommerce-front" ]; then
    echo "❌ Erreur: Le dossier ecommerce-front n'existe pas"
    exit 1
fi

# Fonction pour vérifier si un port est utilisé
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port utilisé
    else
        return 1  # Port libre
    fi
}

# Vérifier les ports
echo "🔍 Vérification des ports..."
if check_port 8000; then
    echo "⚠️  Le port 8000 (backend) est déjà utilisé"
fi

if check_port 5173; then
    echo "⚠️  Le port 5173 (frontend) est déjà utilisé"
fi

# Démarrer le backend
echo "🔧 Démarrage du backend FastAPI..."
cd ecommerce-backend

# Vérifier si les dépendances Python sont installées
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "📦 Installation des dépendances Python..."
    pip3 install -r requirements.txt
fi

# Démarrer le backend en arrière-plan
echo "🚀 Backend démarré sur http://localhost:8000"
uvicorn api:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Attendre que le backend démarre
echo "⏳ Attente du démarrage du backend..."
sleep 3

# Vérifier que le backend répond
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ Backend opérationnel"
else
    echo "❌ Erreur: Le backend ne répond pas"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Retourner au dossier racine
cd ..

# Démarrer le frontend
echo "🎨 Démarrage du frontend React avec CSS moderne..."
cd ecommerce-front

# Vérifier si node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances Node.js..."
    npm install
fi

# Démarrer le frontend
echo "🚀 Frontend démarré sur http://localhost:5173"
echo "🎉 Application disponible avec le nouveau design moderne !"
echo ""
echo "📋 Fonctionnalités améliorées :"
echo "  • Design moderne avec dégradés et animations"
echo "  • Interface responsive pour mobile et desktop"
echo "  • Indicateurs de force de mot de passe"
echo "  • États de chargement avec spinners"
echo "  • Messages d'erreur et succès stylisés"
echo "  • Cartes produits avec hover effects"
echo "  • Panier interactif avec gestion des quantités"
echo "  • Formulaire de paiement amélioré"
echo ""
echo "🔐 Comptes de test :"
echo "  • Admin: admin@example.com / admin"
echo "  • Client: client@example.com / secret"
echo ""
echo "💡 Conseils d'utilisation :"
echo "  • Ouvrez http://localhost:5173 dans votre navigateur"
echo "  • Testez la responsivité en redimensionnant la fenêtre"
echo "  • Essayez les animations et effets de survol"
echo "  • Utilisez les comptes de test pour tester les fonctionnalités"
echo ""
echo "🛑 Pour arrêter l'application, utilisez Ctrl+C"

# Fonction de nettoyage
cleanup() {
    echo ""
    echo "🛑 Arrêt de l'application..."
    kill $BACKEND_PID 2>/dev/null
    echo "✅ Application arrêtée"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Démarrer le frontend (cela bloquera jusqu'à l'arrêt)
npm run dev

# Nettoyage en cas d'arrêt normal
cleanup
