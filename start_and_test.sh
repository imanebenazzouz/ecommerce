#!/bin/bash

echo "🛒 Démarrage et test de l'application e-commerce"
echo "=============================================="

# Fonction pour vérifier si un port est utilisé
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "✅ Port $1 est utilisé"
        return 0
    else
        echo "❌ Port $1 n'est pas utilisé"
        return 1
    fi
}

# Fonction pour attendre qu'un service soit disponible
wait_for_service() {
    local url=$1
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Attente du service $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            echo "✅ Service $url est disponible"
            return 0
        fi
        
        echo "⏳ Tentative $attempt/$max_attempts..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ Service $url n'est pas disponible après $max_attempts tentatives"
    return 1
}

# Vérifier si PostgreSQL est en cours d'exécution
echo "🔍 Vérification de PostgreSQL..."
if ! check_port 5432; then
    echo "❌ PostgreSQL n'est pas en cours d'exécution"
    echo "💡 Veuillez démarrer PostgreSQL avant de continuer"
    exit 1
fi

# Démarrer le backend
echo "🚀 Démarrage du backend..."
cd ecommerce-backend

# Vérifier si le backend est déjà en cours d'exécution
if check_port 8000; then
    echo "⚠️  Le backend est déjà en cours d'exécution sur le port 8000"
    echo "💡 Arrêt du processus existant..."
    pkill -f "python.*api.py" || true
    sleep 2
fi

# Démarrer le backend en arrière-plan
echo "🔄 Démarrage du backend en arrière-plan..."
nohup python3 api.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Attendre que le backend soit disponible
if wait_for_service "http://localhost:8000/health"; then
    echo "✅ Backend démarré avec succès (PID: $BACKEND_PID)"
else
    echo "❌ Échec du démarrage du backend"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Démarrer le frontend
echo "🚀 Démarrage du frontend..."
cd ../ecommerce-front

# Vérifier si le frontend est déjà en cours d'exécution
if check_port 5173; then
    echo "⚠️  Le frontend est déjà en cours d'exécution sur le port 5173"
    echo "💡 Arrêt du processus existant..."
    pkill -f "vite" || true
    sleep 2
fi

# Démarrer le frontend en arrière-plan
echo "🔄 Démarrage du frontend en arrière-plan..."
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Attendre que le frontend soit disponible
if wait_for_service "http://localhost:5173"; then
    echo "✅ Frontend démarré avec succès (PID: $FRONTEND_PID)"
else
    echo "❌ Échec du démarrage du frontend"
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Attendre un peu pour que tout soit prêt
echo "⏳ Attente de la stabilisation des services..."
sleep 5

# Exécuter les tests
echo "🧪 Exécution des tests complets..."
cd ..
python3 test_complete_fix.py

# Afficher les URLs
echo ""
echo "🌐 URLs de l'application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   Documentation API: http://localhost:8000/docs"
echo ""
echo "📊 Logs:"
echo "   Backend: logs/backend.log"
echo "   Frontend: logs/frontend.log"
echo ""
echo "🛑 Pour arrêter l'application:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "✅ Application e-commerce démarrée avec succès !"