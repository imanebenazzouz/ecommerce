#!/usr/bin/env python3
"""
Tests pour le module d'authentification
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

from backend_demo import (
    User, AuthService, UserRepository, SessionManager, PasswordHasher
)
import uuid


class TestPasswordHasher(unittest.TestCase):
    """Tests pour le hachage des mots de passe"""
    
    def test_hash_password(self):
        """Test le hachage d'un mot de passe"""
        password = "monmotdepasse123"
        hashed = PasswordHasher.hash(password)
        
        # Vérifier que le hash est différent du mot de passe original
        self.assertNotEqual(password, hashed)
        # Vérifier que le hash n'est pas vide
        self.assertTrue(len(hashed) > 0)
        # Vérifier que le hash contient le préfixe bcrypt
        self.assertTrue(hashed.startswith('$2b$'))
    
    def test_verify_password(self):
        """Test la vérification d'un mot de passe"""
        password = "monmotdepasse123"
        hashed = PasswordHasher.hash(password)
        
        # Vérification correcte
        self.assertTrue(PasswordHasher.verify(password, hashed))
        
        # Vérification avec mauvais mot de passe
        self.assertFalse(PasswordHasher.verify("mauvais", hashed))
        self.assertFalse(PasswordHasher.verify("", hashed))


class TestUserRepository(unittest.TestCase):
    """Tests pour le repository des utilisateurs"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.repo = UserRepository()
    
    def test_add_user(self):
        """Test l'ajout d'un utilisateur"""
        user = User(
            id=str(uuid.uuid4()),
            email="test@example.com",
            password_hash="hash123",
            first_name="John",
            last_name="Doe",
            address="123 Main St",
            is_admin=False
        )
        
        self.repo.add(user)
        
        # Vérifier que l'utilisateur est récupérable par ID
        retrieved = self.repo.get(user.id)
        self.assertEqual(retrieved.id, user.id)
        self.assertEqual(retrieved.email, user.email)
        
        # Vérifier que l'utilisateur est récupérable par email
        retrieved_by_email = self.repo.get_by_email(user.email)
        self.assertEqual(retrieved_by_email.id, user.id)
        
        # Test avec email en majuscules (normalisation)
        retrieved_by_email_upper = self.repo.get_by_email(user.email.upper())
        self.assertEqual(retrieved_by_email_upper.id, user.id)
    
    def test_get_nonexistent_user(self):
        """Test la récupération d'un utilisateur inexistant"""
        self.assertIsNone(self.repo.get("nonexistent"))
        self.assertIsNone(self.repo.get_by_email("nonexistent@example.com"))
    
    def test_multiple_users(self):
        """Test avec plusieurs utilisateurs"""
        user1 = User(
            id=str(uuid.uuid4()),
            email="user1@example.com",
            password_hash="hash1",
            first_name="User1",
            last_name="Doe",
            address="Address 1"
        )
        user2 = User(
            id=str(uuid.uuid4()),
            email="user2@example.com",
            password_hash="hash2",
            first_name="User2",
            last_name="Smith",
            address="Address 2",
            is_admin=True
        )
        
        self.repo.add(user1)
        self.repo.add(user2)
        
        # Vérifier que chaque utilisateur est récupérable
        self.assertEqual(self.repo.get(user1.id).email, "user1@example.com")
        self.assertEqual(self.repo.get(user2.id).email, "user2@example.com")
        
        # Vérifier les emails
        self.assertEqual(self.repo.get_by_email("user1@example.com").first_name, "User1")
        self.assertEqual(self.repo.get_by_email("user2@example.com").first_name, "User2")
        
        # Vérifier les privilèges admin
        self.assertFalse(self.repo.get(user1.id).is_admin)
        self.assertTrue(self.repo.get(user2.id).is_admin)


class TestSessionManager(unittest.TestCase):
    """Tests pour la gestion des sessions"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.session_manager = SessionManager(secret_key="test-secret-key")
        self.user_id = str(uuid.uuid4())
    
    def test_create_session(self):
        """Test la création d'une session"""
        token = self.session_manager.create_session(self.user_id)
        
        # Vérifier que le token est généré
        self.assertIsNotNone(token)
        self.assertTrue(len(token) > 0)
        
        # Vérifier que le token contient 3 parties (JWT)
        parts = token.split('.')
        self.assertEqual(len(parts), 3)
    
    def test_get_user_id_from_token(self):
        """Test la récupération de l'ID utilisateur depuis un token"""
        token = self.session_manager.create_session(self.user_id)
        retrieved_user_id = self.session_manager.get_user_id(token)
        
        self.assertEqual(retrieved_user_id, self.user_id)
    
    def test_invalid_token(self):
        """Test avec un token invalide"""
        # Token malformé
        self.assertIsNone(self.session_manager.get_user_id("invalid.token"))
        self.assertIsNone(self.session_manager.get_user_id(""))
        self.assertIsNone(self.session_manager.get_user_id("invalid"))
    
    def test_destroy_session(self):
        """Test la destruction d'une session"""
        token = self.session_manager.create_session(self.user_id)
        
        # Vérifier que le token fonctionne
        self.assertEqual(self.session_manager.get_user_id(token), self.user_id)
        
        # Détruire la session
        self.session_manager.destroy_session(token)
        
        # Vérifier que le token ne fonctionne plus
        self.assertIsNone(self.session_manager.get_user_id(token))


