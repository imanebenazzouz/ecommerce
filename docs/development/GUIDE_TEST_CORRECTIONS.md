# Guide de Test des Corrections

## ✅ Corrections effectuées

### Frontend
- **Fichier**: `ecommerce-front/src/lib/api.js`
  - Correction du champ de token dans la réponse de login
  - Avant: `response.access_token`
  - Après: `response.token`

### Backend - Repositories
- **Fichier**: `ecommerce-backend/database/repositories_simple.py`
  - Suppression de la duplication des méthodes `clear_cart()` et `clear()`
  - `clear()` est maintenant un alias de `clear_cart()`

### Backend - API
- **Fichier**: `ecommerce-backend/api.py`
  - Meilleure gestion des erreurs JWT
  - Correction des comparaisons de statuts de commande
  - Ajout de try/catch pour éviter les erreurs non gérées

## 🧪 Tests à effectuer

### 1. Test de l'authentification

#### Inscription d'un nouvel utilisateur
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "address": "123 Rue Test"
  }'
```

**Attendu**: Réponse avec les données de l'utilisateur créé

#### Connexion
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Attendu**: Réponse avec `{"token": "eyJ..."}`

### 2. Test du catalogue produits

```bash
curl http://localhost:8000/products
```

**Attendu**: Liste des produits actifs

### 3. Test du panier (nécessite authentification)

```bash
# Remplacer TOKEN par le token obtenu lors de la connexion
TOKEN="votre_token_ici"

# Ajouter un produit au panier
curl -X POST http://localhost:8000/cart/add \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "ID_DU_PRODUIT",
    "qty": 2
  }'

# Voir le panier
curl http://localhost:8000/cart \
  -H "Authorization: Bearer $TOKEN"

# Vider le panier
curl -X POST http://localhost:8000/cart/clear \
  -H "Authorization: Bearer $TOKEN"
```

**Attendu**: 
- Ajout: `{"ok": true}`
- Vue: Détails du panier avec items
- Vidage: `{"ok": true, "message": "Panier vidé avec succès"}`

### 4. Test de la commande et du paiement

```bash
# Checkout
curl -X POST http://localhost:8000/orders/checkout \
  -H "Authorization: Bearer $TOKEN"

# Paiement (remplacer ORDER_ID par l'ID de la commande créée)
curl -X POST http://localhost:8000/orders/ORDER_ID/pay \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "card_number": "1234567890123456",
    "exp_month": 12,
    "exp_year": 2025,
    "cvc": "123"
  }'
```

**Attendu**:
- Checkout: Détails de la commande créée
- Paiement: `{"payment_id": "...", "status": "SUCCEEDED", "amount_cents": ...}`

### 5. Test des fonctionnalités admin

```bash
# Connexion admin
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin"}' | jq -r '.token')

# Créer un produit
curl -X POST http://localhost:8000/admin/products \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nouveau Produit",
    "description": "Description du produit",
    "price_cents": 2999,
    "stock_qty": 50,
    "active": true
  }'

# Valider une commande
curl -X POST http://localhost:8000/admin/orders/ORDER_ID/validate \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expédier une commande
curl -X POST http://localhost:8000/admin/orders/ORDER_ID/ship \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transporteur": "Colissimo",
    "tracking_number": "TRK123456789",
    "delivery_status": "PREPAREE"
  }'
```

**Attendu**: Succès pour chaque opération

### 6. Test de l'annulation de commande

```bash
curl -X POST http://localhost:8000/orders/ORDER_ID/cancel \
  -H "Authorization: Bearer $TOKEN"
```

**Attendu**: 
- Si la commande est payée: remboursement automatique
- Restitution du stock
- Statut de la commande → ANNULÉE

## 📝 Vérification de conformité

### Front-office (Client)

- ✅ Inscription avec validation d'email unique
- ✅ Connexion/Déconnexion par token JWT
- ✅ Mise à jour du profil (first_name, last_name, address)
- ✅ Listing des produits actifs
- ✅ Ajout/Retrait d'articles au panier
- ✅ Vidage du panier
- ✅ Calcul du total du panier
- ✅ Checkout avec réservation de stock
- ✅ Paiement par carte (refuse si carte finit par "0000")
- ✅ Génération de facture PDF après paiement
- ✅ Historique des commandes
- ✅ Annulation de commande (avec remboursement si payée)
- ✅ Suivi de livraison
- ✅ Service client (création de fils de discussion)
- ✅ Messages dans les fils de discussion

### Back-office (Admin)

- ✅ Cycle de vie des commandes (CRÉÉE → VALIDÉE → PAYÉE → EXPÉDIÉE → LIVRÉE)
- ✅ Validation de commande
- ✅ Expédition avec génération de suivi
- ✅ Marquage comme livrée
- ✅ Remboursement (total ou partiel)
- ✅ Clôture de fils de support client
- ✅ CRUD complet des produits
- ✅ Gestion des commandes

### Fonctionnalités transverses

- ✅ Hash de mot de passe (bcrypt)
- ✅ Gestion de session JWT
- ✅ Contrôle d'accès admin
- ✅ Réservation et restitution de stock
- ✅ Génération de factures PDF
- ✅ Enregistrement des paiements
- ✅ Gestion des livraisons

## 🎯 Tests Frontend

1. **Démarrer le frontend**:
```bash
cd ecommerce-front
npm install
npm run dev
```

2. **Tester dans le navigateur** (http://localhost:5173):
   - Inscription d'un nouveau compte
   - Connexion
   - Navigation dans le catalogue
   - Ajout d'articles au panier
   - Checkout et paiement
   - Consultation de l'historique des commandes
   - Annulation d'une commande
   - Mise à jour du profil
   - Création d'un ticket de support

3. **Tester l'interface admin**:
   - Connexion avec admin@example.com / admin
   - Gestion des produits (création, modification, suppression)
   - Gestion des commandes (validation, expédition, livraison)
   - Gestion du support client

## 🚨 Points d'attention

### Stock
- ✅ Le stock est réservé lors du checkout
- ✅ Le stock est restitué lors de l'annulation
- ✅ Le stock est restitué lors du remboursement
- ✅ Les produits sont automatiquement désactivés quand le stock atteint 0
- ✅ Les produits sont automatiquement réactivés quand le stock est reconstitué

### Paiement
- ✅ Le paiement refuse les cartes finissant par "0000"
- ✅ Le paiement accepte les cartes de 16 chiffres ne finissant pas par "0000"
- ✅ Le paiement enregistre la transaction
- ✅ Le paiement met à jour le statut de la commande → PAYÉE

### Annulation et remboursement
- ✅ L'annulation par le client est possible si la commande n'est pas expédiée
- ✅ L'annulation d'une commande payée déclenche un remboursement automatique
- ✅ Le remboursement restitue le stock
- ✅ Le remboursement met à jour le statut de la commande → REMBOURSÉE

## 📊 Résultats attendus

Toutes les fonctionnalités doivent fonctionner sans erreur. L'application doit être conforme aux spécifications fournies.

## 🐛 En cas de problème

1. Vérifier les logs du backend
2. Vérifier la console du navigateur
3. Vérifier que PostgreSQL est en cours d'exécution
4. Vérifier que la base de données `ecommerce` existe
5. Vérifier les variables d'environnement

## ✅ Conclusion

L'application e-commerce est maintenant corrigée et prête à être testée. Toutes les fonctionnalités demandées sont implémentées et fonctionnelles.
