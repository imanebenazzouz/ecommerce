# 🛒 E-Commerce Full-Stack

Application e-commerce complète avec backend FastAPI et frontend React, utilisant PostgreSQL comme base de données.

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Docker (optionnel)

### Installation et Démarrage

1. **Cloner le projet**
```bash
git clone <repository-url>
cd ecommerce
```

2. **Démarrer l'application**
```bash
# Démarrer tout (backend + frontend)
./start.sh all

# Ou démarrer séparément
./start.sh backend   # API sur http://localhost:8000
./start.sh frontend  # Frontend sur http://localhost:5173
```

3. **Accéder à l'application**
- Frontend: http://localhost:5173
- API Documentation: http://localhost:8000/docs
- API Health: http://localhost:8000/health

## 📋 Fonctionnalités

### 👤 Gestion des Utilisateurs
- ✅ Inscription avec validation email
- ✅ Connexion/Déconnexion avec JWT
- ✅ Mise à jour du profil
- ✅ Gestion des sessions

### 🛍️ Catalogue Produits
- ✅ Listing des produits actifs
- ✅ Détails des produits
- ✅ Gestion du stock
- ✅ Interface admin pour CRUD

### 🛒 Panier d'Achat
- ✅ Ajout/Suppression d'articles
- ✅ Calcul automatique du total
- ✅ Gestion des quantités
- ✅ Vider le panier

### 📦 Commandes
- ✅ Création de commande depuis le panier
- ✅ Réservation automatique du stock
- ✅ Historique des commandes
- ✅ Annulation par le client

### 💳 Paiement
- ✅ Simulation de paiement par carte
- ✅ Validation des données de carte
- ✅ Gestion des échecs de paiement

### 🏪 Interface Admin
- ✅ Gestion des produits (CRUD)
- ✅ Validation des commandes
- ✅ Expédition des commandes
- ✅ Suivi des livraisons
- ✅ Remboursements

### 📞 Support Client
- ✅ Système de tickets
- ✅ Messagerie client/admin
- ✅ Gestion des statuts

## 🏗️ Architecture

### Backend (FastAPI)
```
ecommerce-backend/
├── api_unified.py          # API principale
├── database/
│   ├── models.py           # Modèles SQLAlchemy
│   ├── database.py         # Configuration DB
│   └── repositories_simple.py  # Repositories
├── services/
│   └── auth_service.py     # Service d'authentification
├── enums.py                # Énumérations
└── init_db.py             # Initialisation DB
```

### Frontend (React + Vite)
```
ecommerce-front/
├── src/
│   ├── components/         # Composants réutilisables
│   ├── pages/             # Pages de l'application
│   ├── contexts/          # Contextes React
│   ├── hooks/             # Hooks personnalisés
│   └── lib/               # Utilitaires
└── public/                # Assets statiques
```

## 🗄️ Base de Données

### Modèles Principaux
- **Users**: Utilisateurs et administrateurs
- **Products**: Catalogue de produits
- **Orders**: Commandes clients
- **OrderItems**: Articles des commandes
- **Carts**: Paniers d'achat
- **Payments**: Paiements
- **Invoices**: Factures
- **MessageThreads**: Tickets de support

### Initialisation
```bash
cd ecommerce-backend
python init_db.py
```

## 🧪 Tests

### Structure des Tests
```
tests/
├── unit/                    # Tests unitaires
│   ├── test_auth.py        # Tests d'authentification
│   ├── test_products.py    # Tests de produits
│   ├── test_cart.py        # Tests de panier
│   ├── test_orders.py      # Tests de commandes
│   ├── test_payments.py    # Tests de paiements
│   ├── test_support.py     # Tests de support
│   └── test_api_endpoints.py # Tests d'endpoints
├── integration/            # Tests d'intégration
├── e2e/                   # Tests end-to-end
│   └── test_final.py      # Test complet de l'application
├── conftest.py            # Configuration commune
└── run_all_tests.py       # Script principal
```

### Exécuter les tests

#### Tous les tests
```bash
python run_all_tests.py
```

#### Par catégorie
```bash
# Tests unitaires uniquement
python tests/run_unit_tests.py

# Tests d'intégration uniquement
python tests/run_integration_tests.py

# Tests end-to-end uniquement
python tests/run_e2e_tests.py
```

#### Avec pytest
```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/

# Tests avec marqueurs
pytest -m unit
pytest -m integration
pytest -m e2e
```

### Tests disponibles
- **Tests unitaires** : Tests des composants individuels
- **Tests d'intégration** : Tests des interactions entre composants
- **Tests end-to-end** : Tests complets de l'application

## 🐳 Déploiement Docker

### Développement
```bash
docker-compose up -d
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Logs
```bash
# Backend
tail -f logs/backend.log

# Frontend
tail -f logs/frontend.log
```

## 🔧 Configuration

### Variables d'environnement
```bash
# Backend (.env)
DATABASE_URL=postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce
SECRET_KEY=your-secret-key
DEBUG=True

# Frontend (.env)
VITE_API_URL=http://localhost:8000
```

## 📚 API Documentation

### Endpoints Principaux

#### Authentification
- `POST /auth/register` - Inscription
- `POST /auth/login` - Connexion
- `GET /auth/me` - Profil utilisateur
- `PUT /auth/profile` - Mise à jour profil

#### Produits
- `GET /products` - Liste des produits
- `GET /products/{id}` - Détail produit

#### Panier
- `GET /cart` - Contenu du panier
- `POST /cart/add` - Ajouter au panier
- `POST /cart/remove` - Retirer du panier
- `DELETE /cart/clear` - Vider le panier

#### Commandes
- `POST /orders/checkout` - Créer commande
- `GET /orders` - Mes commandes
- `GET /orders/{id}` - Détail commande
- `POST /orders/{id}/pay` - Payer commande
- `POST /orders/{id}/cancel` - Annuler commande

#### Admin
- `GET /admin/products` - Gestion produits
- `POST /admin/products` - Créer produit
- `PUT /admin/products/{id}` - Modifier produit
- `DELETE /admin/products/{id}` - Supprimer produit
- `GET /admin/orders` - Toutes les commandes
- `POST /admin/orders/{id}/validate` - Valider commande
- `POST /admin/orders/{id}/ship` - Expédier commande

## 🛡️ Sécurité

- ✅ Hashage des mots de passe (bcrypt)
- ✅ Tokens JWT pour l'authentification
- ✅ Validation des données avec Pydantic
- ✅ CORS configuré
- ✅ Contrôle d'accès admin
- ✅ Protection des routes sensibles

## 📈 Performance

- ✅ Connexions poolées à la base de données
- ✅ Index sur les colonnes fréquemment utilisées
- ✅ Requêtes optimisées
- ✅ Cache des sessions
- ✅ Compression des réponses

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Pour toute question ou problème :
1. Vérifier la documentation API : http://localhost:8000/docs
2. Consulter les logs dans le dossier `logs/`
3. Exécuter les tests pour vérifier l'état du système
4. Ouvrir une issue sur GitHub

---

**Développé avec ❤️ en Python/FastAPI et React**