# 🚀 Ecommerce - Configuration de Production

Application ecommerce complète avec PostgreSQL, Redis, Nginx et monitoring.

## 📋 Prérequis

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB espace disque libre

## 🚀 Déploiement Rapide

### 1. Cloner et configurer

```bash
# Cloner le projet
git clone <votre-repo>
cd ecommerce

# Configurer l'environnement
cp .env.production .env
# Éditer .env avec vos paramètres
```

### 2. Déployer

```bash
# Déploiement automatique
./deploy.sh
```

### 3. Vérifier

```bash
# Monitoring
./monitor.sh

# Vérifier l'application
curl http://localhost/health
```

## 🌐 Accès aux Services

| Service | URL | Description |
|---------|-----|-------------|
| **Application** | http://localhost | Interface utilisateur |
| **API** | http://localhost/api | API REST |
| **Health Check** | http://localhost/health | Statut de l'API |
| **Prometheus** | http://localhost:9090 | Métriques |
| **Grafana** | http://localhost:3001 | Dashboards |

## 🔧 Configuration

### Variables d'environnement importantes

```bash
# Base de données
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password

# Sécurité
SECRET_KEY=your_super_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Domaine (pour la production)
DOMAIN=votre-domaine.com
CORS_ORIGINS=https://votre-domaine.com
```

### SSL/HTTPS

Pour activer HTTPS :

1. Placez vos certificats SSL dans `./ssl/` :
   - `cert.pem` (certificat)
   - `key.pem` (clé privée)

2. Décommentez la section HTTPS dans `nginx/conf.d/ecommerce.conf`

3. Redémarrez : `docker-compose -f docker-compose.prod.yml restart nginx`

## 📊 Monitoring

### Prometheus
- URL : http://localhost:9090
- Métriques des services
- Alertes configurables

### Grafana
- URL : http://localhost:3001
- Login : admin / admin_secure_password_2024
- Dashboards prêts à l'emploi

### Logs
```bash
# Tous les services
docker-compose -f docker-compose.prod.yml logs -f

# Service spécifique
docker-compose -f docker-compose.prod.yml logs -f backend
```

## 🔄 Maintenance

### Sauvegarde de la base de données

```bash
# Sauvegarde
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U ecommerce ecommerce > backup.sql

# Restauration
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U ecommerce ecommerce < backup.sql
```

### Mise à jour

```bash
# Arrêter les services
docker-compose -f docker-compose.prod.yml down

# Mettre à jour le code
git pull

# Redéployer
./deploy.sh
```

### Redémarrage des services

```bash
# Tous les services
docker-compose -f docker-compose.prod.yml restart

# Service spécifique
docker-compose -f docker-compose.prod.yml restart backend
```

## 🛠️ Commandes Utiles

```bash
# Voir le statut
docker-compose -f docker-compose.prod.yml ps

# Voir les logs
docker-compose -f docker-compose.prod.yml logs -f

# Accéder à la base de données
docker-compose -f docker-compose.prod.yml exec postgres psql -U ecommerce ecommerce

# Accéder au conteneur backend
docker-compose -f docker-compose.prod.yml exec backend bash

# Monitoring
./monitor.sh

# Nettoyer les volumes
docker-compose -f docker-compose.prod.yml down -v
```

## 🔒 Sécurité

### Checklist de sécurité

- [ ] Changer tous les mots de passe par défaut
- [ ] Configurer HTTPS avec des certificats valides
- [ ] Limiter l'accès aux ports de monitoring
- [ ] Configurer un firewall
- [ ] Mettre à jour régulièrement les images Docker
- [ ] Surveiller les logs d'accès

### Configuration du firewall

```bash
# Autoriser seulement les ports nécessaires
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 22/tcp   # SSH (si nécessaire)
ufw enable
```

## 📈 Performance

### Optimisations recommandées

1. **Base de données** :
   - Configurer `shared_buffers` et `effective_cache_size`
   - Créer des index sur les colonnes fréquemment utilisées

2. **Nginx** :
   - Activer la compression gzip
   - Configurer le cache des assets statiques

3. **Redis** :
   - Configurer la persistance RDB/AOF
   - Ajuster `maxmemory` selon vos besoins

4. **Application** :
   - Utiliser plusieurs workers (déjà configuré)
   - Implémenter la mise en cache Redis

## 🚨 Dépannage

### Problèmes courants

1. **Port déjà utilisé** :
   ```bash
   sudo lsof -i :80
   sudo kill -9 <PID>
   ```

2. **Base de données non accessible** :
   ```bash
   docker-compose -f docker-compose.prod.yml logs postgres
   ```

3. **Mémoire insuffisante** :
   ```bash
   docker system prune -a
   ```

4. **Certificats SSL** :
   - Vérifier que les fichiers sont dans `./ssl/`
   - Vérifier les permissions (600 pour la clé privée)

### Logs d'erreur

```bash
# Logs système
journalctl -u docker

# Logs de l'application
docker-compose -f docker-compose.prod.yml logs backend

# Logs Nginx
docker-compose -f docker-compose.prod.yml logs nginx
```

## 📞 Support

En cas de problème :

1. Vérifiez les logs : `./monitor.sh`
2. Consultez ce README
3. Vérifiez la configuration Docker
4. Contactez l'équipe de développement

---

**🎉 Votre application ecommerce est maintenant prête pour la production !**
