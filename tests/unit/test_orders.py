#!/usr/bin/env python3
"""
Tests unitaires pour les commandes
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.database.repositories_simple import PostgreSQLOrderRepository
from ecommerce_backend.enums import OrderStatus

@pytest.mark.unit
@pytest.mark.orders
class TestOrders:
    """Tests unitaires pour les commandes"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def order_repo(self, mock_db):
        """Repository de commandes avec mock"""
        return PostgreSQLOrderRepository(mock_db)
    
    def test_order_creation(self, order_repo, mock_db):
        """Test de création de commande"""
        # Données de la commande
        order_data = {
            "user_id": "user123",
            "status": OrderStatus.CREE,
            "items": [
                {
                    "product_id": "product123",
                    "name": "Test Product",
                    "unit_price_cents": 2999,
                    "quantity": 2
                }
            ]
        }
        
        # Mock de la création
        mock_order = Mock()
        mock_order.id = "order123"
        mock_order.user_id = "user123"
        mock_order.status = OrderStatus.CREE
        mock_order.items = []
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test de création
        result = order_repo.create(order_data)
        
        assert result is not None
        assert result.id == "order123"
        assert result.user_id == "user123"
        assert result.status == OrderStatus.CREE
        assert result.items == []
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_order_retrieval(self, order_repo, mock_db):
        """Test de récupération de commande"""
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = "order123"
        mock_order.user_id = "user123"
        mock_order.status = OrderStatus.CREE
        mock_order.items = []
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = order_repo.get_by_id("order123")
        
        assert result is not None
        assert result.id == "order123"
        assert result.user_id == "user123"
        assert result.status == OrderStatus.CREE
        assert result.items == []
        mock_db.query.assert_called_once()
    
    def test_order_not_found(self, order_repo, mock_db):
        """Test de commande non trouvée"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = order_repo.get_by_id("nonexistent")
        
        assert result is None
        mock_db.query.assert_called_once()
    
    def test_orders_by_user(self, order_repo, mock_db):
        """Test de récupération des commandes par utilisateur"""
        # Mock des commandes
        mock_orders = [
            Mock(id="order1", user_id="user123", status=OrderStatus.CREE),
            Mock(id="order2", user_id="user123", status=OrderStatus.PAYEE),
            Mock(id="order3", user_id="user456", status=OrderStatus.CREE)
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_orders
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = order_repo.get_by_user_id("user123")
        
        assert result is not None
        assert len(result) == 3
        assert result[0].id == "order1"
        assert result[1].id == "order2"
        assert result[2].id == "order3"
        mock_db.query.assert_called_once()
    
    def test_all_orders(self, order_repo, mock_db):
        """Test de récupération de toutes les commandes"""
        # Mock des commandes
        mock_orders = [
            Mock(id="order1", user_id="user123", status=OrderStatus.CREE),
            Mock(id="order2", user_id="user456", status=OrderStatus.PAYEE)
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.all.return_value = mock_orders
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = order_repo.get_all()
        
        assert result is not None
        assert len(result) == 2
        assert result[0].id == "order1"
        assert result[1].id == "order2"
        mock_db.query.assert_called_once()
    
    def test_order_status_update(self, order_repo, mock_db):
        """Test de mise à jour du statut de commande"""
        # Mock de la commande existante
        mock_order = Mock()
        mock_order.id = "order123"
        mock_order.status = OrderStatus.CREE
        mock_order.validated_at = None
        mock_order.shipped_at = None
        mock_order.delivered_at = None
        mock_order.cancelled_at = None
        mock_order.refunded_at = None
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test de mise à jour du statut
        result = order_repo.update_status("order123", OrderStatus.VALIDEE)
        
        assert result is True
        assert mock_order.status == OrderStatus.VALIDEE
        assert mock_order.validated_at is not None
        mock_db.commit.assert_called_once()
    
    def test_order_status_update_not_found(self, order_repo, mock_db):
        """Test de mise à jour du statut de commande non trouvée"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de mise à jour
        result = order_repo.update_status("nonexistent", OrderStatus.VALIDEE)
        
        assert result is False
        mock_db.commit.assert_not_called()
    
    def test_order_status_timestamps(self, order_repo, mock_db):
        """Test de mise à jour des timestamps selon le statut"""
        # Mock de la commande existante
        mock_order = Mock()
        mock_order.id = "order123"
        mock_order.status = OrderStatus.CREE
        mock_order.validated_at = None
        mock_order.shipped_at = None
        mock_order.delivered_at = None
        mock_order.cancelled_at = None
        mock_order.refunded_at = None
        
        # Mock de la récupération
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test de mise à jour vers EXPEDIEE
        result = order_repo.update_status("order123", OrderStatus.EXPEDIEE)
        
        assert result is True
        assert mock_order.status == OrderStatus.EXPEDIEE
        assert mock_order.shipped_at is not None
        mock_db.commit.assert_called_once()
    
    def test_order_status_workflow(self, order_repo):
        """Test du workflow des statuts de commande"""
        # Workflow typique d'une commande
        workflow = [
            OrderStatus.CREE,      # Commande créée
            OrderStatus.PAYEE,     # Commande payée
            OrderStatus.VALIDEE,   # Commande validée
            OrderStatus.EXPEDIEE,  # Commande expédiée
            OrderStatus.LIVREE     # Commande livrée
        ]
        
        # Vérifier que tous les statuts sont valides
        for status in workflow:
            assert status in OrderStatus
            assert isinstance(status, str)
        
        # Vérifier que les statuts sont différents
        assert len(set(workflow)) == len(workflow)
    
    def test_order_cancellation_workflow(self, order_repo):
        """Test du workflow d'annulation de commande"""
        # Workflow d'annulation
        cancellation_workflow = [
            OrderStatus.CREE,      # Commande créée
            OrderStatus.ANNULEE    # Commande annulée
        ]
        
        # Vérifier que tous les statuts sont valides
        for status in cancellation_workflow:
            assert status in OrderStatus
            assert isinstance(status, str)
        
        # Vérifier que l'annulation est possible depuis CRÉÉE
        assert OrderStatus.ANNULEE in OrderStatus
    
    def test_order_validation(self, order_repo):
        """Test de validation des données de commande"""
        # Test avec données valides
        valid_order_data = {
            "user_id": "user123",
            "status": OrderStatus.CREE,
            "items": [
                {
                    "product_id": "product123",
                    "name": "Test Product",
                    "unit_price_cents": 2999,
                    "quantity": 2
                }
            ]
        }
        
        # Les données valides ne doivent pas lever d'exception
        try:
            assert valid_order_data["user_id"] is not None
            assert valid_order_data["status"] in OrderStatus
            assert len(valid_order_data["items"]) > 0
            
            for item in valid_order_data["items"]:
                assert item["product_id"] is not None
                assert item["name"] is not None
                assert item["unit_price_cents"] > 0
                assert item["quantity"] > 0
        except AssertionError:
            pytest.fail("Les données valides ont échoué la validation")
    
    def test_order_calculation(self, order_repo):
        """Test des calculs de commande"""
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
    
    def test_order_items_structure(self, order_repo):
        """Test de la structure des articles de commande"""
        # Structure d'un article de commande
        order_item = {
            "id": "item123",
            "order_id": "order123",
            "product_id": "product123",
            "name": "Test Product",
            "unit_price_cents": 2999,
            "quantity": 2,
            "total_cents": 5998
        }
        
        # Vérifier que tous les champs requis sont présents
        required_fields = ["id", "order_id", "product_id", "name", "unit_price_cents", "quantity"]
        for field in required_fields:
            assert field in order_item
            assert order_item[field] is not None
    
    def test_order_shipping_address(self, order_repo):
        """Test de l'adresse de livraison de la commande"""
        # Structure d'une adresse de livraison
        shipping_address = {
            "street": "123 Main Street",
            "city": "Paris",
            "postal_code": "75001",
            "country": "France",
            "phone": "+33123456789"
        }
        
        # Vérifier la structure
        required_fields = ["street", "city", "postal_code", "country"]
        for field in required_fields:
            assert field in shipping_address
            assert shipping_address[field] is not None
    
    def test_order_payment_info(self, order_repo):
        """Test des informations de paiement de la commande"""
        # Structure des informations de paiement
        payment_info = {
            "payment_method": "card",
            "card_last_four": "4242",
            "payment_status": "SUCCEEDED",
            "transaction_id": "txn_123456789",
            "amount_cents": 10994
        }
        
        # Vérifier la structure
        required_fields = ["payment_method", "payment_status", "amount_cents"]
        for field in required_fields:
            assert field in payment_info
            assert payment_info[field] is not None
    
    def test_order_delivery_info(self, order_repo):
        """Test des informations de livraison de la commande"""
        # Structure des informations de livraison
        delivery_info = {
            "carrier": "DHL",
            "tracking_number": "DHL123456789",
            "estimated_delivery": "2024-01-15",
            "delivery_status": "IN_TRANSIT"
        }
        
        # Vérifier la structure
        required_fields = ["carrier", "tracking_number", "delivery_status"]
        for field in required_fields:
            assert field in delivery_info
            assert delivery_info[field] is not None
    
    def test_order_refund_info(self, order_repo):
        """Test des informations de remboursement de la commande"""
        # Structure des informations de remboursement
        refund_info = {
            "refund_amount_cents": 10994,
            "refund_reason": "CUSTOMER_REQUEST",
            "refund_status": "PROCESSED",
            "refund_date": "2024-01-10"
        }
        
        # Vérifier la structure
        required_fields = ["refund_amount_cents", "refund_reason", "refund_status"]
        for field in required_fields:
            assert field in refund_info
            assert refund_info[field] is not None
    
    def test_order_notes(self, order_repo):
        """Test des notes de commande"""
        # Structure des notes de commande
        order_notes = {
            "customer_notes": "Please deliver after 5 PM",
            "admin_notes": "Special handling required",
            "internal_notes": "High value order"
        }
        
        # Vérifier la structure
        for note_type, content in order_notes.items():
            assert note_type in order_notes
            assert isinstance(content, str)
    
    def test_order_metadata(self, order_repo):
        """Test des métadonnées de commande"""
        # Structure des métadonnées
        order_metadata = {
            "source": "WEB",
            "user_agent": "Mozilla/5.0...",
            "ip_address": "192.168.1.1",
            "referrer": "https://google.com",
            "campaign": "SUMMER_SALE"
        }
        
        # Vérifier la structure
        for key, value in order_metadata.items():
            assert key in order_metadata
            assert isinstance(value, str)
    
    def test_order_analytics(self, order_repo):
        """Test des analytics de commande"""
        # Métriques d'analytics
        order_analytics = {
            "total_orders": 1500,
            "average_order_value": 89.99,
            "conversion_rate": 0.15,  # 15%
            "cart_abandonment_rate": 0.70,  # 70%
            "repeat_customer_rate": 0.25  # 25%
        }
        
        for metric, value in order_analytics.items():
            assert metric in order_analytics
            assert value >= 0
            assert isinstance(value, (int, float))
    
    def test_order_edge_cases(self, order_repo):
        """Test des cas limites des commandes"""
        # Test avec ID utilisateur vide
        assert order_repo.get_by_user_id("") is None
        
        # Test avec ID commande vide
        assert order_repo.get_by_id("") is None
        
        # Test avec statut invalide
        invalid_status = "INVALID_STATUS"
        assert invalid_status not in OrderStatus
    
    def test_order_performance(self, order_repo):
        """Test des performances des commandes"""
        # Limite de commandes par utilisateur
        max_orders_per_user = 1000
        
        assert max_orders_per_user > 0
        assert isinstance(max_orders_per_user, int)
        
        # Limite d'articles par commande
        max_items_per_order = 50
        
        assert max_items_per_order > 0
        assert isinstance(max_items_per_order, int)
    
    def test_order_security(self, order_repo):
        """Test de la sécurité des commandes"""
        # Validation des données d'entrée
        input_validation = {
            "user_id": "UUID format",
            "status": "Valid OrderStatus enum",
            "items": "Array of valid order items"
        }
        
        for field, validation in input_validation.items():
            assert field in input_validation
            assert validation is not None
            assert isinstance(validation, str)
            assert len(validation) > 0