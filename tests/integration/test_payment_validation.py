"""
Tests d'intégration pour les validations de paiement API
Ces tests vérifient que les validations strictes sont bien appliquées côté API
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))

from api import app
from database.database import get_db, SessionLocal, create_tables
from database.repositories_simple import (
    PostgreSQLUserRepository,
    PostgreSQLProductRepository,
    PostgreSQLOrderRepository,
    PostgreSQLCartRepository
)
from services.auth_service import AuthService

# Créer les tables avant les tests
create_tables()

client = TestClient(app)
auth_service = AuthService()


@pytest.fixture
def db_session():
    """Crée une session de base de données pour les tests"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(db_session):
    """Crée un utilisateur de test"""
    user_repo = PostgreSQLUserRepository(db_session)
    user_data = {
        "email": f"test_payment_{os.urandom(8).hex()}@example.com",
        "password": "Test1234!",
        "first_name": "Test",
        "last_name": "User"
    }
    user = user_repo.create(user_data)
    return user


@pytest.fixture
def test_product(db_session):
    """Crée un produit de test"""
    product_repo = PostgreSQLProductRepository(db_session)
    product_data = {
        "name": "Test Product",
        "description": "Test Description",
        "price_cents": 1000,  # 10.00 EUR
        "stock_qty": 100,
        "active": True
    }
    product = product_repo.create(product_data)
    return product


@pytest.fixture
def test_order(db_session, test_user, test_product):
    """Crée une commande de test"""
    order_repo = PostgreSQLOrderRepository(db_session)
    order_data = {
        "user_id": str(test_user.id),
        "items": [
            {
                "product_id": str(test_product.id),
                "name": test_product.name,
                "unit_price_cents": test_product.price_cents,
                "quantity": 2
            }
        ]
    }
    order = order_repo.create(order_data)
    return order


@pytest.fixture
def auth_token(test_user):
    """Crée un token d'authentification pour l'utilisateur de test"""
    token = auth_service.create_access_token(data={"sub": str(test_user.id)})
    return token


class TestPaymentValidationAPI:
    """Tests d'intégration pour l'API de paiement"""

    def test_payment_with_valid_data(self, test_order, auth_token):
        """Test avec toutes les données valides"""
        payment_data = {
            "card_number": "4242424242424242",  # Numéro valide (Luhn OK)
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCEEDED"
        assert "payment_id" in data

    def test_payment_with_invalid_card_number_luhn(self, test_order, auth_token):
        """Test avec un numéro de carte invalide (échec Luhn)"""
        payment_data = {
            "card_number": "4242424242424241",  # Luhn invalide
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
        assert "invalide" in response.json()["detail"].lower()

    def test_payment_with_invalid_card_length(self, test_order, auth_token):
        """Test avec un numéro de carte de longueur invalide"""
        payment_data = {
            "card_number": "42424242",  # Trop court
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
        assert "13 à 19" in response.json()["detail"]

    def test_payment_with_invalid_cvv(self, test_order, auth_token):
        """Test avec un CVV invalide"""
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "12",  # Trop court
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
        assert "CVV" in response.json()["detail"]

    def test_payment_with_past_expiry_date(self, test_order, auth_token):
        """Test avec une date d'expiration passée"""
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 1,
            "exp_year": 2020,  # Passé
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
        assert "expiration" in response.json()["detail"].lower()

    def test_payment_with_invalid_postal_code(self, test_order, auth_token):
        """Test avec un code postal invalide"""
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "7500",  # Trop court
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
        assert "postal" in response.json()["detail"].lower()
        assert "5 chiffres" in response.json()["detail"]

    def test_payment_with_invalid_phone(self, test_order, auth_token):
        """Test avec un téléphone invalide"""
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "061234567",  # Trop court
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
        assert "téléphone" in response.json()["detail"].lower()
        assert "10 chiffres" in response.json()["detail"]

    def test_payment_with_invalid_street_number(self, test_order, auth_token):
        """Test avec un numéro de rue invalide"""
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "abc"  # Lettres
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
        assert "rue" in response.json()["detail"].lower()

    def test_payment_card_ending_with_0000_refused(self, test_order, auth_token):
        """Test qu'une carte se terminant par 0000 est refusée (règle métier)"""
        payment_data = {
            "card_number": "4242424242420000",  # Se termine par 0000 (mais Luhn valide)
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Doit être refusé avec un code 402 (Payment Required)
        assert response.status_code == 402
        assert "refusé" in response.json()["detail"].lower()

    def test_payment_with_spaces_in_fields(self, test_order, auth_token):
        """Test que les espaces sont correctement gérés (sanitization)"""
        payment_data = {
            "card_number": "4242 4242 4242 4242",  # Avec espaces
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75 001",  # Avec espace
            "phone": "06 12 34 56 78",  # Avec espaces
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Doit réussir car la sanitization est appliquée
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCEEDED"

    def test_payment_without_optional_fields(self, test_order, auth_token):
        """Test que les champs optionnels peuvent être omis"""
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123"
            # postal_code, phone, street_number omis
        }
        
        response = client.post(
            f"/orders/{test_order.id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Doit réussir car ces champs sont optionnels
        assert response.status_code == 200

    def test_error_messages_in_french(self, test_order, auth_token):
        """Test que tous les messages d'erreur sont en français"""
        # Test plusieurs cas d'erreur
        test_cases = [
            {
                "data": {"card_number": "1234", "exp_month": 12, "exp_year": 2030, "cvc": "123"},
                "expected_words": ["chiffres", "carte"]
            },
            {
                "data": {"card_number": "4242424242424242", "exp_month": 13, "exp_year": 2030, "cvc": "123"},
                "expected_words": ["mois"]
            },
            {
                "data": {"card_number": "4242424242424242", "exp_month": 12, "exp_year": 2030, "cvc": "12"},
                "expected_words": ["CVV", "chiffres"]
            }
        ]
        
        for test_case in test_cases:
            response = client.post(
                f"/orders/{test_order.id}/pay",
                json=test_case["data"],
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == 422
            detail = response.json()["detail"].lower()
            
            # Vérifier qu'au moins un des mots attendus est présent
            assert any(word.lower() in detail for word in test_case["expected_words"])

