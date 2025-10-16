#!/usr/bin/env python3
"""
Tests pour la gestion des produits
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

from backend_demo import (
    Product, ProductRepository, CatalogService
)
import uuid


class TestProduct(unittest.TestCase):
    """Tests pour l'entité Product"""
    
    def test_create_product(self):
        """Test la création d'un produit"""
        product = Product(
            id=str(uuid.uuid4()),
            name="Test Product",
            description="A test product",
            price_cents=1999,  # 19.99€
            stock_qty=100,
            active=True
        )
        
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.description, "A test product")
        self.assertEqual(product.price_cents, 1999)
        self.assertEqual(product.stock_qty, 100)
        self.assertTrue(product.active)
        self.assertIsNotNone(product.id)
    
    def test_product_default_active(self):
        """Test que le produit est actif par défaut"""
        product = Product(
            id=str(uuid.uuid4()),
            name="Test Product",
            description="A test product",
            price_cents=1000,
            stock_qty=50
        )
        
        self.assertTrue(product.active)


class TestProductRepository(unittest.TestCase):
    """Tests pour le repository des produits"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.repo = ProductRepository()
    
    def test_add_product(self):
        """Test l'ajout d'un produit"""
        product = Product(
            id=str(uuid.uuid4()),
            name="Test Product",
            description="A test product",
            price_cents=1999,
            stock_qty=100
        )
        
        self.repo.add(product)
        
        # Vérifier que le produit est récupérable
        retrieved = self.repo.get(product.id)
        self.assertEqual(retrieved.id, product.id)
        self.assertEqual(retrieved.name, product.name)
        self.assertEqual(retrieved.price_cents, product.price_cents)
        self.assertEqual(retrieved.stock_qty, product.stock_qty)
    
    def test_get_nonexistent_product(self):
        """Test la récupération d'un produit inexistant"""
        self.assertIsNone(self.repo.get("nonexistent-id"))
    
    def test_list_active_products(self):
        """Test la liste des produits actifs"""
        # Créer des produits actifs et inactifs
        active_product1 = Product(
            id=str(uuid.uuid4()),
            name="Active Product 1",
            description="Active product",
            price_cents=1000,
            stock_qty=50,
            active=True
        )
        
        active_product2 = Product(
            id=str(uuid.uuid4()),
            name="Active Product 2",
            description="Another active product",
            price_cents=2000,
            stock_qty=25,
            active=True
        )
        
        inactive_product = Product(
            id=str(uuid.uuid4()),
            name="Inactive Product",
            description="Inactive product",
            price_cents=1500,
            stock_qty=10,
            active=False
        )
        
        self.repo.add(active_product1)
        self.repo.add(active_product2)
        self.repo.add(inactive_product)
        
        # Récupérer les produits actifs
        active_products = self.repo.list_active()
        
        # Vérifier qu'on a seulement les produits actifs
        self.assertEqual(len(active_products), 2)
        product_ids = [p.id for p in active_products]
        self.assertIn(active_product1.id, product_ids)
        self.assertIn(active_product2.id, product_ids)
        self.assertNotIn(inactive_product.id, product_ids)
    
    def test_reserve_stock(self):
        """Test la réservation de stock"""
        product = Product(
            id=str(uuid.uuid4()),
            name="Stock Product",
            description="Product for stock tests",
            price_cents=1000,
            stock_qty=100
        )
        
        self.repo.add(product)
        
        # Réserver du stock
        self.repo.reserve_stock(product.id, 30)
        
        # Vérifier que le stock a diminué
        updated_product = self.repo.get(product.id)
        self.assertEqual(updated_product.stock_qty, 70)
    
    def test_reserve_stock_insufficient(self):
        """Test la réservation de stock insuffisant"""
        product = Product(
            id=str(uuid.uuid4()),
            name="Low Stock Product",
            description="Product with low stock",
            price_cents=1000,
            stock_qty=10
        )
        
        self.repo.add(product)
        
        # Essayer de réserver plus que disponible
        with self.assertRaises(ValueError) as context:
            self.repo.reserve_stock(product.id, 50)
        
        self.assertIn("Stock insuffisant", str(context.exception))
        
        # Vérifier que le stock n'a pas changé
        unchanged_product = self.repo.get(product.id)
        self.assertEqual(unchanged_product.stock_qty, 10)
    
    def test_reserve_nonexistent_product(self):
        """Test la réservation de stock pour un produit inexistant"""
        with self.assertRaises(ValueError) as context:
            self.repo.reserve_stock("nonexistent-id", 10)
        
        self.assertIn("Stock insuffisant", str(context.exception))
    
    def test_release_stock(self):
        """Test la libération de stock"""
        product = Product(
            id=str(uuid.uuid4()),
            name="Release Stock Product",
            description="Product for release tests",
            price_cents=1000,
            stock_qty=50
        )
        
        self.repo.add(product)
        
        # Libérer du stock
        self.repo.release_stock(product.id, 20)
        
        # Vérifier que le stock a augmenté
        updated_product = self.repo.get(product.id)
        self.assertEqual(updated_product.stock_qty, 70)
    
    def test_release_stock_nonexistent_product(self):
        """Test la libération de stock pour un produit inexistant"""
        # Ne devrait pas lever d'exception
        self.repo.release_stock("nonexistent-id", 10)
    
    def test_multiple_stock_operations(self):
        """Test plusieurs opérations de stock"""
        product = Product(
            id=str(uuid.uuid4()),
            name="Multi Stock Product",
            description="Product for multiple stock operations",
            price_cents=1000,
            stock_qty=100
        )
        
        self.repo.add(product)
        
        # Réserver 30
        self.repo.reserve_stock(product.id, 30)
        self.assertEqual(self.repo.get(product.id).stock_qty, 70)
        
        # Libérer 10
        self.repo.release_stock(product.id, 10)
        self.assertEqual(self.repo.get(product.id).stock_qty, 80)
        
        # Réserver 20
        self.repo.reserve_stock(product.id, 20)
        self.assertEqual(self.repo.get(product.id).stock_qty, 60)


