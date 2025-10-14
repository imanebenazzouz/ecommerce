# E-commerce Application

Une application e-commerce complète avec un backend FastAPI et un frontend React.

## 🏗️ Architecture

- **Backend**: FastAPI (Python) - API REST
- **Frontend**: React + Vite - Interface utilisateur
- **Base de données**: En mémoire (pour la démo)

## 🚀 Démarrage rapide

### Prérequis
- Python 3.8+ avec pip
- Node.js 16+ avec npm

### 1. Démarrer le backend

```bash
# Option 1: Utiliser le script automatique
./start-backend.sh

# Option 2: Manuel
cd ecommerce-backend
pip install -r requirements.txt
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Le backend sera disponible sur : http://localhost:8000
- Documentation API : http://localhost:8000/docs

### 2. Démarrer le frontend

```bash
# Option 1: Utiliser le script automatique
./start-frontend.sh

# Option 2: Manuel
cd ecommerce-front
npm install
npm run dev
```

Le frontend sera disponible sur : http://localhost:5173

## 🔧 Configuration

### Variables d'environnement
Le frontend utilise par défaut `http://localhost:8000` pour l'API. 
Pour changer cela, créez un fichier `.env` dans `ecommerce-front/` :

```
VITE_API_BASE=http://votre-api-url:port
```

## 👥 Comptes de test

L'application crée automatiquement des comptes de test :

- **Admin** : `admin@example.com` / `admin`
- **Client** : `client@example.com` / `secret`

## 📋 Fonctionnalités

### ✅ Authentification
- Inscription utilisateur
- Connexion/Déconnexion
- Gestion des sessions avec JWT

### 🛍️ E-commerce
- Catalogue de produits
- Panier d'achat
- Passage de commande
- Paiement par carte (simulé)

### 🔒 Sécurité
- Authentification Bearer Token
- Validation des données
- Gestion des erreurs

## 🛠️ API Endpoints

### Authentification
- `POST /auth/register` - Inscription
- `POST /auth/login` - Connexion
- `POST /auth/logout` - Déconnexion

### Produits
- `GET /products` - Liste des produits

### Panier
- `GET /cart` - Voir le panier
- `POST /cart/add` - Ajouter au panier
- `POST /cart/remove` - Retirer du panier

### Commandes
- `POST /orders/checkout` - Passer commande
- `POST /orders/{id}/pay` - Payer une commande
- `GET /orders` - Mes commandes

## 🐛 Dépannage

### Problème de CORS
Si vous avez des erreurs CORS, vérifiez que :
1. Le backend est démarré sur le port 8000
2. Le frontend est démarré sur le port 5173
3. Les deux serveurs sont accessibles

### Problème de connexion
1. Vérifiez que les deux serveurs sont démarrés
2. Testez l'API directement : http://localhost:8000
3. Vérifiez la console du navigateur pour les erreurs

## 📝 Notes de développement

- Le backend utilise FastAPI avec Pydantic pour la validation
- Le frontend utilise React avec React Router pour la navigation
- L'authentification utilise des tokens JWT stockés dans localStorage
- Les données sont stockées en mémoire (redémarrage = perte des données)
