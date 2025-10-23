#!/bin/bash

echo "🚀 Démarrage et debug de l'e-commerce"
echo "====================================="

# Fonction pour vérifier si un port est utilisé
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "✅ Port $1 déjà utilisé"
        return 0
    else
        echo "❌ Port $1 libre"
        return 1
    fi
}

# Vérifier les ports
echo "\n1. Vérification des ports..."
check_port 8000
check_port 5173

# Démarrer le backend si nécessaire
if ! check_port 8000; then
    echo "\n2. Démarrage du backend..."
    cd ecommerce-backend
    python3 api.py &
    BACKEND_PID=$!
    echo "Backend démarré (PID: $BACKEND_PID)"
    
    # Attendre que le backend soit prêt
    echo "Attente du démarrage du backend..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/ > /dev/null; then
            echo "✅ Backend prêt"
            break
        fi
        sleep 1
    done
else
    echo "Backend déjà en cours d'exécution"
fi

# Test de l'API
echo "\n3. Test de l'API..."
cd ..
python3 debug_requests.py

# Démarrer le frontend si nécessaire
if ! check_port 5173; then
    echo "\n4. Démarrage du frontend..."
    cd ecommerce-front
    npm run dev &
    FRONTEND_PID=$!
    echo "Frontend démarré (PID: $FRONTEND_PID)"
    
    # Attendre que le frontend soit prêt
    echo "Attente du démarrage du frontend..."
    for i in {1..30}; do
        if curl -s http://localhost:5173/ > /dev/null; then
            echo "✅ Frontend prêt"
            break
        fi
        sleep 1
    done
else
    echo "Frontend déjà en cours d'exécution"
fi

echo "\n5. URLs d'accès:"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend API: http://localhost:8000"
echo "   - Documentation API: http://localhost:8000/docs"
echo "   - Test HTML: file://$(pwd)/test_frontend_timing.html"

echo "\n6. Comptes de test:"
echo "   - Admin: admin@example.com / admin"
echo "   - Client: client@example.com / secret"

echo "\n7. Debug du problème 'load failed':"
echo "   - Ouvrez http://localhost:5173"
echo "   - Connectez-vous avec admin@example.com / admin"
echo "   - Vérifiez la console du navigateur (F12)"
echo "   - Regardez les erreurs réseau dans l'onglet Network"

echo "\n✅ Système prêt pour le debug !"
echo "Appuyez sur Ctrl+C pour arrêter les serveurs"
