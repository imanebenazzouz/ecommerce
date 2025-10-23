#!/usr/bin/env python3
"""
Tests end-to-end complets du parcours utilisateur
"""

import pytest
import requests
import json
import time
import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Ajouter le répertoire ecommerce-backend au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ecommerce-backend'))

@pytest.mark.e2e
@pytest.mark.user_journey
class TestUserJourney:
    """Tests complets du parcours utilisateur"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """URL de base de l'API"""
        return "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def frontend_url(self):
        """URL du frontend"""
        return "http://localhost:5173"
    
    @pytest.fixture
    def test_user_data(self):
        """Données de test utilisateur"""
        timestamp = int(time.time())
        return {
            "email": f"test{timestamp}@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test Street"
        }
    
    @pytest.fixture
    def admin_user_data(self):
        """Données de test admin"""
        return {
            "email": "admin@example.com",
            "password": "admin123"
        }
    
    def test_api_health_check(self, api_base_url):
        """Test de santé de l'API"""
        response = requests.get(f"{api_base_url}/", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Ecommerce API" in data["message"]
    
    def test_user_registration_and_login(self, api_base_url, test_user_data):
        """Test d'inscription et de connexion utilisateur"""
        # Test d'inscription
        response = requests.post(f"{api_base_url}/auth/register", json=test_user_data, timeout=10)
        assert response.status_code == 200
        register_data = response.json()
        assert "id" in register_data
        assert register_data["email"] == test_user_data["email"]
        assert register_data["first_name"] == test_user_data["first_name"]
        assert register_data["last_name"] == test_user_data["last_name"]
        assert register_data["is_admin"] is False
        
        # Test de connexion
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        login_response = response.json()
        assert "token" in login_response
        assert login_response["token"] is not None
        
        return login_response["token"]
    
    def test_product_listing(self, api_base_url, test_user_data):
        """Test de listing des produits"""
        # Se connecter d'abord
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        token = response.json()["token"]
        
        # Lister les produits
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{api_base_url}/products", headers=headers, timeout=10)
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        
        return products
    
    def test_cart_operations(self, api_base_url, test_user_data):
        """Test des opérations de panier"""
        # Se connecter
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        token = response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Lister les produits pour obtenir un ID
        response = requests.get(f"{api_base_url}/products", headers=headers, timeout=10)
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0
        product_id = products[0]["id"]
        
        # Ajouter au panier
        cart_data = {"product_id": product_id, "qty": 2}
        response = requests.post(f"{api_base_url}/cart/add", json=cart_data, headers=headers, timeout=10)
        assert response.status_code == 200
        
        # Voir le panier
        response = requests.get(f"{api_base_url}/cart", headers=headers, timeout=10)
        assert response.status_code == 200
        cart = response.json()
        assert "items" in cart
        assert len(cart["items"]) > 0
        
        # Modifier la quantité
        cart_data = {"product_id": product_id, "qty": 1}
        response = requests.post(f"{api_base_url}/cart/remove", json=cart_data, headers=headers, timeout=10)
        assert response.status_code == 200
        
        # Vérifier le panier mis à jour
        response = requests.get(f"{api_base_url}/cart", headers=headers, timeout=10)
        assert response.status_code == 200
        cart = response.json()
        assert len(cart["items"]) > 0
        
        return cart
    
    def test_order_creation_and_payment(self, api_base_url, test_user_data):
        """Test de création de commande et paiement"""
        # Se connecter
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        token = response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Ajouter des produits au panier
        response = requests.get(f"{api_base_url}/products", headers=headers, timeout=10)
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0
        
        for product in products[:2]:  # Ajouter les 2 premiers produits
            cart_data = {"product_id": product["id"], "qty": 1}
            response = requests.post(f"{api_base_url}/cart/add", json=cart_data, headers=headers, timeout=10)
            assert response.status_code == 200
        
        # Créer une commande
        response = requests.post(f"{api_base_url}/orders/checkout", headers=headers, timeout=10)
        assert response.status_code == 200
        order_data = response.json()
        assert "order_id" in order_data
        assert "total_cents" in order_data
        assert "status" in order_data
        order_id = order_data["order_id"]
        
        # Payer la commande
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2025,
            "cvc": "123"
        }
        response = requests.post(f"{api_base_url}/orders/{order_id}/pay", json=payment_data, headers=headers, timeout=10)
        assert response.status_code == 200
        payment_response = response.json()
        assert "payment_id" in payment_response
        assert "status" in payment_response
        assert payment_response["status"] == "SUCCEEDED"
        
        return order_id
    
    def test_order_tracking(self, api_base_url, test_user_data):
        """Test de suivi de commande"""
        # Se connecter
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        token = response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Lister les commandes
        response = requests.get(f"{api_base_url}/orders", headers=headers, timeout=10)
        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)
        
        if len(orders) > 0:
            order = orders[0]
            order_id = order["id"]
            
            # Voir les détails de la commande
            response = requests.get(f"{api_base_url}/orders/{order_id}", headers=headers, timeout=10)
            assert response.status_code == 200
            order_details = response.json()
            assert order_details["id"] == order_id
            assert "items" in order_details
            assert "status" in order_details
            assert "total_cents" in order_details
    
    def test_invoice_generation(self, api_base_url, test_user_data):
        """Test de génération de facture"""
        # Se connecter
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        token = response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Lister les commandes
        response = requests.get(f"{api_base_url}/orders", headers=headers, timeout=10)
        assert response.status_code == 200
        orders = response.json()
        
        if len(orders) > 0:
            order = orders[0]
            order_id = order["id"]
            
            # Générer la facture
            response = requests.get(f"{api_base_url}/orders/{order_id}/invoice", headers=headers, timeout=10)
            assert response.status_code == 200
            invoice = response.json()
            assert "id" in invoice
            assert "order_id" in invoice
            assert "number" in invoice
            assert "lines" in invoice
            assert "total_cents" in invoice
            assert "issued_at" in invoice
            
            # Télécharger la facture PDF
            response = requests.get(f"{api_base_url}/orders/{order_id}/invoice/download", headers=headers, timeout=10)
            assert response.status_code == 200
            assert response.headers["content-type"] == "application/pdf"
            assert len(response.content) > 0
    
    def test_support_system(self, api_base_url, test_user_data):
        """Test du système de support"""
        # Se connecter
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        token = response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Créer un fil de support
        thread_data = {
            "subject": "Test Support Request",
            "order_id": None
        }
        response = requests.post(f"{api_base_url}/support/threads", json=thread_data, headers=headers, timeout=10)
        assert response.status_code == 200
        thread = response.json()
        assert "id" in thread
        assert thread["subject"] == "Test Support Request"
        assert thread["closed"] is False
        
        thread_id = thread["id"]
        
        # Ajouter un message
        message_data = {
            "content": "This is a test support message"
        }
        response = requests.post(f"{api_base_url}/support/threads/{thread_id}/messages", json=message_data, headers=headers, timeout=10)
        assert response.status_code == 200
        message = response.json()
        assert "id" in message
        assert message["content"] == "This is a test support message"
        assert message["author_user_id"] is not None
        
        # Récupérer le fil avec ses messages
        response = requests.get(f"{api_base_url}/support/threads/{thread_id}", headers=headers, timeout=10)
        assert response.status_code == 200
        thread_details = response.json()
        assert thread_details["id"] == thread_id
        assert "messages" in thread_details
        assert len(thread_details["messages"]) > 0
        
        # Lister tous les fils de support
        response = requests.get(f"{api_base_url}/support/threads", headers=headers, timeout=10)
        assert response.status_code == 200
        threads = response.json()
        assert isinstance(threads, list)
        assert len(threads) > 0
    
    def test_admin_operations(self, api_base_url, admin_user_data):
        """Test des opérations administrateur"""
        # Se connecter en tant qu'admin
        login_data = {
            "email": admin_user_data["email"],
            "password": admin_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        token = response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Lister tous les produits (admin)
        response = requests.get(f"{api_base_url}/admin/products", headers=headers, timeout=10)
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        
        # Créer un nouveau produit
        product_data = {
            "name": "Admin Test Product",
            "description": "A product created by admin",
            "price_cents": 3999,
            "stock_qty": 50,
            "active": True
        }
        response = requests.post(f"{api_base_url}/admin/products", json=product_data, headers=headers, timeout=10)
        assert response.status_code == 201
        new_product = response.json()
        assert new_product["name"] == product_data["name"]
        assert new_product["price_cents"] == product_data["price_cents"]
        assert new_product["stock_qty"] == product_data["stock_qty"]
        assert new_product["active"] is True
        
        product_id = new_product["id"]
        
        # Modifier le produit
        update_data = {
            "name": "Updated Admin Product",
            "price_cents": 4999,
            "stock_qty": 75
        }
        response = requests.put(f"{api_base_url}/admin/products/{product_id}", json=update_data, headers=headers, timeout=10)
        assert response.status_code == 200
        updated_product = response.json()
        assert updated_product["name"] == update_data["name"]
        assert updated_product["price_cents"] == update_data["price_cents"]
        assert updated_product["stock_qty"] == update_data["stock_qty"]
        
        # Lister toutes les commandes (admin)
        response = requests.get(f"{api_base_url}/admin/orders", headers=headers, timeout=10)
        assert response.status_code == 200
        orders = response.json()
        assert isinstance(orders, list)
        
        # Supprimer le produit (désactiver)
        response = requests.delete(f"{api_base_url}/admin/products/{product_id}", headers=headers, timeout=10)
        assert response.status_code == 200
        
        # Vérifier que le produit est désactivé
        response = requests.get(f"{api_base_url}/admin/products", headers=headers, timeout=10)
        assert response.status_code == 200
        products = response.json()
        product = next((p for p in products if p["id"] == product_id), None)
        assert product is not None
        assert product["active"] is False
    
    def test_admin_support_operations(self, api_base_url, admin_user_data):
        """Test des opérations de support administrateur"""
        # Se connecter en tant qu'admin
        login_data = {
            "email": admin_user_data["email"],
            "password": admin_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        token = response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Lister tous les fils de support (admin)
        response = requests.get(f"{api_base_url}/admin/support/threads", headers=headers, timeout=10)
        assert response.status_code == 200
        threads = response.json()
        assert isinstance(threads, list)
        
        if len(threads) > 0:
            thread = threads[0]
            thread_id = thread["id"]
            
            # Récupérer les détails du fil
            response = requests.get(f"{api_base_url}/admin/support/threads/{thread_id}", headers=headers, timeout=10)
            assert response.status_code == 200
            thread_details = response.json()
            assert thread_details["id"] == thread_id
            assert "messages" in thread_details
            
            # Ajouter un message admin
            message_data = {
                "content": "This is an admin response"
            }
            response = requests.post(f"{api_base_url}/admin/support/threads/{thread_id}/messages", json=message_data, headers=headers, timeout=10)
            assert response.status_code == 200
            message = response.json()
            assert message["content"] == message_data["content"]
            assert message["author_user_id"] is None  # Message admin
            
            # Fermer le fil
            response = requests.post(f"{api_base_url}/admin/support/threads/{thread_id}/close", headers=headers, timeout=10)
            assert response.status_code == 200
    
    def test_order_management_workflow(self, api_base_url, test_user_data, admin_user_data):
        """Test du workflow complet de gestion des commandes"""
        # 1. Utilisateur crée une commande
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        user_token = response.json()["token"]
        
        user_headers = {"Authorization": f"Bearer {user_token}"}
        
        # Ajouter des produits au panier
        response = requests.get(f"{api_base_url}/products", headers=user_headers, timeout=10)
        assert response.status_code == 200
        products = response.json()
        
        for product in products[:2]:
            cart_data = {"product_id": product["id"], "qty": 1}
            response = requests.post(f"{api_base_url}/cart/add", json=cart_data, headers=user_headers, timeout=10)
            assert response.status_code == 200
        
        # Créer une commande
        response = requests.post(f"{api_base_url}/orders/checkout", headers=user_headers, timeout=10)
        assert response.status_code == 200
        order_data = response.json()
        order_id = order_data["order_id"]
        
        # Payer la commande
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2025,
            "cvc": "123"
        }
        response = requests.post(f"{api_base_url}/orders/{order_id}/pay", json=payment_data, headers=user_headers, timeout=10)
        assert response.status_code == 200
        
        # 2. Admin valide la commande
        admin_login_data = {
            "email": admin_user_data["email"],
            "password": admin_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=admin_login_data, timeout=10)
        assert response.status_code == 200
        admin_token = response.json()["token"]
        
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Valider la commande
        response = requests.post(f"{api_base_url}/admin/orders/{order_id}/validate", headers=admin_headers, timeout=10)
        assert response.status_code == 200
        
        # 3. Admin expédie la commande
        delivery_data = {
            "transporteur": "Test Transport",
            "tracking_number": "TRACK123",
            "delivery_status": "PREPAREE"
        }
        response = requests.post(f"{api_base_url}/admin/orders/{order_id}/ship", json=delivery_data, headers=admin_headers, timeout=10)
        assert response.status_code == 200
        
        # 4. Admin marque comme livrée
        response = requests.post(f"{api_base_url}/admin/orders/{order_id}/mark-delivered", headers=admin_headers, timeout=10)
        assert response.status_code == 200
        
        # 5. Vérifier le statut final
        response = requests.get(f"{api_base_url}/orders/{order_id}", headers=user_headers, timeout=10)
        assert response.status_code == 200
        order = response.json()
        assert order["status"] == "LIVREE"
        assert "delivery" in order
        assert order["delivery"]["transporteur"] == "Test Transport"
        assert order["delivery"]["tracking_number"] == "TRACK123"
    
    def test_error_handling(self, api_base_url):
        """Test de gestion des erreurs"""
        # Test avec endpoint inexistant
        response = requests.get(f"{api_base_url}/nonexistent", timeout=10)
        assert response.status_code == 404
        
        # Test avec données invalides
        invalid_data = {
            "email": "invalid-email",
            "password": "123"
        }
        response = requests.post(f"{api_base_url}/auth/register", json=invalid_data, timeout=10)
        assert response.status_code == 422
        
        # Test avec token invalide
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(f"{api_base_url}/orders", headers=headers, timeout=10)
        assert response.status_code == 401
        
        # Test avec accès non autorisé
        response = requests.get(f"{api_base_url}/admin/products", headers=headers, timeout=10)
        assert response.status_code == 401
    
    def test_performance_under_load(self, api_base_url, test_user_data):
        """Test de performance sous charge"""
        # Se connecter
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        token = response.json()["token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test de performance avec de nombreuses requêtes
        start_time = time.time()
        
        for i in range(10):
            response = requests.get(f"{api_base_url}/products", headers=headers, timeout=10)
            assert response.status_code == 200
            
            response = requests.get(f"{api_base_url}/orders", headers=headers, timeout=10)
            assert response.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Vérifier que les requêtes sont traitées rapidement
        assert duration < 10  # Moins de 10 secondes pour 20 requêtes
