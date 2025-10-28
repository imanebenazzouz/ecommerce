#!/bin/bash
# Script de nettoyage du projet ecommerce
# Supprime les fichiers obsolètes et redondants

echo "🧹 Nettoyage du projet ecommerce..."

# 1. Supprimer les fichiers API redondants
echo "📁 Suppression des fichiers API obsolètes..."
rm -f ecommerce-backend/api_backup.py
rm -f ecommerce-backend/api_fixed.py
rm -f ecommerce-backend/api_postgres_direct.py
rm -f ecommerce-backend/api_postgres_simple.py
rm -f ecommerce-backend/api_postgres.py
rm -f ecommerce-backend/api_simple.py
rm -f ecommerce-backend/api_sqlite.py
rm -f ecommerce-backend/api_unified.py

# 2. Supprimer les bases SQLite obsolètes
echo "🗄️ Suppression des bases SQLite obsolètes..."
rm -f ecommerce-backend/ecommerce.db
rm -f ecommerce.db
rm -f tests/ecommerce.db

# 3. Supprimer les fichiers de migration temporaires
echo "🔄 Suppression des fichiers de migration temporaires..."
rm -f ecommerce-backend/migrate_add_street_name.py
rm -f ecommerce-backend/migrate_payment_fields.py

# 4. Supprimer les fichiers de démonstration
echo "🎭 Suppression des fichiers de démonstration..."
rm -f ecommerce-backend/demo_advanced_features.py
rm -f ecommerce-backend/test_services.py

# 5. Supprimer les fichiers PDF de test
echo "📄 Suppression des fichiers PDF de test..."
rm -f ecommerce-backend/test_invoice_client.pdf
rm -f ecommerce-backend/test_invoice.pdf

# 6. Supprimer les fichiers de données JSON obsolètes
echo "📊 Suppression des fichiers JSON obsolètes..."
rm -rf ecommerce-backend/data/
rm -rf data/

# 7. Supprimer les fichiers de cache Python
echo "🐍 Suppression des fichiers de cache Python..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f -delete 2>/dev/null || true
find . -name "*.pyo" -type f -delete 2>/dev/null || true

# 8. Supprimer les fichiers de logs temporaires
echo "📝 Suppression des logs temporaires..."
rm -f logs/backend.log
rm -f logs/frontend.log

# 9. Supprimer les fichiers de build frontend
echo "🏗️ Suppression des fichiers de build frontend..."
rm -rf ecommerce-front/dist/

echo "✅ Nettoyage terminé !"
echo ""
echo "📋 Résumé des suppressions :"
echo "   - Fichiers API redondants : 8 fichiers"
echo "   - Bases SQLite obsolètes : 3 fichiers"
echo "   - Fichiers de migration : 2 fichiers"
echo "   - Fichiers de démonstration : 2 fichiers"
echo "   - Fichiers PDF de test : 2 fichiers"
echo "   - Dossiers de données JSON : 2 dossiers"
echo "   - Fichiers de cache Python : tous"
echo "   - Logs temporaires : 2 fichiers"
echo "   - Build frontend : 1 dossier"
echo ""
echo "🎉 Votre projet est maintenant propre et optimisé !"
