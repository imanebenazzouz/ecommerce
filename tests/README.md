# 🧪 Guide des Tests - E-Commerce

Ce dossier contient tous les tests de l'application e-commerce, organisés par catégorie.

## 📁 Structure des Tests

```
tests/
├── unit/                    # Tests unitaires
│   ├── test_auth.py        # Tests d'authentification
│   ├── test_products.py    # Tests de produits
│   ├── test_cart.py        # Tests de panier
│   ├── test_orders.py      # Tests de commandes
│   ├── test_payments.py    # Tests de paiements
│   ├── test_support.py     # Tests de support
│   └── test_api_endpoints.py # Tests d'endpoints
├── integration/            # Tests d'intégration
├── e2e/                   # Tests end-to-end
│   └── test_final.py      # Test complet de l'application
├── conftest.py            # Configuration commune
├── run_all_tests.py       # Script principal
├── run_unit_tests.py      # Script tests unitaires
├── run_integration_tests.py # Script tests d'intégration
├── run_e2e_tests.py       # Script tests end-to-end
└── README.md              # Ce fichier
```

## 🎯 Types de Tests

### Tests Unitaires (`unit/`)
Testent les composants individuels en isolation :
- **test_auth.py** : Authentification, hashage, tokens JWT
- **test_products.py** : CRUD produits, gestion stock
- **test_cart.py** : Opérations panier, calculs
- **test_orders.py** : Création commandes, statuts
- **test_payments.py** : Simulation paiements
- **test_support.py** : Système de tickets
- **test_api_endpoints.py** : Endpoints API individuels

### Tests d'Intégration (`integration/`)
Testent les interactions entre composants :
- Intégration base de données
- Intégration services
- Intégration repositories
- Flux de données complets

### Tests End-to-End (`e2e/`)
Testent l'application complète :
- **test_final.py** : Parcours utilisateur complet
- Scénarios réels d'utilisation
- Tests de bout en bout

## 🚀 Exécution des Tests

### Scripts de Test

#### Tous les tests
```bash
# Depuis la racine du projet
python run_all_tests.py

# Ou depuis le dossier tests
cd tests
python run_all_tests.py
```

#### Par catégorie
```bash
# Tests unitaires uniquement
python tests/run_unit_tests.py

# Tests d'intégration uniquement
python tests/run_integration_tests.py

# Tests end-to-end uniquement
python tests/run_e2e_tests.py
```

### Avec pytest

#### Installation
```bash
pip install pytest pytest-cov
```

#### Exécution
```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/

# Tests avec marqueurs
pytest -m unit
pytest -m integration
pytest -m e2e

# Avec couverture de code
pytest --cov=ecommerce-backend --cov-report=html

# Tests lents uniquement
pytest -m slow

# Tests d'authentification uniquement
pytest -m auth
```

## 📊 Marqueurs de Test

Les tests utilisent des marqueurs pour la catégorisation :

- `@pytest.mark.unit` : Tests unitaires
- `@pytest.mark.integration` : Tests d'intégration
- `@pytest.mark.e2e` : Tests end-to-end
- `@pytest.mark.slow` : Tests lents
- `@pytest.mark.auth` : Tests d'authentification
- `@pytest.mark.products` : Tests de produits
- `@pytest.mark.cart` : Tests de panier
- `@pytest.mark.orders` : Tests de commandes
- `@pytest.mark.payments` : Tests de paiements
- `@pytest.mark.admin` : Tests d'administration

### Utilisation des marqueurs
```python
import pytest

@pytest.mark.unit
@pytest.mark.auth
def test_user_login():
    """Test de connexion utilisateur"""
    pass

@pytest.mark.integration
@pytest.mark.orders
def test_order_creation_flow():
    """Test du flux de création de commande"""
    pass

@pytest.mark.e2e
@pytest.mark.slow
def test_complete_user_journey():
    """Test du parcours utilisateur complet"""
    pass
```

## 🔧 Configuration

### Variables d'environnement
```bash
# Base de données de test
TEST_DATABASE_URL=postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce_test

# URLs de test
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# Configuration de test
TESTING=true
```

### Fixtures disponibles
- `test_config` : Configuration des tests
- `mock_database` : Mock de la base de données
- `sample_user_data` : Données d'utilisateur de test
- `sample_product_data` : Données de produit de test
- `sample_order_data` : Données de commande de test
- `sample_payment_data` : Données de paiement de test

## 📈 Couverture de Code

### Générer un rapport de couverture
```bash
# Avec pytest-cov
pytest --cov=ecommerce-backend --cov-report=html --cov-report=term

# Le rapport HTML sera généré dans htmlcov/
```

### Objectifs de couverture
- **Tests unitaires** : > 90%
- **Tests d'intégration** : > 80%
- **Tests end-to-end** : > 70%
- **Couverture globale** : > 85%

## 🐛 Débogage des Tests

### Mode verbose
```bash
pytest -v
```

### Arrêt au premier échec
```bash
pytest -x
```

### Exécution d'un test spécifique
```bash
pytest tests/unit/test_auth.py::test_user_login
```

### Affichage des prints
```bash
pytest -s
```

### Mode debug
```bash
pytest --pdb
```

## 📝 Bonnes Pratiques

### Écriture des Tests
1. **Nommage clair** : `test_<fonctionnalité>_<scenario>`
2. **Un test = une assertion** : Un test ne doit vérifier qu'une chose
3. **Données de test** : Utiliser des fixtures plutôt que des données hardcodées
4. **Isolation** : Chaque test doit être indépendant
5. **Nettoyage** : Nettoyer les données après chaque test

### Structure d'un Test
```python
def test_user_registration_success():
    """Test de l'inscription réussie d'un utilisateur"""
    # Arrange (Préparation)
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "address": "123 Test Street"
    }
    
    # Act (Action)
    result = auth_service.register_user(**user_data)
    
    # Assert (Vérification)
    assert result is not None
    assert result.email == user_data["email"]
    assert result.first_name == user_data["first_name"]
```

### Gestion des Erreurs
```python
def test_user_registration_duplicate_email():
    """Test de l'inscription avec email existant"""
    # Arrange
    user_data = {"email": "existing@example.com", ...}
    auth_service.register_user(**user_data)  # Premier utilisateur
    
    # Act & Assert
    with pytest.raises(ValueError, match="Email déjà utilisé"):
        auth_service.register_user(**user_data)  # Deuxième utilisateur
```

## 🚨 Tests en Échec

### Vérifications communes
1. **Base de données** : Vérifier que PostgreSQL est démarré
2. **API** : Vérifier que l'API est accessible
3. **Frontend** : Vérifier que React est démarré
4. **Dépendances** : Vérifier que toutes les dépendances sont installées
5. **Variables d'environnement** : Vérifier la configuration

### Logs de débogage
```bash
# Activer les logs détaillés
pytest -v -s --log-cli-level=DEBUG

# Logs spécifiques à un test
pytest tests/unit/test_auth.py -v -s --log-cli-level=DEBUG
```

## 📚 Ressources

- [Documentation pytest](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
