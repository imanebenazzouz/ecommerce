# 🧪 Tests - E-Commerce

Suite de tests complète pour l'application e-commerce.

## 📁 Structure des Tests

```
tests/
├── unit/                       # Tests unitaires (26 fichiers)
│   ├── test_address_validation.py
│   ├── test_address_symbols_validation.py  # 🆕 Déplacé
│   ├── test_validations.py
│   ├── test_payment_storage.py            # 🆕 Déplacé
│   ├── test_imports.py                    # 🆕 Déplacé
│   ├── test_db_simple.py                  # 🆕 Déplacé
│   ├── test_auth*.py                      # Tests d'authentification
│   ├── test_cart*.py                      # Tests de panier
│   ├── test_orders*.py                    # Tests de commandes
│   ├── test_products*.py                  # Tests de produits
│   ├── test_payments*.py                  # Tests de paiements
│   ├── test_support*.py                   # Tests de support
│   └── test_user_profile_advanced.py      # Tests profil utilisateur
│
├── integration/               # Tests d'intégration (9 fichiers)
│   ├── test_payment_validation.py
│   ├── test_inventory_management.py
│   ├── test_database*.py
│   ├── test_refund_system.py              # 🆕 Déplacé
│   ├── test_name_validation.py            # 🆕 Déplacé
│   ├── test_address_validation_manual.py  # 🆕 Déplacé
│   └── test_full_sync.py                  # 🆕 Déplacé
│
├── e2e/                      # Tests end-to-end (6 fichiers)
│   ├── test_final.py
│   ├── test_checkout_validation.py
│   ├── test_user_journey*.py
│   ├── test_app.py                        # 🆕 Déplacé
│   └── test_api_complete.py               # 🆕 Déplacé
│
├── legacy/                   # Anciens tests (35 fichiers)
│   └── [Tests historiques conservés]
│
├── conftest.py               # Configuration commune
├── run_all_tests.py          # Lance tous les tests
├── run_unit_tests.py         # Tests unitaires uniquement
├── run_integration_tests.py  # Tests d'intégration uniquement
├── run_e2e_tests.py          # Tests E2E uniquement
└── run_profile_inventory_tests.py  # Tests profil & inventaire
```

## 🎯 Types de Tests

### Tests Unitaires (`unit/`)
Testent les composants individuels en isolation.

**Fichiers récemment organisés :**
- ✅ `test_address_symbols_validation.py` - Validation symboles dans adresses
- ✅ `test_payment_storage.py` - Stockage des données de paiement
- ✅ `test_imports.py` - Vérification des imports
- ✅ `test_db_simple.py` - Tests simples de connexion DB

### Tests d'Intégration (`integration/`)
Testent les interactions entre composants.

**Fichiers récemment organisés :**
- ✅ `test_refund_system.py` - Système complet de remboursement
- ✅ `test_name_validation.py` - Validation noms/prénoms
- ✅ `test_address_validation_manual.py` - Tests manuels d'adresses
- ✅ `test_full_sync.py` - Synchronisation complète du système

### Tests End-to-End (`e2e/`)
Testent l'application complète.

**Fichiers récemment organisés :**
- ✅ `test_app.py` - Test principal de l'application
- ✅ `test_api_complete.py` - Test complet de l'API

## 🚀 Exécution des Tests

### Tous les tests
```bash
# Depuis la racine
python run_all_tests.py

# Ou avec pytest
pytest
```

### Par catégorie
```bash
# Tests unitaires
python tests/run_unit_tests.py
pytest tests/unit/

# Tests d'intégration
python tests/run_integration_tests.py
pytest tests/integration/

# Tests end-to-end
python tests/run_e2e_tests.py
pytest tests/e2e/
```

### Tests spécifiques déplacés
```bash
# Test du système de remboursement
python tests/integration/test_refund_system.py

# Test de validation des noms
python tests/integration/test_name_validation.py

# Test de stockage des paiements
python tests/unit/test_payment_storage.py

# Avec pytest
pytest tests/unit/test_address_validation.py -v
pytest tests/integration/test_refund_system.py -v
```

### Par marqueur
```bash
pytest -m unit          # Tests unitaires
pytest -m integration   # Tests d'intégration
pytest -m e2e           # Tests end-to-end
pytest -m auth          # Tests d'authentification
pytest -m payments      # Tests de paiements
pytest -m profile       # Tests de profil
pytest -m inventory     # Tests d'inventaire
```

## ✅ Corrections Effectuées

Lors de la réorganisation, les imports ont été corrigés pour tous les fichiers déplacés :

### Ancien import (incorrect)
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))
```

### Nouvel import (correct)
```python
# Depuis tests/unit/
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))
sys.path.insert(0, backend_path)

# Depuis tests/integration/
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))
sys.path.insert(0, backend_path)

# Depuis tests/e2e/
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))
sys.path.insert(0, backend_path)
```

## 📊 Statistiques

- **Total des tests** : 100+
- **Tests unitaires** : 60+
- **Tests d'intégration** : 30+
- **Tests end-to-end** : 10+
- **Fichiers déplacés et corrigés** : 10
- **Tests fonctionnels** : ✅ 100%

## 🔧 Configuration

### Variables d'Environnement
Configurées automatiquement via `conftest.py` :
- `TESTING=true`
- `DATABASE_URL=postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce_test`
- `API_BASE_URL=http://localhost:8000`
- `FRONTEND_URL=http://localhost:5173`

### Fixtures Disponibles
Définies dans `conftest.py` :
- `test_config` - Configuration des tests
- `mock_database` - Mock de la base de données
- `sample_user_data` - Données utilisateur de test
- `sample_product_data` - Données produit de test
- `sample_order_data` - Données commande de test
- `sample_payment_data` - Données paiement de test

## 📝 Notes

### Tests Legacy
Le dossier `legacy/` contient les anciens tests conservés pour référence. Ils ne sont pas exécutés par défaut.

### Couverture de Code
```bash
# Générer un rapport de couverture
pytest --cov=ecommerce-backend --cov-report=html

# Voir le rapport
open htmlcov/index.html
```

**Objectifs de couverture :**
- Tests unitaires : > 90%
- Tests d'intégration : > 80%
- Tests end-to-end : > 70%
- **Couverture globale : > 85%**

## 🐛 Débogage

### Mode verbose
```bash
pytest -v
```

### Arrêt au premier échec
```bash
pytest -x
```

### Affichage des prints
```bash
pytest -s
```

### Mode debug
```bash
pytest --pdb
```

### Logs détaillés
```bash
pytest -v -s --log-cli-level=DEBUG
```

## ✨ Améliorations Récentes

### Octobre 2025
- ✅ Nettoyage et réorganisation de tous les tests
- ✅ Déplacement de 10 fichiers de test vers la bonne structure
- ✅ Correction de tous les imports et chemins
- ✅ Vérification du bon fonctionnement de tous les tests
- ✅ Amélioration de la documentation

---

**Pour plus d'informations :** Voir `DOCUMENTATION.md` à la racine du projet.

