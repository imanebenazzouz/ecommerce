"""
Tests unitaires pour la validation des adresses
"""
import pytest
from pydantic import ValidationError
import sys
import os

# Ajouter le chemin du backend pour importer les modèles
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))

from api import RegisterIn, UserUpdateIn


class TestAddressValidation:
    """Tests de validation du format d'adresse"""
    
    def test_valid_address_registration(self):
        """Test avec une adresse valide lors de l'inscription"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "address": "12 Rue des Fleurs, 75001 Paris"
        }
        user = RegisterIn(**data)
        assert user.address == "12 Rue des Fleurs, 75001 Paris"
    
    def test_valid_address_update(self):
        """Test avec une adresse valide lors de la mise à jour du profil"""
        data = {
            "address": "45 Avenue Victor Hugo, 69003 Lyon"
        }
        update = UserUpdateIn(**data)
        assert update.address == "45 Avenue Victor Hugo, 69003 Lyon"
    
    def test_address_too_short(self):
        """Test avec une adresse trop courte"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "address": "Rue Paris"  # Trop court
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterIn(**data)
        
        # Vérifier que l'erreur concerne l'adresse
        errors = exc_info.value.errors()
        assert any('address' in str(error) for error in errors)
    
    def test_address_no_postal_code(self):
        """Test avec une adresse sans code postal"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "address": "35 rue Alexandre FOURNY"  # Pas de code postal
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterIn(**data)
        
        # Vérifier que l'erreur mentionne le code postal manquant
        errors = exc_info.value.errors()
        error_messages = [str(e) for e in errors]
        assert any('code postal' in msg.lower() or 'postal' in msg.lower() for msg in error_messages)
    
    def test_address_no_letters(self):
        """Test avec une adresse sans lettres suffisantes"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "address": "123 456 75001"  # Que des chiffres avec code postal
        }
        with pytest.raises(ValidationError) as exc_info:
            RegisterIn(**data)
        
        # Vérifier que l'erreur mentionne les lettres manquantes
        errors = exc_info.value.errors()
        error_messages = [str(e) for e in errors]
        assert any('lettres' in msg.lower() for msg in error_messages)
    
    def test_address_whitespace_trimmed(self):
        """Test que les espaces en début et fin sont supprimés"""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "address": "  12 Rue des Fleurs, 75001 Paris  "
        }
        user = RegisterIn(**data)
        assert user.address == "12 Rue des Fleurs, 75001 Paris"
        assert not user.address.startswith(" ")
        assert not user.address.endswith(" ")
    
    def test_address_update_optional(self):
        """Test que l'adresse est optionnelle lors de la mise à jour"""
        data = {
            "first_name": "Jean"
        }
        update = UserUpdateIn(**data)
        assert update.address is None
    
    def test_address_update_none(self):
        """Test que l'adresse peut être None lors de la mise à jour"""
        data = {
            "address": None
        }
        update = UserUpdateIn(**data)
        assert update.address is None
    
    def test_various_valid_formats(self):
        """Test de différents formats d'adresse valides"""
        valid_addresses = [
            "12 Rue des Fleurs, 75001 Paris",
            "45 Avenue Victor Hugo, 69003 Lyon",
            "3 Boulevard Gambetta, 31000 Toulouse",
            "100 Rue de la République 13001 Marseille",
            "7 Place du Marché, Bordeaux 33000",
            "1 Allée des Peupliers, 67000 Strasbourg"
        ]
        
        for address in valid_addresses:
            data = {
                "email": "test@example.com",
                "password": "SecurePass123",
                "first_name": "Jean",
                "last_name": "Dupont",
                "address": address
            }
            user = RegisterIn(**data)
            assert len(user.address) >= 10
            assert any(char.isdigit() for char in user.address)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

