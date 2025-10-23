#!/usr/bin/env python3
"""
Tests unitaires pour les endpoints API
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.api import app

@pytest.mark.unit
@pytest.mark.api
class TestAPIEndpoints:
    """Tests unitaires pour les endpoints API"""
    
    @pytest.fixture
    def client(self):
        """Client de test FastAPI"""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test du point d'entrée racine"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert data["message"] == "API E-commerce"
    
    def test_health_check_endpoint(self, client):
        """Test du point de santé"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
    
    def test_register_endpoint_validation(self, client):
        """Test de validation de l'endpoint d'inscription"""
        # Test avec données valides
        valid_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test Street"
        }
        
        # Mock de la création d'utilisateur
        with patch('ecommerce-backend.api.AuthService') as mock_auth_service:
            mock_auth_service.return_value.register_user.return_value = Mock(
                id="user123",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                is_admin=False
            )
            mock_auth_service.return_value.create_access_token.return_value = "mock_token"
            
            response = client.post("/auth/register", json=valid_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "message" in data
            assert "user" in data
            assert "access_token" in data
            assert data["user"]["email"] == "test@example.com"
    
    def test_register_endpoint_validation_errors(self, client):
        """Test des erreurs de validation de l'endpoint d'inscription"""
        # Test avec email invalide
        invalid_email_data = {
            "email": "invalid-email",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test Street"
        }
        
        response = client.post("/auth/register", json=invalid_email_data)
        assert response.status_code == 422  # Validation error
        
        # Test avec mot de passe trop court
        short_password_data = {
            "email": "test@example.com",
            "password": "123",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test Street"
        }
        
        response = client.post("/auth/register", json=short_password_data)
        assert response.status_code == 422  # Validation error
        
        # Test avec champs manquants
        missing_fields_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/auth/register", json=missing_fields_data)
        assert response.status_code == 422  # Validation error
    
    def test_login_endpoint_validation(self, client):
        """Test de validation de l'endpoint de connexion"""
        # Test avec données valides
        valid_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        # Mock de l'authentification
        with patch('ecommerce-backend.api.AuthService') as mock_auth_service:
            mock_auth_service.return_value.authenticate_user.return_value = Mock(
                id="user123",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                is_admin=False
            )
            mock_auth_service.return_value.create_access_token.return_value = "mock_token"
            
            response = client.post("/auth/login", json=valid_data)
            
            assert response.status_code == 200
        data = response.json()
            assert "access_token" in data
            assert "token_type" in data
            assert "user" in data
            assert data["token_type"] == "bearer"
    
    def test_login_endpoint_authentication_failure(self, client):
        """Test d'échec d'authentification de l'endpoint de connexion"""
        # Test avec identifiants incorrects
        invalid_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        # Mock de l'authentification qui échoue
        with patch('ecommerce-backend.api.AuthService') as mock_auth_service:
            mock_auth_service.return_value.authenticate_user.return_value = None
            
            response = client.post("/auth/login", json=invalid_data)
            
            assert response.status_code == 401
        data = response.json()
            assert "detail" in data
            assert "incorrect" in data["detail"].lower()
    
    def test_products_endpoint_authentication(self, client):
        """Test de l'endpoint des produits avec authentification"""
        # Test sans token
        response = client.get("/products")
        assert response.status_code == 401  # Unauthorized
        
        # Test avec token valide
        with patch('ecommerce_backend.api_unified.current_user') as mock_current_user:
            mock_current_user.return_value = Mock(
                id="user123",
                email="test@example.com",
                is_admin=False
            )
            
            with patch('ecommerce_backend.api_unified.PostgreSQLProductRepository') as mock_repo:
                mock_repo.return_value.get_all_active.return_value = [
                    Mock(id="product1", name="Product 1", price_cents=2999, stock_qty=100, active=True)
                ]
                
                response = client.get("/products", headers={"Authorization": "Bearer mock_token"})
                
                assert response.status_code == 200
        data = response.json()
                assert isinstance(data, list)
                assert len(data) > 0
                assert "id" in data[0]
                assert "name" in data[0]
                assert "price_cents" in data[0]
    
    def test_cart_endpoint_authentication(self, client):
        """Test de l'endpoint du panier avec authentification"""
        # Test sans token
        response = client.get("/cart")
        assert response.status_code == 401  # Unauthorized
        
        # Test avec token valide
        with patch('ecommerce_backend.api_unified.current_user') as mock_current_user:
            mock_current_user.return_value = Mock(
                id="user123",
                email="test@example.com",
                is_admin=False
            )
            
            with patch('ecommerce_backend.api_unified.PostgreSQLCartRepository') as mock_repo:
                mock_repo.return_value.get_by_user_id.return_value = Mock(
                    items=[],
                    total_cents=0
                )
                
                response = client.get("/cart", headers={"Authorization": "Bearer mock_token"})
                
                assert response.status_code == 200
        data = response.json()
                assert "items" in data
                assert "total_cents" in data
                assert isinstance(data["items"], list)
    
    def test_orders_endpoint_authentication(self, client):
        """Test de l'endpoint des commandes avec authentification"""
        # Test sans token
        response = client.get("/orders")
        assert response.status_code == 401  # Unauthorized
        
        # Test avec token valide
        with patch('ecommerce_backend.api_unified.current_user') as mock_current_user:
            mock_current_user.return_value = Mock(
                id="user123",
                email="test@example.com",
                is_admin=False
            )
            
            with patch('ecommerce_backend.api_unified.PostgreSQLOrderRepository') as mock_repo:
                mock_repo.return_value.get_by_user_id.return_value = [
                    Mock(id="order1", status="CREE", created_at="2024-01-01", items=[])
                ]
                
                response = client.get("/orders", headers={"Authorization": "Bearer mock_token"})
                
                assert response.status_code == 200
        data = response.json()
                assert isinstance(data, list)
                assert len(data) > 0
                assert "id" in data[0]
                assert "status" in data[0]
                assert "created_at" in data[0]
    
    def test_admin_endpoints_authorization(self, client):
        """Test de l'autorisation des endpoints admin"""
        # Test sans token
        response = client.get("/admin/products")
        assert response.status_code == 401  # Unauthorized
        
        # Test avec token d'utilisateur normal
        with patch('ecommerce_backend.api_unified.current_user') as mock_current_user:
            mock_current_user.return_value = Mock(
                id="user123",
                email="test@example.com",
                is_admin=False
            )
            
            response = client.get("/admin/products", headers={"Authorization": "Bearer mock_token"})
            assert response.status_code == 403  # Forbidden
        
        # Test avec token d'admin
        with patch('ecommerce_backend.api_unified.require_admin') as mock_require_admin:
            mock_require_admin.return_value = Mock(
                id="admin123",
                email="admin@example.com",
                is_admin=True
            )
            
            with patch('ecommerce_backend.api_unified.PostgreSQLProductRepository') as mock_repo:
                mock_repo.return_value.get_all.return_value = [
                    Mock(id="product1", name="Product 1", price_cents=2999, stock_qty=100, active=True)
                ]
                
                response = client.get("/admin/products", headers={"Authorization": "Bearer mock_token"})
                assert response.status_code == 200
    
    def test_cors_headers(self, client):
        """Test des en-têtes CORS"""
        response = client.options("/")
        
        # Vérifier que les en-têtes CORS sont présents
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers
    
    def test_error_handling(self, client):
        """Test de la gestion des erreurs"""
        # Test avec endpoint inexistant
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        # Test avec méthode non autorisée
        response = client.delete("/")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_request_validation(self, client):
        """Test de la validation des requêtes"""
        # Test avec JSON invalide
        response = client.post("/auth/register", data="invalid json")
        assert response.status_code == 422
        
        # Test avec Content-Type incorrect
        response = client.post("/auth/register", 
                             data="email=test@example.com&password=password123",
                             headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 422
    
    def test_response_format(self, client):
        """Test du format des réponses"""
        # Test de la réponse d'erreur
        response = client.get("/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
    
    def test_api_documentation(self, client):
        """Test de la documentation API"""
        # Test de l'endpoint de documentation
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test de l'endpoint OpenAPI
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data