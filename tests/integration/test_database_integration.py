#!/usr/bin/env python3
"""
Tests d'intégration pour la base de données
"""

import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.database.models import Base, User, Product, Order
from ecommerce_backend.database.repositories_simple import PostgreSQLUserRepository, PostgreSQLProductRepository
from ecommerce_backend.services.auth_service import AuthService

@pytest.mark.integration
@pytest.mark.database
class TestDatabaseIntegration:
    """Tests d'intégration de la base de données"""
    
    @pytest.fixture(scope="class")
    def test_engine(self):
        """Moteur de base de données de test"""
        database_url = os.getenv("TEST_DATABASE_URL", "postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce_test")
        engine = create_engine(database_url, echo=False)
        
        # Créer les tables
        Base.metadata.create_all(engine)
        
        yield engine
        
        # Nettoyer après les tests
        Base.metadata.drop_all(engine)
    
    @pytest.fixture
    def test_session(self, test_engine):
        """Session de base de données de test"""
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        session = SessionLocal()
        
        yield session
        
        session.close()
    
    def test_user_repository_integration(self, test_session):
        """Test d'intégration du repository utilisateur"""
        user_repo = PostgreSQLUserRepository(test_session)
        auth_service = AuthService(user_repo)
        
        # Créer un utilisateur
        user_data = {
            "email": "integration@test.com",
            "password_hash": auth_service.hash_password("password123"),
            "first_name": "Integration",
            "last_name": "Test",
            "address": "123 Integration Street",
            "is_admin": False
        }
        
        user = user_repo.create(user_data)
        assert user is not None
        assert user.email == "integration@test.com"
        assert user.first_name == "Integration"
        
        # Récupérer l'utilisateur
        retrieved_user = user_repo.get_by_id(str(user.id))
        assert retrieved_user is not None
        assert retrieved_user.email == user.email
        
        # Récupérer par email
        user_by_email = user_repo.get_by_email("integration@test.com")
        assert user_by_email is not None
        assert user_by_email.id == user.id
        
        # Mettre à jour l'utilisateur
        updated_user = user_repo.update(str(user.id), {"first_name": "Updated"})
        assert updated_user is not None
        assert updated_user.first_name == "Updated"
        
        # Supprimer l'utilisateur
        success = user_repo.delete(str(user.id))
        assert success is True
        
        # Vérifier la suppression
        deleted_user = user_repo.get_by_id(str(user.id))
        assert deleted_user is None
    
    def test_product_repository_integration(self, test_session):
        """Test d'intégration du repository produit"""
        product_repo = PostgreSQLProductRepository(test_session)
        
        # Créer un produit
        product_data = {
            "name": "Integration Test Product",
            "description": "A product for integration testing",
            "price_cents": 2999,
            "stock_qty": 100,
            "active": True
        }
        
        product = product_repo.create(product_data)
        assert product is not None
        assert product.name == "Integration Test Product"
        assert product.price_cents == 2999
        assert product.stock_qty == 100
        
        # Récupérer le produit
        retrieved_product = product_repo.get_by_id(str(product.id))
        assert retrieved_product is not None
        assert retrieved_product.name == product.name
        
        # Tester la gestion du stock
        success = product_repo.reserve_stock(str(product.id), 10)
        assert success is True
        
        # Vérifier que le stock a été réservé
        updated_product = product_repo.get_by_id(str(product.id))
        assert updated_product.stock_qty == 90
        
        # Libérer le stock
        success = product_repo.release_stock(str(product.id), 5)
        assert success is True
        
        # Vérifier que le stock a été libéré
        final_product = product_repo.get_by_id(str(product.id))
        assert final_product.stock_qty == 95
        
        # Tester la réservation avec stock insuffisant
        success = product_repo.reserve_stock(str(product.id), 1000)
        assert success is False
        
        # Supprimer le produit
        success = product_repo.delete(str(product.id))
        assert success is True
    
    def test_database_transactions(self, test_session):
        """Test des transactions de base de données"""
        user_repo = PostgreSQLUserRepository(test_session)
        product_repo = PostgreSQLProductRepository(test_session)
        
        # Créer un utilisateur et un produit dans la même transaction
        user_data = {
            "email": "transaction@test.com",
            "password_hash": "hashed_password",
            "first_name": "Transaction",
            "last_name": "Test",
            "address": "123 Transaction Street",
            "is_admin": False
        }
        
        product_data = {
            "name": "Transaction Test Product",
            "description": "A product for transaction testing",
            "price_cents": 1999,
            "stock_qty": 50,
            "active": True
        }
        
        user = user_repo.create(user_data)
        product = product_repo.create(product_data)
        
        assert user is not None
        assert product is not None
        
        # Vérifier que les deux entités existent
        retrieved_user = user_repo.get_by_id(str(user.id))
        retrieved_product = product_repo.get_by_id(str(product.id))
        
        assert retrieved_user is not None
        assert retrieved_product is not None
        
        # Nettoyer
        user_repo.delete(str(user.id))
        product_repo.delete(str(product.id))
    
    def test_database_constraints(self, test_session):
        """Test des contraintes de base de données"""
        user_repo = PostgreSQLUserRepository(test_session)
        
        # Créer un utilisateur
        user_data = {
            "email": "constraint@test.com",
            "password_hash": "hashed_password",
            "first_name": "Constraint",
            "last_name": "Test",
            "address": "123 Constraint Street",
            "is_admin": False
        }
        
        user = user_repo.create(user_data)
        assert user is not None
        
        # Tenter de créer un utilisateur avec le même email
        duplicate_user_data = user_data.copy()
        duplicate_user_data["first_name"] = "Duplicate"
        
        # Cela devrait échouer à cause de la contrainte unique sur l'email
        with pytest.raises(Exception):  # SQLAlchemy exception
            user_repo.create(duplicate_user_data)
        
        # Nettoyer
        user_repo.delete(str(user.id))