class TestCatalogService(unittest.TestCase):
    """Tests pour le service catalogue"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.product_repo = ProductRepository()
        self.catalog_service = CatalogService(self.product_repo)
    
    def test_list_products(self):
        """Test la liste des produits du catalogue"""
        # Créer des produits
        product1 = Product(
            id=str(uuid.uuid4()),
            name="Catalogue Product 1",
            description="First catalogue product",
            price_cents=1000,
            stock_qty=50,
            active=True
        )
        
        product2 = Product(
            id=str(uuid.uuid4()),
            name="Catalogue Product 2",
            description="Second catalogue product",
            price_cents=2000,
            stock_qty=25,
            active=True
        )
        
        inactive_product = Product(
            id=str(uuid.uuid4()),
            name="Inactive Catalogue Product",
            description="Inactive catalogue product",
            price_cents=1500,
            stock_qty=10,
            active=False
        )
        
        self.product_repo.add(product1)
        self.product_repo.add(product2)
        self.product_repo.add(inactive_product)
        
        # Récupérer les produits du catalogue
        catalog_products = self.catalog_service.list_products()
        
        # Vérifier qu'on a seulement les produits actifs
        self.assertEqual(len(catalog_products), 2)
        product_ids = [p.id for p in catalog_products]
        self.assertIn(product1.id, product_ids)
        self.assertIn(product2.id, product_ids)
        self.assertNotIn(inactive_product.id, product_ids)
    
    def test_empty_catalog(self):
        """Test un catalogue vide"""
        products = self.catalog_service.list_products()
        self.assertEqual(len(products), 0)
    
    def test_catalog_with_mixed_products(self):
        """Test un catalogue avec des produits mixtes"""
        # Créer plusieurs produits avec différents statuts
        products_data = [
            ("Active Product 1", True, 1000),
            ("Active Product 2", True, 2000),
            ("Inactive Product 1", False, 1500),
            ("Active Product 3", True, 3000),
            ("Inactive Product 2", False, 2500),
        ]
        
        for name, active, price in products_data:
            product = Product(
                id=str(uuid.uuid4()),
                name=name,
                description=f"Description for {name}",
                price_cents=price,
                stock_qty=50,
                active=active
            )
            self.product_repo.add(product)
        
        # Récupérer les produits actifs
        active_products = self.catalog_service.list_products()
        
        # Vérifier qu'on a seulement les 3 produits actifs
        self.assertEqual(len(active_products), 3)
        active_names = [p.name for p in active_products]
        self.assertIn("Active Product 1", active_names)
        self.assertIn("Active Product 2", active_names)
        self.assertIn("Active Product 3", active_names)
        self.assertNotIn("Inactive Product 1", active_names)
        self.assertNotIn("Inactive Product 2", active_names)


class TestProductBusinessLogic(unittest.TestCase):
    """Tests pour la logique métier des produits"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.repo = ProductRepository()
    
    def test_price_precision(self):
        """Test la précision des prix en centimes"""
        # Prix avec centimes
        product = Product(
            id=str(uuid.uuid4()),
            name="Precision Product",
            description="Product with precise pricing",
            price_cents=1999,  # 19.99€
            stock_qty=1
        )
        
        self.repo.add(product)
        retrieved = self.repo.get(product.id)
        self.assertEqual(retrieved.price_cents, 1999)
    
    def test_zero_price(self):
        """Test un produit gratuit"""
        free_product = Product(
            id=str(uuid.uuid4()),
            name="Free Product",
            description="A free product",
            price_cents=0,
            stock_qty=100
        )
        
        self.repo.add(free_product)
        retrieved = self.repo.get(free_product.id)
        self.assertEqual(retrieved.price_cents, 0)
    
    def test_zero_stock(self):
        """Test un produit sans stock"""
        out_of_stock = Product(
            id=str(uuid.uuid4()),
            name="Out of Stock Product",
            description="Product with no stock",
            price_cents=1000,
            stock_qty=0
        )
        
        self.repo.add(out_of_stock)
        
        # Essayer de réserver du stock
        with self.assertRaises(ValueError):
            self.repo.reserve_stock(out_of_stock.id, 1)
    
    def test_large_stock(self):
        """Test avec un grand stock"""
        large_stock_product = Product(
            id=str(uuid.uuid4()),
            name="Large Stock Product",
            description="Product with large stock",
            price_cents=1000,
            stock_qty=10000
        )
        
        self.repo.add(large_stock_product)
        
        # Réserver une grande quantité
        self.repo.reserve_stock(large_stock_product.id, 5000)
        
        updated = self.repo.get(large_stock_product.id)
        self.assertEqual(updated.stock_qty, 5000)


if __name__ == '__main__':
    print("=== Tests des produits ===")
    unittest.main(verbosity=2)
