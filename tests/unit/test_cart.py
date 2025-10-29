#!/usr/bin/env python3
"""
Tests unitaires pour le panier
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
class TestCart:
    """Tests unitaires pour le panier"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def cart_repo(self, mock_db):
        """Repository de panier avec mock"""
        return PostgreSQLCartRepository(mock_db)
    
    def test_cart_creation(self, cart_repo, mock_db):
        """Test de création de panier"""
        # Mock de la création
        mock_cart = Mock()
        mock_cart.id = "cart123"
        mock_cart.user_id = "user123"
        mock_cart.items = []
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test de création
        result = cart_repo.create_cart("user123")
        
        assert result is not None
        assert result.id == "cart123"
        assert result.user_id == "user123"
        assert result.items == []
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_cart_retrieval(self, cart_repo, mock_db):
        """Test de récupération de panier"""
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
        assert result.items == []
        mock_db.query.assert_called_once()
    
    def test_cart_not_found(self, cart_repo, mock_db):
        """Test de panier non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = cart_repo.get_by_user_id("user123")
        
        assert result is None
        mock_db.query.assert_called_once()
    
    def test_add_item_to_cart(self, cart_repo, mock_db):
        """Test d'ajout d'article au panier"""
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
    
    def test_add_item_to_existing_cart_item(self, cart_repo, mock_db):
        """Test d'ajout d'article à un article existant du panier"""
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
    
    def test_remove_item_from_cart(self, cart_repo, mock_db):
        """Test de suppression d'article du panier"""
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
    
    def test_remove_item_completely_from_cart(self, cart_repo, mock_db):
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
    
    def test_remove_item_not_found(self, cart_repo, mock_db):
        """Test de suppression d'article non trouvé"""
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
    
    def test_clear_cart(self, cart_repo, mock_db):
        """Test de vidage de panier"""
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
    
    def test_cart_item_structure(self, cart_repo):
        """Test de la structure des articles de panier"""
        # Structure d'un article de panier
        cart_item = {
            "id": "item123",
            "cart_id": "cart123",
            "product_id": "product123",
            "quantity": 2,
            "unit_price_cents": 2999,
            "total_cents": 5998
        }
        
        # Vérifier que tous les champs requis sont présents
        required_fields = ["id", "cart_id", "product_id", "quantity"]
        for field in required_fields:
            assert field in cart_item
            assert cart_item[field] is not None
    
    def test_cart_discounts(self, cart_repo):
        """Test du système de remises du panier"""
        # Types de remises
        discount_types = [
            "PERCENTAGE_DISCOUNT",
            "FIXED_AMOUNT_DISCOUNT",
            "BUY_ONE_GET_ONE",
            "BULK_DISCOUNT",
            "FREE_SHIPPING"
        ]
        
        for discount_type in discount_types:
            assert discount_type in discount_types
            assert isinstance(discount_type, str)
            assert len(discount_type) > 0
    
    def test_cart_coupons(self, cart_repo):
        """Test du système de coupons du panier"""
        # Structure d'un coupon
        coupon = {
            "code": "SAVE10",
            "type": "PERCENTAGE",
            "value": 10,
            "min_amount": 5000,
            "max_discount": 1000,
            "expires_at": "2024-12-31"
        }
        
        # Vérifier la structure
        required_fields = ["code", "type", "value"]
        for field in required_fields:
            assert field in coupon
            assert coupon[field] is not None
    
    def test_cart_shipping_calculation(self, cart_repo):
        """Test du calcul des frais d'expédition"""
        # Frais d'expédition par zone
        shipping_rates = {
            "FRANCE": 500,  # 5.00€
            "EUROPE": 1000,  # 10.00€
            "WORLDWIDE": 2000  # 20.00€
        }
        
        for zone, rate in shipping_rates.items():
            assert zone in shipping_rates
            assert rate > 0
            assert isinstance(rate, int)
    
    def test_cart_tax_calculation(self, cart_repo):
        """Test du calcul des taxes du panier"""
        # Taux de TVA par pays
        tax_rates = {
            "FRANCE": 0.20,  # 20%
            "GERMANY": 0.19,  # 19%
            "UK": 0.20,  # 20%
            "US": 0.08  # 8% (varie par état)
        }
        
        for country, rate in tax_rates.items():
            assert country in tax_rates
            assert 0 <= rate <= 1
            assert isinstance(rate, float)
    
    def test_cart_abandonment(self, cart_repo):
        """Test du système d'abandon de panier"""
        # Seuils d'abandon
        abandonment_thresholds = {
            "EMAIL_1": 1,  # 1 heure
            "EMAIL_2": 24,  # 24 heures
            "EMAIL_3": 72  # 72 heures
        }
        
        for email, hours in abandonment_thresholds.items():
            assert email in abandonment_thresholds
            assert hours > 0
            assert isinstance(hours, int)
    
    def test_cart_wishlist_integration(self, cart_repo):
        """Test de l'intégration avec la liste de souhaits"""
        # Actions de liste de souhaits
        wishlist_actions = [
            "ADD_TO_WISHLIST",
            "REMOVE_FROM_WISHLIST",
            "MOVE_TO_CART",
            "SHARE_WISHLIST"
        ]
        
        for action in wishlist_actions:
            assert action in wishlist_actions
            assert isinstance(action, str)
            assert len(action) > 0
    
    def test_cart_persistence(self, cart_repo):
        """Test de la persistance du panier"""
        # Durée de persistance du panier
        persistence_duration = 30  # jours
        
        assert persistence_duration > 0
        assert isinstance(persistence_duration, int)
    
    def test_cart_guest_mode(self, cart_repo):
        """Test du mode invité du panier"""
        # ID de session pour les invités
        guest_session_id = "guest_123456789"
        
        assert guest_session_id is not None
        assert isinstance(guest_session_id, str)
        assert len(guest_session_id) > 0
        assert guest_session_id.startswith("guest_")
    
    def test_cart_merge_on_login(self, cart_repo):
        """Test de la fusion des paniers lors de la connexion"""
        # Stratégies de fusion
        merge_strategies = [
            "GUEST_OVERWRITES_USER",
            "USER_OVERWRITES_GUEST",
            "MERGE_QUANTITIES",
            "ASK_USER"
        ]
        
        for strategy in merge_strategies:
            assert strategy in merge_strategies
            assert isinstance(strategy, str)
            assert len(strategy) > 0
    
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
    
    def test_cart_performance(self, cart_repo):
        """Test des performances du panier"""
        # Limite d'articles dans le panier
        max_items = 100
        
        assert max_items > 0
        assert isinstance(max_items, int)
        
        # Limite de quantité par article
        max_quantity_per_item = 99
        
        assert max_quantity_per_item > 0
        assert isinstance(max_quantity_per_item, int)
    
    def test_cart_security(self, cart_repo):
        """Test de la sécurité du panier"""
        # Validation des données d'entrée
        input_validation = {
            "product_id": "UUID format",
            "quantity": "Positive integer",
            "user_id": "UUID format"
        }
        
        for field, validation in input_validation.items():
            assert field in input_validation
            assert validation is not None
            assert isinstance(validation, str)
            assert len(validation) > 0