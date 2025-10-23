# 🚀 Guide d'accès pour Yannis - Site E-commerce

## 🌐 Accès au site web

### URL du site
- **Site principal**: http://localhost
- **API Documentation**: http://localhost/api/docs
- **Health Check**: http://localhost/health

### Comptes de test
- **Admin**: admin@ecommerce.com / admin123
- **Client test**: client@test.com / client123

## 🗄️ Accès à la base de données PostgreSQL

### Informations de connexion
```
Host: localhost
Port: 5432
Database: ecommerce
User: ecommerce
Password: [Voir config.env.production]
```

### Méthodes d'accès

#### 1. Avec psql (recommandé)
```bash
psql -h localhost -p 5432 -U ecommerce -d ecommerce
```

#### 2. Avec Docker
```bash
docker exec -it ecommerce-postgres-prod psql -U ecommerce -d ecommerce
```

#### 3. Avec un client graphique (pgAdmin, DBeaver, etc.)
- Host: localhost
- Port: 5432
- Database: ecommerce
- Username: ecommerce
- Password: [Voir config.env.production]

### Commandes utiles

#### Voir toutes les tables
```sql
\dt
```

#### Voir la structure d'une table
```sql
\d users
\d products
\d orders
```

#### Requêtes utiles
```sql
-- Voir tous les utilisateurs
SELECT * FROM users;

-- Voir tous les produits
SELECT * FROM products;

-- Voir toutes les commandes
SELECT * FROM orders;

-- Statistiques
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_products FROM products;
SELECT COUNT(*) as total_orders FROM orders;
```

## 📊 Monitoring et logs

### Prometheus (métriques)
- URL: http://localhost:9090

### Grafana (dashboards)
- URL: http://localhost:3001
- Login: admin
- Password: [Voir config.env.production]

### Logs de l'application
```bash
# Voir tous les logs
docker-compose -f docker-compose.prod.yml logs -f

# Logs du backend uniquement
docker-compose -f docker-compose.prod.yml logs -f backend

# Logs de la base de données
docker-compose -f docker-compose.prod.yml logs -f postgres
```

## 🔧 Commandes de gestion

### Démarrer l'application
```bash
./deploy_simple.sh
```

### Arrêter l'application
```bash
docker-compose -f docker-compose.prod.yml down
```

### Redémarrer l'application
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Voir le statut des services
```bash
docker-compose -f docker-compose.prod.yml ps
```

### Accès rapide à la base de données
```bash
./access_database.sh
```

## 🛠️ Dépannage

### Si le site n'est pas accessible
1. Vérifier que Docker est démarré
2. Vérifier le statut des conteneurs: `docker-compose -f docker-compose.prod.yml ps`
3. Voir les logs: `docker-compose -f docker-compose.prod.yml logs`

### Si la base de données n'est pas accessible
1. Vérifier que le conteneur PostgreSQL est démarré
2. Tester la connexion: `docker exec ecommerce-postgres-prod pg_isready -U ecommerce -d ecommerce`

### Redémarrage complet
```bash
# Arrêter tout
docker-compose -f docker-compose.prod.yml down

# Nettoyer
docker system prune -f

# Redémarrer
./deploy_simple.sh
```

## 📱 Fonctionnalités disponibles

### Pour les clients
- ✅ Inscription/Connexion
- ✅ Catalogue de produits
- ✅ Panier d'achat
- ✅ Passer commande
- ✅ Paiement simulé
- ✅ Suivi des commandes
- ✅ Support client

### Pour les administrateurs
- ✅ Gestion des produits (CRUD)
- ✅ Validation des commandes
- ✅ Expédition des commandes
- ✅ Gestion des utilisateurs
- ✅ Support client
- ✅ Statistiques

## 🆘 Support

En cas de problème:
1. Vérifier les logs: `docker-compose -f docker-compose.prod.yml logs -f`
2. Vérifier le statut: `docker-compose -f docker-compose.prod.yml ps`
3. Redémarrer si nécessaire: `./deploy_simple.sh`
