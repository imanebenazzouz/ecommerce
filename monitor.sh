#!/bin/bash
set -e

echo "📊 Monitoring de l'application ecommerce..."

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

# Vérifier le statut des conteneurs
log_info "Statut des conteneurs:"
docker-compose -f docker-compose.prod.yml ps

echo ""

# Vérifier l'utilisation des ressources
log_info "Utilisation des ressources:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

echo ""

# Vérifier la connectivité
log_info "Test de connectivité:"

# Test API
if curl -f http://localhost/health > /dev/null 2>&1; then
    log_success "API accessible"
else
    log_error "API non accessible"
fi

# Test Frontend
if curl -f http://localhost/ > /dev/null 2>&1; then
    log_success "Frontend accessible"
else
    log_error "Frontend non accessible"
fi

# Test Base de données
if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U ecommerce -d ecommerce > /dev/null 2>&1; then
    log_success "Base de données accessible"
else
    log_error "Base de données non accessible"
fi

# Test Redis
if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    log_success "Redis accessible"
else
    log_error "Redis non accessible"
fi

echo ""

# Afficher les logs récents
log_info "Logs récents (dernières 10 lignes):"
docker-compose -f docker-compose.prod.yml logs --tail=10

echo ""

# Afficher les métriques de l'API
log_info "Métriques de l'API:"
if curl -f http://localhost/api/stats > /dev/null 2>&1; then
    curl -s http://localhost/api/stats | python3 -m json.tool 2>/dev/null || echo "Impossible d'afficher les métriques JSON"
else
    log_warning "Impossible de récupérer les métriques de l'API"
fi

echo ""

# Afficher l'espace disque
log_info "Utilisation de l'espace disque:"
df -h | grep -E "(Filesystem|/dev/)"

echo ""

# Afficher la mémoire
log_info "Utilisation de la mémoire:"
free -h

echo ""

# Afficher les ports ouverts
log_info "Ports ouverts:"
netstat -tlnp | grep -E ":(80|443|8000|5432|6379|9090|3001)" || ss -tlnp | grep -E ":(80|443|8000|5432|6379|9090|3001)"

echo ""

log_success "Monitoring terminé!"
