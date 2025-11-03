"""
========================================
SERVICE CATALOGUE PRODUITS
========================================

Ce service gère le catalogue de produits et la gestion des stocks.

Responsabilités :
- ✅ Lister les produits disponibles (actifs)
- ✅ Récupérer un produit par son ID
- ✅ Réserver du stock (lors d'un achat)
- ✅ Libérer du stock (si commande annulée)
- ✅ Mettre à jour le stock (admin)

GESTION DU STOCK :
- Reserve : Diminue le stock (lors d'une commande)
- Release : Augmente le stock (si annulation)
- Update : Change le stock à une valeur fixe (admin)
"""

# ========== IMPORTS ==========
from typing import List, Optional  # Pour le typage Python
from database.models import Product  # Modèle SQLAlchemy du produit
from database.repositories_simple import PostgreSQLProductRepository  # Accès BDD

# ========================================
# CLASSE CatalogService
# ========================================
class CatalogService:
    """
    Service métier pour la gestion du catalogue de produits.
    
    Ce service gère :
    - L'affichage des produits sur le site
    - La gestion des stocks (réservation, libération)
    """
    
    def __init__(self, product_repo: PostgreSQLProductRepository):
        """
        Initialise le service avec le repository produits.
        
        Args:
            product_repo: Repository pour accéder à la table products
        """
        self.product_repo = product_repo  # Repository pour accéder aux produits
    
    # ========================================
    # LISTER LES PRODUITS
    # ========================================
    def list_products(self) -> List[Product]:
        """
        Récupère tous les produits actifs (visibles sur le site).
        
        Ne retourne que les produits avec active=True.
        Les produits avec active=False sont cachés (archivés).
        
        Returns:
            Liste de tous les produits actifs
        """
        return self.product_repo.get_all_active()
    
    # ========================================
    # RÉCUPÉRER UN PRODUIT
    # ========================================
    def get_product(self, product_id: str) -> Optional[Product]:
        """
        Récupère un produit spécifique par son ID.
        
        Utilisé pour :
        - Afficher la page détail d'un produit
        - Vérifier le stock avant ajout au panier
        
        Args:
            product_id: ID unique du produit (UUID)
            
        Returns:
            L'objet Product ou None si introuvable
        """
        return self.product_repo.get_by_id(product_id)
    
    # ========================================
    # RÉSERVER DU STOCK
    # ========================================
    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """
        Réserve du stock pour un produit (diminue le stock disponible).
        
        Utilisé lors :
        - De la création d'une commande
        - Du paiement validé
        
        Exemple : Stock = 10, réservation de 2 → Stock devient 8
        
        Args:
            product_id: ID du produit
            quantity: Quantité à réserver
            
        Returns:
            True si réservation réussie
            
        Raises:
            ValueError: Si produit introuvable ou stock insuffisant
        """
        # Vérifier que le produit existe
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Produit introuvable")
        
        # Vérifier qu'il y a assez de stock
        if product.stock_qty < quantity:
            raise ValueError("Stock insuffisant")
        
        # Réserver le stock (stock_qty = stock_qty - quantity)
        self.product_repo.reserve_stock(product_id, quantity)
        return True
    
    # ========================================
    # LIBÉRER DU STOCK
    # ========================================
    def release_stock(self, product_id: str, quantity: int) -> bool:
        """
        Libère du stock pour un produit (augmente le stock disponible).
        
        Utilisé lors :
        - D'une annulation de commande
        - D'un remboursement
        
        Exemple : Stock = 8, libération de 2 → Stock redevient 10
        
        Args:
            product_id: ID du produit
            quantity: Quantité à libérer
            
        Returns:
            True si libération réussie, False si produit introuvable
        """
        # Vérifier que le produit existe
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False  # Produit introuvable
        
        # Libérer le stock (stock_qty = stock_qty + quantity)
        self.product_repo.release_stock(product_id, quantity)
        return True
    
    # ========================================
    # METTRE À JOUR LE STOCK (ADMIN)
    # ========================================
    def update_stock(self, product_id: str, new_stock: int) -> bool:
        """
        Met à jour le stock d'un produit à une valeur fixe.
        
        Utilisé par :
        - L'admin pour corriger le stock
        - Un script de réapprovisionnement
        
        Exemple : Peu importe le stock actuel, on le met à new_stock
        
        Args:
            product_id: ID du produit
            new_stock: Nouvelle valeur du stock
            
        Returns:
            True si mise à jour réussie, False si produit introuvable
        """
        # Vérifier que le produit existe
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False  # Produit introuvable
        
        # Mettre à jour le stock avec la nouvelle valeur
        product.stock_qty = new_stock  # type: ignore
        self.product_repo.update(product)
        return True
