#!/bin/bash

echo "🗄️ Accès à la base de données PostgreSQL"
echo "========================================"

# Informations de connexion
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="ecommerce"
DB_USER="ecommerce"
DB_PASSWORD="ecommerce_secure_2024"

echo "📋 Informations de connexion:"
echo "   Host: $DB_HOST"
echo "   Port: $DB_PORT"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Password: $DB_PASSWORD"
echo ""

echo "🔧 Commandes utiles:"
echo ""
echo "1. Connexion avec psql:"
echo "   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
echo ""
echo "2. Connexion avec Docker:"
echo "   docker exec -it ecommerce-postgres-prod psql -U $DB_USER -d $DB_NAME"
echo ""
echo "3. Sauvegarde de la base de données:"
echo "   pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME > backup.sql"
echo ""
echo "4. Restauration de la base de données:"
echo "   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < backup.sql"
echo ""

# Vérifier si PostgreSQL est accessible
echo "🔍 Test de connexion à la base de données..."
if docker exec ecommerce-postgres-prod pg_isready -U $DB_USER -d $DB_NAME > /dev/null 2>&1; then
    echo "✅ Base de données accessible!"
    echo ""
    echo "📊 Tables disponibles:"
    docker exec ecommerce-postgres-prod psql -U $DB_USER -d $DB_NAME -c "\dt"
else
    echo "❌ Base de données non accessible. Vérifiez que les conteneurs sont démarrés."
    echo "   Commande: docker-compose -f docker-compose.prod.yml ps"
fi


