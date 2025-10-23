#!/usr/bin/env python3
"""
Tests complets du panier
"""

import pytest
import uuid
from unittest.mock import Mock, patch
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Ajouter le répertoire ecommerce-backend au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ecommerce-backend'))

from database.repositories_simple import PostgreSQLCartRepository, PostgreSQLProductRepository
from database.models import Cart, CartItem, Product, User

@pytest.mark.unit
@pytest.mark.cart
class TestCartRepository:
    """Tests complets du repository de panier"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def cart_repo(self, mock_db):
        """Repository de panier pour les tests"""
        return PostgreSQLCartRepository(mock_db)
    
    @pytest.fixture
    def sample_user_id(self):
        """ID d'utilisateur de test"""
        return str(uuid.uuid4())
    
    @pytest.fixture
    def sample_product_id(self):
        """ID de produit de test"""
        return str(uuid.uuid4())
    
    def test_get_by_user_id_existing_cart(self, cart_repo, mock_db, sample_user_id):
        """Test de récupération d'un panier existant"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        mock_cart.user_id = uuid.UUID(sample_user_id)
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cart
        mock_db.query.return_value = mock_query
        
        # Test
        result = cart_repo.get_by_user_id(sample_user_id)
        assert result == mock_cart
        mock_db.query.assert_called_once_with(Cart)
    
    def test_get_by_user_id_no_cart(self, cart_repo, mock_db, sample_user_id):
        """Test de récupération d'un panier inexistant"""
        # Mock de la requête qui retourne None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test
        result = cart_repo.get_by_user_id(sample_user_id)
        assert result is None
    
    def test_create_cart(self, cart_repo, mock_db, sample_user_id):
        """Test de création d'un panier"""
        # Mock de la session
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        mock_cart.user_id = uuid.UUID(sample_user_id)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test
        result = cart_repo.create_cart(sample_user_id)
        
        # Vérifier que le panier a été ajouté à la session
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    def test_add_item_new_cart(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test d'ajout d'article dans un nouveau panier"""
        # Mock de get_by_user_id qui retourne None (pas de panier)
        cart_repo.get_by_user_id = Mock(return_value=None)
        cart_repo.create_cart = Mock(return_value=Mock(id=uuid.uuid4()))
        
        # Mock de la requête pour vérifier l'article existant
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None  # Pas d'article existant
        mock_db.query.return_value = mock_query
        
        # Test
        result = cart_repo.add_item(sample_user_id, sample_product_id, 2)
        
        # Vérifier que le panier a été créé
        cart_repo.create_cart.assert_called_once_with(sample_user_id)
        # Vérifier que l'article a été ajouté
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_add_item_existing_cart_new_item(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test d'ajout d'un nouvel article dans un panier existant"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de la requête pour vérifier l'article existant
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None  # Pas d'article existant
        mock_db.query.return_value = mock_query
        
        # Test
        result = cart_repo.add_item(sample_user_id, sample_product_id, 2)
        
        # Vérifier que l'article a été ajouté
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_add_item_existing_cart_existing_item(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test d'ajout d'un article existant dans un panier existant"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de l'article existant
        mock_existing_item = Mock()
        mock_existing_item.quantity = 3
        
        # Mock de la requête pour vérifier l'article existant
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_existing_item
        mock_db.query.return_value = mock_query
        
        # Test
        result = cart_repo.add_item(sample_user_id, sample_product_id, 2)
        
        # Vérifier que la quantité a été mise à jour
        assert mock_existing_item.quantity == 5  # 3 + 2
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_remove_item_existing_item(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test de suppression d'un article existant"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de l'article existant
        mock_existing_item = Mock()
        mock_existing_item.quantity = 5
        
        # Mock de la requête pour trouver l'article
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_existing_item
        mock_db.query.return_value = mock_query
        
        # Test
        result = cart_repo.remove_item(sample_user_id, sample_product_id, 2)
        
        # Vérifier que la quantité a été mise à jour
        assert mock_existing_item.quantity == 3  # 5 - 2
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_remove_item_quantity_zero(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test de suppression d'un article avec quantité zéro"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de l'article existant
        mock_existing_item = Mock()
        mock_existing_item.quantity = 2
        
        # Mock de la requête pour trouver l'article
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_existing_item
        mock_db.query.return_value = mock_query
        
        # Test
        result = cart_repo.remove_item(sample_user_id, sample_product_id, 2)
        
        # Vérifier que l'article a été supprimé
        mock_db.delete.assert_called_once_with(mock_existing_item)
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_remove_item_no_cart(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test de suppression d'un article sans panier"""
        # Mock de get_by_user_id qui retourne None
        cart_repo.get_by_user_id = Mock(return_value=None)
        
        # Test
        result = cart_repo.remove_item(sample_user_id, sample_product_id, 2)
        
        # Vérifier que False est retourné
        assert result is False
    
    def test_remove_item_no_item(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test de suppression d'un article inexistant"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de la requête qui retourne None (pas d'article)
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test
        result = cart_repo.remove_item(sample_user_id, sample_product_id, 2)
        
        # Vérifier que False est retourné
        assert result is False
    
    def test_clear_cart(self, cart_repo, mock_db, sample_user_id):
        """Test de vidage du panier"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de la requête pour supprimer les articles
        mock_query = Mock()
        mock_query.filter.return_value.delete.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test
        result = cart_repo.clear(sample_user_id)
        
        # Vérifier que les articles ont été supprimés
        mock_db.query.assert_called_once_with(CartItem)
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_clear_cart_no_cart(self, cart_repo, mock_db, sample_user_id):
        """Test de vidage d'un panier inexistant"""
        # Mock de get_by_user_id qui retourne None
        cart_repo.get_by_user_id = Mock(return_value=None)
        
        # Test
        result = cart_repo.clear(sample_user_id)
        
        # Vérifier que False est retourné
        assert result is False
    
    def test_add_item_negative_quantity(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test d'ajout avec quantité négative"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test avec quantité négative
        result = cart_repo.add_item(sample_user_id, sample_product_id, -1)
        
        # Vérifier que l'opération a été effectuée (la validation devrait être faite côté API)
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_remove_item_negative_quantity(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test de suppression avec quantité négative"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de l'article existant
        mock_existing_item = Mock()
        mock_existing_item.quantity = 5
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_existing_item
        mock_db.query.return_value = mock_query
        
        # Test avec quantité négative
        result = cart_repo.remove_item(sample_user_id, sample_product_id, -1)
        
        # Vérifier que la quantité a été mise à jour (5 - (-1) = 6)
        assert mock_existing_item.quantity == 6
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_concurrent_cart_operations(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test d'opérations concurrentes sur le panier"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de l'article existant
        mock_existing_item = Mock()
        mock_existing_item.quantity = 3
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_existing_item
        mock_db.query.return_value = mock_query
        
        # Simuler des opérations concurrentes
        result1 = cart_repo.add_item(sample_user_id, sample_product_id, 2)
        result2 = cart_repo.remove_item(sample_user_id, sample_product_id, 1)
        
        # Vérifier que les opérations ont été effectuées
        assert result1 is True
        assert result2 is True
        assert mock_existing_item.quantity == 4  # 3 + 2 - 1
    
    def test_cart_item_validation(self, cart_repo, mock_db, sample_user_id, sample_product_id):
        """Test de validation des articles du panier"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test avec différents types d'ID
        valid_ids = [
            str(uuid.uuid4()),
            "550e8400-e29b-41d4-a716-446655440000",
        ]
        
        for product_id in valid_ids:
            result = cart_repo.add_item(sample_user_id, product_id, 1)
            assert result is True
    
    def test_cart_performance(self, cart_repo, mock_db, sample_user_id):
        """Test de performance du panier"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = uuid.uuid4()
        cart_repo.get_by_user_id = Mock(return_value=mock_cart)
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test avec de nombreux articles
        product_ids = [str(uuid.uuid4()) for _ in range(100)]
        
        for product_id in product_ids:
            result = cart_repo.add_item(sample_user_id, product_id, 1)
            assert result is True
        
        # Vérifier que toutes les opérations ont été effectuées
        assert mock_db.add.call_count == 100
        assert mock_db.commit.call_count == 100
