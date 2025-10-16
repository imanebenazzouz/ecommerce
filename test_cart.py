#!/usr/bin/env python3
"""
Tests pour la gestion du panier
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

from backend_demo import (
    Product, Cart, CartItem, CartRepository, CartService, ProductRepository
)
import uuid


class TestCartItem(unittest.TestCase):
    """Tests pour l'entité CartItem"""
    
    def test_create_cart_item(self):
        """Test la création d'un article de panier"""
        product_id = str(uuid.uuid4())
        cart_item = CartItem(product_id=product_id, quantity=3)
        
        self.assertEqual(cart_item.product_id, product_id)
        self.assertEqual(cart_item.quantity, 3)


class TestCart(unittest.TestCase):
    """Tests pour l'entité Cart"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.user_id = str(uuid.uuid4())
        self.cart = Cart(user_id=self.user_id)
        self.product_repo = ProductRepository()
        
        # Créer des produits de test
        self.product1 = Product(
            id=str(uuid.uuid4()),
            name="Product 1",
            description="Test product 1",
            price_cents=1000,
            stock_qty=100,
            active=True
        )
        
        self.product2 = Product(
            id=str(uuid.uuid4()),
            name="Product 2",
            description="Test product 2",
            price_cents=2000,
            stock_qty=50,
            active=True
        )
        
        self.inactive_product = Product(
            id=str(uuid.uuid4()),
            name="Inactive Product",
            description="Inactive test product",
            price_cents=1500,
            stock_qty=25,
            active=False
        )
        
        self.product_repo.add(self.product1)
        self.product_repo.add(self.product2)
        self.product_repo.add(self.inactive_product)
    
    def test_empty_cart(self):
        """Test un panier vide"""
        self.assertEqual(len(self.cart.items), 0)
        self.assertEqual(self.cart.total_cents(self.product_repo), 0)
    
    def test_add_product_to_cart(self):
        """Test l'ajout d'un produit au panier"""
        self.cart.add(self.product1, 3)
        
        self.assertEqual(len(self.cart.items), 1)
        self.assertIn(self.product1.id, self.cart.items)
        self.assertEqual(self.cart.items[self.product1.id].quantity, 3)
    
    def test_add_same_product_multiple_times(self):
        """Test l'ajout du même produit plusieurs fois"""
        self.cart.add(self.product1, 2)
        self.cart.add(self.product1, 3)
        
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.items[self.product1.id].quantity, 5)
    
    def test_add_inactive_product(self):
        """Test l'ajout d'un produit inactif"""
        with self.assertRaises(ValueError) as context:
            self.cart.add(self.inactive_product, 1)
        
        self.assertIn("Produit inactif", str(context.exception))
        self.assertEqual(len(self.cart.items), 0)
    
    def test_add_insufficient_stock(self):
        """Test l'ajout avec stock insuffisant"""
        with self.assertRaises(ValueError) as context:
            self.cart.add(self.product1, 150)  # Plus que le stock disponible (100)
        
        self.assertIn("Stock insuffisant", str(context.exception))
        self.assertEqual(len(self.cart.items), 0)
    
    def test_add_zero_quantity(self):
        """Test l'ajout avec quantité zéro"""
        with self.assertRaises(ValueError) as context:
            self.cart.add(self.product1, 0)
        
        self.assertIn("Quantité invalide", str(context.exception))
        self.assertEqual(len(self.cart.items), 0)
    
    def test_add_negative_quantity(self):
        """Test l'ajout avec quantité négative"""
        with self.assertRaises(ValueError) as context:
            self.cart.add(self.product1, -1)
        
        self.assertIn("Quantité invalide", str(context.exception))
        self.assertEqual(len(self.cart.items), 0)
    
    def test_remove_from_cart(self):
        """Test la suppression d'un produit du panier"""
        self.cart.add(self.product1, 5)
        self.cart.remove(self.product1.id, 2)
        
        self.assertEqual(self.cart.items[self.product1.id].quantity, 3)
    
    def test_remove_more_than_in_cart(self):
        """Test la suppression de plus que ce qui est dans le panier"""
        self.cart.add(self.product1, 3)
        self.cart.remove(self.product1.id, 5)
        
        # Le produit devrait être complètement retiré
        self.assertNotIn(self.product1.id, self.cart.items)
    
    def test_remove_zero_quantity(self):
        """Test la suppression avec quantité zéro (supprime complètement)"""
        self.cart.add(self.product1, 3)
        self.cart.remove(self.product1.id, 0)
        
        # Le produit devrait être complètement retiré
        self.assertNotIn(self.product1.id, self.cart.items)
    
    def test_remove_nonexistent_product(self):
        """Test la suppression d'un produit non présent dans le panier"""
        # Ne devrait pas lever d'exception
        self.cart.remove("nonexistent-product-id", 1)
        self.assertEqual(len(self.cart.items), 0)
    
    def test_clear_cart(self):
        """Test le vidage du panier"""
        self.cart.add(self.product1, 2)
        self.cart.add(self.product2, 3)
        
        self.assertEqual(len(self.cart.items), 2)
        
        self.cart.clear()
        
        self.assertEqual(len(self.cart.items), 0)
    
    def test_cart_total(self):
        """Test le calcul du total du panier"""
        self.cart.add(self.product1, 2)  # 2 * 1000 = 2000 cents
        self.cart.add(self.product2, 1)  # 1 * 2000 = 2000 cents
        
        total = self.cart.total_cents(self.product_repo)
        self.assertEqual(total, 4000)  # 40.00€
    
    def test_cart_total_with_inactive_product(self):
        """Test le calcul du total avec un produit devenu inactif"""
        self.cart.add(self.product1, 2)
        self.cart.add(self.product2, 1)
        
        # Désactiver un produit
        self.product1.active = False
        
        total = self.cart.total_cents(self.product_repo)
        self.assertEqual(total, 2000)  # Seulement product2 (2000 cents)
    
    def test_cart_total_with_nonexistent_product(self):
        """Test le calcul du total avec un produit inexistant"""
        self.cart.add(self.product1, 2)
        
        # Modifier l'ID du produit pour simuler un produit supprimé
        self.product1.id = "new-id"
        
        total = self.cart.total_cents(self.product_repo)
        self.assertEqual(total, 0)


