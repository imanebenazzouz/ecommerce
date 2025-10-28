#!/bin/bash
# Script de déploiement simplifié pour l'e-commerce
# ================================================
#
# Version simplifiée du déploiement pour les tests rapides :
# 1. Vérifie Docker et Docker Compose
# 2. Arrête les services existants
# 3. Nettoie les images inutilisées
# 4. Construit et démarre les services
# 5. Affiche les informations d'accès
#
# Prérequis :
# - Docker et Docker Compose installés
# - Fichier docker-compose.prod.yml configuré
#
# Usage : ./deploy_simple.sh

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Installez Docker d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Installez Docker Compose d'abord."
    exit 1
fi

log_info "Arrêt des conteneurs existants..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

log_info "Nettoyage des images inutilisées..."
docker system prune -f

log_info "Construction des images..."
docker-compose -f docker-compose.prod.yml build

log_info "Démarrage des services..."
docker-compose -f docker-compose.prod.yml up -d

log_info "Attente du démarrage (30 secondes)..."
sleep 30

log_info "Vérification du statut..."
docker-compose -f docker-compose.prod.yml ps

log_success "Déploiement terminé!"
echo ""
echo "📋 Pour plus d'informations sur l'accès: ./access_database.sh"
echo ""
echo "🌐 Votre site est accessible sur:"
echo "   - Site web: http://localhost"
echo "   - API: http://localhost/api"
echo "   - Documentation API: http://localhost/api/docs"
echo ""
echo "🗄️ Base de données PostgreSQL:"
echo "   - Host: localhost"
echo "   - Port: 5432"
echo "   - Database: ecommerce"
echo "   - User: ecommerce"
echo "   - Password: [Voir config.env.production]"
echo ""
echo "📊 Monitoring:"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3001"
echo ""
echo "🔧 Commandes utiles:"
echo "   - Voir les logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   - Arrêter: docker-compose -f docker-compose.prod.yml down"
echo "   - Redémarrer: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "📋 Pour Yannis:"
echo "   - URL du site: http://localhost"
echo "   - Accès à la base de données: voir les informations ci-dessus"
echo "   - Documentation API: http://localhost/api/docs"
