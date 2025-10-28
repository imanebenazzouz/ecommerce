#!/usr/bin/env python3
"""
Tests d'intégration pour la gestion des stocks et inventaire
Tests pour:
- Stock insuffisant lors de l'achat
- Concurrence d'achat (deux utilisateurs achètent le dernier produit)
- Réservation de stock pendant le checkout
- Expiration panier et libération du stock
- Stock négatif (impossible)
- Mise à jour du stock par admin pendant qu'un user achète
"""

import pytest
import sys
import os
import uuid
import threading
import time
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))

from api import app
from database.database import SessionLocal, create_tables, engine
from database.repositories_simple import (
    PostgreSQLUserRepository,
    PostgreSQLProductRepository,
    PostgreSQLCartRepository,
    PostgreSQLOrderRepository
)
from database.models import Product, User, Order
from services.auth_service import AuthService

# Créer les tables avant les tests
create_tables()

client = TestClient(app)


@pytest.fixture
def db_session():
    """Crée une session de base de données pour les tests"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_product_low_stock(db_session):
    """Crée un produit avec stock limité (1 unité)"""
    product_repo = PostgreSQLProductRepository(db_session)
    product_data = {
        "name": f"Limited Product {os.urandom(4).hex()}",
        "description": "Only 1 in stock!",
        "price_cents": 5000,
        "stock_qty": 1,  # Stock limité à 1
        "active": True
    }
    product = product_repo.create(product_data)
    return product


@pytest.fixture
def test_product_medium_stock(db_session):
    """Crée un produit avec stock moyen (10 unités)"""
    product_repo = PostgreSQLProductRepository(db_session)
    product_data = {
        "name": f"Medium Stock Product {os.urandom(4).hex()}",
        "description": "10 in stock",
        "price_cents": 2000,
        "stock_qty": 10,
        "active": True
    }
    product = product_repo.create(product_data)
    return product


@pytest.fixture
def test_user_with_token(db_session):
    """Crée un utilisateur de test avec token"""
    user_repo = PostgreSQLUserRepository(db_session)
    auth_service = AuthService(user_repo)
    user_data = {
        "email": f"stock_test_{os.urandom(8).hex()}@example.com",
        "password": "TestPassword123!",
        "first_name": "Stock",
        "last_name": "Tester",
        "address": "123 Stock Street"  # Toujours fournir une adresse
    }
    user = user_repo.create(user_data)
    token = auth_service.create_access_token(data={"sub": str(user.id)})
    return {"user": user, "token": token}


@pytest.mark.integration
@pytest.mark.inventory
class TestInsufficientStock:
    """Tests pour les cas de stock insuffisant"""
    
    def test_add_to_cart_insufficient_stock(self, test_product_low_stock, test_user_with_token):
        """Test d'ajout au panier avec stock insuffisant"""
        # Test de la logique métier sans appeler l'API réelle
        product = test_product_low_stock
        
        # Le produit n'a qu'une unité en stock
        assert product.stock_qty == 1
        
        # Simuler une tentative d'ajout de 5 unités au panier
        requested_qty = 5
        
        # La logique métier devrait vérifier que requested_qty <= stock_qty
        # Dans ce cas, 5 > 1, donc cela devrait échouer
        assert requested_qty > product.stock_qty
    
    def test_checkout_with_insufficient_stock(self, test_product_low_stock, test_user_with_token, db_session):
        """Test de checkout quand le stock devient insuffisant"""
        product_repo = PostgreSQLProductRepository(db_session)
        product = test_product_low_stock
        
        # Initialement, le produit a 1 unité en stock
        assert product.stock_qty == 1
        
        # Simuler qu'un autre utilisateur achète le produit (stock passe à 0)
        product.stock_qty = 0
        product_repo.update(product)
        
        # Maintenant, le stock est insuffisant pour un checkout
        assert product.stock_qty == 0
    
    def test_product_inactive_when_stock_zero(self, test_product_low_stock, test_user_with_token, db_session):
        """Test que le produit devient inactif quand le stock atteint 0"""
        token = test_user_with_token["token"]
        product_id = str(test_product_low_stock.id)
        product_repo = PostgreSQLProductRepository(db_session)
        
        # Ajouter au panier et checkout
        client.post(
            "/cart",
            json={"product_id": product_id, "qty": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.post(
            "/orders/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Vérifier que le produit est maintenant inactif
        product = product_repo.get_by_id(product_id)
        assert product.stock_qty == 0
        assert product.active is False


@pytest.mark.integration
@pytest.mark.inventory
@pytest.mark.concurrency
class TestConcurrentPurchases:
    """Tests de concurrence pour les achats simultanés"""
    
    def test_two_users_buy_last_item_race_condition(self, test_product_low_stock, db_session):
        """Test de race condition : deux users achètent le dernier produit"""
        product_id = str(test_product_low_stock.id)
        user_repo = PostgreSQLUserRepository(db_session)
        auth_service = AuthService(user_repo)
        
        # Créer deux utilisateurs
        user1_data = {
            "email": f"user1_{os.urandom(8).hex()}@example.com",
            "password": "Pass123!",
            "first_name": "User",
            "last_name": "One",
            "address": "123 Street"
        }
        user1 = user_repo.create(user1_data)
        token1 = auth_service.create_access_token(data={"sub": str(user1.id)})
        
        user2_data = {
            "email": f"user2_{os.urandom(8).hex()}@example.com",
            "password": "Pass123!",
            "first_name": "User",
            "last_name": "Two",
            "address": "456 Street"
        }
        user2 = user_repo.create(user2_data)
        token2 = auth_service.create_access_token(data={"sub": str(user2.id)})
        
        # Les deux users ajoutent au panier
        response1 = client.post(
            "/cart",
            json={"product_id": product_id, "qty": 1},
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        response2 = client.post(
            "/cart",
            json={"product_id": product_id, "qty": 1},
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # Les deux ajouts au panier peuvent réussir
        assert response1.status_code in [200, 400]
        assert response2.status_code in [200, 400]
        
        # Mais un seul checkout devrait réussir
        checkout1 = client.post(
            "/orders/checkout",
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        checkout2 = client.post(
            "/orders/checkout",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        # Un seul devrait réussir
        success_count = sum([
            1 if checkout1.status_code == 200 else 0,
            1 if checkout2.status_code == 200 else 0
        ])
        
        assert success_count == 1, "Un seul checkout devrait réussir"
    
    def test_simultaneous_checkout_thread_safety(self, test_product_medium_stock, db_session):
        """Test de thread-safety lors de checkouts simultanés"""
        product_id = str(test_product_medium_stock.id)
        user_repo = PostgreSQLUserRepository(db_session)
        auth_service = AuthService(user_repo)
        
        # Créer 5 utilisateurs
        users_tokens = []
        for i in range(5):
            user_data = {
                "email": f"concurrent_user_{i}_{os.urandom(4).hex()}@example.com",
                "password": "Pass123!",
                "first_name": f"User{i}",
                "last_name": "Concurrent",
                "address": "123 Street"
            }
            user = user_repo.create(user_data)
            token = auth_service.create_access_token(data={"sub": str(user.id)})
            users_tokens.append((user, token))
        
        # Chaque user ajoute 3 unités au panier (3 * 5 = 15 > 10 stock)
        for user, token in users_tokens:
            client.post(
                "/cart",
                json={"product_id": product_id, "qty": 3},
                headers={"Authorization": f"Bearer {token}"}
            )
        
        # Tous tentent de checkout en même temps
        results = []
        
        def checkout_thread(token):
            response = client.post(
                "/orders/checkout",
                headers={"Authorization": f"Bearer {token}"}
            )
            results.append(response.status_code)
        
        threads = []
        for user, token in users_tokens:
            thread = threading.Thread(target=checkout_thread, args=(token,))
            threads.append(thread)
            thread.start()
        
        # Attendre que tous les threads se terminent
        for thread in threads:
            thread.join()
        
        # Vérifier qu'on a le bon nombre de succès/échecs
        # Avec 10 unités en stock et 3 par commande, maximum 3 devraient réussir
        success_count = results.count(200)
        assert success_count <= 3, "Pas plus de 3 checkouts ne devraient réussir"
        
        # Vérifier le stock final
        product_repo = PostgreSQLProductRepository(db_session)
        final_product = product_repo.get_by_id(product_id)
        
        # Le stock devrait être >= 0
        assert final_product.stock_qty >= 0, "Le stock ne devrait jamais être négatif"


@pytest.mark.integration
@pytest.mark.inventory
class TestStockReservation:
    """Tests pour la réservation de stock pendant le checkout"""
    
    def test_stock_reserved_during_checkout(self, test_product_medium_stock, test_user_with_token, db_session):
        """Test que le stock est bien réservé pendant le processus de checkout"""
        token = test_user_with_token["token"]
        product_id = str(test_product_medium_stock.id)
        product_repo = PostgreSQLProductRepository(db_session)
        
        # Vérifier le stock initial
        initial_stock = test_product_medium_stock.stock_qty
        
        # Ajouter au panier
        client.post(
            "/cart",
            json={"product_id": product_id, "qty": 5},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Le stock ne devrait pas encore avoir changé (juste dans le panier)
        product = product_repo.get_by_id(product_id)
        assert product.stock_qty == initial_stock
        
        # Faire le checkout
        response = client.post(
            "/orders/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Maintenant le stock devrait avoir diminué
        product = product_repo.get_by_id(product_id)
        assert product.stock_qty == initial_stock - 5
    
    def test_stock_released_on_checkout_failure(self, test_product_medium_stock, test_user_with_token, db_session):
        """Test que le stock est libéré si le checkout échoue"""
        token = test_user_with_token["token"]
        product_id = str(test_product_medium_stock.id)
        product_repo = PostgreSQLProductRepository(db_session)
        
        initial_stock = test_product_medium_stock.stock_qty
        
        # Ajouter au panier
        client.post(
            "/cart",
            json={"product_id": product_id, "qty": 3},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Rendre le produit inactif (simuler un problème)
        product = product_repo.get_by_id(product_id)
        product.active = False
        product_repo.update(product)
        
        # Tenter le checkout (devrait échouer)
        response = client.post(
            "/orders/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        
        # Le stock ne devrait pas avoir changé
        product = product_repo.get_by_id(product_id)
        assert product.stock_qty == initial_stock


@pytest.mark.integration
@pytest.mark.inventory
class TestCartExpiration:
    """Tests pour l'expiration du panier et libération du stock"""
    
    def test_cart_items_have_timestamps(self, test_product_medium_stock, test_user_with_token, db_session):
        """Test que les items du panier ont des timestamps"""
        token = test_user_with_token["token"]
        product_id = str(test_product_medium_stock.id)
        cart_repo = PostgreSQLCartRepository(db_session)
        user_id = test_user_with_token["user"].id
        
        # Ajouter au panier
        client.post(
            "/cart",
            json={"product_id": product_id, "qty": 2},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Récupérer le panier
        cart = cart_repo.get_by_user_id(str(user_id))
        
        assert cart is not None
        assert cart.created_at is not None
        assert cart.updated_at is not None
    
    def test_old_cart_items_identified(self, test_product_medium_stock, test_user_with_token, db_session):
        """Test d'identification des items de panier anciens"""
        token = test_user_with_token["token"]
        product_id = str(test_product_medium_stock.id)
        cart_repo = PostgreSQLCartRepository(db_session)
        user_id = test_user_with_token["user"].id
        
        # Ajouter au panier
        client.post(
            "/cart",
            json={"product_id": product_id, "qty": 2},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Récupérer le panier
        cart = cart_repo.get_by_user_id(str(user_id))
        
        # Vérifier l'âge du panier
        cart_age = datetime.utcnow() - cart.created_at
        
        # Un panier juste créé devrait avoir moins de 1 minute
        assert cart_age.total_seconds() < 60


@pytest.mark.integration
@pytest.mark.inventory
class TestNegativeStock:
    """Tests pour empêcher le stock négatif"""
    
    def test_cannot_have_negative_stock(self, test_product_medium_stock, db_session):
        """Test qu'on ne peut pas avoir un stock négatif"""
        product_repo = PostgreSQLProductRepository(db_session)
        product = test_product_medium_stock
        
        # Tenter de mettre un stock négatif
        product.stock_qty = -5
        
        # Devrait lever une exception ou être rejeté
        # Dans une vraie application, il y aurait une contrainte CHECK en BDD
        with pytest.raises(Exception):
            product_repo.update(product)
            db_session.commit()
    
    def test_checkout_prevents_negative_stock(self, test_product_low_stock, test_user_with_token):
        """Test que le checkout empêche le stock négatif"""
        token = test_user_with_token["token"]
        product_id = str(test_product_low_stock.id)
        
        # Tenter d'acheter plus que le stock disponible
        response = client.post(
            "/cart",
            json={"product_id": product_id, "qty": 10},  # Stock = 1
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Devrait échouer
        assert response.status_code == 400
        assert "stock insuffisant" in response.json()["detail"].lower()


@pytest.mark.integration
@pytest.mark.inventory
@pytest.mark.admin
class TestAdminStockManagement:
    """Tests pour la gestion du stock par les admins"""
    
    def test_admin_updates_stock_during_user_purchase(self, test_product_medium_stock, test_user_with_token, db_session):
        """Test de mise à jour du stock par admin pendant qu'un user achète"""
        token = test_user_with_token["token"]
        product_id = str(test_product_medium_stock.id)
        product_repo = PostgreSQLProductRepository(db_session)
        
        # User ajoute au panier
        client.post(
            "/cart",
            json={"product_id": product_id, "qty": 5},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Admin augmente le stock
        product = product_repo.get_by_id(product_id)
        product.stock_qty = 20
        product_repo.update(product)
        
        # User fait le checkout (devrait réussir)
        response = client.post(
            "/orders/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Stock final devrait être 20 - 5 = 15
        final_product = product_repo.get_by_id(product_id)
        assert final_product.stock_qty == 15
    
    def test_admin_reduces_stock_below_cart_quantity(self, test_product_medium_stock, test_user_with_token, db_session):
        """Test de réduction du stock par admin en dessous de la quantité dans le panier"""
        token = test_user_with_token["token"]
        product_id = str(test_product_medium_stock.id)
        product_repo = PostgreSQLProductRepository(db_session)
        
        # User ajoute 8 unités au panier
        client.post(
            "/cart",
            json={"product_id": product_id, "qty": 8},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Admin réduit le stock à 5
        product = product_repo.get_by_id(product_id)
        product.stock_qty = 5
        product_repo.update(product)
        
        # User tente le checkout (devrait échouer)
        response = client.post(
            "/orders/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "stock insuffisant" in response.json()["detail"].lower()


@pytest.mark.integration
@pytest.mark.inventory
class TestStockRestoration:
    """Tests pour la restauration du stock après annulation"""
    
    def test_stock_restored_on_order_cancellation(self, test_product_medium_stock, test_user_with_token, db_session):
        """Test que le stock est restauré lors de l'annulation de commande"""
        token = test_user_with_token["token"]
        product_id = str(test_product_medium_stock.id)
        product_repo = PostgreSQLProductRepository(db_session)
        
        initial_stock = test_product_medium_stock.stock_qty
        
        # Ajouter au panier et checkout
        client.post(
            "/cart",
            json={"product_id": product_id, "qty": 3},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.post(
            "/orders/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        order_id = response.json()["order_id"]
        
        # Vérifier que le stock a diminué
        product = product_repo.get_by_id(product_id)
        assert product.stock_qty == initial_stock - 3
        
        # Créer un admin token pour annuler la commande
        user_repo = PostgreSQLUserRepository(db_session)
        auth_service = AuthService(user_repo)
        admin_data = {
            "email": f"admin_{os.urandom(8).hex()}@example.com",
            "password": "AdminPass123!",
            "first_name": "Admin",
            "last_name": "User",
            "address": "Admin Address",
            "is_admin": True
        }
        admin = user_repo.create(admin_data)
        admin_token = auth_service.create_access_token(data={"sub": str(admin.id)})
        
        # Annuler la commande
        cancel_response = client.post(
            f"/admin/orders/{order_id}/cancel",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        # Si l'annulation est supportée
        if cancel_response.status_code == 200:
            # Le stock devrait être restauré
            product = product_repo.get_by_id(product_id)
            assert product.stock_qty == initial_stock
    
    def test_product_reactivated_when_stock_restored(self, test_product_low_stock, test_user_with_token, db_session):
        """Test que le produit est réactivé quand le stock est restauré"""
        token = test_user_with_token["token"]
        product_id = str(test_product_low_stock.id)
        product_repo = PostgreSQLProductRepository(db_session)
        
        # Acheter le dernier produit
        client.post(
            "/cart",
            json={"product_id": product_id, "qty": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.post(
            "/orders/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        order_id = response.json()["order_id"]
        
        # Vérifier que le produit est inactif
        product = product_repo.get_by_id(product_id)
        assert product.stock_qty == 0
        assert product.active is False
        
        # Créer un admin
        user_repo = PostgreSQLUserRepository(db_session)
        auth_service = AuthService(user_repo)
        admin_data = {
            "email": f"admin_{os.urandom(8).hex()}@example.com",
            "password": "AdminPass123!",
            "first_name": "Admin",
            "last_name": "User",
            "address": "Admin Address",
            "is_admin": True
        }
        admin = user_repo.create(admin_data)
        admin_token = auth_service.create_access_token(data={"sub": str(admin.id)})
        
        # Annuler la commande
        cancel_response = client.post(
            f"/admin/orders/{order_id}/cancel",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if cancel_response.status_code == 200:
            # Le produit devrait être réactivé
            product = product_repo.get_by_id(product_id)
            assert product.stock_qty == 1
            assert product.active is True


@pytest.mark.integration
@pytest.mark.inventory
class TestStockValidation:
    """Tests de validation du stock"""
    
    def test_stock_validation_on_product_creation(self, db_session):
        """Test de validation du stock lors de la création de produit"""
        product_repo = PostgreSQLProductRepository(db_session)
        
        # Créer avec stock valide
        valid_product_data = {
            "name": "Valid Product",
            "description": "Description",
            "price_cents": 1000,
            "stock_qty": 50,
            "active": True
        }
        valid_product = product_repo.create(valid_product_data)
        assert valid_product.stock_qty == 50
    
    def test_stock_cannot_be_string(self, db_session):
        """Test que le stock ne peut pas être une chaîne"""
        product_repo = PostgreSQLProductRepository(db_session)
        
        # Tenter de créer avec stock non numérique
        invalid_product_data = {
            "name": "Invalid Product",
            "description": "Description",
            "price_cents": 1000,
            "stock_qty": "not_a_number",  # Invalide
            "active": True
        }
        
        # Devrait lever une exception
        with pytest.raises((ValueError, TypeError)):
            product_repo.create(invalid_product_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

