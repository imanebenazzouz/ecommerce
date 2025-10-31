# 🐍 Documentation Backend - E-Commerce API

**Version:** 2.0  
**Date:** Janvier 2025  
**Status:** ✅ Production Ready

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Installation et Configuration](#installation-et-configuration)
3. [Architecture](#architecture)
4. [API Endpoints](#api-endpoints)
5. [Base de Données](#base-de-données)
6. [Services](#services)
7. [Validation](#validation)
8. [Tests](#tests)
9. [Dépannage](#dépannage)

---

## 🎯 Vue d'Ensemble

Le backend est une **API REST FastAPI** qui fournit toutes les fonctionnalités e-commerce :
- Authentification JWT sécurisée
- Gestion des produits, panier, commandes
- Paiements et remboursements
- Support client
- Interface admin

### Technologies

- **Python 3.13** - Langage principal
- **FastAPI 0.115.6** - Framework web moderne
- **PostgreSQL** - Base de données relationnelle
- **SQLAlchemy 2.0.36** - ORM
- **Pydantic 2.10.4** - Validation des données
- **JWT** - Authentification
- **ReportLab** - Génération PDF

---

## 🚀 Installation et Configuration

### Prérequis

- Python 3.8+ (Python 3.13 recommandé)
- PostgreSQL 12+
- Docker & Docker Compose (pour PostgreSQL)

### Installation Rapide

```bash
# 1. Naviguer vers le dossier backend
cd ecommerce-backend

# 2. Créer l'environnement virtuel
python3 -m venv venv

# 3. Activer l'environnement virtuel
source venv/bin/activate  # Linux/Mac
# OU
venv\Scripts\activate     # Windows

# 4. Installer les dépendances
# Pour Python 3.13 (recommandé)
pip install -r requirements_python313.txt

# Pour Python 3.8-3.12
pip install -r requirements.txt

# 5. Configurer PostgreSQL
# Via Docker Compose (le plus simple)
docker-compose up -d postgres

# OU installer PostgreSQL manuellement
# Créer une base de données 'ecommerce'
# User: ecommerce / Password: ecommerce123

# 6. Initialiser la base de données
python init_db.py

# 7. Démarrer l'API
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Configuration Base de Données

Le backend utilise PostgreSQL par défaut. Configuration dans `database/database.py` :

```python
DATABASE_URL = "postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce"
```

Vous pouvez changer via variable d'environnement :
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

### Variables d'Environnement

Créer un fichier `.env` à la racine de `ecommerce-backend/` :

```env
# Base de données
DATABASE_URL=postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce

# Sécurité
SECRET_KEY=your_super_secret_key_change_in_production
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256

# Debug
DEBUG=True

# API
API_HOST=0.0.0.0
API_PORT=8000
```

---

## 🏗️ Architecture

### Structure du Projet

```
ecommerce-backend/
├── api.py                      # 🔥 API principale (2000+ lignes)
├── api_unified.py             # Wrapper vers api.py (compatibilité tests)
├── database/
│   ├── __init__.py
│   ├── models.py              # 📊 Modèles SQLAlchemy
│   ├── database.py            # ⚙️ Configuration DB
│   └── repositories_simple.py # 🔧 Repositories
├── services/
│   ├── __init__.py
│   ├── auth_service.py        # 🔐 Authentification JWT
│   ├── cart_service.py        # 🛒 Logique panier
│   ├── catalog_service.py     # 📦 Catalogue produits
│   ├── order_service.py       # 📋 Logique commandes
│   ├── payment_service.py     # 💳 Paiements
│   ├── billing_service.py     # 🧾 Facturation
│   ├── delivery_service.py    # 🚚 Livraisons
│   ├── customer_service.py    # 👤 Service client
│   └── service_container.py   # 📦 Conteneur de services
├── utils/
│   ├── __init__.py
│   └── validations.py         # ✅ Validations métier
├── enums.py                   # 📝 Énumérations
├── init_db.py                 # 🗄️ Initialisation DB
├── requirements.txt           # Dependencies Python 3.8-3.12
├── requirements_python313.txt # Dependencies Python 3.13 ✅
└── docker-compose.yml         # 🐳 Docker Compose
```

### Architecture en Couches

```
┌─────────────────────────────────────────┐
│         COUCHE API (api.py)             │
│  Endpoints REST FastAPI                 │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       COUCHE SERVICES                   │
│  Logique métier réutilisable            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     COUCHE REPOSITORY                   │
│  Accès aux données (repositories)       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│    COUCHE DONNÉES                       │
│  PostgreSQL via SQLAlchemy              │
└─────────────────────────────────────────┘
```

---

## 📡 API Endpoints

### Authentification

```http
POST   /auth/register          # Inscription utilisateur
POST   /auth/login             # Connexion → token JWT
GET    /auth/me                # Profil utilisateur courant
PUT    /auth/profile           # Mettre à jour le profil
POST   /auth/logout            # Déconnexion
```

### Produits (Public)

```http
GET    /products               # Liste des produits actifs
GET    /products/{id}          # Détails d'un produit
```

### Panier (Authentifié)

```http
GET    /cart                   # Contenu du panier
POST   /cart/add               # Ajouter un produit
POST   /cart/remove            # Retirer un produit
DELETE /cart/clear             # Vider le panier
```

### Commandes (Authentifié)

```http
POST   /orders/checkout        # Créer une commande depuis le panier
GET    /orders                 # Mes commandes
GET    /orders/{id}            # Détails d'une commande
POST   /orders/{id}/pay        # Payer une commande
POST   /orders/{id}/cancel     # Annuler une commande
GET    /orders/{id}/invoice    # Récupérer la facture
GET    /orders/{id}/invoice/download  # Télécharger facture PDF
```

### Admin - Produits

```http
GET    /admin/products         # Liste tous les produits
POST   /admin/products         # Créer un produit
PUT    /admin/products/{id}    # Modifier un produit
DELETE /admin/products/{id}    # Supprimer un produit
```

### Admin - Commandes

```http
GET    /admin/orders           # Toutes les commandes
GET    /admin/orders/{id}      # Détails d'une commande
GET    /admin/orders/{id}/status  # Statut d'une commande
POST   /admin/orders/{id}/validate    # Valider une commande
POST   /admin/orders/{id}/ship        # Expédier une commande
POST   /admin/orders/{id}/mark-delivered  # Marquer comme livrée
POST   /admin/orders/{id}/refund      # Rembourser une commande
```

### Support Client

```http
POST   /support/threads        # Créer un ticket
GET    /support/threads        # Mes tickets
GET    /support/threads/{id}   # Détails d'un ticket
POST   /support/threads/{id}/messages  # Envoyer un message
POST   /support/threads/{id}/mark-read # Marquer comme lu
```

### Admin - Support

```http
GET    /admin/support/threads        # Tous les tickets
GET    /admin/support/threads/{id}   # Détails d'un ticket
POST   /admin/support/threads/{id}/close   # Fermer un ticket
POST   /admin/support/threads/{id}/messages  # Répondre
```

### Santé

```http
GET    /health                 # Vérification de santé
GET    /                       # Point d'entrée API
```

---

## 🗄️ Base de Données

### Modèles Principaux

#### User (Utilisateurs)
```python
id: UUID
email: str (unique)
password_hash: str
first_name: str
last_name: str
address: str
is_admin: bool
created_at: datetime
```

#### Product (Produits)
```python
id: UUID
name: str
description: str
price_cents: int
stock_qty: int
active: bool
created_at: datetime
```

#### Order (Commandes)
```python
id: UUID
user_id: UUID
status: OrderStatus (CREE, PAYEE, VALIDEE, EXPEDIEE, LIVREE, ANNULEE)
created_at: datetime
validated_at: datetime
shipped_at: datetime
delivered_at: datetime
```

#### OrderItem (Articles)
```python
id: UUID
order_id: UUID
product_id: UUID
name: str
unit_price_cents: int
quantity: int
```

#### Payment (Paiements)
```python
id: UUID
order_id: UUID
amount_cents: int
status: str (PENDING, SUCCEEDED, FAILED, REFUNDED)
payment_method: str
card_last_4: str
card_brand: str
postal_code: str
phone: str
street_number: str
street_name: str
created_at: datetime
```

### Relations

- **User** → **Order** (1:N)
- **Order** → **OrderItem** (1:N)
- **Order** → **Payment** (1:N)
- **Product** → **CartItem** (1:N)

### Initialisation

```bash
python init_db.py
```

Ce script :
- Crée toutes les tables
- Crée l'utilisateur admin par défaut
- Ajoute quelques produits de test

---

## 🔧 Services

### AuthService

Gestion de l'authentification JWT.

```python
from services.auth_service import AuthService

# Créer un utilisateur
user = auth_service.register_user(
    email="test@example.com",
    password="secret123",
    first_name="Test",
    last_name="User",
    address="123 Rue Test"
)

# Authentifier
user = auth_service.authenticate_user("test@example.com", "secret123")

# Créer un token
token = auth_service.create_access_token({"sub": str(user.id)})

# Vérifier un token
payload = auth_service.verify_token(token)
```

### Services Métier

Chaque service encapsule la logique métier spécifique :
- **CartService** : Gestion du panier
- **OrderService** : Logique des commandes
- **PaymentService** : Traitement des paiements
- **BillingService** : Génération de factures
- **DeliveryService** : Gestion des livraisons
- **CustomerService** : Support client

---

## ✅ Validation

### Validation des Noms/Prénoms

```python
Règles:
- 2-100 caractères
- Aucun chiffre
- Lettres, espaces, tirets, apostrophes uniquement
- Accents français autorisés (é, è, ê, à, ç, etc.)
```

### Validation des Adresses

```python
Règles:
- Minimum 10 caractères
- Au moins 1 chiffre (numéro ou code postal)
- Au moins 5 lettres (nom de rue, ville)
```

### Validation des Paiements

```python
- Numéro de carte: 13-19 chiffres + Algorithme de Luhn
- CVV: 3-4 chiffres
- Date: MM/YYYY, doit être future
- Code postal: 5 chiffres exactement
- Téléphone: 10 chiffres, commence par 06 ou 07
- Numéro de rue: chiffres uniquement
- Nom de rue: 3-100 caractères
```

---

## 🧪 Tests

### Exécuter les Tests

```bash
# Tous les tests
cd ecommerce-backend
source venv/bin/activate
pytest ../tests/ -v

# Tests unitaires uniquement
pytest ../tests/unit/ -v

# Tests avec couverture
pytest ../tests/ -v --cov=.

# Tests spécifiques
pytest ../tests/ -v -k "test_payment"
```

### Structure des Tests

```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_cart.py
│   ├── test_catalog.py
│   ├── test_orders.py
│   ├── test_payments.py
│   └── test_validations.py
├── integration/
│   └── test_payment_validation.py
└── e2e/
    └── test_final.py
```

---

## 🔧 Dépannage

### Port 8000 déjà utilisé

```bash
# Trouver le processus
lsof -ti:8000 | xargs kill -9
```

### Base de données non accessible

```bash
# Vérifier que PostgreSQL tourne
docker-compose -f ecommerce-backend/docker-compose.yml ps

# Redémarrer PostgreSQL
docker-compose -f ecommerce-backend/docker-compose.yml restart postgres

# Voir les logs
docker-compose -f ecommerce-backend/docker-compose.yml logs -f postgres
```

### Erreurs de dépendances

```bash
# Si Python 3.13
pip install -r requirements_python313.txt

# Si Python < 3.13
pip install -r requirements.txt

# Mettre à jour pip
pip install --upgrade pip
```

### Erreurs de migration

```bash
# Réinitialiser complètement la base
python init_db.py
```

---

## 📚 Ressources

- **Documentation FastAPI**: https://fastapi.tiangolo.com
- **Documentation SQLAlchemy**: https://docs.sqlalchemy.org
- **Documentation Pydantic**: https://docs.pydantic.dev

---

**Backend prêt pour la production !** 🚀

