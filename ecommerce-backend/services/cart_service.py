"""
============================================================
SERVICE PANIER (CART) - LOGIQUE MÉTIER
============================================================

DESCRIPTION :
Ce fichier contient TOUTE la logique métier du panier d'achat.
C'est la "couche service" qui se situe entre l'API (routes HTTP) 
et la base de données (repositories).

RESPONSABILITÉS :
- ✅ Ajouter des produits au panier avec validation du stock
- ✅ Retirer des produits du panier (partiellement ou totalement)
- ✅ Vérifier que les produits existent et sont actifs
- ✅ Calculer le montant total du panier
- ✅ Vider complètement le panier
- ✅ Empêcher la survente (vérification stock disponible)

ARCHITECTURE :
┌─────────────┐
│   API       │  ← Reçoit les requêtes HTTP du frontend
│  (api.py)   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ CartService │  ← LOGIQUE MÉTIER (ce fichier)
│ (ce fichier)│     - Validations
└──────┬──────┘     - Règles de gestion
       │            - Calculs
       ↓
┌─────────────┐
│ Repository  │  ← Accès direct à la base de données
│  (BDD)      │     - Requêtes SQL
└─────────────┘

RÈGLES MÉTIER :
1. Chaque utilisateur a UN SEUL panier (relation 1:1 user ↔ cart)
2. On ne peut ajouter que des produits actifs (active = True)
3. La quantité demandée doit être ≤ stock disponible
4. Le prix est toujours stocké en centimes (ex: 1250 = 12,50€)
5. Le panier est vidé après création d'une commande

EXEMPLE D'UTILISATION :
```python
cart_service = CartService(cart_repo, product_repo)
cart_service.add_to_cart(user_id="abc-123", product_id="xyz-456", quantity=2)
total = cart_service.get_cart_total(user_id="abc-123")
```
============================================================
"""

# ========================================
# IMPORTS - DÉPENDANCES EXTERNES
# ========================================

# typing.Optional : Pour indiquer qu'une valeur peut être None
# Exemple : Optional[Cart] signifie "un objet Cart ou None"
# Améliore la lisibilité et permet au linter de détecter les erreurs
from typing import Optional

# database.models.Cart : Modèle SQLAlchemy représentant la table 'carts'
# Structure : { id, user_id, items: [CartItem, ...] }
# database.models.Product : Modèle SQLAlchemy représentant la table 'products'
# Structure : { id, name, price_cents, stock_qty, active, ... }
from database.models import Cart, Product

# PostgreSQLCartRepository : Classe qui gère l'accès à la table 'carts'
# Méthodes : add_item(), remove_item(), get_by_user_id(), clear()
# PostgreSQLProductRepository : Classe qui gère l'accès à la table 'products'
# Méthodes : get_by_id(), get_all(), reserve_stock(), etc.
from database.repositories_simple import PostgreSQLCartRepository, PostgreSQLProductRepository

