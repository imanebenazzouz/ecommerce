#!/usr/bin/env python3
"""
Tests complets d'authentification
"""

import pytest
import bcrypt
import jwt
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Ajouter le répertoire ecommerce-backend au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ecommerce-backend'))

from services.auth_service import AuthService
from database.repositories_simple import PostgreSQLUserRepository

@pytest.mark.unit
@pytest.mark.auth
class TestAuthService:
    """Tests complets du service d'authentification"""
    
    @pytest.fixture
    def auth_service(self):
        """Service d'authentification pour les tests"""
        mock_user_repo = Mock(spec=PostgreSQLUserRepository)
        return AuthService(mock_user_repo)
    
    def test_hash_password(self, auth_service):
        """Test du hachage des mots de passe"""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        # Vérifier que le hash est différent du mot de passe original
        assert hashed != password
        assert len(hashed) > 0
        
        # Vérifier que le hash peut être vérifié
        assert auth_service.verify_password(password, hashed)
        assert not auth_service.verify_password("wrong_password", hashed)
    
    def test_verify_password(self, auth_service):
        """Test de la vérification des mots de passe"""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        # Test avec le bon mot de passe
        assert auth_service.verify_password(password, hashed)
        
        # Test avec un mauvais mot de passe
        assert not auth_service.verify_password("wrong_password", hashed)
        
        # Test avec chaîne vide (devrait retourner False)
        assert not auth_service.verify_password("", hashed)
        
        # Test avec None (devrait retourner False, pas lever d'exception)
        assert not auth_service.verify_password(None, hashed)
    
    def test_create_access_token(self, auth_service):
        """Test de création de token JWT"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = auth_service.create_access_token(data)
        
        # Vérifier que le token est créé
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Vérifier que le token peut être décodé
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload
    
    def test_verify_token_valid(self, auth_service):
        """Test de vérification d'un token valide"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = auth_service.create_access_token(data)
        
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
    
    def test_verify_token_invalid(self, auth_service):
        """Test de vérification d'un token invalide"""
        # Token invalide
        assert auth_service.verify_token("invalid_token") is None
        assert auth_service.verify_token("") is None
        assert auth_service.verify_token(None) is None
        
        # Token expiré
        expired_data = {"sub": "user123", "exp": datetime.utcnow() - timedelta(hours=1)}
        expired_token = jwt.encode(expired_data, auth_service.secret_key, algorithm=auth_service.algorithm)
        assert auth_service.verify_token(expired_token) is None
    
    def test_authenticate_user_success(self, auth_service):
        """Test d'authentification réussie"""
        # Mock de l'utilisateur
        mock_user = Mock()
        mock_user.password_hash = auth_service.hash_password("password123")
        
        # Mock du repository
        auth_service.user_repo.get_by_email.return_value = mock_user
        
        # Test d'authentification
        result = auth_service.authenticate_user("test@example.com", "password123")
        assert result == mock_user
        auth_service.user_repo.get_by_email.assert_called_once_with("test@example.com")
    
    def test_authenticate_user_wrong_password(self, auth_service):
        """Test d'authentification avec mauvais mot de passe"""
        # Mock de l'utilisateur
        mock_user = Mock()
        mock_user.password_hash = auth_service.hash_password("password123")
        
        # Mock du repository
        auth_service.user_repo.get_by_email.return_value = mock_user
        
        # Test avec mauvais mot de passe
        result = auth_service.authenticate_user("test@example.com", "wrong_password")
        assert result is None
    
    def test_authenticate_user_not_found(self, auth_service):
        """Test d'authentification avec utilisateur inexistant"""
        # Mock du repository qui retourne None
        auth_service.user_repo.get_by_email.return_value = None
        
        # Test d'authentification
        result = auth_service.authenticate_user("nonexistent@example.com", "password123")
        assert result is None
    
    def test_register_success(self, auth_service):
        """Test d'inscription réussie"""
        # Mock du repository
        mock_user = Mock()
        mock_user.id = "user123"
        auth_service.user_repo.get_by_email.return_value = None  # Email n'existe pas
        auth_service.user_repo.create.return_value = mock_user
        
        # Test d'inscription
        result = auth_service.register(
            "test@example.com",
            "password123",
            "Test",
            "User",
            "123 Test Street"
        )
        
        assert result == mock_user
        auth_service.user_repo.get_by_email.assert_called_once_with("test@example.com")
        auth_service.user_repo.create.assert_called_once()
        
        # Vérifier que les données passées au repository sont correctes
        call_args = auth_service.user_repo.create.call_args[0][0]
        assert call_args["email"] == "test@example.com"
        assert call_args["first_name"] == "Test"
        assert call_args["last_name"] == "User"
        assert call_args["address"] == "123 Test Street"
        assert call_args["is_admin"] is False
        assert "password_hash" in call_args
    
    def test_register_email_exists(self, auth_service):
        """Test d'inscription avec email existant"""
        # Mock du repository qui retourne un utilisateur existant
        mock_existing_user = Mock()
        auth_service.user_repo.get_by_email.return_value = mock_existing_user
        
        # Test d'inscription avec email existant
        with pytest.raises(ValueError, match="Email déjà utilisé"):
            auth_service.register(
                "existing@example.com",
                "password123",
                "Test",
                "User",
                "123 Test Street"
            )
    
    def test_token_expiration(self, auth_service):
        """Test de l'expiration des tokens"""
        data = {"sub": "user123"}
        token = auth_service.create_access_token(data)
        
        # Vérifier que le token est valide maintenant
        payload = auth_service.verify_token(token)
        assert payload is not None
        
        # Simuler l'expiration en modifiant le secret
        old_secret = auth_service.secret_key
        auth_service.secret_key = "different_secret"
        
        # Le token devrait maintenant être invalide
        payload = auth_service.verify_token(token)
        assert payload is None
        
        # Restaurer le secret
        auth_service.secret_key = old_secret
    
    def test_password_strength(self, auth_service):
        """Test de la force des mots de passe"""
        # Test avec différents types de mots de passe
        passwords = [
            "password123",
            "P@ssw0rd!",
            "123456789",
            "abcdefgh",
            "P@ssw0rd!@#$%^&*()",
        ]
        
        for password in passwords:
            hashed = auth_service.hash_password(password)
            assert auth_service.verify_password(password, hashed)
            assert not auth_service.verify_password(password + "x", hashed)
    
    def test_concurrent_authentication(self, auth_service):
        """Test d'authentification concurrente"""
        # Simuler plusieurs tentatives d'authentification simultanées
        mock_user = Mock()
        mock_user.password_hash = auth_service.hash_password("password123")
        auth_service.user_repo.get_by_email.return_value = mock_user
        
        # Test avec le même utilisateur
        result1 = auth_service.authenticate_user("test@example.com", "password123")
        result2 = auth_service.authenticate_user("test@example.com", "password123")
        
        assert result1 == mock_user
        assert result2 == mock_user
    
    def test_unicode_passwords(self, auth_service):
        """Test avec des mots de passe Unicode"""
        unicode_passwords = [
            "motdepasse123",
            "пароль123",
            "密码123",
            "كلمة المرور123",
            "🔐password123",
        ]
        
        for password in unicode_passwords:
            hashed = auth_service.hash_password(password)
            assert auth_service.verify_password(password, hashed)
            assert not auth_service.verify_password(password + "x", hashed)
    
    def test_empty_inputs(self, auth_service):
        """Test avec des entrées vides"""
        # Créer un hash valide pour les tests
        valid_hash = auth_service.hash_password("test_password")
        
        # Test avec des chaînes vides (devrait retourner False)
        assert not auth_service.verify_password("", valid_hash)
        
        # Test avec hash vide (devrait retourner False, pas lever d'exception)
        assert not auth_service.verify_password("password", "")
        
        # Test avec None (devrait retourner False, pas lever d'exception)
        assert not auth_service.verify_password(None, valid_hash)
        assert not auth_service.verify_password("password", None)
    
    def test_token_manipulation(self, auth_service):
        """Test de manipulation de token"""
        data = {"sub": "user123"}
        token = auth_service.create_access_token(data)
        
        # Test avec token modifié
        modified_token = token[:-1] + "x"
        assert auth_service.verify_token(modified_token) is None
        
        # Test avec token tronqué
        truncated_token = token[:len(token)//2]
        assert auth_service.verify_token(truncated_token) is None
        
        # Test avec token vide
        assert auth_service.verify_token("") is None
        assert auth_service.verify_token(None) is None