class TestAuthService(unittest.TestCase):
    """Tests pour le service d'authentification"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.users = UserRepository()
        self.sessions = SessionManager(secret_key="test-secret-key")
        self.auth_service = AuthService(self.users, self.sessions)
    
    def test_register_user(self):
        """Test l'inscription d'un utilisateur"""
        user = self.auth_service.register(
            email="newuser@example.com",
            password="password123",
            first_name="New",
            last_name="User",
            address="123 New St"
        )
        
        # Vérifier les propriétés de l'utilisateur
        self.assertEqual(user.email, "newuser@example.com")
        self.assertEqual(user.first_name, "New")
        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.address, "123 New St")
        self.assertFalse(user.is_admin)
        self.assertIsNotNone(user.id)
        
        # Vérifier que l'utilisateur est dans le repository
        retrieved = self.users.get(user.id)
        self.assertEqual(retrieved.email, user.email)
    
    def test_register_admin_user(self):
        """Test l'inscription d'un utilisateur admin"""
        admin = self.auth_service.register(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
            address="Admin Address",
            is_admin=True
        )
        
        self.assertTrue(admin.is_admin)
        self.assertEqual(admin.email, "admin@example.com")
    
    def test_register_duplicate_email(self):
        """Test l'inscription avec un email déjà utilisé"""
        # Premier utilisateur
        self.auth_service.register(
            email="duplicate@example.com",
            password="pass1",
            first_name="User1",
            last_name="Doe",
            address="Address1"
        )
        
        # Deuxième utilisateur avec le même email
        with self.assertRaises(ValueError) as context:
            self.auth_service.register(
                email="duplicate@example.com",
                password="pass2",
                first_name="User2",
                last_name="Smith",
                address="Address2"
            )
        
        self.assertIn("Email déjà utilisé", str(context.exception))
    
    def test_login_valid_credentials(self):
        """Test la connexion avec des identifiants valides"""
        # Inscrire un utilisateur
        user = self.auth_service.register(
            email="login@example.com",
            password="loginpass",
            first_name="Login",
            last_name="User",
            address="Login Address"
        )
        
        # Se connecter
        token = self.auth_service.login("login@example.com", "loginpass")
        
        # Vérifier que le token est généré
        self.assertIsNotNone(token)
        
        # Vérifier que le token correspond à l'utilisateur
        user_id = self.sessions.get_user_id(token)
        self.assertEqual(user_id, user.id)
    
    def test_login_invalid_credentials(self):
        """Test la connexion avec des identifiants invalides"""
        # Inscrire un utilisateur
        self.auth_service.register(
            email="testlogin@example.com",
            password="correctpass",
            first_name="Test",
            last_name="User",
            address="Test Address"
        )
        
        # Test avec mauvais mot de passe
        with self.assertRaises(ValueError) as context:
            self.auth_service.login("testlogin@example.com", "wrongpass")
        self.assertIn("Identifiants invalides", str(context.exception))
        
        # Test avec email inexistant
        with self.assertRaises(ValueError) as context:
            self.auth_service.login("nonexistent@example.com", "anypass")
        self.assertIn("Identifiants invalides", str(context.exception))
    
    def test_logout(self):
        """Test la déconnexion"""
        # Inscrire et connecter un utilisateur
        user = self.auth_service.register(
            email="logout@example.com",
            password="logoutpass",
            first_name="Logout",
            last_name="User",
            address="Logout Address"
        )
        
        token = self.auth_service.login("logout@example.com", "logoutpass")
        
        # Vérifier que le token fonctionne
        self.assertEqual(self.sessions.get_user_id(token), user.id)
        
        # Se déconnecter
        self.auth_service.logout(token)
        
        # Vérifier que le token ne fonctionne plus
        self.assertIsNone(self.sessions.get_user_id(token))


class TestUserProfile(unittest.TestCase):
    """Tests pour la gestion du profil utilisateur"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.users = UserRepository()
        self.sessions = SessionManager(secret_key="test-secret-key")
        self.auth_service = AuthService(self.users, self.sessions)
    
    def test_update_profile(self):
        """Test la mise à jour du profil"""
        # Inscrire un utilisateur
        user = self.auth_service.register(
            email="profile@example.com",
            password="profilepass",
            first_name="Original",
            last_name="Name",
            address="Original Address"
        )
        
        # Mettre à jour le profil
        user.update_profile(
            first_name="Updated",
            last_name="Name",
            address="Updated Address"
        )
        
        # Vérifier les modifications
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "Name")
        self.assertEqual(user.address, "Updated Address")
        
        # Vérifier que l'email et l'ID n'ont pas changé
        self.assertEqual(user.email, "profile@example.com")
        self.assertIsNotNone(user.id)
    
    def test_update_profile_partial(self):
        """Test la mise à jour partielle du profil"""
        user = self.auth_service.register(
            email="partial@example.com",
            password="partialpass",
            first_name="Original",
            last_name="Original",
            address="Original Address"
        )
        
        # Mettre à jour seulement le prénom
        user.update_profile(first_name="NewFirst")
        
        self.assertEqual(user.first_name, "NewFirst")
        self.assertEqual(user.last_name, "Original")  # Inchangé
        self.assertEqual(user.address, "Original Address")  # Inchangé


if __name__ == '__main__':
    print("=== Tests d'authentification ===")
    unittest.main(verbosity=2)
