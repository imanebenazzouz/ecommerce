#!/usr/bin/env python3
"""
Tests simples pour l'authentification
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.services.auth_service import AuthService

class TestAuthServiceSimple(unittest.TestCase):
    """Tests simples pour AuthService"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.mock_user_repo = Mock()
        self.auth_service = AuthService(self.mock_user_repo)
    
    def test_hash_password(self):
        """Test le hachage d'un mot de passe"""
        password = "testpassword123"
        hashed = self.auth_service.hash_password(password)
        
        # Vérifier que le hash est différent du mot de passe original
        self.assertNotEqual(password, hashed)
        # Vérifier que le hash n'est pas vide
        self.assertTrue(len(hashed) > 0)
        # Vérifier que le hash contient le préfixe sha256
        self.assertTrue(hashed.startswith('sha256::'))
    
    def test_verify_password(self):
        """Test la vérification d'un mot de passe"""
        password = "testpassword123"
        hashed = self.auth_service.hash_password(password)
        
        # Vérification correcte
        self.assertTrue(self.auth_service.verify_password(password, hashed))
        
        # Vérification avec mauvais mot de passe
        self.assertFalse(self.auth_service.verify_password("wrongpassword", hashed))
        self.assertFalse(self.auth_service.verify_password("", hashed))
    
    def test_register_user_success(self):
        """Test l'inscription d'un utilisateur avec succès"""
        # Mock du repository
        self.mock_user_repo.get_by_email.return_value = None
        self.mock_user_repo.create.return_value = Mock(
            id="user-123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            address="123 Test St",
            is_admin=False
        )
        
        user = self.auth_service.register(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            address="123 Test St"
        )
        
        # Vérifier que l'utilisateur est créé
        self.mock_user_repo.create.assert_called_once()
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "Test")
        self.assertFalse(user.is_admin)
    
    def test_register_user_duplicate_email(self):
        """Test l'inscription avec un email déjà utilisé"""
        # Mock du repository pour retourner un utilisateur existant
        self.mock_user_repo.get_by_email.return_value = Mock(email="test@example.com")
        
        with self.assertRaises(ValueError) as context:
            self.auth_service.register(
                email="test@example.com",
                password="password123",
                first_name="Test",
                last_name="User",
                address="123 Test St"
            )
        
        self.assertIn("Email déjà utilisé", str(context.exception))
    
    def test_login_success(self):
        """Test la connexion avec succès"""
        # Mock d'un utilisateur existant
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_user.password_hash = self.auth_service.hash_password("password123")
        
        self.mock_user_repo.get_by_email.return_value = mock_user
        
        # Mock du session manager
        with patch.object(self.auth_service, 'sessions') as mock_sessions:
            mock_sessions.create_session.return_value = "token-123"
            
            token = self.auth_service.login("test@example.com", "password123")
            
            self.assertEqual(token, "token-123")
            mock_sessions.create_session.assert_called_once_with("user-123")
    
    def test_login_invalid_credentials(self):
        """Test la connexion avec des identifiants invalides"""
        # Mock d'un utilisateur existant
        mock_user = Mock()
        mock_user.password_hash = self.auth_service.hash_password("correctpassword")
        
        self.mock_user_repo.get_by_email.return_value = mock_user
        
        with self.assertRaises(ValueError) as context:
            self.auth_service.login("test@example.com", "wrongpassword")
        
        self.assertIn("Identifiants invalides", str(context.exception))
    
    def test_login_nonexistent_user(self):
        """Test la connexion avec un utilisateur inexistant"""
        self.mock_user_repo.get_by_email.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.auth_service.login("nonexistent@example.com", "password123")
        
        self.assertIn("Identifiants invalides", str(context.exception))

if __name__ == '__main__':
    unittest.main(verbosity=2)
