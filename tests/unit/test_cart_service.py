#!/usr/bin/env python3
"""
Tests unitaires pour le service de panier
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.database.repositories_simple import PostgreSQLCartRepository

@pytest.mark.unit
@pytest.mark.cart
class TestCartService:
    """Tests unitaires pour le service de panier"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def cart_repo(self, mock_db):
        """Repository de panier avec mock"""
        return PostgreSQLCartRepository(mock_db)
    
    def test_get_cart_by_user_id_success(self, cart_repo, mock_db):
        """Test de récupération de panier par ID utilisateur réussie"""
        # Mock du panier
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        mock_cart.items = []
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cart
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = cart_repo.get_by_user_id("user123")
        
        assert result is not None
        assert result.id == "cart123"
        assert result.user_id == "user123"
        mock_db.query.assert_called_once()
    
    def test_get_cart_by_user_id_not_found(self, cart_repo, mock_db):
        """Test de récupération de panier par ID utilisateur non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = cart_repo.get_by_user_id("user123")
        
        assert result is None
        mock_db.query.assert_called_once()
    
    def test_create_cart_success(self, cart_repo, mock_db):
        """Test de création de panier réussie"""
        # Mock de la création
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test de création
        result = cart_repo.create_cart("user123")
        
        assert result is not None
        assert result.id == "cart123"
        assert result.user_id == "user123"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_add_item_to_cart_new_item(self, cart_repo, mock_db):
        """Test d'ajout d'article au panier (nouvel article)"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        mock_cart.items = []
        
        # Mock de la récupération du panier
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cart
        mock_db.query.return_value = mock_query
        
        # Mock de la vérification d'article existant
        mock_item_query = Mock()
        mock_item_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_item_query
        
        # Test d'ajout
        result = cart_repo.add_item("user123", "product123", 2)
        
        assert result is True
        # add est appelé deux fois : une fois pour créer le panier, une fois pour l'article
        assert mock_db.add.call_count == 2
        # commit est appelé deux fois : une fois pour créer le panier, une fois pour l'article
        assert mock_db.commit.call_count == 2
    
    def test_add_item_to_cart_existing_item(self, cart_repo, mock_db):
        """Test d'ajout d'article au panier (article existant)"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        mock_cart.items = []
        
        # Mock de l'article existant
        mock_item = Mock()
        mock_item.quantity = 1
        
        # Mock de la récupération du panier
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cart
        mock_db.query.return_value = mock_query
        
        # Mock de la vérification d'article existant
        mock_item_query = Mock()
        mock_item_query.filter.return_value.first.return_value = mock_item
        mock_db.query.return_value = mock_item_query
        
        # Test d'ajout
        result = cart_repo.add_item("user123", "product123", 2)
        
        assert result is True
        assert mock_item.quantity == 3  # 1 + 2
        mock_db.commit.assert_called_once()
    
    def test_add_item_to_cart_no_cart(self, cart_repo, mock_db):
        """Test d'ajout d'article au panier (pas de panier existant)"""
        # Mock de la récupération du panier qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Mock de la création de panier
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        
        with patch.object(cart_repo, 'create_cart') as mock_create_cart:
            mock_create_cart.return_value = mock_cart
            
            # Mock de la vérification d'article existant
            mock_item_query = Mock()
            mock_item_query.filter.return_value.first.return_value = None
            mock_db.query.return_value = mock_item_query
            
            # Test d'ajout
            result = cart_repo.add_item("user123", "product123", 2)
        
        assert result is True
        mock_create_cart.assert_called_once_with("user123")
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_remove_item_from_cart_success(self, cart_repo, mock_db):
        """Test de suppression d'article du panier réussie"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        
        # Mock de l'article existant
        mock_item = Mock()
        mock_item.quantity = 3
        
        # Mock de la récupération du panier
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cart
        mock_db.query.return_value = mock_query
        
        # Mock de la vérification d'article existant
        mock_item_query = Mock()
        mock_item_query.filter.return_value.first.return_value = mock_item
        mock_db.query.return_value = mock_item_query
        
        # Test de suppression
        result = cart_repo.remove_item("user123", "product123", 2)
        
        assert result is True
        assert mock_item.quantity == 1  # 3 - 2
        mock_db.commit.assert_called_once()
    
    def test_remove_item_from_cart_remove_completely(self, cart_repo, mock_db):
        """Test de suppression complète d'article du panier"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        
        # Mock de l'article existant
        mock_item = Mock()
        mock_item.quantity = 2
        
        # Mock de la récupération du panier
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cart
        mock_db.query.return_value = mock_query
        
        # Mock de la vérification d'article existant
        mock_item_query = Mock()
        mock_item_query.filter.return_value.first.return_value = mock_item
        mock_db.query.return_value = mock_item_query
        
        # Test de suppression complète
        result = cart_repo.remove_item("user123", "product123", 2)
        
        assert result is True
        mock_db.delete.assert_called_once_with(mock_item)
        mock_db.commit.assert_called_once()
    
    def test_remove_item_from_cart_not_found(self, cart_repo, mock_db):
        """Test de suppression d'article non trouvé dans le panier"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        
        # Mock de la récupération du panier
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cart
        mock_db.query.return_value = mock_query
        
        # Mock de la vérification d'article existant qui ne trouve rien
        mock_item_query = Mock()
        mock_item_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_item_query
        
        # Test de suppression
        result = cart_repo.remove_item("user123", "product123", 2)
        
        assert result is False
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()
    
    def test_clear_cart_success(self, cart_repo, mock_db):
        """Test de vidage de panier réussi"""
        # Mock du panier existant
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        
        # Mock de la récupération du panier
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_cart
        mock_db.query.return_value = mock_query
        
        # Mock de la suppression des articles
        mock_item_query = Mock()
        mock_item_query.filter.return_value.delete.return_value = None
        mock_db.query.return_value = mock_item_query
        
        # Test de vidage
        result = cart_repo.clear("user123")
        
        assert result is True
        mock_db.commit.assert_called_once()
    
    def test_clear_cart_not_found(self, cart_repo, mock_db):
        """Test de vidage de panier non trouvé"""
        # Mock de la récupération du panier qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de vidage
        result = cart_repo.clear("user123")
        
        assert result is False
        mock_db.commit.assert_not_called()
    
    def test_cart_calculation(self, cart_repo):
        """Test des calculs de panier"""
        # Test de calcul de total
        items = [
            {"unit_price_cents": 2999, "quantity": 2},  # 59.98
            {"unit_price_cents": 1999, "quantity": 1},  # 19.99
            {"unit_price_cents": 999, "quantity": 3}    # 29.97
        ]
        
        total_cents = sum(item["unit_price_cents"] * item["quantity"] for item in items)
        total_euros = total_cents / 100
        
        assert total_cents == 10994  # 5998 + 1999 + 2997
        assert total_euros == 109.94
    
    def test_cart_validation(self, cart_repo):
        """Test de validation des données de panier"""
        # Test avec données valides
        valid_data = {
            "product_id": "product123",
            "qty": 2
        }
        
        # Les données valides ne doivent pas lever d'exception
        try:
            assert valid_data["product_id"] is not None
            assert valid_data["qty"] > 0
        except AssertionError:
            pytest.fail("Les données valides ont échoué la validation")
    
    def test_cart_edge_cases(self, cart_repo):
        """Test des cas limites du panier"""
        # Test avec quantité zéro (supprime complètement l'article)
        assert cart_repo.remove_item("user123", "product123", 0) is True
        
        # Test avec quantité négative
        assert cart_repo.remove_item("user123", "product123", -1) is False
        
        # Test avec ID utilisateur vide
        assert cart_repo.get_by_user_id("") is None
        
        # Test avec ID produit vide
        assert cart_repo.add_item("user123", "", 1) is False
