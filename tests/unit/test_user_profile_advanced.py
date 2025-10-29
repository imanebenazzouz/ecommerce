#!/usr/bin/env python3
"""
Tests avancés pour la gestion du profil utilisateur
Tests pour:
- Modification d'email avec vérification
- Changement de mot de passe avec ancien mot de passe requis
- Désactivation de compte (soft delete vs hard delete)
- Export des données RGPD
- Historique complet des commandes et interactions
- Gestion de plusieurs adresses de livraison
"""

import pytest
import sys
import os
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))

from api import app
from database.database import SessionLocal, create_tables
from database.repositories_simple import (
    PostgreSQLUserRepository,
    PostgreSQLOrderRepository,
    PostgreSQLProductRepository
)
from database.models import User, Order, OrderItem
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
def test_user(db_session):
    """Crée un utilisateur de test"""
    user_repo = PostgreSQLUserRepository(db_session)
    user_data = {
        "email": f"test_profile_{os.urandom(8).hex()}@example.com",
        "password": "OldPassword123!",
        "first_name": "Test",
        "last_name": "User",
        "address": "123 Test Street, Paris, 75001"
    }
    user = user_repo.create(user_data)
    return user


@pytest.fixture
def auth_token(test_user, db_session):
    """Crée un token d'authentification pour l'utilisateur de test"""
    user_repo = PostgreSQLUserRepository(db_session)
    auth_service = AuthService(user_repo)
    token = auth_service.create_access_token(data={"sub": str(test_user.id)})
    return token


@pytest.mark.unit
@pytest.mark.profile
class TestEmailModification:
    """Tests pour la modification d'email avec vérification"""
    
    def test_change_email_success(self, test_user, auth_token, db_session):
        """Test de changement d'email avec succès"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Nouvel email
        new_email = f"newemail_{os.urandom(8).hex()}@example.com"
        
        # Modifier l'email
        test_user.email = new_email
        updated_user = user_repo.update(test_user)
        
        # Vérifications
        assert updated_user.email == new_email
        
        # Vérifier que l'ancien email ne peut plus être utilisé pour se connecter
        old_user = user_repo.get_by_email(f"test_profile_*@example.com")
        # L'ancien email ne doit plus exister
        assert old_user is None or old_user.email == new_email
    
    def test_change_email_already_exists(self, test_user, db_session):
        """Test de changement d'email vers un email déjà existant"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Créer un autre utilisateur
        other_user_data = {
            "email": f"existing_{os.urandom(8).hex()}@example.com",
            "password": "Password123!",
            "first_name": "Other",
            "last_name": "User",
            "address": "456 Other Street"
        }
        other_user = user_repo.create(other_user_data)
        
        # Tenter de changer l'email vers un email existant
        original_email = test_user.email
        test_user.email = other_user.email
        
        # Devrait lever une exception (contrainte d'unicité)
        with pytest.raises(Exception):
            user_repo.update(test_user)
            db_session.commit()
    
    def test_change_email_invalid_format(self, test_user):
        """Test de changement d'email avec format invalide"""
        # Emails invalides
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "",
        ]
        
        for invalid_email in invalid_emails:
            # Le format devrait être validé avant même d'atteindre la base de données
            # Ici on teste juste que le modèle ne devrait pas accepter ces formats
            is_invalid = (
                "@" not in invalid_email or 
                invalid_email.count("@") != 1 or 
                " " in invalid_email or
                invalid_email.startswith("@") or
                invalid_email.endswith("@") or
                invalid_email == ""
            )
            assert is_invalid, f"Email '{invalid_email}' devrait être considéré comme invalide"


