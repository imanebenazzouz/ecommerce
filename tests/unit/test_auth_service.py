#!/usr/bin/env python3
"""
Tests unitaires pour le service d'authentification
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.services.auth_service import AuthService

@pytest.mark.unit
@pytest.mark.auth
class TestAuthService:
    """Tests unitaires pour AuthService"""
    
    @pytest.fixture
    def mock_user_repo(self):
        """Mock du repository utilisateur"""
        return Mock()
    
    @pytest.fixture
    def auth_service(self, mock_user_repo):
        """Service d'authentification avec mock"""
        return AuthService(mock_user_repo)
    
    def test_hash_password(self, auth_service):
        """Test du hashage des mots de passe"""
        password = "testpassword123"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt format
    
    def test_verify_password_correct(self, auth_service):
        """Test de vérification de mot de passe correct"""
        password = "testpassword123"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self, auth_service):
        """Test de vérification de mot de passe incorrect"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(wrong_password, hashed) is False
    
    def test_create_access_token(self, auth_service):
        """Test de création de token d'accès"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = auth_service.create_access_token(data)
        
        assert token is not None
        assert len(token) > 0
        assert isinstance(token, str)
    
    def test_verify_token_valid(self, auth_service):
        """Test de vérification de token valide"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = auth_service.create_access_token(data)
        
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
    
    def test_verify_token_invalid(self, auth_service):
        """Test de vérification de token invalide"""
        invalid_token = "invalid.token.here"
        
        payload = auth_service.verify_token(invalid_token)
        assert payload is None
    
    def test_verify_token_expired(self, auth_service):
        """Test de vérification de token expiré"""
        # Créer un token expiré (simulation)
        import jwt
        from datetime import datetime, timedelta
        
        expired_data = {
            "sub": "user123",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expiré il y a 1 heure
        }
        
        expired_token = jwt.encode(expired_data, auth_service.secret_key, algorithm=auth_service.algorithm)
        
        payload = auth_service.verify_token(expired_token)
        assert payload is None
    
    def test_authenticate_user_success(self, auth_service, mock_user_repo):
        """Test d'authentification utilisateur réussie"""
        # Mock de l'utilisateur
        mock_user = Mock()
        mock_user.password_hash = auth_service.hash_password("password123")
        mock_user_repo.get_by_email.return_value = mock_user
        
        # Test d'authentification
        user = auth_service.authenticate_user("test@example.com", "password123")
        
        assert user is not None
        assert user == mock_user
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    
    def test_authenticate_user_wrong_password(self, auth_service, mock_user_repo):
        """Test d'authentification avec mot de passe incorrect"""
        # Mock de l'utilisateur
        mock_user = Mock()
        mock_user.password_hash = auth_service.hash_password("correctpassword")
        mock_user_repo.get_by_email.return_value = mock_user
        
        # Test d'authentification avec mauvais mot de passe
        user = auth_service.authenticate_user("test@example.com", "wrongpassword")
        
        assert user is None
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    
    def test_authenticate_user_not_found(self, auth_service, mock_user_repo):
        """Test d'authentification utilisateur non trouvé"""
        # Mock de l'utilisateur non trouvé
        mock_user_repo.get_by_email.return_value = None
        
        # Test d'authentification
        user = auth_service.authenticate_user("nonexistent@example.com", "password123")
        
        assert user is None
        mock_user_repo.get_by_email.assert_called_once_with("nonexistent@example.com")
    
    def test_register_user_success(self, auth_service, mock_user_repo):
        """Test d'inscription utilisateur réussie"""
        # Mock de l'utilisateur non existant
        mock_user_repo.get_by_email.return_value = None
        
        # Mock de la création d'utilisateur
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user_repo.create.return_value = mock_user
        
        # Test d'inscription
        user = auth_service.register_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            address="123 Test Street"
        )
        
        assert user is not None
        assert user == mock_user
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
        mock_user_repo.create.assert_called_once()
    
    def test_register_user_duplicate_email(self, auth_service, mock_user_repo):
        """Test d'inscription avec email existant"""
        # Mock de l'utilisateur existant
        mock_user = Mock()
        mock_user_repo.get_by_email.return_value = mock_user
        
        # Test d'inscription avec email existant
        with pytest.raises(ValueError, match="Email déjà utilisé"):
            auth_service.register_user(
                email="existing@example.com",
                password="password123",
                first_name="Test",
                last_name="User",
                address="123 Test Street"
            )
        
        mock_user_repo.get_by_email.assert_called_once_with("existing@example.com")
        mock_user_repo.create.assert_not_called()
    
    def test_register_user_validation(self, auth_service, mock_user_repo):
        """Test de validation des données d'inscription"""
        # Mock de l'utilisateur non existant
        mock_user_repo.get_by_email.return_value = None
        
        # Mock de la création d'utilisateur
        mock_user = Mock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        mock_user_repo.create.return_value = mock_user
        
        # Le service d'authentification ne valide pas la longueur du mot de passe
        # Cette validation se fait au niveau de l'API avec Pydantic
        # Test avec mot de passe court (devrait passer au niveau du service)
        user = auth_service.register_user(
            email="test@example.com",
            password="123",  # Court mais accepté par le service
            first_name="Test",
            last_name="User",
            address="123 Test Street"
        )
        
        assert user is not None
        assert user == mock_user
    
    def test_password_hash_consistency(self, auth_service):
        """Test de la cohérence du hashage des mots de passe"""
        password = "testpassword123"
        
        # Hasher le même mot de passe plusieurs fois
        hash1 = auth_service.hash_password(password)
        hash2 = auth_service.hash_password(password)
        
        # Les hashs doivent être différents (salt différent)
        assert hash1 != hash2
        
        # Mais la vérification doit fonctionner pour les deux
        assert auth_service.verify_password(password, hash1) is True
        assert auth_service.verify_password(password, hash2) is True
    
    def test_token_expiration(self, auth_service):
        """Test de l'expiration des tokens"""
        data = {"sub": "user123"}
        token = auth_service.create_access_token(data)
        
        # Le token doit être valide immédiatement
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        
        # Simuler l'expiration en modifiant la configuration
        original_expire = auth_service.access_token_expire_minutes
        auth_service.access_token_expire_minutes = 0  # Expire immédiatement
        
        # Créer un nouveau token qui expire immédiatement
        expired_token = auth_service.create_access_token(data)
        
        # Attendre un peu pour que le token expire
        import time
        time.sleep(1)
        
        # Le token expiré ne doit plus être valide
        payload = auth_service.verify_token(expired_token)
        assert payload is None
        
        # Restaurer la configuration originale
        auth_service.access_token_expire_minutes = original_expire
