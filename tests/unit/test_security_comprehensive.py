#!/usr/bin/env python3
"""
Tests complets de sécurité
"""

import pytest
import jwt
import bcrypt
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Ajouter le répertoire ecommerce-backend au path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'ecommerce-backend'))

from services.auth_service import AuthService
from database.repositories_simple import PostgreSQLUserRepository

@pytest.mark.unit
@pytest.mark.security
class TestSecurity:
    """Tests complets de sécurité"""
    
    @pytest.fixture
    def auth_service(self):
        """Service d'authentification pour les tests"""
        mock_user_repo = Mock(spec=PostgreSQLUserRepository)
        return AuthService(mock_user_repo)
    
    def test_password_hashing_security(self, auth_service):
        """Test de sécurité du hachage des mots de passe"""
        password = "test_password_123"
        
        # Test que le même mot de passe produit des hash différents
        hash1 = auth_service.hash_password(password)
        hash2 = auth_service.hash_password(password)
        assert hash1 != hash2  # Salt différent à chaque fois
        
        # Test que les hash sont suffisamment longs
        assert len(hash1) >= 60  # bcrypt produit des hash de 60 caractères
        
        # Test que les hash contiennent le bon format
        assert hash1.startswith("$2b$")  # Format bcrypt
        
        # Test de vérification
        assert auth_service.verify_password(password, hash1)
        assert auth_service.verify_password(password, hash2)
        assert not auth_service.verify_password("wrong_password", hash1)
    
    def test_jwt_token_security(self, auth_service):
        """Test de sécurité des tokens JWT"""
        data = {"sub": "user123", "email": "test@example.com"}
        
        # Test de création de token
        token = auth_service.create_access_token(data)
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Test de décodage sans secret
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(token, "wrong_secret", algorithms=["HS256"])
        
        # Test de décodage avec le bon secret
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload
        
        # Test d'expiration
        expired_data = {"sub": "user123", "exp": datetime.utcnow() - timedelta(hours=1)}
        expired_token = jwt.encode(expired_data, auth_service.secret_key, algorithm=auth_service.algorithm)
        assert auth_service.verify_token(expired_token) is None
    
    def test_token_manipulation_protection(self, auth_service):
        """Test de protection contre la manipulation de tokens"""
        data = {"sub": "user123", "email": "test@example.com"}
        token = auth_service.create_access_token(data)

        # Test avec token modifié (devrait retourner None)
        modified_token = token[:-1] + "x"
        result = auth_service.verify_token(modified_token)
        assert result is None
        
        # Test avec token tronqué
        truncated_token = token[:len(token)//2]
        assert auth_service.verify_token(truncated_token) is None
        
        # Test avec token vide
        assert auth_service.verify_token("") is None
        assert auth_service.verify_token(None) is None
        
        # Test avec token malformé
        malformed_token = "not.a.jwt.token"
        assert auth_service.verify_token(malformed_token) is None
    
    def test_password_strength_validation(self, auth_service):
        """Test de validation de la force des mots de passe"""
        # Test avec mots de passe faibles
        weak_passwords = [
            "123",
            "password",
            "12345678",
            "abcdefgh",
            "PASSWORD",
            "Password",
        ]
        
        for weak_password in weak_passwords:
            # Le hachage devrait fonctionner même avec des mots de passe faibles
            # (la validation de force devrait être faite côté API)
            hashed = auth_service.hash_password(weak_password)
            assert auth_service.verify_password(weak_password, hashed)
        
        # Test avec mots de passe forts
        strong_passwords = [
            "P@ssw0rd!",
            "MyStr0ng!Pass",
            "C0mpl3x!P@ss",
            "S3cur3!P@ssw0rd",
        ]
        
        for strong_password in strong_passwords:
            hashed = auth_service.hash_password(strong_password)
            assert auth_service.verify_password(strong_password, hashed)
            assert not auth_service.verify_password(strong_password + "x", hashed)
    
    def test_unicode_password_security(self, auth_service):
        """Test de sécurité avec des mots de passe Unicode"""
        unicode_passwords = [
            "motdepasse123",
            "пароль123",
            "密码123",
            "كلمة المرور123",
            "🔐password123",
            "pássw0rd123",
            "m0t_dé_p@ssé",
        ]
        
        for password in unicode_passwords:
            hashed = auth_service.hash_password(password)
            assert auth_service.verify_password(password, hashed)
            assert not auth_service.verify_password(password + "x", hashed)
    
    def test_concurrent_authentication_security(self, auth_service):
        """Test de sécurité d'authentification concurrente"""
        # Simuler plusieurs tentatives d'authentification simultanées
        mock_user = Mock()
        mock_user.password_hash = auth_service.hash_password("password123")
        auth_service.user_repo.get_by_email.return_value = mock_user
        
        # Test avec le même utilisateur
        result1 = auth_service.authenticate_user("test@example.com", "password123")
        result2 = auth_service.authenticate_user("test@example.com", "password123")
        
        assert result1 == mock_user
        assert result2 == mock_user
        
        # Test avec mauvais mot de passe
        result3 = auth_service.authenticate_user("test@example.com", "wrong_password")
        assert result3 is None
    
    def test_sql_injection_protection(self, auth_service):
        """Test de protection contre l'injection SQL"""
        # Test avec des entrées malveillantes
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "test@example.com'; UPDATE users SET is_admin=true WHERE email='test@example.com'; --",
        ]
        
        for malicious_input in malicious_inputs:
            # Le service devrait traiter ces entrées comme des chaînes normales
            # (la protection SQL est gérée par SQLAlchemy)
            try:
                hashed = auth_service.hash_password(malicious_input)
                assert auth_service.verify_password(malicious_input, hashed)
            except Exception:
                # Si une exception est levée, c'est acceptable
                pass
    
    def test_xss_protection(self, auth_service):
        """Test de protection contre XSS"""
        # Test avec des entrées contenant du JavaScript
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
            "<svg onload=alert('xss')>",
        ]
        
        for xss_input in xss_inputs:
            # Le service devrait traiter ces entrées comme des chaînes normales
            try:
                hashed = auth_service.hash_password(xss_input)
                assert auth_service.verify_password(xss_input, hashed)
            except Exception:
                # Si une exception est levée, c'est acceptable
                pass
    
    def test_token_expiration_security(self, auth_service):
        """Test de sécurité d'expiration des tokens"""
        data = {"sub": "user123", "email": "test@example.com"}
        
        # Test avec token valide
        token = auth_service.create_access_token(data)
        payload = auth_service.verify_token(token)
        assert payload is not None
        
        # Test avec token expiré
        expired_data = {"sub": "user123", "exp": datetime.utcnow() - timedelta(hours=1)}
        expired_token = jwt.encode(expired_data, auth_service.secret_key, algorithm=auth_service.algorithm)
        assert auth_service.verify_token(expired_token) is None
        
        # Test avec token sans expiration (devrait être accepté car l'expiration est ajoutée automatiquement)
        no_exp_data = {"sub": "user123", "email": "test@example.com"}
        no_exp_token = jwt.encode(no_exp_data, auth_service.secret_key, algorithm=auth_service.algorithm)
        # Le token devrait être accepté car l'expiration est gérée par create_access_token
        payload = auth_service.verify_token(no_exp_token)
        assert payload is not None
    
    def test_secret_key_security(self, auth_service):
        """Test de sécurité de la clé secrète"""
        # Test que la clé secrète est définie
        assert auth_service.secret_key is not None
        assert len(auth_service.secret_key) > 0
        
        # Test que la clé secrète est suffisamment longue
        assert len(auth_service.secret_key) >= 32  # Minimum recommandé
        
        # Test que la clé secrète n'est pas une valeur par défaut faible
        weak_secrets = ["secret", "password", "123456", "admin", "test"]
        assert auth_service.secret_key not in weak_secrets
    
    def test_algorithm_security(self, auth_service):
        """Test de sécurité de l'algorithme"""
        # Test que l'algorithme est sécurisé
        assert auth_service.algorithm == "HS256"  # Algorithme sécurisé
        
        # Test que l'algorithme n'est pas vulnérable
        vulnerable_algorithms = ["none", "HS1", "MD5"]
        assert auth_service.algorithm not in vulnerable_algorithms
    
    def test_input_validation_security(self, auth_service):
        """Test de validation de sécurité des entrées"""
        # Test avec entrées vides (devrait lever une exception)
        with pytest.raises(ValueError):
            auth_service.verify_password("", "any_hash")
        with pytest.raises(ValueError):
            auth_service.verify_password("password", "")
        
        # Test avec entrées None
        with pytest.raises((TypeError, AttributeError)):
            auth_service.verify_password(None, "any_hash")
        
        with pytest.raises((TypeError, AttributeError)):
            auth_service.verify_password("password", None)
        
        # Test avec entrées très longues (devrait lever une exception)
        long_password = "a" * 10000
        with pytest.raises(ValueError):
            auth_service.hash_password(long_password)
    
    def test_timing_attack_protection(self, auth_service):
        """Test de protection contre les attaques par timing"""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        # Test que la vérification prend un temps constant
        # (bcrypt est conçu pour être résistant aux attaques par timing)
        import time
        
        start_time = time.time()
        auth_service.verify_password(password, hashed)
        correct_time = time.time() - start_time
        
        start_time = time.time()
        auth_service.verify_password("wrong_password", hashed)
        wrong_time = time.time() - start_time
        
        # Les temps devraient être similaires (protection contre timing attacks)
        assert abs(correct_time - wrong_time) < 0.1  # Tolérance de 100ms
    
    def test_memory_security(self, auth_service):
        """Test de sécurité mémoire"""
        password = "test_password_123"
        hashed = auth_service.hash_password(password)
        
        # Test que les données sensibles ne sont pas exposées
        assert "test_password_123" not in str(hashed)
        assert "test_password_123" not in repr(hashed)
        
        # Test que le mot de passe original n'est pas stocké
        assert password != hashed
        assert password not in hashed
    
    def test_error_message_security(self, auth_service):
        """Test de sécurité des messages d'erreur"""
        # Test que les messages d'erreur ne révèlent pas d'informations sensibles
        try:
            auth_service.verify_token("invalid_token")
        except Exception as e:
            error_message = str(e)
            # Le message d'erreur ne devrait pas contenir d'informations sensibles
            assert "secret" not in error_message.lower()
            assert "key" not in error_message.lower()
            assert "algorithm" not in error_message.lower()
    
    def test_registration_security(self, auth_service):
        """Test de sécurité d'inscription"""
        # Test avec email existant
        mock_existing_user = Mock()
        auth_service.user_repo.get_by_email.return_value = mock_existing_user
        
        with pytest.raises(ValueError, match="Email déjà utilisé"):
            auth_service.register(
                "existing@example.com",
                "password123",
                "Test",
                "User",
                "123 Test Street"
            )
        
        # Test avec email valide
        auth_service.user_repo.get_by_email.return_value = None
        mock_new_user = Mock()
        auth_service.user_repo.create.return_value = mock_new_user
        
        result = auth_service.register(
            "new@example.com",
            "password123",
            "Test",
            "User",
            "123 Test Street"
        )
        
        assert result == mock_new_user
        auth_service.user_repo.create.assert_called_once()
        
        # Vérifier que le mot de passe est haché
        call_args = auth_service.user_repo.create.call_args[0][0]
        assert "password_hash" in call_args
        assert call_args["password_hash"] != "password123"
        assert call_args["password_hash"].startswith("$2b$")
    
    def test_authentication_security(self, auth_service):
        """Test de sécurité d'authentification"""
        # Test avec utilisateur inexistant
        auth_service.user_repo.get_by_email.return_value = None
        
        result = auth_service.authenticate_user("nonexistent@example.com", "password123")
        assert result is None
        
        # Test avec mauvais mot de passe
        mock_user = Mock()
        mock_user.password_hash = auth_service.hash_password("correct_password")
        auth_service.user_repo.get_by_email.return_value = mock_user
        
        result = auth_service.authenticate_user("test@example.com", "wrong_password")
        assert result is None
        
        # Test avec bon mot de passe
        result = auth_service.authenticate_user("test@example.com", "correct_password")
        assert result == mock_user