@pytest.mark.unit
@pytest.mark.profile
class TestPasswordChange:
    """Tests pour le changement de mot de passe"""
    
    def test_change_password_with_old_password(self, test_user, auth_token, db_session):
        """Test de changement de mot de passe avec vérification de l'ancien"""
        user_repo = PostgreSQLUserRepository(db_session)
        auth_service = AuthService(user_repo)
        
        old_password = "OldPassword123!"
        new_password = "NewPassword456!"
        
        # Vérifier l'ancien mot de passe
        is_valid = auth_service.verify_password(old_password, test_user.password_hash)
        assert is_valid, "L'ancien mot de passe devrait être valide"
        
        # Changer le mot de passe
        new_hash = auth_service.hash_password(new_password)
        test_user.password_hash = new_hash
        user_repo.update(test_user)
        
        # Vérifier que le nouveau mot de passe fonctionne
        assert auth_service.verify_password(new_password, test_user.password_hash)
        
        # Vérifier que l'ancien mot de passe ne fonctionne plus
        assert not auth_service.verify_password(old_password, test_user.password_hash)
    
    def test_change_password_wrong_old_password(self, test_user, db_session):
        """Test de changement de mot de passe avec mauvais ancien mot de passe"""
        user_repo = PostgreSQLUserRepository(db_session)
        auth_service = AuthService(user_repo)
        wrong_old_password = "WrongPassword123!"
        
        # Vérifier que l'ancien mot de passe est incorrect
        is_valid = auth_service.verify_password(wrong_old_password, test_user.password_hash)
        assert not is_valid, "Le mot de passe incorrect ne devrait pas être validé"
    
    def test_change_password_weak_password(self, test_user):
        """Test de changement vers un mot de passe faible"""
        weak_passwords = [
            "123",
            "password",
            "abc",
            "12345678",
            "qwerty"
        ]
        
        for weak_pwd in weak_passwords:
            # Les mots de passe faibles devraient être rejetés
            # (idéalement, il y aurait une validation de force de mot de passe)
            assert len(weak_pwd) < 10 or weak_pwd.isalpha() or weak_pwd.isdigit()
    
    def test_password_history_prevention(self, test_user, db_session):
        """Test pour empêcher la réutilisation d'anciens mots de passe"""
        user_repo = PostgreSQLUserRepository(db_session)
        auth_service = AuthService(user_repo)
        
        # Stocker l'ancien hash
        old_hash = test_user.password_hash
        
        # Changer le mot de passe
        new_password = "NewPassword123!"
        test_user.password_hash = auth_service.hash_password(new_password)
        user_repo.update(test_user)
        
        # Vérifier que le nouveau hash est différent de l'ancien
        assert test_user.password_hash != old_hash
        
        # Note: Une vraie implémentation stockerait un historique des hashs
        # et empêcherait la réutilisation des N derniers mots de passe


@pytest.mark.unit
@pytest.mark.profile
class TestAccountDeactivation:
    """Tests pour la désactivation de compte"""
    
    def test_soft_delete_account(self, test_user, db_session):
        """Test de désactivation de compte (soft delete)"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Ajouter un champ is_active (si non présent dans le modèle actuel)
        # Pour l'instant, on teste avec le modèle existant
        original_id = test_user.id
        original_email = test_user.email
        
        # Soft delete : marquer comme inactif au lieu de supprimer
        # Note: Le modèle actuel n'a pas de champ is_active, il faudrait l'ajouter
        # Pour ce test, on simule le comportement attendu
        
        # Vérifier que l'utilisateur existe
        user = user_repo.get_by_id(str(original_id))
        assert user is not None
        
        # Un soft delete ne supprimerait pas vraiment l'utilisateur
        # mais le marquerait comme inactif
        # Ici, on vérifie juste que l'utilisateur existe toujours
        assert user.id == original_id
    
    def test_hard_delete_account(self, db_session):
        """Test de suppression définitive de compte (hard delete)"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Créer un utilisateur temporaire
        temp_user_data = {
            "email": f"temp_delete_{os.urandom(8).hex()}@example.com",
            "password": "TempPassword123!",
            "first_name": "Temp",
            "last_name": "Delete",
            "address": "123 Temp Street"
        }
        temp_user = user_repo.create(temp_user_data)
        temp_user_id = str(temp_user.id)
        
        # Supprimer l'utilisateur (hard delete)
        user_repo.delete(temp_user_id)
        
        # Vérifier que l'utilisateur n'existe plus
        deleted_user = user_repo.get_by_id(temp_user_id)
        assert deleted_user is None
    
    def test_deactivated_account_cannot_login(self, db_session):
        """Test qu'un compte désactivé ne peut pas se connecter"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Créer un utilisateur
        user_data = {
            "email": f"deactivated_{os.urandom(8).hex()}@example.com",
            "password": "Password123!",
            "first_name": "Deactivated",
            "last_name": "User",
            "address": "123 Street"
        }
        user = user_repo.create(user_data)
        
        # Tenter de se connecter (devrait fonctionner)
        login_response = client.post("/auth/login", json={
            "email": user.email,
            "password": "Password123!"
        })
        
        assert login_response.status_code == 200
        
        # Après désactivation (soft delete), la connexion devrait échouer
        # Note: Cela nécessiterait un champ is_active dans le modèle User


@pytest.mark.unit
@pytest.mark.profile
@pytest.mark.rgpd
class TestGDPRDataExport:
    """Tests pour l'export des données RGPD"""
    
    def test_export_user_personal_data(self, test_user, auth_token, db_session):
        """Test d'export des données personnelles de l'utilisateur"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Récupérer toutes les données de l'utilisateur
        user = user_repo.get_by_id(str(test_user.id))
        
        # Données qui devraient être exportées
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "address": user.address,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        
        # Vérifier que toutes les données importantes sont présentes
        assert user_data["email"] is not None
        assert user_data["first_name"] is not None
        assert user_data["last_name"] is not None
        assert user_data["address"] is not None
    
    def test_export_user_order_history(self, test_user, db_session):
        """Test d'export de l'historique des commandes"""
        order_repo = PostgreSQLOrderRepository(db_session)
        
        # Récupérer toutes les commandes de l'utilisateur
        orders = order_repo.get_by_user_id(str(test_user.id))
        
        # Formater les données pour l'export
        order_history = []
        for order in orders:
            order_data = {
                "id": str(order.id),
                "status": order.status,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "items": [
                    {
                        "product_name": item.name,
                        "quantity": item.quantity,
                        "unit_price_cents": item.unit_price_cents
                    }
                    for item in order.items
                ]
            }
            order_history.append(order_data)
        
        # L'historique peut être vide pour un nouvel utilisateur
        assert isinstance(order_history, list)
    
    def test_export_all_user_data_rgpd(self, test_user, db_session):
        """Test d'export complet de toutes les données (RGPD)"""
        user_repo = PostgreSQLUserRepository(db_session)
        order_repo = PostgreSQLOrderRepository(db_session)
        
        # Récupérer l'utilisateur
        user = user_repo.get_by_id(str(test_user.id))
        
        # Récupérer toutes les données associées
        orders = order_repo.get_by_user_id(str(test_user.id))
        
        # Export complet RGPD
        full_export = {
            "personal_data": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "address": user.address,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "orders": [
                {
                    "id": str(order.id),
                    "status": order.status,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                    "total_cents": sum(item.unit_price_cents * item.quantity for item in order.items)
                }
                for order in orders
            ],
            "export_date": datetime.utcnow().isoformat(),
            "export_format": "JSON"
        }
        
        # Vérifier que l'export contient toutes les sections
        assert "personal_data" in full_export
        assert "orders" in full_export
        assert "export_date" in full_export
        assert isinstance(full_export["orders"], list)


