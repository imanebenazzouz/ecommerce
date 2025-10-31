# ⚛️ Documentation Frontend - E-Commerce React

**Version:** 2.0  
**Date:** Janvier 2025  
**Status:** ✅ Production Ready

---

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Installation et Configuration](#installation-et-configuration)
3. [Architecture](#architecture)
4. [Pages](#pages)
5. [Composants](#composants)
6. [API Client](#api-client)
7. [Validation](#validation)
8. [Authentification](#authentification)
9. [Dépannage](#dépannage)

---

## 🎯 Vue d'Ensemble

Le frontend est une **application React 19** moderne qui fournit une interface utilisateur complète pour l'e-commerce :
- Catalogue de produits
- Panier et commandes
- Paiements sécurisés
- Gestion de profil
- Interface admin
- Support client

### Technologies

- **React 19.1.1** - Bibliothèque UI
- **React Router 7.9.4** - Navigation SPA
- **Vite 7.1.7** - Build tool ultra-rapide
- **Vitest** - Tests unitaires
- **CSS3** - Styles personnalisés

---

## 🚀 Installation et Configuration

### Prérequis

- Node.js 16+ (18+ recommandé)
- npm ou yarn

### Installation Rapide

```bash
# 1. Naviguer vers le dossier frontend
cd ecommerce-front

# 2. Installer les dépendances
npm install

# 3. Démarrer le serveur de développement
npm run dev
```

Le frontend sera accessible sur **http://localhost:5173**

### Configuration API

L'URL de l'API est configurée dans `src/lib/api.js` :

```javascript
const API = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
```

Vous pouvez changer via variable d'environnement :
```bash
export VITE_API_BASE="https://api.example.com"
```

### Scripts Disponibles

```bash
npm run dev          # Serveur de développement
npm run build        # Build de production
npm run preview      # Prévisualiser le build
npm run test         # Lancer les tests
npm run test:ui      # Tests avec interface
npm run lint         # Linter ESLint
```

---

## 🏗️ Architecture

### Structure du Projet

```
ecommerce-front/
├── src/
│   ├── pages/              # 📄 21 pages différentes
│   │   ├── Catalog.jsx     # Catalogue produits
│   │   ├── Cart.jsx        # Panier
│   │   ├── Orders.jsx      # Commandes
│   │   ├── Login.jsx       # Connexion
│   │   ├── Register.jsx    # Inscription
│   │   ├── Profile.jsx     # Profil
│   │   ├── Admin.jsx       # Interface admin
│   │   └── ...
│   ├── components/         # 🧩 Composants réutilisables
│   │   ├── Header.jsx      # Header principal
│   │   ├── Footer.jsx      # Footer
│   │   ├── ProtectedRoute.jsx  # Route protégée
│   │   └── PaymentModal.jsx    # Modal de paiement
│   ├── contexts/           # 📦 Contextes React
│   │   ├── AuthContext.jsx      # Contexte authentification
│   │   ├── AuthContextProvider.jsx
│   │   └── AuthProvider.jsx
│   ├── hooks/              # 🎣 Hooks personnalisés
│   │   └── useAuth.js      # Hook d'authentification
│   ├── lib/                # 📚 Utilitaires
│   │   └── api.js          # Client API HTTP
│   ├── utils/              # 🔧 Utilitaires
│   │   └── validations.js  # Validations frontend
│   ├── constants/          # 📝 Constantes
│   │   └── auth.js         # Constantes auth
│   ├── styles/             # 🎨 Styles
│   ├── assets/             # 🖼️ Assets
│   └── main.jsx            # Point d'entrée
├── public/                 # 📦 Assets publics
├── vite.config.js          # Configuration Vite
├── package.json            # Dependencies
└── index.html              # Template HTML
```

### Architecture des États

```
┌─────────────────────────────────────────┐
│      AuthProvider (Context)             │
│  Gestion globale de l'authentification  │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         useAuth (Hook)                  │
│  Interface simple pour l'auth            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       Pages & Components                │
│  Consomment useAuth()                    │
└─────────────────────────────────────────┘
```

---

## 📄 Pages

### Pages Publiques

#### 1. Catalogue (`/`)
- Affichage de tous les produits actifs
- Détails des produits
- Ajout au panier

#### 2. Login (`/login`)
- Formulaire de connexion
- Validation email/mot de passe
- Redirection automatique

#### 3. Register (`/register`)
- Formulaire d'inscription complet
- Validations strictes :
  - Nom/Prénom : lettres uniquement
  - Adresse : avec numéro de rue
  - Email : format valide
  - Mot de passe : min 6 caractères

### Pages Utilisateur (Protégées)

#### 4. Panier (`/cart`)
- Affichage des articles
- Modification des quantités
- Suppression d'articles
- Vider le panier
- Création de commande

#### 5. Commandes (`/orders`)
- Historique des commandes
- Statuts en temps réel
- Filtres

#### 6. Détail Commande (`/orders/:id`)
- Détails complets d'une commande
- Articles commandés
- Informations de paiement
- Téléchargement facture PDF
- Annulation (si autorisée)

#### 7. Profil (`/profile`)
- Informations personnelles
- Modification du profil
- Historique des commandes

#### 8. Support (`/support`)
- Création de tickets
- Envoi de messages
- Suivi des conversations

### Pages Admin (Protégées)

#### 9. Admin (`/admin`)
- Dashboard admin
- Statistiques
- Navigation rapide

#### 10. Détail Commande Admin (`/admin/orders/:id`)
- Gestion des commandes
- Validation / Expédition
- Remboursements

#### 11. Support Admin (`/admin/support`)
- Gestion des tickets
- Réponses aux messages
- Fermeture de tickets

### Pages Informatives

- **FAQ** (`/faq`) - Foire aux questions
- **Livraison** (`/livraison`) - Informations livraison
- **Paiement Sécurisé** (`/paiement-securise`) - Sécurité
- **Garanties** (`/garanties`) - Politique garanties

### Pages Légales

- **CGV** (`/legal/cgv`) - Conditions générales
- **Mentions Légales** (`/legal/mentions-legales`)
- **Confidentialité** (`/legal/confidentialite`)
- **Cookies** (`/legal/cookies`)
- **Rétractation** (`/legal/retractation`)

---

## 🧩 Composants

### Composants Principaux

#### Header
Navigation principale avec :
- Logo
- Liens vers Catalogue, Panier, Commandes
- Menu utilisateur / admin
- Déconnexion

#### Footer
Pied de page avec :
- Liens légaux
- Informations entreprise
- Réseaux sociaux

#### ProtectedRoute
Route protégée qui vérifie :
- Authentification requise
- Rôle admin (optionnel)
- Loading state pendant vérification
- Redirection si non authentifié

```javascript
<ProtectedRoute requireAuth={true} requireAdmin={false}>
  <Orders />
</ProtectedRoute>
```

#### PaymentModal
Modal de paiement sécurisé avec :
- Formulaire complet
- Validations en temps réel
- Algorithme de Luhn
- Messages d'erreur français
- Sanitization automatique

---

## 🌐 API Client

### Client HTTP

Le client API est centralisé dans `src/lib/api.js` :

```javascript
import { api } from './lib/api';

// Authentification
await api.register({ email, password, first_name, last_name, address });
await api.login({ email, password });
await api.logout();
const user = await api.me();

// Produits
const products = await api.listProducts();
const product = await api.getProduct(productId);

// Panier
const cart = await api.viewCart();
await api.addToCart({ product_id, qty: 1 });
await api.removeFromCart({ product_id, qty: 1 });
await api.clearCart();

// Commandes
await api.checkout();
const orders = await api.myOrders();
const order = await api.getOrder(orderId);
await api.cancelOrder(orderId);

// Paiement
await api.payOrder(orderId, { card_number, exp_month, exp_year, cvc });
await api.processPayment({ orderId, cardNumber, ... });

// Admin
await api.adminListProducts();
await api.adminCreateProduct(productData);
await api.adminListOrders();
await api.adminValidateOrder(orderId);
```

### Gestion des Erreurs

Le client API gère automatiquement :
- Conversion des erreurs HTTP en erreurs JavaScript
- Messages d'erreur localisés
- Extraction des détails d'erreur du backend
- Gestion des tokens expirés

---

## ✅ Validation

### Validation des Noms/Prénoms

```javascript
// utils/validations.js
export function validateName(name) {
  if (!name || name.length < 2) return "Le nom doit contenir au moins 2 caractères";
  if (name.length > 100) return "Le nom est trop long (max 100 caractères)";
  if (/\d/.test(name)) return "Le nom ne peut pas contenir de chiffres";
  if (!/^[a-zA-ZÀ-ÿ\s'-]+$/.test(name)) return "Caractères non autorisés";
  return null;
}
```

### Validation des Adresses

```javascript
export function validateAddress(address) {
  if (!address || address.length < 10) {
    return "L'adresse doit contenir au moins 10 caractères";
  }
  if (!/\d/.test(address)) {
    return "L'adresse doit contenir un numéro";
  }
  const letters = address.match(/[a-zA-ZÀ-ÿ]/g)?.length || 0;
  if (letters < 5) {
    return "L'adresse doit contenir au moins 5 lettres";
  }
  return null;
}
```

### Validation des Paiements

Validations complètes pour :
- Numéro de carte (Luhn)
- CVV (3-4 chiffres)
- Date d'expiration (future)
- Code postal (5 chiffres)
- Téléphone (10 chiffres, 06/07)
- Numéro de rue (chiffres)
- Nom de rue (3-100 caractères)

---

## 🔐 Authentification

### Système d'Authentification

#### AuthProvider
Context global qui gère :
- État de l'utilisateur
- Token JWT
- Loading state
- Méthodes login/logout

#### useAuth Hook
Hook simplifié pour accéder à l'auth :

```javascript
import { useAuth } from '../hooks/useAuth';

function MyComponent() {
  const { 
    user,           // Utilisateur courant
    token,          // Token JWT
    loading,        // Loading state
    login,          // Fonction login
    logout,         // Fonction logout
    isAuthenticated,// Vérifier si connecté
    isAdmin         // Vérifier si admin
  } = useAuth();

  if (loading) return <div>Chargement...</div>;
  
  return <div>Bonjour {user?.first_name}</div>;
}
```

### Flux de Connexion

```
1. User entre email/password
   ↓
2. Frontend valide les données
   ↓
3. Frontend envoie POST /auth/login
   ↓
4. Backend vérifie credentials
   ↓
5. Backend retourne token JWT
   ↓
6. Frontend stocke token (localStorage)
   ↓
7. Frontend appelle GET /auth/me
   ↓
8. Frontend stocke user data
   ↓
9. User est connecté
```

### Protection des Routes

```javascript
import ProtectedRoute from '../components/ProtectedRoute';

// Route simple (auth requise)
<ProtectedRoute>
  <Orders />
</ProtectedRoute>

// Route admin
<ProtectedRoute requireAuth={true} requireAdmin={true}>
  <Admin />
</ProtectedRoute>
```

---

## 🧪 Tests

### Exécuter les Tests

```bash
# Tous les tests
npm run test

# Tests avec UI
npm run test:ui

# Tests avec couverture
npm run test:coverage
```

### Structure des Tests

```
src/
├── utils/
│   └── validations.test.js  # Tests de validation
└── ...
```

---

## 🔧 Dépannage

### Port 5173 déjà utilisé

```bash
# Trouver le processus
lsof -ti:5173 | xargs kill -9

# OU utiliser le script
../kill_frontend.sh
```

### Erreur "Failed to fetch"

**Cause:** Le backend n'est pas accessible

**Solution:**
1. Vérifier que le backend tourne sur port 8000
2. Vérifier l'URL de l'API dans `src/lib/api.js`
3. Vérifier les CORS du backend

### Erreurs de dépendances

```bash
# Supprimer node_modules et réinstaller
rm -rf node_modules package-lock.json
npm install
```

### Build de production

```bash
# Créer le build
npm run build

# Prévisualiser le build
npm run preview
```

Le build sera dans le dossier `dist/`

---

## 📚 Ressources

- **Documentation React**: https://react.dev
- **Documentation React Router**: https://reactrouter.com
- **Documentation Vite**: https://vitejs.dev

---

**Frontend prêt pour la production !** 🚀

