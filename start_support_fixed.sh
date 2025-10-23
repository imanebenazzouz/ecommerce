#!/bin/bash

echo "🛠️ Démarrage de l'application e-commerce avec support corrigé"
echo "============================================================="

# Fonction pour tuer les processus existants
cleanup() {
    echo "🧹 Nettoyage des processus existants..."
    pkill -f "python.*api" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    pkill -f "npm.*dev" 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    lsof -ti:5174 | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Nettoyer les processus existants
cleanup

# Vérifier PostgreSQL
echo "🔍 Vérification de PostgreSQL..."
if ! psql -h localhost -U ecommerce -d ecommerce -c "SELECT 1;" >/dev/null 2>&1; then
    echo "❌ PostgreSQL n'est pas accessible"
    echo "💡 Veuillez démarrer PostgreSQL et créer la base de données 'ecommerce'"
    exit 1
fi
echo "✅ PostgreSQL accessible"

# Démarrer le backend
echo "🚀 Démarrage du backend..."
cd ecommerce-backend

# Créer les tables si nécessaire
echo "📊 Initialisation de la base de données..."
DATABASE_URL="postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce" python3 -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce'
from database.database import create_tables
create_tables()
print('✅ Tables créées')
"

# Démarrer l'API avec uvicorn
echo "🔄 Démarrage de l'API avec uvicorn..."
DATABASE_URL="postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce" uvicorn api:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Attendre que l'API soit prête
echo "⏳ Attente du démarrage de l'API..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ API démarrée (PID: $BACKEND_PID)"
        break
    fi
    echo "⏳ Tentative $i/30..."
    sleep 2
done

# Vérifier que l'API fonctionne
if ! curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "❌ L'API n'a pas démarré correctement"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Initialiser les données
echo "📝 Initialisation des données..."
curl -s -X POST http://localhost:8000/init-data >/dev/null 2>&1 || echo "⚠️ Données déjà initialisées"

# Démarrer le frontend
echo "🚀 Démarrage du frontend..."
cd ../ecommerce-front

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
    echo "📦 Installation des dépendances..."
    npm install
fi

# Démarrer le frontend
echo "🔄 Démarrage du frontend avec Vite..."
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Attendre que le frontend soit prêt
echo "⏳ Attente du démarrage du frontend..."
for i in {1..30}; do
    if curl -s http://localhost:5173 >/dev/null 2>&1 || curl -s http://localhost:5174 >/dev/null 2>&1; then
        echo "✅ Frontend démarré (PID: $FRONTEND_PID)"
        break
    fi
    echo "⏳ Tentative $i/30..."
    sleep 2
done

# Déterminer le port du frontend
FRONTEND_PORT="5173"
if ! curl -s http://localhost:5173 >/dev/null 2>&1; then
    FRONTEND_PORT="5174"
fi

# Test de l'authentification
echo "🧪 Test de l'authentification..."
cd ..
python3 test_auth_quick.py

# Test du support
echo "🧪 Test du support..."
python3 test_support.py

echo ""
echo "🎉 Application démarrée avec succès !"
echo ""
echo "🌐 URLs disponibles:"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Test Support: http://localhost:$FRONTEND_PORT/support-test"
echo "   Test Support Browser: file://$(pwd)/test_support_browser.html"
echo ""
echo "👤 Comptes de test:"
echo "   Admin: admin@example.com / admin"
echo "   Client: client@example.com / secret"
echo ""
echo "📊 Logs:"
echo "   Backend: logs/backend.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "🛑 Pour arrêter l'application:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "💡 Si vous avez une page blanche sur le support:"
echo "   1. Ouvrez http://localhost:$FRONTEND_PORT/support-test pour diagnostiquer"
echo "   2. Ouvrez la console du navigateur (F12) pour voir les erreurs"
echo "   3. Testez avec le fichier test_support_browser.html"
echo ""
echo "✅ Application prête !"
