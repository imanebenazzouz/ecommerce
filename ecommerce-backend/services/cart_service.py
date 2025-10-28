"""
Service métier pour la gestion des paniers.

Ce service gère :
- Ajout/suppression d'articles dans le panier
- Calcul du total du panier
- Validation du stock
- Gestion des quantités
"""

from typing import Optional
from database.models import Cart, Product
from database.repositories_simple import PostgreSQLCartRepository, PostgreSQLProductRepository


class CartService:
    """Service métier pour la gestion des paniers."""
    
    def __init__(self, cart_repo: PostgreSQLCartRepository, product_repo: PostgreSQLProductRepository):
        self.cart_repo = cart_repo
        self.product_repo = product_repo
    
    def add_to_cart(self, user_id: str, product_id: str, quantity: int = 1) -> bool:
        """Ajoute un produit au panier."""
        if quantity <= 0:
            raise ValueError("Quantité invalide")
        
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Produit introuvable")
        
        if not product.active:
            raise ValueError("Produit inactif")
        
        if product.stock_qty < quantity:
            raise ValueError("Stock insuffisant")
        
        # Ajouter au panier
        self.cart_repo.add_item(user_id, product_id, quantity)
        return True
    
    def remove_from_cart(self, user_id: str, product_id: str, quantity: int = 1) -> bool:
        """Retire un produit du panier."""
        if quantity <= 0:
            # Supprimer complètement l'article
            self.cart_repo.remove_item(user_id, product_id, 0)
            return True
        
        # Retirer la quantité spécifiée
        self.cart_repo.remove_item(user_id, product_id, quantity)
        return True
    
    def get_cart(self, user_id: str) -> Optional[Cart]:
        """Récupère le panier d'un utilisateur."""
        return self.cart_repo.get_by_user_id(user_id)
    
    def clear_cart(self, user_id: str) -> bool:
        """Vide le panier d'un utilisateur."""
        self.cart_repo.clear(user_id)
        return True
    
    def get_cart_total(self, user_id: str) -> int:
        """Calcule le total du panier en centimes."""
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart or not cart.items:
            return 0
        
        total = 0
        for item in cart.items:
            product = self.product_repo.get_by_id(str(item.product_id))
            if product and product.active:
                total += product.price_cents * item.quantity
        
        return total
