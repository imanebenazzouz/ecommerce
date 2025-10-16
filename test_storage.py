#!/usr/bin/env python3
"""
Tests pour le stockage persistant
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
sys.path.append(os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

from persistent_storage import PersistentStorage


class TestPersistentStorage(unittest.TestCase):
    """Tests pour le système de stockage persistant"""
    
    def setUp(self):
        """Setup avant chaque test"""
        # Créer un dossier temporaire pour les tests
        self.test_dir = tempfile.mkdtemp()
        self.storage = PersistentStorage(self.test_dir)
    
    def tearDown(self):
        """Cleanup après chaque test"""
        # Supprimer le dossier temporaire
        shutil.rmtree(self.test_dir)
    
    def test_storage_directory_creation(self):
        """Test la création automatique du dossier de stockage"""
        # Créer un nouveau storage dans un dossier qui n'existe pas
        new_test_dir = os.path.join(self.test_dir, "new_storage")
        new_storage = PersistentStorage(new_test_dir)
        
        # Vérifier que le dossier a été créé
        self.assertTrue(os.path.exists(new_test_dir))
    
    def test_save_and_get_item(self):
        """Test la sauvegarde et récupération d'un élément"""
        collection = "test_collection"
        item_id = "item_1"
        item_data = {
            "name": "Test Item",
            "price": 1999,
            "active": True,
            "tags": ["test", "example"]
        }
        
        # Sauvegarder l'élément
        self.storage.save_item(collection, item_id, item_data)
        
        # Récupérer l'élément
        retrieved = self.storage.get_item(collection, item_id)
        
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Test Item")
        self.assertEqual(retrieved["price"], 1999)
        self.assertTrue(retrieved["active"])
        self.assertEqual(retrieved["tags"], ["test", "example"])
    
    def test_get_nonexistent_item(self):
        """Test la récupération d'un élément inexistant"""
        retrieved = self.storage.get_item("nonexistent_collection", "nonexistent_id")
        self.assertIsNone(retrieved)
    
    def test_get_all_items(self):
        """Test la récupération de tous les éléments d'une collection"""
        collection = "products"
        
        # Ajouter plusieurs éléments
        self.storage.save_item(collection, "prod_1", {"name": "Product 1", "price": 1000})
        self.storage.save_item(collection, "prod_2", {"name": "Product 2", "price": 2000})
        self.storage.save_item(collection, "prod_3", {"name": "Product 3", "price": 3000})
        
        # Récupérer tous les éléments
        all_items = self.storage.get_all_items(collection)
        
        self.assertEqual(len(all_items), 3)
        
        # Vérifier que tous les éléments sont présents
        names = [item["name"] for item in all_items]
        self.assertIn("Product 1", names)
        self.assertIn("Product 2", names)
        self.assertIn("Product 3", names)
    
    def test_get_all_items_empty_collection(self):
        """Test la récupération d'éléments d'une collection vide"""
        all_items = self.storage.get_all_items("empty_collection")
        self.assertEqual(len(all_items), 0)
    
    def test_delete_item(self):
        """Test la suppression d'un élément"""
        collection = "test_collection"
        item_id = "item_to_delete"
        item_data = {"name": "To Delete", "value": 123}
        
        # Sauvegarder l'élément
        self.storage.save_item(collection, item_id, item_data)
        
        # Vérifier qu'il existe
        self.assertIsNotNone(self.storage.get_item(collection, item_id))
        
        # Supprimer l'élément
        self.storage.delete_item(collection, item_id)
        
        # Vérifier qu'il n'existe plus
        self.assertIsNone(self.storage.get_item(collection, item_id))
    
    def test_delete_nonexistent_item(self):
        """Test la suppression d'un élément inexistant"""
        # Ne devrait pas lever d'exception
        self.storage.delete_item("nonexistent_collection", "nonexistent_id")
    
    def test_update_item(self):
        """Test la mise à jour d'un élément"""
        collection = "test_collection"
        item_id = "item_to_update"
        original_data = {"name": "Original", "price": 1000, "active": True}
        
        # Sauvegarder l'élément original
        self.storage.save_item(collection, item_id, original_data)
        
        # Mettre à jour avec de nouvelles données
        update_data = {"price": 2000, "active": False}
        self.storage.update_item(collection, item_id, update_data)
        
        # Vérifier la mise à jour
        updated = self.storage.get_item(collection, item_id)
        
        self.assertEqual(updated["name"], "Original")  # Inchangé
        self.assertEqual(updated["price"], 2000)  # Mis à jour
        self.assertFalse(updated["active"])  # Mis à jour
    
    def test_update_nonexistent_item(self):
        """Test la mise à jour d'un élément inexistant"""
        # Ne devrait pas lever d'exception, mais ne devrait rien faire
        self.storage.update_item("nonexistent_collection", "nonexistent_id", {"new": "data"})
    
    def test_multiple_collections(self):
        """Test plusieurs collections séparées"""
        # Données pour différentes collections
        products_data = {
            "prod_1": {"name": "Product 1", "price": 1000},
            "prod_2": {"name": "Product 2", "price": 2000}
        }
        
        users_data = {
            "user_1": {"name": "User 1", "email": "user1@example.com"},
            "user_2": {"name": "User 2", "email": "user2@example.com"}
        }
        
        orders_data = {
            "order_1": {"user_id": "user_1", "total": 1000},
            "order_2": {"user_id": "user_2", "total": 2000}
        }
        
        # Sauvegarder dans différentes collections
        for item_id, item_data in products_data.items():
            self.storage.save_item("products", item_id, item_data)
        
        for item_id, item_data in users_data.items():
            self.storage.save_item("users", item_id, item_data)
        
        for item_id, item_data in orders_data.items():
            self.storage.save_item("orders", item_id, item_data)
        
        # Vérifier que chaque collection est indépendante
        products = self.storage.get_all_items("products")
        users = self.storage.get_all_items("users")
        orders = self.storage.get_all_items("orders")
        
        self.assertEqual(len(products), 2)
        self.assertEqual(len(users), 2)
        self.assertEqual(len(orders), 2)
        
        # Vérifier qu'on ne peut pas récupérer des produits dans la collection users
        self.assertIsNone(self.storage.get_item("users", "prod_1"))
        self.assertIsNone(self.storage.get_item("products", "user_1"))
    
    def test_persistence_across_instances(self):
        """Test que les données persistent entre différentes instances"""
        collection = "persistence_test"
        item_id = "persistent_item"
        item_data = {"name": "Persistent Data", "value": 42}
        
        # Sauvegarder avec la première instance
        self.storage.save_item(collection, item_id, item_data)
        
        # Créer une nouvelle instance avec le même dossier
        new_storage = PersistentStorage(self.test_dir)
        
        # Vérifier que les données sont toujours là
        retrieved = new_storage.get_item(collection, item_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Persistent Data")
        self.assertEqual(retrieved["value"], 42)
    
    def test_complex_data_structures(self):
        """Test avec des structures de données complexes"""
        collection = "complex_data"
        item_id = "complex_item"
        
        complex_data = {
            "user": {
                "id": "user_123",
                "profile": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "address": {
                        "street": "123 Main St",
                        "city": "Paris",
                        "country": "France"
                    }
                },
                "orders": [
                    {"id": "order_1", "items": ["item_a", "item_b"]},
                    {"id": "order_2", "items": ["item_c"]}
                ],
                "preferences": {
                    "language": "fr",
                    "notifications": True,
                    "categories": ["electronics", "books"]
                }
            },
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "version": 1,
                "tags": ["test", "complex", "nested"]
            }
        }
        
        # Sauvegarder les données complexes
        self.storage.save_item(collection, item_id, complex_data)
        
        # Récupérer et vérifier
        retrieved = self.storage.get_item(collection, item_id)
        
        self.assertEqual(retrieved["user"]["id"], "user_123")
        self.assertEqual(retrieved["user"]["profile"]["first_name"], "John")
        self.assertEqual(retrieved["user"]["profile"]["address"]["city"], "Paris")
        self.assertEqual(len(retrieved["user"]["orders"]), 2)
        self.assertEqual(retrieved["user"]["orders"][0]["items"], ["item_a", "item_b"])
        self.assertEqual(retrieved["user"]["preferences"]["language"], "fr")
        self.assertTrue(retrieved["user"]["preferences"]["notifications"])
        self.assertEqual(retrieved["metadata"]["version"], 1)
        self.assertEqual(retrieved["metadata"]["tags"], ["test", "complex", "nested"])
    
    def test_unicode_and_special_characters(self):
        """Test avec des caractères Unicode et spéciaux"""
        collection = "unicode_test"
        item_id = "unicode_item"
        
        unicode_data = {
            "name": "Produit spécial",
            "description": "Description avec des caractères spéciaux: éàçù€£¥",
            "emoji": "🚀🎉💻",
            "accents": "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ",
            "symbols": "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        }
        
        # Sauvegarder les données Unicode
        self.storage.save_item(collection, item_id, unicode_data)
        
        # Récupérer et vérifier
        retrieved = self.storage.get_item(collection, item_id)
        
        self.assertEqual(retrieved["name"], "Produit spécial")
        self.assertEqual(retrieved["description"], "Description avec des caractères spéciaux: éàçù€£¥")
        self.assertEqual(retrieved["emoji"], "🚀🎉💻")
        self.assertEqual(retrieved["accents"], "ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ")
        self.assertEqual(retrieved["symbols"], "!@#$%^&*()_+-=[]{}|;':\",./<>?")
    
    def test_large_dataset(self):
        """Test avec un grand nombre d'éléments"""
        collection = "large_dataset"
        num_items = 100
        
        # Créer beaucoup d'éléments
        for i in range(num_items):
            item_data = {
                "id": f"item_{i}",
                "name": f"Item {i}",
                "price": i * 100,
                "active": i % 2 == 0,
                "tags": [f"tag_{j}" for j in range(i % 5)]
            }
            self.storage.save_item(collection, f"item_{i}", item_data)
        
        # Vérifier que tous les éléments sont sauvegardés
        all_items = self.storage.get_all_items(collection)
        self.assertEqual(len(all_items), num_items)
        
        # Vérifier quelques éléments spécifiques
        item_0 = self.storage.get_item(collection, "item_0")
        self.assertEqual(item_0["name"], "Item 0")
        self.assertEqual(item_0["price"], 0)
        self.assertTrue(item_0["active"])
        
        item_50 = self.storage.get_item(collection, "item_50")
        self.assertEqual(item_50["name"], "Item 50")
        self.assertEqual(item_50["price"], 5000)
        self.assertTrue(item_50["active"])
        
        item_99 = self.storage.get_item(collection, "item_99")
        self.assertEqual(item_99["name"], "Item 99")
        self.assertEqual(item_99["price"], 9900)
        self.assertFalse(item_99["active"])
    
    def test_file_operations_error_handling(self):
        """Test la gestion d'erreurs lors des opérations sur fichiers"""
        # Créer un fichier JSON corrompu
        corrupted_file = os.path.join(self.test_dir, "corrupted.json")
        with open(corrupted_file, 'w') as f:
            f.write("{ invalid json content")
        
        # Essayer de charger une collection avec un fichier corrompu
        # Cela ne devrait pas lever d'exception mais retourner une collection vide
        items = self.storage.get_all_items("corrupted")
        self.assertEqual(len(items), 0)
        
        # Essayer de récupérer un élément d'une collection corrompue
        item = self.storage.get_item("corrupted", "any_id")
        self.assertIsNone(item)


class TestPersistentStorageIntegration(unittest.TestCase):
    """Tests d'intégration pour le stockage persistant"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Cleanup après chaque test"""
        shutil.rmtree(self.test_dir)
    
    def test_real_world_simulation(self):
        """Test une simulation d'usage réel du système ecommerce"""
        storage = PersistentStorage(self.test_dir)
        
        # Simuler la création d'un utilisateur
        user_data = {
            "id": "user_123",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "address": "123 Main St, Paris, France",
            "is_admin": False,
            "created_at": "2024-01-01T00:00:00Z"
        }
        storage.save_item("users", "user_123", user_data)
        
        # Simuler la création de produits
        products_data = [
            {
                "id": "prod_1",
                "name": "T-Shirt Logo",
                "description": "Coton bio",
                "price_cents": 1999,
                "stock_qty": 100,
                "active": True
            },
            {
                "id": "prod_2", 
                "name": "Sweat Capuche",
                "description": "Molleton",
                "price_cents": 4999,
                "stock_qty": 50,
                "active": True
            }
        ]
        
        for product in products_data:
            storage.save_item("products", product["id"], product)
        
        # Simuler une commande
        order_data = {
            "id": "order_456",
            "user_id": "user_123",
            "items": [
                {
                    "product_id": "prod_1",
                    "name": "T-Shirt Logo",
                    "unit_price_cents": 1999,
                    "quantity": 2
                },
                {
                    "product_id": "prod_2",
                    "name": "Sweat Capuche", 
                    "unit_price_cents": 4999,
                    "quantity": 1
                }
            ],
            "status": "PAYEE",
            "total_cents": 8997,  # (2 * 1999) + (1 * 4999)
            "created_at": "2024-01-02T10:30:00Z",
            "paid_at": "2024-01-02T10:35:00Z"
        }
        storage.save_item("orders", "order_456", order_data)
        
        # Simuler un paiement
        payment_data = {
            "id": "payment_789",
            "order_id": "order_456",
            "user_id": "user_123",
            "amount_cents": 8997,
            "provider": "CB",
            "provider_ref": "TXN123456",
            "succeeded": True,
            "created_at": "2024-01-02T10:35:00Z",
            "card_last4": "1234"
        }
        storage.save_item("payments", "payment_789", payment_data)
        
        # Simuler une facture
        invoice_data = {
            "id": "invoice_101",
            "order_id": "order_456",
            "user_id": "user_123",
            "lines": [
                {
                    "product_id": "prod_1",
                    "name": "T-Shirt Logo",
                    "unit_price_cents": 1999,
                    "quantity": 2,
                    "line_total_cents": 3998
                },
                {
                    "product_id": "prod_2",
                    "name": "Sweat Capuche",
                    "unit_price_cents": 4999,
                    "quantity": 1,
                    "line_total_cents": 4999
                }
            ],
            "total_cents": 8997,
            "issued_at": "2024-01-02T10:35:00Z"
        }
        storage.save_item("invoices", "invoice_101", invoice_data)
        
        # Vérifier que toutes les données sont correctement sauvegardées
        user = storage.get_item("users", "user_123")
        self.assertEqual(user["email"], "john@example.com")
        self.assertEqual(user["first_name"], "John")
        
        products = storage.get_all_items("products")
        self.assertEqual(len(products), 2)
        
        order = storage.get_item("orders", "order_456")
        self.assertEqual(order["user_id"], "user_123")
        self.assertEqual(order["total_cents"], 8997)
        self.assertEqual(len(order["items"]), 2)
        
        payment = storage.get_item("payments", "payment_789")
        self.assertEqual(payment["order_id"], "order_456")
        self.assertTrue(payment["succeeded"])
        self.assertEqual(payment["amount_cents"], 8997)
        
        invoice = storage.get_item("invoices", "invoice_101")
        self.assertEqual(invoice["order_id"], "order_456")
        self.assertEqual(invoice["total_cents"], 8997)
        self.assertEqual(len(invoice["lines"]), 2)
        
        # Créer une nouvelle instance pour tester la persistance
        new_storage = PersistentStorage(self.test_dir)
        
        # Vérifier que toutes les données sont toujours là
        self.assertIsNotNone(new_storage.get_item("users", "user_123"))
        self.assertEqual(len(new_storage.get_all_items("products")), 2)
        self.assertIsNotNone(new_storage.get_item("orders", "order_456"))
        self.assertIsNotNone(new_storage.get_item("payments", "payment_789"))
        self.assertIsNotNone(new_storage.get_item("invoices", "invoice_101"))


if __name__ == '__main__':
    print("=== Tests du stockage persistant ===")
    unittest.main(verbosity=2)
