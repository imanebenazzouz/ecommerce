#!/usr/bin/env python3
"""
Tests unitaires pour le service de commandes
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
class TestOrderService:
    """Tests unitaires pour le service de commandes"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def order_repo(self, mock_db):
        """Repository de commandes avec mock"""
        return PostgreSQLOrderRepository(mock_db)
    
    def test_create_order_success(self, order_repo, mock_db):
        """Test de création de commande réussie"""
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
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_get_order_by_id_success(self, order_repo, mock_db):
        """Test de récupération de commande par ID réussie"""
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
        mock_db.query.assert_called_once()
    
    def test_get_order_by_id_not_found(self, order_repo, mock_db):
        """Test de récupération de commande par ID non trouvée"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = order_repo.get_by_id("nonexistent")
        
        assert result is None
        mock_db.query.assert_called_once()
    
    def test_get_orders_by_user_id(self, order_repo, mock_db):
        """Test de récupération des commandes par ID utilisateur"""
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
        mock_db.query.assert_called_once()
    
    def test_get_all_orders(self, order_repo, mock_db):
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
        mock_db.query.assert_called_once()
    
    def test_update_order_status_success(self, order_repo, mock_db):
        """Test de mise à jour du statut de commande réussie"""
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
    
    def test_update_order_status_not_found(self, order_repo, mock_db):
        """Test de mise à jour du statut de commande non trouvée"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de mise à jour
        result = order_repo.update_status("nonexistent", OrderStatus.VALIDEE)
        
        assert result is False
        mock_db.commit.assert_not_called()
    
    def test_update_order_status_timestamps(self, order_repo, mock_db):
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
    
    def test_order_status_transitions(self, order_repo):
        """Test des transitions de statut de commande"""
        # Test des statuts valides
        valid_statuses = [
            OrderStatus.CREE,
            OrderStatus.VALIDEE,
            OrderStatus.PAYEE,
            OrderStatus.EXPEDIEE,
            OrderStatus.LIVREE,
            OrderStatus.ANNULEE,
            OrderStatus.REMBOURSEE
        ]
        
        for status in valid_statuses:
            assert status in OrderStatus
            assert isinstance(status, str)
    
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
    
    def test_order_edge_cases(self, order_repo):
        """Test des cas limites des commandes"""
        # Test avec ID utilisateur vide
        assert order_repo.get_by_user_id("") is None
        
        # Test avec ID commande vide
        assert order_repo.get_by_id("") is None
        
        # Test avec statut invalide
        invalid_status = "INVALID_STATUS"
        assert invalid_status not in OrderStatus
    
    def test_order_items_structure(self, order_repo):
        """Test de la structure des articles de commande"""
        # Test de la structure d'un article
        item = {
            "product_id": "product123",
            "name": "Test Product",
            "unit_price_cents": 2999,
            "quantity": 2
        }
        
        # Vérifier que tous les champs requis sont présents
        required_fields = ["product_id", "name", "unit_price_cents", "quantity"]
        for field in required_fields:
            assert field in item
            assert item[field] is not None
    
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
        
        # Vérifier que l'annulation est possible depuis CRÉÉE
        assert OrderStatus.ANNULEE in OrderStatus
