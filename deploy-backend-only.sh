#!/bin/bash
set -e

echo "🚀 Déploiement du backend seulement..."

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

log_info "Configuration de l'environnement..."

# Copier le fichier d'environnement
cp .env.production .env

# Créer les répertoires nécessaires
log_info "Création des répertoires nécessaires..."
mkdir -p ssl logs monitoring

# Arrêter les conteneurs existants
log_info "Arrêt des conteneurs existants..."
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Construire seulement le backend et la base de données
log_info "Construction des images backend et base de données..."
docker-compose -f docker-compose.prod.yml build postgres redis backend

# Démarrer les services essentiels
log_info "Démarrage des services essentiels..."
docker-compose -f docker-compose.prod.yml up -d postgres redis backend

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
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
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
log_success "Déploiement backend terminé!"
echo ""
echo "🌐 Backend accessible sur:"
echo "   - API: http://localhost:8000"
echo "   - Health Check: http://localhost:8000/health"
echo "   - Stats: http://localhost:8000/stats"
echo ""
echo "🔧 Commandes utiles:"
echo "   - Voir les logs: docker-compose -f docker-compose.prod.yml logs -f backend"
echo "   - Arrêter: docker-compose -f docker-compose.prod.yml down"
echo "   - Redémarrer: docker-compose -f docker-compose.prod.yml restart backend"
echo ""

# Vérifier l'état final
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log_success "Backend déployé avec succès!"
    exit 0
else
    log_error "Le backend n'est pas accessible. Vérifiez les logs."
    exit 1
fi
