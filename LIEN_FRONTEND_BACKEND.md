# 🎯 Comment le Frontend est relié au Backend

> **📖 Récapitulatif ultra-court** : 
> - Le **frontend** (React) appelle le **backend** (FastAPI) via des requêtes HTTP
> - Le client HTTP est dans `ecommerce-front/src/lib/api.js` avec la fonction `request()`
> - Le backend expose des endpoints comme `POST /cart/add` dans `ecommerce-backend/api.py`
> - L'authentification se fait via JWT token stocké dans `localStorage`
> - Pour un exemple concret, voir [Exemple : Ajouter au panier](#-exemple-concret--ajouter-un-produit-au-panier)

---

## Vue d'ensemble

Votre application e-commerce suit l'architecture **Client-Serveur** :
- **Frontend** (React) : Interface utilisateur qui tourne dans le navigateur
- **Backend** (FastAPI) : API REST qui gère la logique métier et la base de données
- **Communication** : Via des requêtes HTTP (GET, POST, PUT, DELETE) avec format JSON

---

## 📑 Table des matières

1. [Architecture de communication](#-architecture-de-communication)
2. [Exemple concret : Ajouter un produit au panier](#-exemple-concret--ajouter-un-produit-au-panier)
3. [Authentification : Le JWT Token](#-authentification--le-jwt-token)
4. [Liste des principaux Endpoints](#️-liste-des-principaux-endpoints)
5. [Sécurité : CORS Configuration](#️-sécurité--cors-configuration)
6. [Exemple complet : Passage de commande](#-exemple-complet--passage-de-commande)
7. [Test d'un endpoint](#-test-dun-endpoint)
8. [Concepts Clés](#-concepts-clés)
9. [Exemple Pratique : Page de Connexion](#-exemple-pratique--page-de-connexion)

---

## 🔗 Architecture de communication

```
┌─────────────────────────────────────────────────────────────┐
│                    NAVIGATEUR (Browser)                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │         FRONTEND REACT (localhost:5173)             │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │    │
│  │  │   Pages      │  │  Components  │  │ Context  │ │    │
│  │  │ (Cart.jsx)   │─→│ (Payment...) │─→│ (Auth)   │ │    │
│  │  └──────┬───────┘  └──────┬───────┘  └────┬─────┘ │    │
│  │         │                 │                 │        │    │
│  │         └─────────────────┴─────────────────┘        │    │
│  │                       ↓                               │    │
│  │  ┌────────────────────────────────────────────┐     │    │
│  │  │          LIB/API.JS (Client HTTP)          │     │    │
│  │  │  - request() : wrapper fetch()              │     │    │
│  │  │  - addToCart() : POST /cart/add             │     │    │
│  │  │  - login() : POST /auth/login               │     │    │
│  │  └──────────────┬─────────────────────────────┘     │    │
│  └─────────────────┼────────────────────────────────────┘    │
└─────────────────────┼────────────────────────────────────────┘
                      │  HTTP Request (JSON + Bearer Token)
                      ↓
┌─────────────────────┼────────────────────────────────────────┐
│                    SERVEUR                                    │
│  ┌─────────────────┼───────────────────────────────┐         │
│  │    BACKEND FASTAPI (localhost:8000)             │         │
│  │          ┌────────────────────┐                 │         │
│  │          │  API.PY (Routes)   │                 │         │
│  │          │  @app.post('/cart') │                │         │
│  │          │  @app.get('/auth/me')│               │         │
│  │          └──────────┬─────────┘                 │         │
│  │                     ↓                            │         │
│  │          ┌────────────────────┐                 │         │
│  │          │   Services         │                 │         │
│  │          │ - auth_service.py  │                 │         │
│  │          │ - cart_service.py  │                 │         │
│  │          └──────────┬─────────┘                 │         │
│  │                     ↓                            │         │
│  │          ┌────────────────────┐                 │         │
│  │          │  Repositories      │                 │         │
│  │          │ - PostgreSQLCart   │                 │         │
│  │          │ - PostgreSQLUser   │                 │         │
│  │          └──────────┬─────────┘                 │         │
│  │                     ↓                            │         │
│  └─────────────────────┼───────────────────────────┘         │
│                        ↓                                      │
│          ┌────────────────────────────┐                      │
│          │   BASE DE DONNÉES (SQLite) │                      │
│          │   - users, products        │                      │
│          │   - orders, cart_items     │                      │
│          └────────────────────────────┘                      │
└───────────────────────────────────────────────────────────────┘
```

---

## 📝 Exemple Concret : Ajouter un produit au panier

Prenons l'exemple **"Ajouter un produit au panier"** pour expliquer le flux complet.

### Étape 1 : L'utilisateur clique sur "Ajouter au panier" dans le Catalogue

```jsx
// fichier: ecommerce-front/src/pages/Catalog.jsx
function Catalog() {
  const handleAddToCart = async (productId) => {
    try {
      // ✅ On appelle la fonction API depuis lib/api.js
      await api.addToCart({ product_id: productId, qty: 1 });
      alert("✅ Produit ajouté au panier !");
    } catch (error) {
      alert("❌ Erreur : " + error.message);
    }
  };
  
  return (
    <button onClick={() => handleAddToCart(product.id)}>
      Ajouter au panier
    </button>
  );
}
```

**Explication** : 
- Le composant `Catalog` appelle `api.addToCart()` fourni par `lib/api.js`
- Cette fonction retourne une **Promise** (opération asynchrone)

---

### Étape 2 : Le client HTTP prépare la requête

```javascript
// fichier: ecommerce-front/src/lib/api.js

// 1️⃣ Définir la fonction addToCart()
async function addToCart({ product_id, qty = 1 }) {
  // 2️⃣ Appeler la fonction générique request()
  return request("/cart/add", {
    method: "POST",                      // Méthode HTTP
    body: JSON.stringify({ product_id, qty }),  // Données converties en JSON
  });
}

// 3️⃣ Fonction générique request() qui fait le vrai travail
async function request(path, init = {}) {
  // Configuration de l'URL
  const API = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";
  
  // Récupération du token JWT depuis localStorage
  const token = getToken();  // Exemple: "eyJhbGc.eyJzdWI.SflKxwRJ"
  
  // Préparation des headers HTTP
  const headers = {
    "Content-Type": "application/json",              // Indique qu'on envoie du JSON
    ...(token ? { Authorization: `Bearer ${token}` } : {}),  // Token d'authentification
  };

  // 4️⃣ Appel HTTP effectif avec fetch() (API native du navigateur)
  const res = await fetch(API + path, {
    credentials: "include",  // Permet les cookies
    ...init,
    headers,
  });

  // 5️⃣ Lecture de la réponse (toujours en JSON)
  let payload = null;
  const text = await res.text();
  if (text) {
    try { 
      payload = JSON.parse(text); 
    } catch { 
      payload = text; 
    }
  }

  // 6️⃣ Gestion des erreurs HTTP
  if (!res.ok) {
    const err = new Error(payload.detail || payload.message || `Erreur ${res.status}`);
    err.status = res.status;
    throw err;
  }
  
  // 7️⃣ Retourner les données au composant
  return payload;
}
```

**Ce qui se passe** :
1. **URL construite** : `http://localhost:8000/cart/add`
2. **Méthode HTTP** : `POST`
3. **Headers** : 
   - `Content-Type: application/json`
   - `Authorization: Bearer eyJhbGc.eyJzdWI.SflKxwRJ`
4. **Body** : `{"product_id": "123e4567-e89b-12d3-a456-426614174000", "qty": 1}`
5. **Envoi** : La requête part vers le serveur

---

### Étape 3 : Le backend FastAPI reçoit la requête

```python
# fichier: ecommerce-backend/api.py

# 1️⃣ Définir l'endpoint /cart/add
@app.post("/cart/add")
def add_to_cart(inp: CartAddIn, u: User = Depends(current_user), db: Session = Depends(get_db)):
    """
    Endpoint pour ajouter un produit au panier.
    
    Paramètres:
    - inp: CartAddIn (contient product_id et qty) - validé automatiquement par Pydantic
    - u: User - Récupéré via Depends(current_user) pour l'authentification
    - db: Session - Connexion à la base de données
    """
    try:
        # 2️⃣ Récupérer les repositories (accès aux données)
        CartRepo = _get_repo_class('PostgreSQLCartRepository')
        ProductRepo = _get_repo_class('PostgreSQLProductRepository')
        cart_repo = CartRepo(db)
        product_repo = ProductRepo(db)
        
        # 3️⃣ Vérifier que le produit existe et est actif
        product_uuid = _uuid_or_raw(inp.product_id)
        product = db.query(Product).filter(Product.id == product_uuid).with_for_update().first()
        
        if not product:
            raise HTTPException(404, f"Produit {inp.product_id} introuvable")
        
        if not product.active:
            raise HTTPException(400, f"Produit {product.name} non disponible")
        
        # 4️⃣ Vérifier le stock disponible
        # ... (logique de vérification du stock) ...
        
        # 5️⃣ Ajouter l'article au panier dans la base de données
        cart_repo.add_item(str(u.id), inp.product_id, inp.qty)
        
        # 6️⃣ Retourner le panier mis à jour
        cart = cart_repo.get_by_user_id(str(u.id))
        return cart.to_dict()
        
    except HTTPException:
        raise  # Re-lancer les erreurs HTTP
    except Exception as e:
        raise HTTPException(500, f"Erreur serveur: {str(e)}")
```

**Authentification automatique** :
```python
# La fonction current_user() est appelée AUTOMATIQUEMENT par FastAPI
def current_user(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    """
    Extrait l'ID utilisateur depuis le token JWT.
    Cette fonction est appelée AVANT add_to_cart() grâce à Depends(current_user).
    """
    # 1. Vérifier que le header Authorization existe
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Token manquant")
    
    # 2. Extraire le token
    token = authorization.split(" ", 1)[1].strip()
    
    # 3. Décoder et vérifier le token JWT
    user_repo = PostgreSQLUserRepository(db)
    auth_service = AuthService(user_repo)
    payload = auth_service.verify_token(token)
    
    # 4. Récupérer l'utilisateur en base
    uid = payload["sub"]
    u = user_repo.get_by_id(uid)
    
    if not u:
        raise HTTPException(401, "Session invalide")
    
    # 5. Retourner l'utilisateur
    return u
```

**Ce qui se passe** :
1. FastAPI **reçoit** la requête POST sur `/cart/add`
2. FastAPI **authentifie** automatiquement l'utilisateur via `current_user()`
3. FastAPI **valide** les données avec Pydantic (`CartAddIn`)
4. La fonction `add_to_cart()` :
   - Vérifie l'existence du produit
   - Vérifie le stock
   - Ajoute l'article au panier dans la DB
   - Retourne le panier mis à jour

---

### Étape 4 : Le frontend reçoit la réponse

```javascript
// Retour dans lib/api.js

// Après await fetch() dans request()
const res = await fetch(API + path, { ... });
const text = await res.text();
const payload = JSON.parse(text);  // Exemple: { items: {...}, total: 5000 }

// Vérification succès (res.ok = true)
if (!res.ok) {
  throw new Error(...);
}

// Retourner les données au composant
return payload;  // { items: {...}, total: 5000 }
```

**Le composant reçoit** :
```json
{
  "items": {
    "123e4567-e89b-12d3-a456-426614174000": {
      "product_id": "123e4567-e89b-12d3-a456-426614174000",
      "quantity": 1
    }
  },
  "total": 4999
}
```

---

### Étape 5 : Mise à jour de l'interface utilisateur

```jsx
// Retour dans Catalog.jsx

const handleAddToCart = async (productId) => {
  try {
    // L'appel API retourne le panier mis à jour
    await api.addToCart({ product_id: productId, qty: 1 });
    
    // ✅ Succès : Afficher un message
    alert("✅ Produit ajouté au panier !");
    
    // Optionnel : Rafraîchir l'état local
    // await reloadCart();
    
  } catch (error) {
    // ❌ Erreur : Afficher le message d'erreur
    alert("❌ Erreur : " + error.message);
  }
};
```

**Le cycle est complet** :
1. ✅ Clic utilisateur
2. ✅ Appel API frontend
3. ✅ Requête HTTP
4. ✅ Authentification backend
5. ✅ Vérifications métier
6. ✅ Mise à jour base de données
7. ✅ Réponse JSON
8. ✅ Mise à jour interface

---

## 🔐 Authentification : Le JWT Token

### Comment le token circule

```
1️⃣ CONNEXION (POST /auth/login)
   Frontend envoie : { "email": "user@example.com", "password": "secret123" }
   Backend retourne : { "access_token": "eyJhbGc...", "token_type": "bearer", "user": {...} }
   
2️⃣ STOCKAGE LOCAL
   Frontend stocke le token dans localStorage
   localStorage.setItem("token", "eyJhbGc...")
   
3️⃣ UTILISATION DANS LES REQUÊTES
   Frontend ajoute automatiquement le header :
   Authorization: Bearer eyJhbGc...
   
4️⃣ VÉRIFICATION BACKEND
   Backend décode et vérifie le token
   Si valide → accès autorisé
   Si invalide → erreur 401 Unauthorized
```

### Exemple de token JWT

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3OCIsImlzX2FkbWluIjpmYWxzZX0.SflKxwRJ
│─────────────────────────││────────────────────────││────────────│
        HEADER                  PAYLOAD              SIGNATURE
       (algorithme)          (données utiles)      (signature)
```

**Payload décodé** :
```json
{
  "sub": "12345678",      // ID utilisateur
  "is_admin": false,      // Rôle
  "exp": 1234567890       // Date d'expiration
}
```

---

## 🗺️ Liste des principaux Endpoints

### Authentification

| Endpoint | Méthode | Frontend (api.js) | Backend (api.py) |
|----------|---------|-------------------|------------------|
| `/auth/register` | POST | `register()` | `register()` |
| `/auth/login` | POST | `login()` | `login()` |
| `/auth/logout` | POST | `logout()` | `logout()` |
| `/auth/me` | GET | `me()` | `current_user_info()` |

### Catalogue (Public)

| Endpoint | Méthode | Frontend | Backend |
|----------|---------|----------|---------|
| `/products` | GET | `listProducts()` | `list_products()` |
| `/products/{id}` | GET | `getProduct(id)` | `get_product(id)` |

### Panier (Authentifié)

| Endpoint | Méthode | Frontend | Backend |
|----------|---------|----------|---------|
| `/cart` | GET | `viewCart()` | `view_cart()` |
| `/cart/add` | POST | `addToCart()` | `add_to_cart()` |
| `/cart/remove` | POST | `removeFromCart()` | `remove_from_cart()` |
| `/cart/clear` | DELETE | `clearCart()` | `clear_cart()` |

### Commandes (Authentifié)

| Endpoint | Méthode | Frontend | Backend |
|----------|---------|----------|---------|
| `/orders/checkout` | POST | `checkout()` | `checkout()` |
| `/orders` | GET | `myOrders()` | `list_orders()` |
| `/orders/{id}` | GET | `getOrder(id)` | `get_order(id)` |
| `/orders/{id}/cancel` | POST | `cancelOrder(id)` | `cancel_order(id)` |
| `/orders/{id}/pay` | POST | `payOrder(id, card)` | `pay_order(id, card)` |

### Administration (Admin uniquement)

| Endpoint | Méthode | Frontend | Backend |
|----------|---------|----------|---------|
| `/admin/products` | GET/POST | `adminListProducts()` | `admin_list_products()` |
| `/admin/products/{id}` | PUT/DELETE | `adminUpdateProduct()` | `admin_update_product()` |
| `/admin/orders` | GET | `adminListOrders()` | `admin_list_orders()` |
| `/admin/orders/{id}` | GET | `adminGetOrder(id)` | `admin_get_order(id)` |

---

## 🛡️ Sécurité : CORS Configuration

### Pourquoi CORS ?

Par défaut, les navigateurs **bloquent** les requêtes entre domaines différents pour la sécurité :
- Frontend : `http://localhost:5173`
- Backend : `http://localhost:8000`

**Sans CORS** : ❌ `Access-Control-Allow-Origin` blocked

### Configuration Backend

```python
# fichier: ecommerce-backend/api.py

from fastapi.middleware.cors import CORSMiddleware

# Liste des origines autorisées
ALLOWED_ORIGINS = [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:3000",   # React dev server
    "http://127.0.0.1:5173",
]

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

**Avec CORS** : ✅ Requêtes autorisées entre frontend et backend

---

## 📊 Exemple complet : Passage de commande

### Flux complet avec toutes les étapes

```
1️⃣ CLIENT SAISIT SES INFORMATIONS
   Cart.jsx → User remplit : Prénom, Nom, Adresse

2️⃣ CLICK "PASSER COMMANDE"
   Cart.jsx → handleCheckout()
   
3️⃣ APPEL API CHECKOUT
   api.js → checkout()
   POST http://localhost:8000/orders/checkout
   Headers: Authorization: Bearer ...
   Body: {} (vide, les infos sont déjà dans le panier)
   
4️⃣ BACKEND CRÉE LA COMMANDE
   api.py → checkout(u: User)
   - Récupère le panier de l'utilisateur
   - Vérifie le stock de chaque article
   - Crée une commande en base (statut: CREE)
   - Retourne: { order_id: "...", total: 4999 }
   
5️⃣ FRONTEND REÇOIT L'ID COMMANDE
   Cart.jsx → { order_id: "abc-123", total_cents: 4999 }
   
6️⃣ OUVERTURE MODAL DE PAIEMENT
   Cart.jsx → setShowPaymentModal(true)
   PaymentModal.jsx → User saisit carte bancaire
   
7️⃣ APPEL API PAIEMENT
   api.js → payOrder(orderId, { card_number, exp_month, exp_year, cvc })
   POST http://localhost:8000/orders/{orderId}/pay
   Body: { card_number: "1234567890123456", exp_month: 12, exp_year: 2025, cvc: "123" }
   
8️⃣ BACKEND TRAITE LE PAIEMENT
   api.py → pay_order(orderId, card)
   - Vérifie que la commande existe et est en statut CREE
   - Simule le paiement (génère un ID transaction)
   - Met à jour la commande (statut: PAYEE)
   - Crée un enregistrement de paiement
   - Génère une facture PDF
   - Envoie un email de confirmation
   - Retourne: { success: true, transaction_id: "tx_123" }
   
9️⃣ FRONTEND CONFIRME LE SUCCÈS
   Cart.jsx → alert("✅ Commande payée avec succès !")
   Cart.jsx → navigate("/orders")  // Redirection vers la liste des commandes
   
🔟 VIDAGE DU PANIER
   backend → Automatiquement vide le panier après checkout réussi
```

---

## 🧪 Test d'un endpoint

### Test manuel avec curl

```bash
# 1. Se connecter
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'

# Réponse:
# {"access_token":"eyJhbGc...","token_type":"bearer"}

# 2. Ajouter au panier (avec le token)
curl -X POST http://localhost:8000/cart/add \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGc..." \
  -d '{"product_id":"123e4567-e89b-12d3-a456-426614174000","qty":1}'

# Réponse:
# {"items":{"123e4567":{"quantity":1}},"total":4999}
```

### Test dans le navigateur (Console DevTools)

```javascript
// Ouvrir la console du navigateur (F12)
// et tester l'API directement

// 1. Se connecter
const loginRes = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'secret123' })
});
const loginData = await loginRes.json();
console.log('Token:', loginData.access_token);

// 2. Ajouter au panier
const cartRes = await fetch('http://localhost:8000/cart/add', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${loginData.access_token}`
  },
  body: JSON.stringify({ product_id: '123e4567-e89b-12d3-a456-426614174000', qty: 1 })
});
const cartData = await cartRes.json();
console.log('Panier:', cartData);
```

---

## 🎓 Concepts Clés

### 1. **Asynchrone / Promesses**

```javascript
// ❌ SYNCHRONE (bloquant, ne marche pas en HTTP)
const result = api.addToCart(productId);
console.log(result);  // undefined !

// ✅ ASYNCHRONE (non-bloquant, avec await)
const result = await api.addToCart(productId);
console.log(result);  // { items: {...}, total: 5000 }
```

### 2. **Gestion d'erreurs**

```javascript
// Frontend doit TOUJOURS gérer les erreurs
try {
  await api.addToCart(productId);
} catch (error) {
  if (error.status === 401) {
    // Token expiré → rediriger vers login
    navigate('/login');
  } else if (error.status === 400) {
    // Erreur métier → afficher message
    alert(error.message);
  } else {
    // Erreur serveur → afficher erreur générique
    alert('Erreur serveur, veuillez réessayer');
  }
}
```

### 3. **État local vs État serveur**

```javascript
// Frontend garde un état local pour UX
const [cart, setCart] = useState(null);

// MAIS le backend est la source de vérité
async function reloadCart() {
  const freshCart = await api.getCart();  // Toujours récupérer depuis le serveur
  setCart(freshCart);
}
```

### 4. **Optimistic Updates**

```javascript
// Mise à jour optimiste : afficher le résultat avant la réponse serveur
function inc(productId) {
  // 1. Mise à jour immédiate de l'UI
  const newCart = { ...cart };
  newCart.items[productId].quantity += 1;
  setCart(newCart);  // ✅ UI mise à jour instantanément
  
  // 2. Envoi au serveur en arrière-plan
  api.addToCart({ product_id: productId, qty: 1 })
    .catch(error => {
      // En cas d'erreur, restaurer l'ancien état
      setCart(cart);
      alert('Erreur: ' + error.message);
    });
}
```

---

## 🔧 Configuration Environnement

### Frontend (.env)

```bash
# fichier: ecommerce-front/.env
VITE_API_BASE=http://localhost:8000
```

### Backend (config)

```python
# fichier: ecommerce-backend/api.py
API = import.meta.env.VITE_API_BASE ?? "http://localhost:8000"
```

### Ports par défaut

- **Frontend** : `http://localhost:5173` (Vite)
- **Backend** : `http://localhost:8000` (FastAPI)
- **Base de données** : `ecommerce.db` (SQLite)

---

## 📚 Ressources pour aller plus loin

- [React Documentation](https://react.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [JWT.io (décoder les tokens)](https://jwt.io/)
- [MDN Web Docs - Fetch API](https://developer.mozilla.org/fr/docs/Web/API/Fetch_API)

---

## 🎯 Récapitulatif

| Étape | Frontend | Backend |
|-------|----------|---------|
| **Langage** | JavaScript (React) | Python (FastAPI) |
| **Communication** | HTTP + JSON | HTTP + JSON |
| **Authentification** | Token JWT dans localStorage | Vérification JWT dans headers |
| **Client HTTP** | `lib/api.js` (wrapper fetch) | FastAPI routes |
| **Validation données** | Validation JavaScript (optionnel) | Pydantic (automatique) |
| **Base de données** | Aucun accès direct | SQLAlchemy + PostgreSQL/SQLite |
| **CORS** | Nécessaire pour appeler backend | Middleware CORS configuré |

---

## 🎬 Exemple Pratique : Page de Connexion

Voici comment la page de **connexion** fonctionne de bout en bout :

### Frontend : Login.jsx

```jsx
// ecommerce-front/src/pages/Login.jsx
import { api } from '../lib/api';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      // 1️⃣ Appel API de connexion
      const { token, user } = await api.login({ email, password });
      
      // 2️⃣ Mise à jour du contexte d'authentification
      await login(user, token);
      
      // 3️⃣ Redirection selon le rôle
      if (user.is_admin) {
        navigate('/admin');
      } else {
        navigate('/');
      }
      
    } catch (error) {
      alert('Erreur de connexion : ' + error.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input 
        type="email" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)} 
      />
      <input 
        type="password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)} 
      />
      <button type="submit">Se connecter</button>
    </form>
  );
}
```

### Flux API : api.login()

```javascript
// ecommerce-front/src/lib/api.js

async function login({ email, password }) {
  // 1. Envoi POST vers /auth/login
  const response = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  
  // 2. Le backend retourne { access_token, token_type, user }
  const token = response.access_token;
  setToken(token);  // ✅ Stockage dans localStorage
  
  // 3. Récupération des infos utilisateur complètes
  let user = null;
  try { 
    user = await me();  // GET /auth/me
  } catch (error) {
    // Si erreur, déconnexion automatique
    setToken(null);
    throw new Error('Erreur d\'authentification');
  }
  
  // 4. Retourne { token, user }
  return { token, user };
}
```

### Backend : POST /auth/login

```python
# ecommerce-backend/api.py

@app.post("/auth/login")
def login(inp: LoginIn, db: Session = Depends(get_db)):
    """
    Endpoint de connexion utilisateur.
    Retourne un JWT token si les identifiants sont corrects.
    """
    # 1. Récupérer le repository utilisateur
    user_repo = PostgreSQLUserRepository(db)
    auth_service = AuthService(user_repo)
    
    # 2. Vérifier les identifiants
    user = auth_service.authenticate(inp.email, inp.password)
    
    if not user:
        raise HTTPException(401, "Email ou mot de passe incorrect")
    
    # 3. Générer un token JWT
    token = auth_service.create_token(str(user.id))
    
    # 4. Retourner le token + infos utilisateur
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin,
        }
    }
```

### Context d'authentification : AuthProvider

```jsx
// ecommerce-front/src/contexts/AuthProvider.jsx

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Au chargement de l'application, vérifier si un token existe
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
          setToken(storedToken);
          // Vérifier si le token est encore valide
          const userData = await api.me();  // GET /auth/me
          setUser(userData);
        }
      } catch {
        // Token invalide, déconnexion automatique
        clearAuth();
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = async (userData, tokenData) => {
    setUser(userData);
    setToken(tokenData);
    localStorage.setItem('token', tokenData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const value = {
    user,
    token,
    login,
    logout,
    isAuthenticated: () => !!user && !!token,
    isAdmin: () => user?.is_admin === true,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Hook personnalisé : useAuth

```jsx
// ecommerce-front/src/hooks/useAuth.js
import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
}

// Utilisation dans n'importe quel composant :
function MonComposant() {
  const { user, isAuthenticated, isAdmin } = useAuth();
  
  if (!isAuthenticated()) {
    return <div>Veuillez vous connecter</div>;
  }
  
  return (
    <div>
      Bonjour {user.first_name} {user.last_name} !
      {isAdmin() && <div>Vous êtes admin</div>}
    </div>
  );
}
```

**Résultat** : Toute l'application React a accès à l'état d'authentification via `useAuth()` ! 🎉

---

**🎉 Vous comprenez maintenant comment le frontend et le backend communiquent !**

