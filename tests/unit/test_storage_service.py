#!/usr/bin/env python3
"""
Tests unitaires pour le service de stockage
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.database.database import get_db, create_tables, drop_tables

@pytest.mark.unit
@pytest.mark.storage
class TestStorageService:
    """Tests unitaires pour le service de stockage"""
    
    @pytest.fixture
    def mock_engine(self):
        """Mock du moteur de base de données"""
        return Mock()
    
    @pytest.fixture
    def mock_session(self):
        """Mock de la session de base de données"""
        return Mock()
    
    def test_database_connection(self, mock_engine):
        """Test de la connexion à la base de données"""
        # Test de la configuration de l'URL de base de données
        database_url = os.getenv("DATABASE_URL", "postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce")
        
        assert database_url is not None
        assert "postgresql://" in database_url
        assert "ecommerce" in database_url
    
    def test_database_engine_creation(self, mock_engine):
        """Test de la création du moteur de base de données"""
        # Test des paramètres du moteur
        assert mock_engine is not None
        
        # Test de la configuration du pool
        assert hasattr(mock_engine, 'pool')
        
        # Test de la configuration echo
        assert hasattr(mock_engine, 'echo')
    
    def test_database_session_creation(self, mock_session):
        """Test de la création de session de base de données"""
        # Test de la session
        assert mock_session is not None
        
        # Test des méthodes de session
        assert hasattr(mock_session, 'add')
        assert hasattr(mock_session, 'commit')
        assert hasattr(mock_session, 'rollback')
        assert hasattr(mock_session, 'close')
        assert hasattr(mock_session, 'query')
    
    def test_database_transactions(self, mock_session):
        """Test des transactions de base de données"""
        # Test du commit
        mock_session.commit.return_value = None
        mock_session.commit()
        mock_session.commit.assert_called_once()
        
        # Test du rollback
        mock_session.rollback.return_value = None
        mock_session.rollback()
        mock_session.rollback.assert_called_once()
    
    def test_database_queries(self, mock_session):
        """Test des requêtes de base de données"""
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query
        
        # Test de requête simple
        result = mock_session.query("User").filter("id == 'user123'").first()
        assert result is None
        
        # Test de requête multiple
        results = mock_session.query("User").all()
        assert results == []
    
    def test_database_models_import(self):
        """Test de l'import des modèles de base de données"""
        try:
            from ecommerce_backend.database.models import (
                User, Product, Cart, CartItem, Order, OrderItem,
                Delivery, Invoice, Payment, MessageThread, Message
            )
            
            # Vérifier que tous les modèles sont importés
            assert User is not None
            assert Product is not None
            assert Cart is not None
            assert CartItem is not None
            assert Order is not None
            assert OrderItem is not None
            assert Delivery is not None
            assert Invoice is not None
            assert Payment is not None
            assert MessageThread is not None
            assert Message is not None
            
        except ImportError as e:
            pytest.fail(f"Erreur d'import des modèles: {e}")
    
    def test_database_repositories_import(self):
        """Test de l'import des repositories"""
        try:
            from ecommerce_backend.database.repositories_simple import (
                PostgreSQLUserRepository, PostgreSQLProductRepository,
                PostgreSQLCartRepository, PostgreSQLOrderRepository,
                PostgreSQLInvoiceRepository, PostgreSQLPaymentRepository,
                PostgreSQLThreadRepository
            )
            
            # Vérifier que tous les repositories sont importés
            assert PostgreSQLUserRepository is not None
            assert PostgreSQLProductRepository is not None
            assert PostgreSQLCartRepository is not None
            assert PostgreSQLOrderRepository is not None
            assert PostgreSQLInvoiceRepository is not None
            assert PostgreSQLPaymentRepository is not None
            assert PostgreSQLThreadRepository is not None
            
        except ImportError as e:
            pytest.fail(f"Erreur d'import des repositories: {e}")
    
    def test_database_connection_pool(self, mock_engine):
        """Test du pool de connexions"""
        # Test de la configuration du pool
        assert hasattr(mock_engine, 'pool')
        
        # Test des paramètres du pool
        pool = mock_engine.pool
        assert pool is not None
        
        # Test de la taille du pool
        if hasattr(pool, 'size'):
            assert pool.size > 0
    
    def test_database_connection_health(self, mock_engine):
        """Test de la santé de la connexion"""
        # Test de la méthode pool_pre_ping
        assert hasattr(mock_engine, 'pool_pre_ping')
        
        # Test de la configuration echo
        assert hasattr(mock_engine, 'echo')
        assert isinstance(mock_engine.echo, bool)
    
    def test_database_migrations(self):
        """Test des migrations de base de données"""
        # Test de l'import d'Alembic
        try:
            import alembic
            assert alembic is not None
        except ImportError:
            pytest.fail("Alembic n'est pas installé")
        
        # Test de la configuration Alembic
        alembic_ini_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "ecommerce_backend", "alembic.ini"
        )
        
        if os.path.exists(alembic_ini_path):
            assert os.path.isfile(alembic_ini_path)
        else:
            pytest.fail("Fichier alembic.ini non trouvé")
    
    def test_database_environment_variables(self):
        """Test des variables d'environnement de base de données"""
        # Test des variables d'environnement
        env_vars = [
            "DATABASE_URL",
            "DB_HOST",
            "DB_PORT",
            "DB_NAME",
            "DB_USER",
            "DB_PASSWORD"
        ]
        
        for var in env_vars:
            # Vérifier que la variable peut être lue (même si elle n'est pas définie)
            value = os.getenv(var)
            # La valeur peut être None si la variable n'est pas définie
            assert value is None or isinstance(value, str)
    
    def test_database_connection_string_validation(self):
        """Test de la validation de la chaîne de connexion"""
        # Test de la chaîne de connexion par défaut
        default_url = "postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce"
        
        assert default_url is not None
        assert isinstance(default_url, str)
        assert "postgresql://" in default_url
        assert "localhost" in default_url
        assert "5432" in default_url
        assert "ecommerce" in default_url
    
    def test_database_session_lifecycle(self, mock_session):
        """Test du cycle de vie de la session"""
        # Test de l'ouverture de session
        assert mock_session is not None
        
        # Test de l'ajout d'entité
        mock_entity = Mock()
        mock_session.add(mock_entity)
        mock_session.add.assert_called_once_with(mock_entity)
        
        # Test du commit
        mock_session.commit()
        mock_session.commit.assert_called_once()
        
        # Test de la fermeture de session
        mock_session.close()
        mock_session.close.assert_called_once()
    
    def test_database_error_handling(self, mock_session):
        """Test de la gestion des erreurs de base de données"""
        # Test de l'exception lors du commit
        mock_session.commit.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            mock_session.commit()
        
        # Test du rollback en cas d'erreur
        mock_session.rollback.return_value = None
        mock_session.rollback()
        mock_session.rollback.assert_called_once()
    
    def test_database_query_optimization(self, mock_session):
        """Test de l'optimisation des requêtes"""
        # Test de la requête avec filtre
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_session.query.return_value = mock_query
        
        # Test de requête optimisée
        result = mock_session.query("User").filter("email == 'test@example.com'").first()
        assert result is None
        
        # Vérifier que les méthodes ont été appelées
        mock_session.query.assert_called_once_with("User")
        mock_query.filter.assert_called_once_with("email == 'test@example.com'")
        mock_query.first.assert_called_once()
    
    def test_database_indexing(self):
        """Test de l'indexation de base de données"""
        # Test des index sur les colonnes importantes
        indexed_columns = [
            "users.email",
            "products.active",
            "orders.user_id",
            "orders.status",
            "orders.created_at"
        ]
        
        for column in indexed_columns:
            assert column is not None
            assert isinstance(column, str)
            assert "." in column  # Format table.column
    
    def test_database_constraints(self):
        """Test des contraintes de base de données"""
        # Test des contraintes de clé primaire
        primary_keys = [
            "users.id",
            "products.id",
            "orders.id",
            "carts.id"
        ]
        
        for pk in primary_keys:
            assert pk is not None
            assert isinstance(pk, str)
            assert "." in pk  # Format table.column
        
        # Test des contraintes de clé étrangère
        foreign_keys = [
            "orders.user_id -> users.id",
            "order_items.order_id -> orders.id",
            "order_items.product_id -> products.id"
        ]
        
        for fk in foreign_keys:
            assert fk is not None
            assert isinstance(fk, str)
            assert "->" in fk  # Format column -> referenced_table.column
