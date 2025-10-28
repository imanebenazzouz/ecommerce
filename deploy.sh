#!/bin/bash
# Script de déploiement en production pour l'e-commerce
# ======================================================
#
# Ce script automatise le déploiement complet en production :
# 1. Vérifie les prérequis (Docker, Docker Compose)
# 2. Configure l'environnement (.env.production)
# 3. Arrête les services existants
# 4. Construit les images Docker
# 5. Démarre tous les services
# 6. Vérifie la santé des services
# 7. Affiche les informations d'accès
#
# Prérequis :
# - Docker et Docker Compose installés
# - Fichier .env.production configuré
# - Ports 80, 443, 3000, 8000, 5432, 6379, 9090, 3001 libres
#
# Usage : ./deploy.sh

set -e

echo "🚀 Déploiement de l'application ecommerce en production..."

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifier si le fichier .env.production existe
if [ ! -f ".env.production" ]; then
    log_error "Le fichier .env.production n'existe pas. Veuillez le créer d'abord."
    exit 1
fi

log_info "Configuration de l'environnement de production..."

# Copier le fichier d'environnement
cp .env.production .env

# Créer les répertoires nécessaires
log_info "Création des répertoires nécessaires..."
mkdir -p ssl logs monitoring

# Arrêter les conteneurs existants
log_info "Arrêt des conteneurs existants..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Nettoyer les images inutilisées
log_info "Nettoyage des images Docker..."
docker system prune -f

# Construire les images
log_info "Construction des images Docker..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Démarrer les services
log_info "Démarrage des services..."
docker-compose -f docker-compose.prod.yml up -d

# Attendre que les services soient prêts
log_info "Attente du démarrage des services..."
sleep 30

# Vérifier le statut des services
log_info "Vérification du statut des services..."
docker-compose -f docker-compose.prod.yml ps

# Tester la connectivité
log_info "Test de la connectivité..."

# Attendre que l'API soit prête
for i in {1..30}; do
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "API accessible!"
        break
    fi
    log_info "Attente de l'API... ($i/30)"
    sleep 2
done

# Afficher les logs des services
log_info "Logs des services:"
docker-compose -f docker-compose.prod.yml logs --tail=20

# Afficher les informations de connexion
log_success "Déploiement terminé!"
echo ""
echo "🌐 Application accessible sur:"
echo "   - Frontend: http://localhost"
echo "   - API: http://localhost/api"
echo "   - Health Check: http://localhost/health"
echo ""
echo "📊 Monitoring:"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3001 (admin/admin_secure_password_2024)"
echo ""
echo "🔧 Commandes utiles:"
echo "   - Voir les logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   - Arrêter: docker-compose -f docker-compose.prod.yml down"
echo "   - Redémarrer: docker-compose -f docker-compose.prod.yml restart"
echo "   - Mise à jour: ./deploy.sh"
echo ""

# Vérifier l'état final
if curl -f http://localhost/health > /dev/null 2>&1; then
    log_success "Application déployée avec succès!"
    exit 0
else
    log_error "L'application n'est pas accessible. Vérifiez les logs."
    exit 1
fi