# ========================================
# CLASSE PRINCIPALE : CartService
# ========================================
# Cette classe encapsule toute la logique métier du panier
# Elle agit comme un intermédiaire entre l'API et la base de données
# Avantage : Sépare les responsabilités (API = transport, Service = logique, Repository = données)
class CartService:
    """
    Service métier pour la gestion des paniers d'achat.
    
    RÔLE :
    Ce service contient toute la LOGIQUE MÉTIER du panier :
    - Validations des données (quantité > 0, produit existe, stock OK)
    - Calculs (total du panier)
    - Règles de gestion (produit actif, pas de survente)
    
    POURQUOI UN SERVICE ?
    - Sépare la logique métier des routes HTTP (api.py)
    - Rend le code réutilisable (peut être appelé depuis l'API, des tests, des scripts)
    - Facilite les tests unitaires (on peut mocker les repositories)
    - Respecte le principe de responsabilité unique (SRP - Single Responsibility Principle)
    
    EXEMPLE :
    ```python
    # Dans api.py
    @app.post("/cart/add")
    def add_to_cart_route(product_id: str, qty: int, user = Depends(get_current_user)):
        cart_service = CartService(cart_repo, product_repo)
        cart_service.add_to_cart(user.id, product_id, qty)
        return {"ok": True}
    ```
    """
    
    # ========================================
    # CONSTRUCTEUR (__init__)
    # ========================================
    def __init__(self, cart_repo: PostgreSQLCartRepository, product_repo: PostgreSQLProductRepository):
        """
        Initialise le service avec les repositories nécessaires.
        
        PRINCIPE D'INJECTION DE DÉPENDANCES :
        On passe les repositories en paramètres au lieu de les créer dans la classe.
        Avantages :
        - Facilite les tests (on peut injecter des fakes/mocks)
        - Rend le code plus flexible
        - Respecte le principe d'inversion de dépendances (DIP)
        
        Args:
            cart_repo: Repository pour accéder à la table 'carts' et 'cart_items'
                       Fournit les méthodes : add_item(), remove_item(), get_by_user_id(), clear()
            product_repo: Repository pour accéder à la table 'products'
                          Fournit les méthodes : get_by_id(), get_all(), reserve_stock()
        
        EXEMPLE :
        ```python
        cart_repo = PostgreSQLCartRepository(db_session)
        product_repo = PostgreSQLProductRepository(db_session)
        service = CartService(cart_repo, product_repo)
        ```
        """
        # Stocker le repository du panier dans une variable d'instance
        # self.cart_repo sera accessible dans toutes les méthodes de cette classe
        # Type : PostgreSQLCartRepository
        self.cart_repo = cart_repo
        
        # Stocker le repository des produits dans une variable d'instance
        # self.product_repo sera accessible dans toutes les méthodes de cette classe
        # Type : PostgreSQLProductRepository
        # Utilisé pour : vérifier l'existence, le stock et le statut actif des produits
        self.product_repo = product_repo
    
    # ========================================
    # MÉTHODE 1 : AJOUTER AU PANIER
    # ========================================
    def add_to_cart(self, user_id: str, product_id: str, quantity: int = 1) -> bool:
        """
        Ajoute un produit au panier de l'utilisateur avec validations complètes.
        
        FLUX D'EXÉCUTION :
        1. Valider que la quantité est positive (> 0)
        2. Vérifier que le produit existe en base de données
        3. Vérifier que le produit est actif (disponible à la vente)
        4. Vérifier qu'il y a assez de stock disponible
        5. Si toutes les validations passent → ajouter au panier
        
        VALIDATIONS EFFECTUÉES :
        ✅ Quantité > 0 (pas de quantité négative ou nulle)
        ✅ Produit existe dans la table 'products'
        ✅ Produit est actif (product.active = True)
        ✅ Stock suffisant (product.stock_qty >= quantity demandée)
        
        RÈGLE MÉTIER :
        On ne peut JAMAIS ajouter plus que le stock disponible.
        Cela empêche la "survente" (vendre un produit qu'on n'a pas en stock).
        
        Args:
            user_id (str): UUID de l'utilisateur propriétaire du panier
                          Exemple : "550e8400-e29b-41d4-a716-446655440000"
            product_id (str): UUID du produit à ajouter au panier
                             Exemple : "7c9e6679-7425-40de-944b-e07fc1f90ae7"
            quantity (int): Nombre d'unités à ajouter
                           Valeur par défaut : 1 (si non spécifié)
                           Doit être > 0
            
        Returns:
            bool: True si l'ajout a réussi
                  Cette fonction ne retourne jamais False, elle lève une exception en cas d'erreur
            
        Raises:
            ValueError: Si une validation échoue, avec un message explicite :
                       - "Quantité invalide" si quantity <= 0
                       - "Produit introuvable" si le product_id n'existe pas
                       - "Produit inactif" si le produit est archivé/désactivé
                       - "Stock insuffisant" si quantity > stock disponible
        
        EXEMPLE D'UTILISATION :
        ```python
        try:
            # Ajouter 2 unités du produit "abc-123" au panier de l'utilisateur "xyz-789"
            success = cart_service.add_to_cart(
                user_id="xyz-789",
                product_id="abc-123",
                quantity=2
            )
            print("✅ Produit ajouté au panier")
        except ValueError as e:
            print(f"❌ Erreur : {e}")
        ```
        
        GESTION DES ERREURS :
        Si une validation échoue, l'exception ValueError est levée IMMÉDIATEMENT.
        Le reste de la fonction n'est PAS exécuté (principe du fail-fast).
        L'appelant (l'API) doit attraper cette exception avec try/except.
        """
        
        # ===== VALIDATION 1 : QUANTITÉ POSITIVE =====
        # Vérifier que la quantité demandée est strictement positive
        # On refuse les quantités <= 0 (négatives ou nulles)
        # Opérateur <= signifie "inférieur ou égal"
        if quantity <= 0:
            # Si la condition est vraie (quantity <= 0), on lève une exception
            # raise ValueError() : Lève une exception de type ValueError
            # ValueError : Type d'exception pour les valeurs invalides
            # Le message "Quantité invalide" sera affiché à l'utilisateur
            # L'exécution de la fonction s'arrête ICI si cette condition est vraie
            raise ValueError("Quantité invalide")
        
        # ===== VALIDATION 2 : PRODUIT EXISTE =====
        # Appeler le repository des produits pour récupérer le produit depuis la BDD
        # self.product_repo : Repository injecté dans __init__
        # .get_by_id(product_id) : Méthode qui exécute SELECT * FROM products WHERE id = product_id
        # Retourne : Un objet Product si trouvé, None si pas trouvé
        product = self.product_repo.get_by_id(product_id)
        
        # Vérifier si le produit a été trouvé
        # if not product : équivalent à "if product is None" ou "if product == False"
        # not : opérateur de négation (inverse True/False)
        if not product:
            # Le produit n'existe pas en base de données
            # Lever une exception avec un message explicite
            # Cela empêche d'ajouter au panier un produit qui n'existe pas
            raise ValueError("Produit introuvable")
        
        # ===== VALIDATION 3 : PRODUIT ACTIF =====
        # Vérifier que le produit est actif (disponible à la vente)
        # product.active : Attribut boolean de l'objet Product (True ou False)
        # active = True : Produit visible sur le site et achetable
        # active = False : Produit archivé/désactivé (ne doit pas être vendu)
        # if not product.active : "si le produit N'EST PAS actif"
        if not product.active:
            # Le produit est désactivé (archivé par l'admin)
            # On refuse de l'ajouter au panier
            # Exemple : un produit en rupture définitive ou retiré du catalogue
            raise ValueError("Produit inactif")
        
        # ===== VALIDATION 4 : STOCK SUFFISANT =====
        # Vérifier qu'il y a assez de stock pour satisfaire la demande
        # product.stock_qty : Quantité en stock dans la table products (colonne stock_qty)
        # Type : int (nombre entier)
        # Exemple : product.stock_qty = 10 signifie "10 unités en stock"
        # quantity : Quantité demandée par l'utilisateur (paramètre de la fonction)
        # Opérateur < : "strictement inférieur à"
        # Condition : "si stock < quantité demandée"
        if product.stock_qty < quantity:
            # Stock insuffisant : on ne peut pas satisfaire la demande
            # Exemple : stock = 5, quantity = 10 → refuser
            # Cela EMPÊCHE LA SURVENTE (vendre ce qu'on n'a pas en stock)
            # Lever une exception pour informer l'utilisateur
            raise ValueError("Stock insuffisant")
        
        # ===== TOUTES LES VALIDATIONS SONT OK =====
        # Si on arrive ici, TOUTES les validations ont réussi :
        # ✅ Quantité > 0
        # ✅ Produit existe
        # ✅ Produit actif
        # ✅ Stock suffisant
        
        # Ajouter l'article au panier via le repository
        # self.cart_repo : Repository du panier injecté dans __init__
        # .add_item() : Méthode qui ajoute ou incrémente un article dans le panier
        # Si l'article existe déjà → incrémente la quantité
        # Si l'article n'existe pas → crée une nouvelle ligne cart_item
        # Paramètres :
        #   - user_id : UUID de l'utilisateur (pour identifier le panier)
        #   - product_id : UUID du produit à ajouter
        #   - quantity : Nombre d'unités à ajouter
        # Cette méthode effectue un INSERT ou UPDATE dans la table cart_items
        self.cart_repo.add_item(user_id, product_id, quantity)
        
        # Retourner True pour indiquer que l'opération a réussi
        # Type de retour : bool (booléen - True ou False)
        # Dans cette fonction, on retourne TOUJOURS True (jamais False)
        # En cas d'erreur, on lève une exception au lieu de retourner False
        # Principe : "Exceptions pour les erreurs, valeurs de retour pour les succès"
        return True
    
    # ========================================
    # MÉTHODE 2 : RETIRER DU PANIER
    # ========================================
    def remove_from_cart(self, user_id: str, product_id: str, quantity: int = 1) -> bool:
        """
        Retire un produit (ou une quantité) du panier de l'utilisateur.
        
        DEUX COMPORTEMENTS POSSIBLES :
        1. quantity <= 0 → Supprime COMPLÈTEMENT le produit du panier
        2. quantity > 0 → Retire uniquement la quantité spécifiée
        
        EXEMPLES :
        - remove_from_cart(user_id, product_id, 0) → Supprime tout
        - remove_from_cart(user_id, product_id, 2) → Retire 2 unités
        - Si panier contient 5 unités et on retire 2 → il reste 3
        - Si panier contient 5 unités et on retire 5 → le produit est supprimé du panier
        
        Args:
            user_id (str): UUID de l'utilisateur propriétaire du panier
            product_id (str): UUID du produit à retirer
            quantity (int): Quantité à retirer
                           - Si 0 ou négatif → suppression totale
                           - Si positif → retrait de la quantité spécifiée
                           Valeur par défaut : 1
            
        Returns:
            bool: True si le retrait a réussi
                  Cette fonction retourne toujours True
        
        CAS D'USAGE :
        - Bouton "Supprimer" dans le panier → quantity = 0
        - Bouton "-" (décrémenter) → quantity = 1
        - Retirer plusieurs unités → quantity = N
        """
        # Vérifier si on doit supprimer complètement l'article
        # quantity <= 0 : Si la quantité est 0, négative ou non spécifiée pour suppression totale
        # Opérateur <= : inférieur ou égal
        if quantity <= 0:
            # CAS 1 : SUPPRESSION TOTALE
            # Supprimer complètement l'article du panier (toutes les unités)
            # Appel au repository avec quantity = 0 pour indiquer "tout supprimer"
            # self.cart_repo.remove_item() : Méthode qui supprime un article du panier
            # Paramètres :
            #   - user_id : Identifier le panier de l'utilisateur
            #   - product_id : Identifier le produit à supprimer
            #   - 0 : Convention pour dire "supprimer toutes les unités"
            self.cart_repo.remove_item(user_id, product_id, 0)
            
            # Retourner True pour indiquer que l'opération a réussi
            return True
        
        # CAS 2 : RETRAIT PARTIEL
        # Si on arrive ici, c'est que quantity > 0
        # On retire uniquement la quantité spécifiée
        # Exemple : Si panier contient 5 unités et quantity = 2 → il restera 3 unités
        # self.cart_repo.remove_item() : Décrémente la quantité dans cart_items
        # Si la quantité devient 0 après le retrait, l'article est automatiquement supprimé
        self.cart_repo.remove_item(user_id, product_id, quantity)
        
        # Retourner True pour indiquer le succès
        return True
    
    # ========================================
    # MÉTHODE 3 : RÉCUPÉRER LE PANIER
    # ========================================
    def get_cart(self, user_id: str) -> Optional[Cart]:
        """
        Récupère le panier complet d'un utilisateur depuis la base de données.
        
        STRUCTURE DU PANIER RETOURNÉ :
        Cart {
            id: UUID                    # ID unique du panier
            user_id: UUID              # ID de l'utilisateur propriétaire
            items: [CartItem, ...]     # Liste des articles dans le panier
        }
        
        STRUCTURE D'UN CartItem :
        CartItem {
            product_id: UUID           # ID du produit
            quantity: int              # Quantité de ce produit dans le panier
            created_at: datetime       # Date d'ajout au panier
        }
        
        Args:
            user_id (str): UUID de l'utilisateur dont on veut récupérer le panier
            
        Returns:
            Optional[Cart]: - Un objet Cart si l'utilisateur a un panier
                           - None si l'utilisateur n'a jamais créé de panier
                           
                           Optional[Cart] signifie "Cart ou None"
        
        UTILISATION :
        ```python
        cart = cart_service.get_cart("user-123")
        if cart:
            print(f"Le panier contient {len(cart.items)} articles")
            for item in cart.items:
                print(f"- Produit {item.product_id} : {item.quantity} unités")
        else:
            print("Panier vide ou inexistant")
        ```
        
        NOTE TECHNIQUE :
        Cette méthode est un simple "pass-through" vers le repository.
        Elle ne fait pas de transformation des données, juste un appel direct.
        Dans une architecture plus complexe, on pourrait ajouter ici de la logique
        (ex: filtrer les produits inactifs, calculer des prix, etc.)
        """
        # Appeler le repository pour récupérer le panier depuis la BDD
        # self.cart_repo.get_by_user_id() : Exécute une requête SQL du type :
        #   SELECT * FROM carts WHERE user_id = 'user-123'
        #   JOIN cart_items ON cart_items.cart_id = carts.id
        # Retourne : Un objet Cart avec ses items, ou None si pas de panier
        return self.cart_repo.get_by_user_id(user_id)
    
    # ========================================
    # MÉTHODE 4 : VIDER LE PANIER
    # ========================================
    def clear_cart(self, user_id: str) -> bool:
        """
        Vide complètement le panier d'un utilisateur (supprime tous les articles).
        
        QUAND UTILISER CETTE MÉTHODE :
        1. Après qu'une commande a été validée (checkout réussi)
           → Le contenu du panier est transféré dans une commande
           → Le panier doit être vidé pour permettre de nouveaux achats
        
        2. L'utilisateur clique sur le bouton "Vider le panier" dans l'interface
           → Suppression volontaire de tous les articles
        
        DIFFÉRENCE AVEC remove_from_cart :
        - remove_from_cart() : Retire UN produit (ou une quantité)
        - clear_cart() : Supprime TOUS les produits d'un coup
        
        IMPACT EN BASE DE DONNÉES :
        - Supprime toutes les lignes de la table cart_items pour ce panier
        - SQL équivalent : DELETE FROM cart_items WHERE cart_id = (SELECT id FROM carts WHERE user_id = ?)
        - Le panier (table carts) reste, mais est vide (items = [])
        
        Args:
            user_id (str): UUID de l'utilisateur dont on veut vider le panier
            
        Returns:
            bool: True si le vidage a réussi
                  Cette fonction retourne toujours True
        
        EXEMPLE D'UTILISATION :
        ```python
        # Après création d'une commande
        order = order_service.create_order(user_id)
        cart_service.clear_cart(user_id)  # Vider le panier
        ```
        
        SÉCURITÉ :
        Cette méthode ne vérifie PAS l'existence du panier.
        Si l'utilisateur n'a pas de panier, ça ne fait rien (opération idempotente).
        """
        # Appeler le repository pour vider le panier
        # self.cart_repo.clear() : Supprime tous les cart_items du panier
        # Paramètre : user_id pour identifier le panier à vider
        # Opération : DELETE FROM cart_items WHERE cart_id IN (SELECT id FROM carts WHERE user_id = ?)
        self.cart_repo.clear(user_id)
        
        # Retourner True pour indiquer le succès
        # Cette opération ne peut pas "échouer" (même si le panier était déjà vide)
        return True
    
    # ========================================
    # MÉTHODE 5 : CALCULER LE TOTAL DU PANIER
    # ========================================
    def get_cart_total(self, user_id: str) -> int:
        """
        Calcule le montant total du panier en centimes (1€ = 100 centimes).
        
        POURQUOI EN CENTIMES ?
        Les prix sont toujours stockés en centimes pour éviter les problèmes
        d'arrondis avec les nombres décimaux (float).
        Exemple : 12,50€ = 1250 centimes (int)
        
        FORMULE DE CALCUL :
        Total = Σ (prix_unitaire × quantité) pour chaque article
        
        EXEMPLE CONCRET :
        Panier contient :
        - 2 x iPhone 15 à 99999 centimes = 2 × 99999 = 199998 centimes
        - 1 x AirPods à 27999 centimes = 1 × 27999 = 27999 centimes
        - 3 x Câble USB à 1500 centimes = 3 × 1500 = 4500 centimes
        ──────────────────────────────────────────────────────────
        TOTAL = 199998 + 27999 + 4500 = 232497 centimes (2324,97€)
        
        RÈGLE MÉTIER :
        Seuls les produits ACTIFS sont pris en compte dans le calcul.
        Si un produit a été désactivé après ajout au panier, il n'est PAS compté.
        
        Args:
            user_id (str): UUID de l'utilisateur dont on veut calculer le total
            
        Returns:
            int: Montant total en centimes
                - 0 si le panier est vide
                - 0 si l'utilisateur n'a pas de panier
                - Sinon : somme de (prix × quantité) pour tous les articles actifs
        
        UTILISATION :
        ```python
        total_cents = cart_service.get_cart_total("user-123")
        total_euros = total_cents / 100
        print(f"Total du panier : {total_euros:.2f}€")
        ```
        
        PERFORMANCE :
        Cette méthode fait une requête BDD par article du panier (N+1 queries).
        Pour un panier de 5 articles, ça fait 6 requêtes (1 pour le panier + 5 pour les produits).
        Dans une version optimisée, on pourrait faire une seule requête avec JOIN.
        """
        # ÉTAPE 1 : Récupérer le panier de l'utilisateur depuis la BDD
        # cart_repo.get_by_user_id() retourne un objet Cart ou None
        cart = self.cart_repo.get_by_user_id(user_id)
        
        # ÉTAPE 2 : Vérifier si le panier existe et contient des articles
        # Deux conditions à vérifier :
        # 1. not cart : Le panier n'existe pas (l'utilisateur n'a jamais ajouté d'article)
        # 2. not cart.items : Le panier existe mais est vide (items = liste vide [])
        # Opérateur or : "OU logique" - si l'une des conditions est vraie, le bloc s'exécute
        if not cart or not cart.items:
            # Panier vide ou inexistant → Total = 0 centimes (0€)
            # On retourne immédiatement sans faire de calcul
            return 0
        
        # ÉTAPE 3 : Initialiser la variable total à 0
        # Cette variable va accumuler la somme des (prix × quantité)
        # Type : int (nombre entier en centimes)
        total = 0
        
        # ÉTAPE 4 : Parcourir tous les articles du panier
        # for : boucle qui itère sur chaque élément de cart.items
        # item : variable temporaire qui représente un CartItem à chaque itération
        # cart.items : liste de CartItem [CartItem1, CartItem2, CartItem3, ...]
        for item in cart.items:
            # Pour chaque article, on doit :
            # 1. Récupérer les infos du produit (notamment le prix)
            # 2. Vérifier que le produit est actif
            # 3. Calculer prix × quantité
            # 4. Ajouter au total
            
            # Récupérer les informations complètes du produit depuis la table products
            # item.product_id : UUID du produit (ex: "7c9e6679-7425-40de-944b-e07fc1f90ae7")
            # str(item.product_id) : Convertir l'UUID en chaîne de caractères
            # product_repo.get_by_id() : SELECT * FROM products WHERE id = ?
            # Retourne : Un objet Product ou None
            product = self.product_repo.get_by_id(str(item.product_id))
            
            # Vérifier que le produit existe ET est actif
            # Deux conditions avec AND (les deux doivent être vraies) :
            # 1. product : Le produit existe en BDD (not None)
            # 2. product.active : Le produit est actif (active = True)
            # Si un produit a été désactivé, il ne compte PAS dans le total
            if product and product.active:
                # Le produit est valide → on peut l'ajouter au total
                
                # Calculer le sous-total pour cet article
                # product.price_cents : Prix unitaire en centimes (ex: 99999 = 999,99€)
                # item.quantity : Nombre d'unités dans le panier (ex: 2)
                # Opérateur * : multiplication
                # Exemple : 99999 centimes × 2 unités = 199998 centimes
                subtotal = product.price_cents * item.quantity
                
                # Ajouter le sous-total au total global
                # Opérateur += : addition et assignation (équivalent à total = total + subtotal)
                # Exemple : Si total = 50000 et subtotal = 199998 → total devient 249998
                total += subtotal
        
        # ÉTAPE 5 : Retourner le total calculé
        # Après avoir parcouru tous les articles, on retourne la somme finale
        # Type de retour : int (nombre entier en centimes)
        # Si aucun produit n'était actif, total reste à 0
        return total
# FIN DE LA CLASSE CartService
# FIN DU FICHIER cart_service.py
