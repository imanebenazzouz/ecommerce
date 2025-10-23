#!/usr/bin/env python3
"""
Tests end-to-end du parcours utilisateur complet
"""

import pytest
import requests
import time
import os
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@pytest.mark.e2e
@pytest.mark.slow
class TestUserJourney:
    """Tests end-to-end du parcours utilisateur"""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """URL de base de l'API"""
        return os.getenv("API_BASE_URL", "http://localhost:8000")
    
    @pytest.fixture(scope="class")
    def frontend_url(self):
        """URL du frontend"""
        return os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    @pytest.fixture(scope="class")
    def test_user_data(self):
        """Données de l'utilisateur de test"""
        return {
            "email": "e2e@test.com",
            "password": "password123",
            "first_name": "E2E",
            "last_name": "Test",
            "address": "123 E2E Street"
        }
    
    def test_api_health_check(self, api_base_url):
        """Test de santé de l'API"""
        response = requests.get(f"{api_base_url}/health", timeout=10)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_user_registration_and_login(self, api_base_url, test_user_data):
        """Test d'inscription et de connexion"""
        # Inscription
        response = requests.post(f"{api_base_url}/auth/register", json=test_user_data, timeout=10)
        assert response.status_code == 200
        
        registration_data = response.json()
        assert "access_token" in registration_data
        assert registration_data["user"]["email"] == test_user_data["email"]
        
        # Connexion
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 200
        
        login_response = response.json()
        assert "access_token" in login_response
        assert login_response["user"]["email"] == test_user_data["email"]
        
        return login_response["access_token"]
    
    def test_product_catalog(self, api_base_url, token):
        """Test du catalogue de produits"""
        headers = {"Authorization": f"Bearer {token}"}
        
        # Récupérer les produits
        response = requests.get(f"{api_base_url}/products", headers=headers, timeout=10)
        assert response.status_code == 200
        
        products = response.json()
        assert len(products) > 0
        
        # Vérifier la structure des produits
        for product in products:
            assert "id" in product
            assert "name" in product
            assert "price_cents" in product
            assert "stock_qty" in product
            assert "active" in product
        
        return products[0]["id"]  # Retourner l'ID du premier produit
    
    def test_cart_operations(self, api_base_url, token, product_id):
        """Test des opérations de panier"""
        headers = {"Authorization": f"Bearer {token}"}
        
        # Ajouter un produit au panier
        cart_data = {"product_id": product_id, "qty": 2}
        response = requests.post(f"{api_base_url}/cart/add", json=cart_data, headers=headers, timeout=10)
        assert response.status_code == 200
        
        # Vérifier le contenu du panier
        response = requests.get(f"{api_base_url}/cart", headers=headers, timeout=10)
        assert response.status_code == 200
        
        cart = response.json()
        assert "items" in cart
        assert "total_cents" in cart
        assert len(cart["items"]) > 0
        
        # Vérifier que le produit est dans le panier
        product_in_cart = False
        for item in cart["items"]:
            if item["product_id"] == product_id:
                product_in_cart = True
                assert item["quantity"] == 2
                break
        
        assert product_in_cart is True
    
    def test_order_creation(self, api_base_url, token):
        """Test de création de commande"""
        headers = {"Authorization": f"Bearer {token}"}
        
        # Créer une commande
        response = requests.post(f"{api_base_url}/orders/checkout", headers=headers, timeout=10)
        assert response.status_code == 200
        
        order_data = response.json()
        assert "order_id" in order_data
        assert "status" in order_data
        
        return order_data["order_id"]
    
    def test_payment_processing(self, api_base_url, token, order_id):
        """Test de traitement du paiement"""
        headers = {"Authorization": f"Bearer {token}"}
        
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2025,
            "cvc": "123"
        }
        
        response = requests.post(f"{api_base_url}/orders/{order_id}/pay", json=payment_data, headers=headers, timeout=10)
        assert response.status_code == 200
        
        payment_response = response.json()
        assert "message" in payment_response
        assert "order_status" in payment_response
    
    def test_order_history(self, api_base_url, token):
        """Test de l'historique des commandes"""
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{api_base_url}/orders", headers=headers, timeout=10)
        assert response.status_code == 200
        
        orders = response.json()
        assert len(orders) > 0
        
        # Vérifier la structure des commandes
        for order in orders:
            assert "id" in order
            assert "status" in order
            assert "created_at" in order
            assert "total_cents" in order
    
    def test_complete_user_journey(self, api_base_url, test_user_data):
        """Test du parcours utilisateur complet"""
        # 1. Inscription
        response = requests.post(f"{api_base_url}/auth/register", json=test_user_data, timeout=10)
        assert response.status_code == 200
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Récupérer les produits
        response = requests.get(f"{api_base_url}/products", headers=headers, timeout=10)
        assert response.status_code == 200
        products = response.json()
        assert len(products) > 0
        
        # 3. Ajouter au panier
        product_id = products[0]["id"]
        cart_data = {"product_id": product_id, "qty": 1}
        response = requests.post(f"{api_base_url}/cart/add", json=cart_data, headers=headers, timeout=10)
        assert response.status_code == 200
        
        # 4. Vérifier le panier
        response = requests.get(f"{api_base_url}/cart", headers=headers, timeout=10)
        assert response.status_code == 200
        cart = response.json()
        assert len(cart["items"]) > 0
        
        # 5. Créer une commande
        response = requests.post(f"{api_base_url}/orders/checkout", headers=headers, timeout=10)
        assert response.status_code == 200
        order_id = response.json()["order_id"]
        
        # 6. Payer la commande
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2025,
            "cvc": "123"
        }
        response = requests.post(f"{api_base_url}/orders/{order_id}/pay", json=payment_data, headers=headers, timeout=10)
        assert response.status_code == 200
        
        # 7. Vérifier l'historique des commandes
        response = requests.get(f"{api_base_url}/orders", headers=headers, timeout=10)
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) > 0
        
        # 8. Vérifier que le panier est vide
        response = requests.get(f"{api_base_url}/cart", headers=headers, timeout=10)
        assert response.status_code == 200
        cart = response.json()
        assert len(cart["items"]) == 0
        
        print("✅ Parcours utilisateur complet réussi !")
    
    def test_error_handling(self, api_base_url):
        """Test de la gestion des erreurs"""
        # Test avec des données invalides
        invalid_data = {
            "email": "invalid-email",
            "password": "123",  # Trop court
            "first_name": "",
            "last_name": "",
            "address": ""
        }
        
        response = requests.post(f"{api_base_url}/auth/register", json=invalid_data, timeout=10)
        assert response.status_code == 422  # Validation error
        
        # Test avec des identifiants incorrects
        login_data = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{api_base_url}/auth/login", json=login_data, timeout=10)
        assert response.status_code == 401  # Unauthorized
        
        # Test d'accès sans token
        response = requests.get(f"{api_base_url}/cart", timeout=10)
        assert response.status_code == 401  # Unauthorized
