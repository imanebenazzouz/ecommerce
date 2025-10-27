"""
Tests E2E pour le processus complet de checkout avec validation
Ces tests simulent le parcours complet d'un utilisateur:
1. Connexion
2. Ajout au panier
3. Création de commande
4. Paiement (happy path + erreurs)
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))

from api import app
from database.database import SessionLocal, create_tables
from database.repositories_simple import (
    PostgreSQLUserRepository,
    PostgreSQLProductRepository,
    PostgreSQLCartRepository
)
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
def setup_user_and_product(db_session):
    """Crée un utilisateur et un produit pour les tests E2E"""
    user_repo = PostgreSQLUserRepository(db_session)
    product_repo = PostgreSQLProductRepository(db_session)
    
    # Créer un utilisateur
    email = f"test_e2e_{os.urandom(8).hex()}@example.com"
    user_data = {
        "email": email,
        "password": "Test1234!",
        "first_name": "Test",
        "last_name": "E2E"
    }
    user = user_repo.create(user_data)
    
    # Créer un produit
    product_data = {
        "name": "Test Product E2E",
        "description": "Test Description",
        "price_cents": 2000,  # 20.00 EUR
        "stock_qty": 100,
        "active": True
    }
    product = product_repo.create(product_data)
    
    # Créer un token
    auth_service = AuthService(user_repo)
    token = auth_service.create_access_token(data={"sub": str(user.id)})
    
    return {
        "user": user,
        "product": product,
        "token": token,
        "email": email,
        "password": "Test1234!"
    }


class TestCheckoutHappyPath:
    """Tests E2E pour le parcours de checkout réussi"""

    def test_complete_checkout_flow_success(self, setup_user_and_product):
        """Test du parcours complet: ajout panier → checkout → paiement réussi"""
        data = setup_user_and_product
        token = data["token"]
        product_id = str(data["product"].id)
        
        # Étape 1: Ajouter un produit au panier
        response = client.post(
            "/cart",
            json={"product_id": product_id, "quantity": 2},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        # Étape 2: Vérifier le panier
        response = client.get(
            "/cart",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        cart = response.json()
        assert len(cart["items"]) == 1
        assert cart["items"][0]["product_id"] == product_id
        assert cart["items"][0]["quantity"] == 2
        
        # Étape 3: Créer une commande (checkout)
        response = client.post(
            "/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        order_data = response.json()
        order_id = order_data["order_id"]
        assert order_data["status"] == "CREE"
        assert order_data["total_cents"] == 4000  # 2 * 2000
        
        # Étape 4: Payer avec des données valides
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{order_id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        payment_result = response.json()
        assert payment_result["status"] == "SUCCEEDED"
        assert "payment_id" in payment_result
        assert payment_result["amount_cents"] == 4000
        
        # Étape 5: Vérifier que la commande est payée
        response = client.get(
            f"/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        order = response.json()
        assert order["status"] == "PAYEE"


class TestCheckoutErrorScenarios:
    """Tests E2E pour les scénarios d'erreur pendant le checkout"""

    def test_checkout_payment_invalid_card_number(self, setup_user_and_product):
        """Test checkout avec un numéro de carte invalide (Luhn)"""
        data = setup_user_and_product
        token = data["token"]
        product_id = str(data["product"].id)
        
        # Ajouter au panier et créer la commande
        client.post(
            "/cart",
            json={"product_id": product_id, "quantity": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.post(
            "/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = response.json()["order_id"]
        
        # Tenter de payer avec un numéro invalide
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
            f"/orders/{order_id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
        assert "invalide" in response.json()["detail"].lower()
        
        # Vérifier que la commande n'est pas payée
        response = client.get(
            f"/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.json()["status"] == "CREE"  # Toujours créée, pas payée

    def test_checkout_payment_expired_card(self, setup_user_and_product):
        """Test checkout avec une carte expirée"""
        data = setup_user_and_product
        token = data["token"]
        product_id = str(data["product"].id)
        
        # Ajouter au panier et créer la commande
        client.post(
            "/cart",
            json={"product_id": product_id, "quantity": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.post(
            "/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = response.json()["order_id"]
        
        # Tenter de payer avec une carte expirée
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 1,
            "exp_year": 2020,  # Expirée
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{order_id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
        assert "expiration" in response.json()["detail"].lower()

    def test_checkout_payment_invalid_cvv(self, setup_user_and_product):
        """Test checkout avec un CVV invalide"""
        data = setup_user_and_product
        token = data["token"]
        product_id = str(data["product"].id)
        
        # Ajouter au panier et créer la commande
        client.post(
            "/cart",
            json={"product_id": product_id, "quantity": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.post(
            "/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = response.json()["order_id"]
        
        # Tenter de payer avec un CVV invalide
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
            f"/orders/{order_id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
        assert "cvv" in response.json()["detail"].lower()

    def test_checkout_payment_invalid_postal_code(self, setup_user_and_product):
        """Test checkout avec un code postal invalide"""
        data = setup_user_and_product
        token = data["token"]
        product_id = str(data["product"].id)
        
        # Ajouter au panier et créer la commande
        client.post(
            "/cart",
            json={"product_id": product_id, "quantity": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.post(
            "/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = response.json()["order_id"]
        
        # Tenter de payer avec un code postal invalide
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
            f"/orders/{order_id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422
        assert "postal" in response.json()["detail"].lower()

    def test_checkout_payment_card_refused(self, setup_user_and_product):
        """Test checkout avec une carte refusée (se termine par 0000)"""
        data = setup_user_and_product
        token = data["token"]
        product_id = str(data["product"].id)
        
        # Ajouter au panier et créer la commande
        client.post(
            "/cart",
            json={"product_id": product_id, "quantity": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.post(
            "/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = response.json()["order_id"]
        
        # Tenter de payer avec une carte refusée
        payment_data = {
            "card_number": "4242424242420000",  # Se termine par 0000
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{order_id}/pay",
            json=payment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 402
        assert "refusé" in response.json()["detail"].lower()

    def test_checkout_retry_after_failed_payment(self, setup_user_and_product):
        """Test réessai de paiement après un échec"""
        data = setup_user_and_product
        token = data["token"]
        product_id = str(data["product"].id)
        
        # Ajouter au panier et créer la commande
        client.post(
            "/cart",
            json={"product_id": product_id, "quantity": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        response = client.post(
            "/checkout",
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = response.json()["order_id"]
        
        # Premier essai avec une carte invalide
        invalid_payment_data = {
            "card_number": "4242424242424241",  # Invalide
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{order_id}/pay",
            json=invalid_payment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 422
        
        # Réessayer avec une carte valide
        valid_payment_data = {
            "card_number": "4242424242424242",  # Valide
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0612345678",
            "street_number": "123"
        }
        
        response = client.post(
            f"/orders/{order_id}/pay",
            json=valid_payment_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Le paiement doit réussir
        assert response.status_code == 200
        assert response.json()["status"] == "SUCCEEDED"


class TestCheckoutQuantityValidation:
    """Tests E2E pour la validation des quantités"""

    def test_checkout_with_quantity_validation(self, setup_user_and_product):
        """Test que les quantités sont validées lors du checkout"""
        data = setup_user_and_product
        token = data["token"]
        product_id = str(data["product"].id)
        
        # Tenter d'ajouter une quantité de 0 (devrait échouer)
        response = client.post(
            "/cart",
            json={"product_id": product_id, "quantity": 0},
            headers={"Authorization": f"Bearer {token}"}
        )
        # Devrait échouer ou être ignoré
        assert response.status_code in [400, 422]
        
        # Ajouter une quantité valide
        response = client.post(
            "/cart",
            json={"product_id": product_id, "quantity": 5},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

