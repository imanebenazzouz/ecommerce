"""
Configuration commune pour tous les tests
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration des tests
TEST_DATABASE_URL = "postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce_test"
API_BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

@pytest.fixture(scope="session")
def test_config():
    """Configuration pour les tests"""
    return {
        "database_url": TEST_DATABASE_URL,
        "api_base_url": API_BASE_URL,
        "frontend_url": FRONTEND_URL,
        "test_user_email": "test@example.com",
        "test_user_password": "password123",
        "admin_email": "admin@ecommerce.com",
        "admin_password": "admin123"
    }

@pytest.fixture
def mock_database():
    """Mock de la base de données pour les tests unitaires"""
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None
    return mock_db

@pytest.fixture
def sample_user_data():
    """Données d'utilisateur de test"""
    return {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "address": "123 Test Street"
    }

@pytest.fixture
def sample_product_data():
    """Données de produit de test"""
    return {
        "name": "Test Product",
        "description": "A test product",
        "price_cents": 2999,
        "stock_qty": 100,
        "active": True
    }

@pytest.fixture
def sample_order_data():
    """Données de commande de test"""
    return {
        "user_id": "test-user-id",
        "status": "CREE",
        "items": [
            {
                "product_id": "test-product-id",
                "name": "Test Product",
                "unit_price_cents": 2999,
                "quantity": 2
            }
        ]
    }

@pytest.fixture
def sample_payment_data():
    """Données de paiement de test"""
    return {
        "card_number": "4242424242424242",
        "exp_month": 12,
        "exp_year": 2025,
        "cvc": "123"
    }

# Marqueurs pour les différents types de tests
def pytest_configure(config):
    """Configuration des marqueurs pytest"""
    config.addinivalue_line("markers", "unit: Tests unitaires")
    config.addinivalue_line("markers", "integration: Tests d'intégration")
    config.addinivalue_line("markers", "e2e: Tests end-to-end")
    config.addinivalue_line("markers", "slow: Tests lents")
    config.addinivalue_line("markers", "auth: Tests d'authentification")
    config.addinivalue_line("markers", "products: Tests de produits")
    config.addinivalue_line("markers", "cart: Tests de panier")
    config.addinivalue_line("markers", "orders: Tests de commandes")
    config.addinivalue_line("markers", "payments: Tests de paiements")
    config.addinivalue_line("markers", "admin: Tests d'administration")

# Configuration des logs pour les tests
def pytest_runtest_setup(item):
    """Setup avant chaque test"""
    print(f"\n🧪 Exécution du test: {item.name}")

def pytest_runtest_teardown(item):
    """Teardown après chaque test"""
    print(f"✅ Test terminé: {item.name}")

# Gestion des erreurs communes
@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup automatique pour tous les tests"""
    # Configuration de l'environnement de test
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    
    yield
    
    # Nettoyage après les tests
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