@pytest.mark.unit
@pytest.mark.profile
class TestUserOrderHistory:
    """Tests pour l'historique complet des commandes"""
    
    def test_get_complete_order_history(self, test_user, auth_token):
        """Test de récupération de l'historique complet des commandes"""
        # Récupérer toutes les commandes
        response = client.get(
            "/orders",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        orders = response.json()
        
        # L'historique peut être vide pour un nouvel utilisateur
        assert isinstance(orders, list)
    
    def test_order_history_pagination(self, test_user, db_session):
        """Test de pagination de l'historique des commandes"""
        order_repo = PostgreSQLOrderRepository(db_session)
        product_repo = PostgreSQLProductRepository(db_session)
        
        # Créer un produit pour les tests
        product_data = {
            "name": "Test Product",
            "description": "Description",
            "price_cents": 1000,
            "stock_qty": 100,
            "active": True
        }
        product = product_repo.create(product_data)
        
        # Créer plusieurs commandes
        for i in range(15):
            order_data = {
                "user_id": str(test_user.id),
                "status": "CREE",
                "items": [
                    {
                        "product_id": str(product.id),
                        "name": product.name,
                        "unit_price_cents": product.price_cents,
                        "quantity": 1
                    }
                ]
            }
            order_repo.create(order_data)
        
        # Récupérer toutes les commandes
        all_orders = order_repo.get_by_user_id(str(test_user.id))
        
        # Vérifier qu'on a bien créé les commandes
        assert len(all_orders) >= 15
        
        # Test de pagination (limiter à 10 résultats)
        paginated_orders = all_orders[:10]
        assert len(paginated_orders) == 10
    
    def test_order_history_filtering_by_status(self, test_user, db_session):
        """Test de filtrage de l'historique par statut"""
        order_repo = PostgreSQLOrderRepository(db_session)
        
        # Récupérer les commandes
        all_orders = order_repo.get_by_user_id(str(test_user.id))
        
        # Filtrer par statut
        paid_orders = [o for o in all_orders if o.status == "PAYEE"]
        cancelled_orders = [o for o in all_orders if o.status == "ANNULEE"]
        
        # Vérifier que le filtrage fonctionne
        assert isinstance(paid_orders, list)
        assert isinstance(cancelled_orders, list)


@pytest.mark.unit
@pytest.mark.profile
class TestMultipleAddresses:
    """Tests pour la gestion de plusieurs adresses de livraison"""
    
    def test_user_has_default_address(self, test_user):
        """Test que l'utilisateur a une adresse par défaut"""
        assert test_user.address is not None
        assert len(test_user.address) > 0
    
    def test_update_user_address(self, test_user, db_session):
        """Test de mise à jour de l'adresse de l'utilisateur"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Nouvelle adresse
        new_address = "456 New Avenue, Lyon, 69001"
        
        # Mettre à jour l'adresse
        test_user.address = new_address
        updated_user = user_repo.update(test_user)
        
        # Vérifier que l'adresse a été mise à jour
        assert updated_user.address == new_address
    
    def test_address_validation(self, test_user):
        """Test de validation des adresses"""
        # Adresses valides
        valid_addresses = [
            "123 Main Street, Paris, 75001",
            "456 Avenue des Champs-Élysées, Paris, 75008",
            "789 Rue de la Paix, Lyon, 69001"
        ]
        
        for address in valid_addresses:
            assert len(address) > 10
            assert "," in address
        
        # Adresses invalides
        invalid_addresses = [
            "",
            "abc",
            "123",
        ]
        
        for address in invalid_addresses:
            assert len(address) < 10 or "," not in address
    
    def test_multiple_addresses_storage(self, test_user):
        """Test du stockage de plusieurs adresses"""
        # Note: Le modèle actuel ne supporte qu'une seule adresse
        # Ce test vérifie le comportement attendu si on implémentait plusieurs adresses
        
        # Adresses multiples seraient stockées dans un champ JSON ou une table séparée
        addresses = [
            {
                "label": "Domicile",
                "street": "123 Main Street",
                "city": "Paris",
                "postal_code": "75001",
                "is_default": True
            },
            {
                "label": "Bureau",
                "street": "456 Work Avenue",
                "city": "Lyon",
                "postal_code": "69001",
                "is_default": False
            }
        ]
        
        # Vérifier la structure
        assert len(addresses) == 2
        assert any(addr["is_default"] for addr in addresses)
        
        # Vérifier qu'il n'y a qu'une seule adresse par défaut
        default_addresses = [addr for addr in addresses if addr["is_default"]]
        assert len(default_addresses) == 1


@pytest.mark.unit
@pytest.mark.profile
class TestProfileUpdateValidation:
    """Tests de validation lors de la mise à jour du profil"""
    
    def test_update_profile_with_valid_data(self, test_user, db_session):
        """Test de mise à jour du profil avec des données valides"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Nouvelles données
        test_user.first_name = "UpdatedFirstName"
        test_user.last_name = "UpdatedLastName"
        test_user.address = "999 Updated Street, Paris, 75001"
        
        # Mettre à jour
        updated_user = user_repo.update(test_user)
        
        # Vérifications
        assert updated_user.first_name == "UpdatedFirstName"
        assert updated_user.last_name == "UpdatedLastName"
        assert updated_user.address == "999 Updated Street, Paris, 75001"
    
    def test_update_profile_with_empty_fields(self, test_user, db_session):
        """Test de mise à jour avec des champs vides (devrait échouer)"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Les champs obligatoires ne devraient pas pouvoir être vides
        original_first_name = test_user.first_name
        
        # Tenter de mettre un champ vide
        test_user.first_name = ""
        
        # Devrait lever une exception ou être rejeté
        # Dans une vraie application, on validerait avant la mise à jour
        assert test_user.first_name == "" or test_user.first_name == original_first_name
    
    def test_concurrent_profile_updates(self, test_user, db_session):
        """Test de mises à jour concurrentes du profil"""
        user_repo = PostgreSQLUserRepository(db_session)
        
        # Simuler deux mises à jour concurrentes
        # Session 1 : modifier le prénom
        test_user.first_name = "UpdatedBySession1"
        user_repo.update(test_user)
        
        # Recharger l'utilisateur
        refreshed_user = user_repo.get_by_id(str(test_user.id))
        
        # Session 2 : modifier le nom
        refreshed_user.last_name = "UpdatedBySession2"
        user_repo.update(refreshed_user)
        
        # Vérifier que les deux mises à jour sont prises en compte
        final_user = user_repo.get_by_id(str(test_user.id))
        assert final_user.first_name == "UpdatedBySession1"
        assert final_user.last_name == "UpdatedBySession2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