class TestCartRepository(unittest.TestCase):
    """Tests pour le repository du panier"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.repo = CartRepository()
        self.user_id = str(uuid.uuid4())
    
    def test_get_or_create_cart(self):
        """Test la récupération ou création d'un panier"""
        cart = self.repo.get_or_create(self.user_id)
        
        self.assertEqual(cart.user_id, self.user_id)
        self.assertEqual(len(cart.items), 0)
    
    def test_get_existing_cart(self):
        """Test la récupération d'un panier existant"""
        # Créer un panier
        cart1 = self.repo.get_or_create(self.user_id)
        cart1.add(Product(
            id=str(uuid.uuid4()),
            name="Test Product",
            description="Test",
            price_cents=1000,
            stock_qty=100
        ), 2)
        
        # Récupérer le même panier
        cart2 = self.repo.get_or_create(self.user_id)
        
        # Vérifier que c'est le même objet
        self.assertEqual(cart1.user_id, cart2.user_id)
        self.assertEqual(len(cart2.items), 1)
    
    def test_clear_cart(self):
        """Test le vidage d'un panier"""
        cart = self.repo.get_or_create(self.user_id)
        
        # Ajouter des articles
        cart.add(Product(
            id=str(uuid.uuid4()),
            name="Test Product",
            description="Test",
            price_cents=1000,
            stock_qty=100
        ), 2)
        
        self.assertEqual(len(cart.items), 1)
        
        # Vider le panier
        self.repo.clear(self.user_id)
        
        # Récupérer le panier
        cleared_cart = self.repo.get_or_create(self.user_id)
        self.assertEqual(len(cleared_cart.items), 0)
    
    def test_multiple_users_carts(self):
        """Test des paniers pour plusieurs utilisateurs"""
        user1_id = str(uuid.uuid4())
        user2_id = str(uuid.uuid4())
        
        cart1 = self.repo.get_or_create(user1_id)
        cart2 = self.repo.get_or_create(user2_id)
        
        # Vérifier que ce sont des paniers différents
        self.assertNotEqual(cart1, cart2)
        self.assertEqual(cart1.user_id, user1_id)
        self.assertEqual(cart2.user_id, user2_id)


