"""
Service métier pour la gestion du catalogue de produits.

Ce service gère :
- Liste des produits actifs
- Gestion du stock
- Réservation et libération de stock
"""

from typing import List, Optional
from database.models import Product
from database.repositories_simple import PostgreSQLProductRepository


class CatalogService:
    """Service métier pour la gestion du catalogue."""
    
    def __init__(self, product_repo: PostgreSQLProductRepository):
        self.product_repo = product_repo
    
    def list_products(self) -> List[Product]:
        """Récupère tous les produits actifs."""
        return self.product_repo.get_all_active()
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Récupère un produit par son ID."""
        return self.product_repo.get_by_id(product_id)
    
    def reserve_stock(self, product_id: str, quantity: int) -> bool:
        """Réserve du stock pour un produit."""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Produit introuvable")
        
        if product.stock_qty < quantity:
            raise ValueError("Stock insuffisant")
        
        # Réserver le stock
        self.product_repo.reserve_stock(product_id, quantity)
        return True
    
    def release_stock(self, product_id: str, quantity: int) -> bool:
        """Libère du stock pour un produit."""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False
        
        # Libérer le stock
        self.product_repo.release_stock(product_id, quantity)
        return True
    
    def update_stock(self, product_id: str, new_stock: int) -> bool:
        """Met à jour le stock d'un produit."""
        product = self.product_repo.get_by_id(product_id)
        if not product:
            return False
        
        product.stock_qty = new_stock
        self.product_repo.update(product)
        return True
