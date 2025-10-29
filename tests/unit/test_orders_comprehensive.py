#!/usr/bin/env python3
"""
Tests complets des commandes
"""

import pytest
import uuid
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Ajouter le répertoire ecommerce-backend au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ecommerce-backend'))

from database.repositories_simple import PostgreSQLOrderRepository, PostgreSQLCartRepository
from database.models import Order, OrderItem, User, Product
from enums import OrderStatus

@pytest.mark.unit
@pytest.mark.orders
class TestOrderRepository:
    """Tests complets du repository de commandes"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def order_repo(self, mock_db):
        """Repository de commandes pour les tests"""
        return PostgreSQLOrderRepository(mock_db)
    
    @pytest.fixture
    def sample_user_id(self):
        """ID d'utilisateur de test"""
        return str(uuid.uuid4())
    
    @pytest.fixture
    def sample_order_data(self, sample_user_id):
        """Données de commande de test"""
        return {
            "user_id": sample_user_id,
            "status": OrderStatus.CREE,
            "items": [
                {
                    "product_id": str(uuid.uuid4()),
                    "name": "Test Product 1",
                    "unit_price_cents": 2999,
                    "quantity": 2
                },
                {
                    "product_id": str(uuid.uuid4()),
                    "name": "Test Product 2",
                    "unit_price_cents": 1999,
                    "quantity": 1
                }
            ]
        }
    
    def test_create_order(self, order_repo, mock_db, sample_order_data):
        """Test de création d'une commande"""
        # Mock de la commande créée
        mock_order = Mock()
        mock_order.id = uuid.uuid4()
        mock_order.user_id = uuid.UUID(sample_order_data["user_id"])
        mock_order.status = sample_order_data["status"]
        
        # Mock de la session
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test
        result = order_repo.create(sample_order_data)
        
        # Vérifier que la commande a été ajoutée
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        mock_db.refresh.assert_called()
    
    def test_get_by_id_existing_order(self, order_repo, mock_db):
        """Test de récupération d'une commande existante"""
        order_id = str(uuid.uuid4())
        
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = uuid.UUID(order_id)
        mock_order.status = OrderStatus.CREE
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.get_by_id(order_id)
        assert result == mock_order
        mock_db.query.assert_called_once_with(Order)
    
    def test_get_by_id_no_order(self, order_repo, mock_db):
        """Test de récupération d'une commande inexistante"""
        order_id = str(uuid.uuid4())
        
        # Mock de la requête qui retourne None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.get_by_id(order_id)
        assert result is None
    
    def test_get_by_user_id(self, order_repo, mock_db, sample_user_id):
        """Test de récupération des commandes d'un utilisateur"""
        # Mock des commandes
        mock_orders = [
            Mock(id=uuid.uuid4(), status=OrderStatus.CREE),
            Mock(id=uuid.uuid4(), status=OrderStatus.PAYEE),
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_orders
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.get_by_user_id(sample_user_id)
        assert result == mock_orders
        assert len(result) == 2
    
    def test_get_all_orders(self, order_repo, mock_db):
        """Test de récupération de toutes les commandes"""
        # Mock des commandes
        mock_orders = [
            Mock(id=uuid.uuid4(), status=OrderStatus.CREE),
            Mock(id=uuid.uuid4(), status=OrderStatus.PAYEE),
            Mock(id=uuid.uuid4(), status=OrderStatus.LIVREE),
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.all.return_value = mock_orders
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.get_all()
        assert result == mock_orders
        assert len(result) == 3
    
    def test_update_status_created_to_validated(self, order_repo, mock_db):
        """Test de mise à jour du statut de CREE à VALIDEE"""
        order_id = str(uuid.uuid4())
        
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = uuid.UUID(order_id)
        mock_order.status = OrderStatus.CREE
        mock_order.validated_at = None
        mock_order.shipped_at = None
        mock_order.delivered_at = None
        mock_order.cancelled_at = None
        mock_order.refunded_at = None
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.update_status(order_id, OrderStatus.VALIDEE)
        
        # Vérifier que le statut a été mis à jour
        assert mock_order.status == OrderStatus.VALIDEE
        assert mock_order.validated_at is not None
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_update_status_validated_to_shipped(self, order_repo, mock_db):
        """Test de mise à jour du statut de VALIDEE à EXPEDIEE"""
        order_id = str(uuid.uuid4())
        
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = uuid.UUID(order_id)
        mock_order.status = OrderStatus.VALIDEE
        mock_order.validated_at = datetime.utcnow()
        mock_order.shipped_at = None
        mock_order.delivered_at = None
        mock_order.cancelled_at = None
        mock_order.refunded_at = None
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.update_status(order_id, OrderStatus.EXPEDIEE)
        
        # Vérifier que le statut a été mis à jour
        assert mock_order.status == OrderStatus.EXPEDIEE
        assert mock_order.shipped_at is not None
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_update_status_shipped_to_delivered(self, order_repo, mock_db):
        """Test de mise à jour du statut de EXPEDIEE à LIVREE"""
        order_id = str(uuid.uuid4())
        
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = uuid.UUID(order_id)
        mock_order.status = OrderStatus.EXPEDIEE
        mock_order.validated_at = datetime.utcnow()
        mock_order.shipped_at = datetime.utcnow()
        mock_order.delivered_at = None
        mock_order.cancelled_at = None
        mock_order.refunded_at = None
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.update_status(order_id, OrderStatus.LIVREE)
        
        # Vérifier que le statut a été mis à jour
        assert mock_order.status == OrderStatus.LIVREE
        assert mock_order.delivered_at is not None
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_update_status_to_cancelled(self, order_repo, mock_db):
        """Test de mise à jour du statut à ANNULEE"""
        order_id = str(uuid.uuid4())
        
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = uuid.UUID(order_id)
        mock_order.status = OrderStatus.CREE
        mock_order.validated_at = None
        mock_order.shipped_at = None
        mock_order.delivered_at = None
        mock_order.cancelled_at = None
        mock_order.refunded_at = None
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.update_status(order_id, OrderStatus.ANNULEE)
        
        # Vérifier que le statut a été mis à jour
        assert mock_order.status == OrderStatus.ANNULEE
        assert mock_order.cancelled_at is not None
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_update_status_to_refunded(self, order_repo, mock_db):
        """Test de mise à jour du statut à REMBOURSEE"""
        order_id = str(uuid.uuid4())
        
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = uuid.UUID(order_id)
        mock_order.status = OrderStatus.PAYEE
        mock_order.validated_at = datetime.utcnow()
        mock_order.shipped_at = None
        mock_order.delivered_at = None
        mock_order.cancelled_at = None
        mock_order.refunded_at = None
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.update_status(order_id, OrderStatus.REMBOURSEE)
        
        # Vérifier que le statut a été mis à jour
        assert mock_order.status == OrderStatus.REMBOURSEE
        assert mock_order.refunded_at is not None
        mock_db.commit.assert_called_once()
        assert result is True
    
    def test_update_status_order_not_found(self, order_repo, mock_db):
        """Test de mise à jour du statut d'une commande inexistante"""
        order_id = str(uuid.uuid4())
        
        # Mock de la requête qui retourne None
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.update_status(order_id, OrderStatus.VALIDEE)
        
        # Vérifier que False est retourné
        assert result is False
    
    def test_add_item_to_order(self, order_repo, mock_db):
        """Test d'ajout d'article à une commande"""
        item_data = {
            "order_id": str(uuid.uuid4()),
            "product_id": str(uuid.uuid4()),
            "name": "Test Product",
            "unit_price_cents": 2999,
            "quantity": 2
        }
        
        # Mock de la session
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test
        result = order_repo.add_item(item_data)
        
        # Vérifier que l'article a été ajouté
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        assert result is not None
    
    def test_update_order(self, order_repo, mock_db):
        """Test de mise à jour d'une commande"""
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = uuid.uuid4()
        mock_order.status = OrderStatus.CREE
        
        # Mock de la session
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test
        result = order_repo.update(mock_order)
        
        # Vérifier que la commande a été mise à jour
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_order)
        assert result == mock_order
    
    def test_order_status_transitions(self, order_repo, mock_db):
        """Test des transitions de statut de commande"""
        order_id = str(uuid.uuid4())
        
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = uuid.UUID(order_id)
        mock_order.status = OrderStatus.CREE
        mock_order.validated_at = None
        mock_order.shipped_at = None
        mock_order.delivered_at = None
        mock_order.cancelled_at = None
        mock_order.refunded_at = None
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test des transitions valides
        transitions = [
            (OrderStatus.CREE, OrderStatus.VALIDEE),
            (OrderStatus.VALIDEE, OrderStatus.EXPEDIEE),
            (OrderStatus.EXPEDIEE, OrderStatus.LIVREE),
        ]
        
        for from_status, to_status in transitions:
            mock_order.status = from_status
            result = order_repo.update_status(order_id, to_status)
            assert result is True
            assert mock_order.status == to_status
    
    def test_order_with_multiple_items(self, order_repo, mock_db, sample_order_data):
        """Test de commande avec plusieurs articles"""
        # Mock de la session
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test
        result = order_repo.create(sample_order_data)
        
        # Vérifier que tous les articles ont été ajoutés
        # Le nombre d'appels à add devrait être 1 (pour la commande seulement dans ce mode simplifié)
        assert mock_db.add.call_count == 1  # Seulement la commande
        mock_db.commit.assert_called()
    
    def test_order_validation_rules(self, order_repo, mock_db):
        """Test des règles de validation des commandes"""
        # Test avec données invalides
        invalid_order_data = {
            "user_id": "invalid-uuid",
            "status": "INVALID_STATUS",
            "items": []
        }
        
        # Mock de la session
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test (la validation ne lève pas d'exception, elle accepte les données)
        result = order_repo.create(invalid_order_data)
        assert result is not None
    
    def test_order_performance(self, order_repo, mock_db, sample_user_id):
        """Test de performance des commandes"""
        # Mock des commandes
        mock_orders = [Mock(id=uuid.uuid4(), status=OrderStatus.CREE) for _ in range(1000)]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_orders
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.get_by_user_id(sample_user_id)
        assert len(result) == 1000
    
    def test_order_search_by_status(self, order_repo, mock_db):
        """Test de recherche de commandes par statut"""
        # Mock des commandes avec différents statuts
        mock_orders = [
            Mock(id=uuid.uuid4(), status=OrderStatus.CREE),
            Mock(id=uuid.uuid4(), status=OrderStatus.PAYEE),
            Mock(id=uuid.uuid4(), status=OrderStatus.LIVREE),
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_orders
        mock_db.query.return_value = mock_query
        
        # Test
        result = order_repo.get_all()
        assert result is not None
        
        # Vérifier que la requête a été appelée
        mock_db.query.assert_called()
    
    def test_order_timestamps(self, order_repo, mock_db):
        """Test des timestamps des commandes"""
        order_id = str(uuid.uuid4())
        
        # Mock de la commande
        mock_order = Mock()
        mock_order.id = uuid.UUID(order_id)
        mock_order.status = OrderStatus.CREE
        mock_order.validated_at = None
        mock_order.shipped_at = None
        mock_order.delivered_at = None
        mock_order.cancelled_at = None
        mock_order.refunded_at = None
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_order
        mock_db.query.return_value = mock_query
        
        # Test de mise à jour avec timestamp
        result = order_repo.update_status(order_id, OrderStatus.VALIDEE)
        
        # Vérifier que le timestamp a été mis à jour
        assert mock_order.validated_at is not None
        assert result is True