class TestCartService(unittest.TestCase):
    """Tests pour le service du panier"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.cart_repo = CartRepository()
        self.product_repo = ProductRepository()
        self.cart_service = CartService(self.cart_repo, self.product_repo)
        self.user_id = str(uuid.uuid4())
        
        # Créer des produits de test
        self.product1 = Product(
            id=str(uuid.uuid4()),
            name="Service Product 1",
            description="Test product for service",
            price_cents=1000,
            stock_qty=100,
            active=True
        )
        
        self.product2 = Product(
            id=str(uuid.uuid4()),
            name="Service Product 2",
            description="Another test product",
            price_cents=2000,
            stock_qty=50,
            active=True
        )
        
        self.product_repo.add(self.product1)
        self.product_repo.add(self.product2)
    
    def test_add_to_cart(self):
        """Test l'ajout d'un produit au panier via le service"""
        self.cart_service.add_to_cart(self.user_id, self.product1.id, 3)
        
        cart = self.cart_service.view_cart(self.user_id)
        self.assertEqual(len(cart.items), 1)
        self.assertEqual(cart.items[self.product1.id].quantity, 3)
    
    def test_add_to_cart_nonexistent_product(self):
        """Test l'ajout d'un produit inexistant"""
        with self.assertRaises(ValueError) as context:
            self.cart_service.add_to_cart(self.user_id, "nonexistent-id", 1)
        
        self.assertIn("Produit introuvable", str(context.exception))
    
    def test_remove_from_cart(self):
        """Test la suppression d'un produit du panier via le service"""
        # Ajouter d'abord
        self.cart_service.add_to_cart(self.user_id, self.product1.id, 5)
        
        # Puis supprimer
        self.cart_service.remove_from_cart(self.user_id, self.product1.id, 2)
        
        cart = self.cart_service.view_cart(self.user_id)
        self.assertEqual(cart.items[self.product1.id].quantity, 3)
    
    def test_view_cart(self):
        """Test la visualisation du panier"""
        # Ajouter des produits
        self.cart_service.add_to_cart(self.user_id, self.product1.id, 2)
        self.cart_service.add_to_cart(self.user_id, self.product2.id, 1)
        
        cart = self.cart_service.view_cart(self.user_id)
        
        self.assertEqual(cart.user_id, self.user_id)
        self.assertEqual(len(cart.items), 2)
        self.assertEqual(cart.items[self.product1.id].quantity, 2)
        self.assertEqual(cart.items[self.product2.id].quantity, 1)
    
    def test_cart_total(self):
        """Test le calcul du total via le service"""
        self.cart_service.add_to_cart(self.user_id, self.product1.id, 2)  # 2000 cents
        self.cart_service.add_to_cart(self.user_id, self.product2.id, 1)  # 2000 cents
        
        total = self.cart_service.cart_total(self.user_id)
        self.assertEqual(total, 4000)  # 40.00€
    
    def test_empty_cart_total(self):
        """Test le total d'un panier vide"""
        total = self.cart_service.cart_total(self.user_id)
        self.assertEqual(total, 0)
    
    def test_add_default_quantity(self):
        """Test l'ajout avec quantité par défaut"""
        self.cart_service.add_to_cart(self.user_id, self.product1.id)
        
        cart = self.cart_service.view_cart(self.user_id)
        self.assertEqual(cart.items[self.product1.id].quantity, 1)
    
    def test_remove_default_quantity(self):
        """Test la suppression avec quantité par défaut"""
        self.cart_service.add_to_cart(self.user_id, self.product1.id, 3)
        self.cart_service.remove_from_cart(self.user_id, self.product1.id)
        
        cart = self.cart_service.view_cart(self.user_id)
        self.assertEqual(cart.items[self.product1.id].quantity, 2)


class TestCartIntegration(unittest.TestCase):
    """Tests d'intégration pour le panier"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.cart_repo = CartRepository()
        self.product_repo = ProductRepository()
        self.cart_service = CartService(self.cart_repo, self.product_repo)
        self.user_id = str(uuid.uuid4())
    
    def test_complete_cart_workflow(self):
        """Test un workflow complet du panier"""
        # Créer des produits
        product1 = Product(
            id=str(uuid.uuid4()),
            name="Workflow Product 1",
            description="Product for workflow test",
            price_cents=1500,
            stock_qty=20,
            active=True
        )
        
        product2 = Product(
            id=str(uuid.uuid4()),
            name="Workflow Product 2",
            description="Another workflow product",
            price_cents=2500,
            stock_qty=15,
            active=True
        )
        
        self.product_repo.add(product1)
        self.product_repo.add(product2)
        
        # 1. Panier vide
        cart = self.cart_service.view_cart(self.user_id)
        self.assertEqual(len(cart.items), 0)
        self.assertEqual(self.cart_service.cart_total(self.user_id), 0)
        
        # 2. Ajouter des produits
        self.cart_service.add_to_cart(self.user_id, product1.id, 2)
        self.cart_service.add_to_cart(self.user_id, product2.id, 1)
        
        # 3. Vérifier le contenu
        cart = self.cart_service.view_cart(self.user_id)
        self.assertEqual(len(cart.items), 2)
        self.assertEqual(cart.items[product1.id].quantity, 2)
        self.assertEqual(cart.items[product2.id].quantity, 1)
        
        # 4. Vérifier le total
        total = self.cart_service.cart_total(self.user_id)
        expected_total = (2 * 1500) + (1 * 2500)  # 5500 cents
        self.assertEqual(total, expected_total)
        
        # 5. Modifier les quantités
        self.cart_service.add_to_cart(self.user_id, product1.id, 1)  # Maintenant 3
        self.cart_service.remove_from_cart(self.user_id, product2.id, 1)  # Supprimer product2
        
        # 6. Vérifier les modifications
        cart = self.cart_service.view_cart(self.user_id)
        self.assertEqual(len(cart.items), 1)  # Seulement product1
        self.assertEqual(cart.items[product1.id].quantity, 3)
        
        # 7. Vérifier le nouveau total
        new_total = self.cart_service.cart_total(self.user_id)
        self.assertEqual(new_total, 3 * 1500)  # 4500 cents
        
        # 8. Vider le panier
        self.cart_service.remove_from_cart(self.user_id, product1.id, 3)
        
        # 9. Vérifier que le panier est vide
        cart = self.cart_service.view_cart(self.user_id)
        self.assertEqual(len(cart.items), 0)
        self.assertEqual(self.cart_service.cart_total(self.user_id), 0)


if __name__ == '__main__':
    print("=== Tests du panier ===")
    unittest.main(verbosity=2)
