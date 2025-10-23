#!/bin/bash

echo "🔄 Redémarrage avec les corrections du problème 'Load failed'"

# Arrêter les processus existants
echo "⏹️  Arrêt des processus existants..."
pkill -f "uvicorn api:app" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

# Attendre un peu
sleep 2

# Redémarrer le backend
echo "🚀 Redémarrage du backend..."
cd /Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Attendre que le backend soit prêt
echo "⏳ Attente du backend..."
sleep 5

# Tester le backend
echo "🧪 Test du backend..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend opérationnel"
else
    echo "❌ Problème avec le backend"
    exit 1
fi

# Redémarrer le frontend
echo "🌐 Redémarrage du frontend..."
cd /Users/imanebenazzouz/Desktop/ecommerce/ecommerce-front
npm run dev &
FRONTEND_PID=$!

# Attendre que le frontend soit prêt
echo "⏳ Attente du frontend..."
sleep 5

# Tester le frontend
echo "🧪 Test du frontend..."
if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend opérationnel"
else
    echo "❌ Problème avec le frontend"
    exit 1
fi

echo ""
echo "🎉 Système redémarré avec succès !"
echo ""
echo "📋 Instructions de test :"
echo "1. Ouvrez http://localhost:5173 dans votre navigateur"
echo "2. Connectez-vous avec admin@example.com / admin"
echo "3. Vérifiez qu'il n'y a plus de 'Load failed'"
echo "4. Testez l'ajout d'articles au panier"
echo ""
echo "🔧 Pour arrêter les services :"
echo "kill $BACKEND_PID $FRONTEND_PID"
