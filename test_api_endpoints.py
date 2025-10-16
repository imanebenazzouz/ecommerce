#!/usr/bin/env python3
"""
Tests pour les endpoints API
"""

import unittest
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

from fastapi.testclient import TestClient
from api import app
from backend_demo import (
    OrderStatus
)
import uuid
import time


class TestAPIEndpoints(unittest.TestCase):
    """Tests pour les endpoints API"""
    
    @classmethod
    def setUpClass(cls):
        """Setup de classe - une fois pour tous les tests"""
        cls.client = TestClient(app)

        # Créer des données de test via l'API pour utiliser les mêmes repositories
        cls.setup_test_data()
    
    @classmethod
    def setup_test_data(cls):
        """Créer les données de test via l'API"""
        # Utiliser l'admin par défaut créé par l'API
        admin_login_resp = cls.client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "admin"
        })
        assert admin_login_resp.status_code == 200, admin_login_resp.text
        cls.admin_token = admin_login_resp.json()["token"]

        # Créer un utilisateur régulier via l'API
        register_resp = cls.client.post("/auth/register", json={
            "email": "user@test.com",
            "password": "userpass",
            "first_name": "Regular",
            "last_name": "User",
            "address": "User Address"
        })
        assert register_resp.status_code == 200, register_resp.text
        cls.regular_user = register_resp.json()

        user_login_resp = cls.client.post("/auth/login", json={
            "email": "user@test.com",
            "password": "userpass"
        })
        assert user_login_resp.status_code == 200, user_login_resp.text
        cls.user_token = user_login_resp.json()["token"]

        # Créer des produits via l'API admin
        headers_admin = {"Authorization": f"Bearer {cls.admin_token}"}
        create1 = cls.client.post("/admin/products", json={
            "name": "Test Product 1",
            "description": "First test product",
            "price_cents": 1000,
            "stock_qty": 100,
            "active": True
        }, headers=headers_admin)
        assert create1.status_code == 201, create1.text
        cls.test_product1 = create1.json()

        create2 = cls.client.post("/admin/products", json={
            "name": "Test Product 2",
            "description": "Second test product",
            "price_cents": 2000,
            "stock_qty": 50,
            "active": True
        }, headers=headers_admin)
        assert create2.status_code == 201, create2.text
        cls.test_product2 = create2.json()
    
    def setUp(self):
        """Setup avant chaque test"""
        # Rafraîchir les tokens avant chaque test (évite les tokens invalidés)
        admin_login_resp = self.client.post("/auth/login", json={
            "email": "admin@example.com",
            "password": "admin"
        })
        self.admin_token = admin_login_resp.json()["token"]
        user_login_resp = self.client.post("/auth/login", json={
            "email": "user@test.com",
            "password": "userpass"
        })
        self.user_token = user_login_resp.json()["token"]
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}
        self.user_headers = {"Authorization": f"Bearer {self.user_token}"}
    
    def test_root_endpoint(self):
        """Test l'endpoint racine"""
        response = self.client.get("/")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "Ecommerce API is running!")
        self.assertEqual(data["version"], "1.0")
    
    def test_register_endpoint(self):
        """Test l'endpoint d'inscription"""
        new_user_data = {
            "email": "newuser@test.com",
            "password": "newpass123",
            "first_name": "New",
            "last_name": "User",
            "address": "New User Address"
        }
        
        response = self.client.post("/auth/register", json=new_user_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], "newuser@test.com")
        self.assertEqual(data["first_name"], "New")
        self.assertEqual(data["last_name"], "User")
        self.assertFalse(data["is_admin"])
        self.assertIsNotNone(data["id"])
    
    def test_register_duplicate_email(self):
        """Test l'inscription avec un email déjà utilisé"""
        duplicate_user_data = {
            "email": "user@test.com",  # Email déjà utilisé
            "password": "newpass123",
            "first_name": "Duplicate",
            "last_name": "User",
            "address": "Duplicate Address"
        }
        
        response = self.client.post("/auth/register", json=duplicate_user_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("email", str(data))
    
    def test_login_endpoint(self):
        """Test l'endpoint de connexion"""
        login_data = {
            "email": "user@test.com",
            "password": "userpass"
        }
        
        response = self.client.post("/auth/login", json=login_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertIsNotNone(data["token"])
    
    def test_login_invalid_credentials(self):
        """Test la connexion avec des identifiants invalides"""
        invalid_login_data = {
            "email": "user@test.com",
            "password": "wrongpassword"
        }
        
        response = self.client.post("/auth/login", json=invalid_login_data)
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("detail", data)
    
    def test_me_endpoint(self):
        """Test l'endpoint pour récupérer le profil utilisateur"""
        response = self.client.get("/auth/me", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["email"], "user@test.com")
        self.assertEqual(data["first_name"], "Regular")
        self.assertEqual(data["last_name"], "User")
        self.assertFalse(data["is_admin"])
    
    def test_me_endpoint_without_token(self):
        """Test l'endpoint me sans token"""
        response = self.client.get("/auth/me")
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertIn("Token manquant", data["detail"])
    
    def test_me_endpoint_invalid_token(self):
        """Test l'endpoint me avec un token invalide"""
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/auth/me", headers=invalid_headers)
        
        self.assertEqual(response.status_code, 401)
        data = response.json()
        # L'API valide d'abord le format du token
        self.assertIn("Format de token invalide", data["detail"])
    
    def test_logout_endpoint(self):
        """Test l'endpoint de déconnexion"""
        response = self.client.post("/auth/logout", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        
        # Vérifier que le token ne fonctionne plus
        response = self.client.get("/auth/me", headers=self.user_headers)
        self.assertEqual(response.status_code, 401)
    
    def test_update_profile_endpoint(self):
        """Test l'endpoint de mise à jour du profil"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "address": "Updated Address"
        }
        
        response = self.client.put("/auth/profile", json=update_data, headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Updated")
        self.assertEqual(data["last_name"], "Name")
        self.assertEqual(data["address"], "Updated Address")
        self.assertEqual(data["email"], "user@test.com")  # Email inchangé
    
    def test_update_profile_partial(self):
        """Test la mise à jour partielle du profil"""
        update_data = {
            "first_name": "Partially Updated"
        }
        
        response = self.client.put("/auth/profile", json=update_data, headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["first_name"], "Partially Updated")
        # Les autres champs devraient rester inchangés
    
    def test_list_products_endpoint(self):
        """Test l'endpoint de liste des produits"""
        response = self.client.get("/products")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)  # Au moins nos 2 produits de test
        
        # Vérifier que les produits de test sont présents
        product_names = [product["name"] for product in data]
        self.assertIn("Test Product 1", product_names)
        self.assertIn("Test Product 2", product_names)
    
    def test_view_cart_endpoint(self):
        """Test l'endpoint de visualisation du panier"""
        response = self.client.get("/cart", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["user_id"], self.regular_user["id"])
        self.assertIsInstance(data["items"], dict)
    
    def test_add_to_cart_endpoint(self):
        """Test l'endpoint d'ajout au panier"""
        add_data = {
            "product_id": self.test_product1["id"],
            "qty": 2
        }
        
        response = self.client.post("/cart/add", json=add_data, headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        
        # Vérifier que l'article est dans le panier
        cart_response = self.client.get("/cart", headers=self.user_headers)
        cart_data = cart_response.json()
        self.assertIn(self.test_product1["id"], cart_data["items"])
        self.assertEqual(cart_data["items"][self.test_product1["id"]]["quantity"], 2)
    
    def test_add_to_cart_nonexistent_product(self):
        """Test l'ajout au panier d'un produit inexistant"""
        add_data = {
            "product_id": "nonexistent-product-id",
            "qty": 1
        }
        
        response = self.client.post("/cart/add", json=add_data, headers=self.user_headers)
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("Produit introuvable", data["detail"])
    
    def test_add_to_cart_insufficient_stock(self):
        """Test l'ajout au panier avec stock insuffisant"""
        add_data = {
            "product_id": self.test_product1["id"],
            "qty": 1000  # Plus que le stock disponible
        }
        
        response = self.client.post("/cart/add", json=add_data, headers=self.user_headers)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Stock insuffisant", data["detail"])
    
    def test_remove_from_cart_endpoint(self):
        """Test l'endpoint de suppression du panier"""
        # D'abord ajouter un article
        add_data = {
            "product_id": self.test_product1["id"],
            "qty": 3
        }
        self.client.post("/cart/add", json=add_data, headers=self.user_headers)
        
        # Puis supprimer une partie
        remove_data = {
            "product_id": self.test_product1["id"],
            "qty": 1
        }
        
        response = self.client.post("/cart/remove", json=remove_data, headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
        
        # Vérifier que la quantité a diminué
        cart_response = self.client.get("/cart", headers=self.user_headers)
        cart_data = cart_response.json()
        self.assertEqual(cart_data["items"][self.test_product1["id"]]["quantity"], 2)
    
    def test_checkout_endpoint(self):
        """Test l'endpoint de checkout"""
        # D'abord ajouter des articles au panier
        add_data1 = {
            "product_id": self.test_product1["id"],
            "qty": 2
        }
        add_data2 = {
            "product_id": self.test_product2["id"],
            "qty": 1
        }
        
        self.client.post("/cart/add", json=add_data1, headers=self.user_headers)
        self.client.post("/cart/add", json=add_data2, headers=self.user_headers)
        
        # Effectuer le checkout
        response = self.client.post("/orders/checkout", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNotNone(data["order_id"])
        self.assertEqual(data["total_cents"], 4000)  # (2 * 1000) + (1 * 2000)
        self.assertEqual(data["status"], "CREE")
        
        # Vérifier que le panier est vidé
        cart_response = self.client.get("/cart", headers=self.user_headers)
        cart_data = cart_response.json()
        self.assertEqual(len(cart_data["items"]), 0)
    
    def test_checkout_empty_cart(self):
        """Test le checkout avec un panier vide"""
        response = self.client.post("/orders/checkout", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("Panier vide", data["detail"])
    
    def test_list_orders_endpoint(self):
        """Test l'endpoint de liste des commandes"""
        # Créer une commande d'abord
        add_data = {"product_id": self.test_product1["id"], "qty": 1}
        self.client.post("/cart/add", json=add_data, headers=self.user_headers)
        checkout_response = self.client.post("/orders/checkout", headers=self.user_headers)
        
        # Lister les commandes
        response = self.client.get("/orders", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        
        # Vérifier les détails de la commande
        order = data[0]
        self.assertEqual(order["user_id"], self.regular_user["id"])
        self.assertIn("items", order)
        self.assertIn("status", order)
        self.assertIn("total_cents", order)
    
    def test_get_order_endpoint(self):
        """Test l'endpoint de récupération d'une commande"""
        # Créer une commande
        add_data = {"product_id": self.test_product1["id"], "qty": 1}
        self.client.post("/cart/add", json=add_data, headers=self.user_headers)
        checkout_response = self.client.post("/orders/checkout", headers=self.user_headers)
        order_id = checkout_response.json()["order_id"]
        
        # Récupérer la commande
        response = self.client.get(f"/orders/{order_id}", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], order_id)
        self.assertEqual(data["user_id"], self.regular_user["id"])
    
    def test_get_nonexistent_order(self):
        """Test la récupération d'une commande inexistante"""
        response = self.client.get("/orders/nonexistent-order-id", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("Commande introuvable", data["detail"])
    
    def test_cancel_order_endpoint(self):
        """Test l'endpoint d'annulation de commande"""
        # Créer une commande
        add_data = {"product_id": self.test_product1["id"], "qty": 1}
        self.client.post("/cart/add", json=add_data, headers=self.user_headers)
        checkout_response = self.client.post("/orders/checkout", headers=self.user_headers)
        order_id = checkout_response.json()["order_id"]
        
        # Annuler la commande
        response = self.client.post(f"/orders/{order_id}/cancel", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], order_id)
        self.assertEqual(data["status"], "ANNULEE")
    
    def test_admin_list_products_endpoint(self):
        """Test l'endpoint admin de liste des produits"""
        response = self.client.get("/admin/products", headers=self.admin_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 2)
    
    def test_admin_list_products_without_admin(self):
        """Test l'endpoint admin de liste des produits sans être admin"""
        response = self.client.get("/admin/products", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("Accès réservé aux administrateurs", data["detail"])
    
    def test_admin_create_product_endpoint(self):
        """Test l'endpoint admin de création de produit"""
        product_data = {
            "name": "Admin Created Product",
            "description": "Product created by admin",
            "price_cents": 3000,
            "stock_qty": 75,
            "active": True
        }
        
        response = self.client.post("/admin/products", json=product_data, headers=self.admin_headers)
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Admin Created Product")
        self.assertEqual(data["description"], "Product created by admin")
        self.assertEqual(data["price_cents"], 3000)
        self.assertEqual(data["stock_qty"], 75)
        self.assertTrue(data["active"])
        self.assertIsNotNone(data["id"])
    
    def test_admin_update_product_endpoint(self):
        """Test l'endpoint admin de mise à jour de produit"""
        # Créer un produit d'abord
        create_data = {
            "name": "Product to Update",
            "description": "Original description",
            "price_cents": 1000,
            "stock_qty": 50,
            "active": True
        }
        create_response = self.client.post("/admin/products", json=create_data, headers=self.admin_headers)
        product_id = create_response.json()["id"]
        
        # Mettre à jour le produit
        update_data = {
            "name": "Updated Product Name",
            "price_cents": 1500,
            "stock_qty": 75
        }
        
        response = self.client.put(f"/admin/products/{product_id}", json=update_data, headers=self.admin_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Updated Product Name")
        self.assertEqual(data["price_cents"], 1500)
        self.assertEqual(data["stock_qty"], 75)
        self.assertEqual(data["description"], "Original description")  # Inchangé
    
    def test_admin_delete_product_endpoint(self):
        """Test l'endpoint admin de suppression de produit"""
        # Créer un produit d'abord
        create_data = {
            "name": "Product to Delete",
            "description": "This product will be deleted",
            "price_cents": 1000,
            "stock_qty": 50,
            "active": True
        }
        create_response = self.client.post("/admin/products", json=create_data, headers=self.admin_headers)
        product_id = create_response.json()["id"]
        
        # Supprimer le produit
        response = self.client.delete(f"/admin/products/{product_id}", headers=self.admin_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["ok"])
    
    def test_admin_list_orders_endpoint(self):
        """Test l'endpoint admin de liste des commandes"""
        response = self.client.get("/admin/orders", headers=self.admin_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
    
    def test_support_create_thread_endpoint(self):
        """Test l'endpoint de création de fil de support"""
        thread_data = {
            "subject": "Test Support Thread",
            "order_id": None
        }
        
        response = self.client.post("/support/threads", json=thread_data, headers=self.user_headers)
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["subject"], "Test Support Thread")
        self.assertEqual(data["user_id"], self.regular_user["id"])
        self.assertFalse(data["closed"])
        self.assertIsNotNone(data["id"])
    
    def test_support_list_threads_endpoint(self):
        """Test l'endpoint de liste des fils de support"""
        # Créer un fil d'abord
        thread_data = {"subject": "List Test Thread"}
        self.client.post("/support/threads", json=thread_data, headers=self.user_headers)
        
        # Lister les fils
        response = self.client.get("/support/threads", headers=self.user_headers)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
    
    def test_support_post_message_endpoint(self):
        """Test l'endpoint de postage de message"""
        # Créer un fil d'abord
        thread_data = {"subject": "Message Test Thread"}
        thread_response = self.client.post("/support/threads", json=thread_data, headers=self.user_headers)
        thread_id = thread_response.json()["id"]
        
        # Poster un message
        message_data = {
            "content": "This is a test message"
        }
        
        response = self.client.post(f"/support/threads/{thread_id}/messages", json=message_data, headers=self.user_headers)
        
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["content"], "This is a test message")
        self.assertEqual(data["thread_id"], thread_id)
        self.assertEqual(data["author_user_id"], self.regular_user["id"])
    
    def test_test_pdf_endpoint(self):
        """Test l'endpoint de test PDF"""
        response = self.client.get("/test-pdf")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/pdf")
        self.assertIn("attachment", response.headers["content-disposition"])
        self.assertIn("test_facture.pdf", response.headers["content-disposition"])


class TestAPIErrorHandling(unittest.TestCase):
    """Tests pour la gestion d'erreurs de l'API"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.client = TestClient(app)
    
    def test_invalid_json_request(self):
        """Test une requête avec JSON invalide"""
        response = self.client.post(
            "/auth/register",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(response.status_code, 422)
    
    def test_missing_required_fields(self):
        """Test une requête avec des champs requis manquants"""
        incomplete_data = {
            "email": "test@example.com"
            # Manque password, first_name, etc.
        }
        
        response = self.client.post("/auth/register", json=incomplete_data)
        
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)
    
    def test_invalid_email_format(self):
        """Test avec un format d'email invalide"""
        invalid_data = {
            "email": "not-an-email",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "address": "Test Address"
        }
        
        response = self.client.post("/auth/register", json=invalid_data)
        
        self.assertEqual(response.status_code, 422)
    
    def test_unauthorized_access(self):
        """Test l'accès non autorisé à des endpoints protégés"""
        # Essayer d'accéder à un endpoint admin sans être connecté
        response = self.client.get("/admin/products")
        
        self.assertEqual(response.status_code, 401)
    
    def test_forbidden_access(self):
        """Test l'accès interdit à des endpoints admin"""
        # Se connecter comme utilisateur régulier
        login_data = {
            "email": "user@test.com",
            "password": "userpass"
        }
        login_response = self.client.post("/auth/login", json=login_data)
        user_token = login_response.json()["token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # Essayer d'accéder à un endpoint admin
        response = self.client.get("/admin/products", headers=user_headers)
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertIn("Accès réservé aux administrateurs", data["detail"])


if __name__ == '__main__':
    print("=== Tests des endpoints API ===")
    unittest.main(verbosity=2)
