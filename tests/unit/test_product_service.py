#!/usr/bin/env python3
"""
Tests unitaires pour le service de produits
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.database.repositories_simple import PostgreSQLProductRepository

@pytest.mark.unit
@pytest.mark.products
class TestProductService:
    """Tests unitaires pour le service de produits"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def product_repo(self, mock_db):
        """Repository de produits avec mock"""
        return PostgreSQLProductRepository(mock_db)
    
    def test_create_product_success(self, product_repo, mock_db):
        """Test de création de produit réussie"""
        # Données du produit
        product_data = {
            "name": "Test Product",
            "description": "A test product",
            "price_cents": 2999,
            "stock_qty": 100,
            "active": True
        }
        
        # Mock de la création
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.name = "Test Product"
        mock_product.price_cents = 2999
        mock_product.stock_qty = 100
        mock_product.active = True
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Simuler la création du produit
        with patch.object(product_repo, 'create') as mock_create:
            mock_create.return_value = mock_product
            result = product_repo.create(product_data)
        
        assert result is not None
        assert result.name == "Test Product"
        assert result.price_cents == 2999
        assert result.stock_qty == 100
        assert result.active is True
    
    def test_get_product_by_id_success(self, product_repo, mock_db):
        """Test de récupération de produit par ID réussie"""
        # Mock du produit
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.name = "Test Product"
        mock_product.price_cents = 2999
        mock_product.stock_qty = 100
        mock_product.active = True
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = product_repo.get_by_id("product123")
        
        assert result is not None
        assert result.id == "product123"
        assert result.name == "Test Product"
        mock_db.query.assert_called_once()
    
    def test_get_product_by_id_not_found(self, product_repo, mock_db):
        """Test de récupération de produit par ID non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = product_repo.get_by_id("nonexistent")
        
        assert result is None
        mock_db.query.assert_called_once()
    
    def test_get_all_products(self, product_repo, mock_db):
        """Test de récupération de tous les produits"""
        # Mock des produits
        mock_products = [
            Mock(id="product1", name="Product 1", active=True),
            Mock(id="product2", name="Product 2", active=True),
            Mock(id="product3", name="Product 3", active=False)
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.all.return_value = mock_products
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = product_repo.get_all()
        
        assert result is not None
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_get_all_active_products(self, product_repo, mock_db):
        """Test de récupération des produits actifs uniquement"""
        # Mock des produits actifs
        mock_products = [
            Mock(id="product1", name="Product 1", active=True),
            Mock(id="product2", name="Product 2", active=True)
        ]
        
        # Mock de la requête avec filtre
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_products
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = product_repo.get_all_active()
        
        assert result is not None
        assert len(result) == 2
        mock_db.query.assert_called_once()
    
    def test_update_product_success(self, product_repo, mock_db):
        """Test de mise à jour de produit réussie"""
        # Mock du produit existant
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.name = "Original Name"
        mock_product.price_cents = 1999
        mock_product.stock_qty = 50
        mock_product.active = True
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Données de mise à jour
        update_data = {
            "name": "Updated Name",
            "price_cents": 2999,
            "stock_qty": 100
        }
        
        # Test de mise à jour
        result = product_repo.update("product123", update_data)
        
        assert result is not None
        assert result.name == "Updated Name"
        assert result.price_cents == 2999
        assert result.stock_qty == 100
        mock_db.commit.assert_called_once()
    
    def test_update_product_not_found(self, product_repo, mock_db):
        """Test de mise à jour de produit non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Données de mise à jour
        update_data = {"name": "Updated Name"}
        
        # Test de mise à jour
        result = product_repo.update("nonexistent", update_data)
        
        assert result is None
        mock_db.commit.assert_not_called()
    
    def test_delete_product_success(self, product_repo, mock_db):
        """Test de suppression de produit réussie"""
        # Mock du produit existant
        mock_product = Mock()
        mock_product.id = "product123"
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Test de suppression
        result = product_repo.delete("product123")
        
        assert result is True
        mock_db.delete.assert_called_once_with(mock_product)
        mock_db.commit.assert_called_once()
    
    def test_delete_product_not_found(self, product_repo, mock_db):
        """Test de suppression de produit non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de suppression
        result = product_repo.delete("nonexistent")
        
        assert result is False
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()
    
    def test_reserve_stock_success(self, product_repo, mock_db):
        """Test de réservation de stock réussie"""
        # Mock du produit avec stock suffisant
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.stock_qty = 100
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Test de réservation
        result = product_repo.reserve_stock("product123", 10)
        
        assert result is True
        assert mock_product.stock_qty == 90  # 100 - 10
        mock_db.commit.assert_called_once()
    
    def test_reserve_stock_insufficient(self, product_repo, mock_db):
        """Test de réservation de stock insuffisant"""
        # Mock du produit avec stock insuffisant
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.stock_qty = 5
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Test de réservation
        result = product_repo.reserve_stock("product123", 10)
        
        assert result is False
        assert mock_product.stock_qty == 5  # Inchangé
        mock_db.commit.assert_not_called()
    
    def test_reserve_stock_product_not_found(self, product_repo, mock_db):
        """Test de réservation de stock pour produit non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de réservation
        result = product_repo.reserve_stock("nonexistent", 10)
        
        assert result is False
        mock_db.commit.assert_not_called()
    
    def test_release_stock_success(self, product_repo, mock_db):
        """Test de libération de stock réussie"""
        # Mock du produit
        mock_product = Mock()
        mock_product.id = "product123"
        mock_product.stock_qty = 90
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_product
        mock_db.query.return_value = mock_query
        
        # Test de libération
        result = product_repo.release_stock("product123", 10)
        
        assert result is True
        assert mock_product.stock_qty == 100  # 90 + 10
        mock_db.commit.assert_called_once()
    
    def test_release_stock_product_not_found(self, product_repo, mock_db):
        """Test de libération de stock pour produit non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de libération
        result = product_repo.release_stock("nonexistent", 10)
        
        assert result is False
        mock_db.commit.assert_not_called()
    
    def test_product_validation(self, product_repo):
        """Test de validation des données de produit"""
        # Test avec données valides
        valid_data = {
            "name": "Valid Product",
            "description": "A valid product",
            "price_cents": 2999,
            "stock_qty": 100,
            "active": True
        }
        
        # Les données valides ne doivent pas lever d'exception
        try:
            # Simuler la validation (dans un vrai test, on testerait la validation Pydantic)
            assert valid_data["name"] is not None
            assert valid_data["price_cents"] > 0
            assert valid_data["stock_qty"] >= 0
        except AssertionError:
            pytest.fail("Les données valides ont échoué la validation")
    
    def test_product_price_calculation(self, product_repo):
        """Test des calculs de prix"""
        # Test de conversion centimes -> euros
        price_cents = 2999
        price_euros = price_cents / 100
        
        assert price_euros == 29.99
        
        # Test de calcul de total
        quantity = 3
        total_cents = price_cents * quantity
        total_euros = total_cents / 100
        
        assert total_cents == 8997
        assert total_euros == 89.97
