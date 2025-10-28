#!/bin/bash
# Script d'arrêt propre du frontend React
# =======================================
#
# Ce script arrête proprement le serveur de développement React
# en tuant les processus qui utilisent les ports Vite (5173, 5175).
#
# Utile quand le frontend ne répond plus ou pour libérer les ports
# avant de redémarrer le serveur de développement.
#
# Usage : ./kill_frontend.sh

# Script pour arrêter proprement le frontend
echo "🛑 Arrêt du frontend..."

# Tuer les processus sur le port 5173
echo "   - Arrêt du port 5173..."
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Tuer les processus sur le port 5175 (au cas où)
echo "   - Arrêt du port 5175..."
lsof -ti:5175 | xargs kill -9 2>/dev/null || true

# Attendre un peu
sleep 2

echo "✅ Frontend arrêté proprement"
echo "   Vous pouvez maintenant redémarrer avec: npm run dev"
