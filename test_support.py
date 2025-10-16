#!/usr/bin/env python3
"""
Tests pour le support client
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

from backend_demo import (
    User, MessageThread, Message, ThreadRepository, CustomerService, UserRepository
)
import uuid
import time


class TestMessage(unittest.TestCase):
    """Tests pour l'entité Message"""
    
    def test_create_message(self):
        """Test la création d'un message"""
        thread_id = str(uuid.uuid4())
        author_user_id = str(uuid.uuid4())
        
        message = Message(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            author_user_id=author_user_id,
            body="Hello, I need help with my order",
            created_at=time.time()
        )
        
        self.assertEqual(message.thread_id, thread_id)
        self.assertEqual(message.author_user_id, author_user_id)
        self.assertEqual(message.body, "Hello, I need help with my order")
        self.assertIsNotNone(message.created_at)
        self.assertFalse(message.read_by_client)  # Par défaut non lu
    
    def test_create_message_from_support(self):
        """Test la création d'un message du support (sans author_user_id)"""
        thread_id = str(uuid.uuid4())
        
        message = Message(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            author_user_id=None,  # Message du support
            body="Thank you for contacting us. How can we help?",
            created_at=time.time()
        )
        
        self.assertEqual(message.thread_id, thread_id)
        self.assertIsNone(message.author_user_id)
        self.assertEqual(message.body, "Thank you for contacting us. How can we help?")
        self.assertFalse(message.read_by_client)


class TestMessageThread(unittest.TestCase):
    """Tests pour l'entité MessageThread"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.user_id = str(uuid.uuid4())
        self.order_id = str(uuid.uuid4())
    
    def test_create_thread(self):
        """Test la création d'un fil de discussion"""
        thread = MessageThread(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            order_id=self.order_id,
            subject="Problem with my order"
        )
        
        self.assertEqual(thread.user_id, self.user_id)
        self.assertEqual(thread.order_id, self.order_id)
        self.assertEqual(thread.subject, "Problem with my order")
        self.assertEqual(len(thread.messages), 0)
        self.assertFalse(thread.closed)
        self.assertEqual(thread.unread_count, 0)
    
    def test_create_thread_without_order(self):
        """Test la création d'un fil sans commande associée"""
        thread = MessageThread(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            order_id=None,
            subject="General inquiry"
        )
        
        self.assertEqual(thread.user_id, self.user_id)
        self.assertIsNone(thread.order_id)
        self.assertEqual(thread.subject, "General inquiry")
        self.assertEqual(len(thread.messages), 0)
        self.assertFalse(thread.closed)
        self.assertEqual(thread.unread_count, 0)
    
    def test_thread_with_messages(self):
        """Test un fil avec des messages"""
        thread = MessageThread(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            order_id=self.order_id,
            subject="Order issue"
        )
        
        # Ajouter des messages
        message1 = Message(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            author_user_id=self.user_id,
            body="I have a problem with my order",
            created_at=time.time()
        )
        
        message2 = Message(
            id=str(uuid.uuid4()),
            thread_id=thread.id,
            author_user_id=None,  # Support
            body="We'll help you resolve this issue",
            created_at=time.time()
        )
        
        thread.messages.append(message1)
        thread.messages.append(message2)
        
        self.assertEqual(len(thread.messages), 2)
        self.assertEqual(thread.messages[0].body, "I have a problem with my order")
        self.assertEqual(thread.messages[1].body, "We'll help you resolve this issue")


class TestThreadRepository(unittest.TestCase):
    """Tests pour le repository des fils de discussion"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.repo = ThreadRepository()
        self.user_id = str(uuid.uuid4())
    
    def test_add_thread(self):
        """Test l'ajout d'un fil de discussion"""
        thread = MessageThread(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            order_id=str(uuid.uuid4()),
            subject="Test thread"
        )
        
        self.repo.add(thread)
        
        # Vérifier que le fil est récupérable
        retrieved = self.repo.get(thread.id)
        self.assertEqual(retrieved.id, thread.id)
        self.assertEqual(retrieved.user_id, self.user_id)
        self.assertEqual(retrieved.subject, "Test thread")
    
    def test_get_nonexistent_thread(self):
        """Test la récupération d'un fil inexistant"""
        self.assertIsNone(self.repo.get("nonexistent-id"))
    
    def test_list_threads_by_user(self):
        """Test la liste des fils par utilisateur"""
        user1_id = str(uuid.uuid4())
        user2_id = str(uuid.uuid4())
        
        # Créer des fils pour différents utilisateurs
        thread1 = MessageThread(
            id=str(uuid.uuid4()),
            user_id=user1_id,
            order_id=None,
            subject="User 1 Thread 1"
        )
        
        thread2 = MessageThread(
            id=str(uuid.uuid4()),
            user_id=user1_id,
            order_id=str(uuid.uuid4()),
            subject="User 1 Thread 2"
        )
        
        thread3 = MessageThread(
            id=str(uuid.uuid4()),
            user_id=user2_id,
            order_id=None,
            subject="User 2 Thread"
        )
        
        self.repo.add(thread1)
        self.repo.add(thread2)
        self.repo.add(thread3)
        
        # Récupérer les fils de user1
        user1_threads = self.repo.list_by_user(user1_id)
        
        self.assertEqual(len(user1_threads), 2)
        thread_ids = [t.id for t in user1_threads]
        self.assertIn(thread1.id, thread_ids)
        self.assertIn(thread2.id, thread_ids)
        self.assertNotIn(thread3.id, thread_ids)
        
        # Récupérer les fils de user2
        user2_threads = self.repo.list_by_user(user2_id)
        
        self.assertEqual(len(user2_threads), 1)
        self.assertEqual(user2_threads[0].id, thread3.id)
    
    def test_empty_user_threads(self):
        """Test la liste des fils pour un utilisateur sans fils"""
        empty_user_id = str(uuid.uuid4())
        threads = self.repo.list_by_user(empty_user_id)
        
        self.assertEqual(len(threads), 0)


class TestCustomerService(unittest.TestCase):
    """Tests pour le service client"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.thread_repo = ThreadRepository()
        self.user_repo = UserRepository()
        self.customer_service = CustomerService(self.thread_repo, self.user_repo)
        
        self.user_id = str(uuid.uuid4())
        self.admin_id = str(uuid.uuid4())
        
        # Créer un utilisateur admin
        admin_user = User(
            id=self.admin_id,
            email="admin@support.com",
            password_hash="hash",
            first_name="Support",
            last_name="Admin",
            address="Support Address",
            is_admin=True
        )
        self.user_repo.add(admin_user)
        
        # Créer un utilisateur régulier
        regular_user = User(
            id=self.user_id,
            email="user@example.com",
            password_hash="hash",
            first_name="Regular",
            last_name="User",
            address="User Address",
            is_admin=False
        )
        self.user_repo.add(regular_user)
    
    def test_open_thread(self):
        """Test l'ouverture d'un fil de discussion"""
        thread = self.customer_service.open_thread(
            self.user_id, 
            "Need help with my order",
            order_id=str(uuid.uuid4())
        )
        
        self.assertEqual(thread.user_id, self.user_id)
        self.assertEqual(thread.subject, "Need help with my order")
        self.assertIsNotNone(thread.order_id)
        self.assertFalse(thread.closed)
        self.assertEqual(len(thread.messages), 0)
        self.assertEqual(thread.unread_count, 0)
        
        # Vérifier que le fil est dans le repository
        retrieved = self.thread_repo.get(thread.id)
        self.assertEqual(retrieved.id, thread.id)
    
    def test_open_thread_without_order(self):
        """Test l'ouverture d'un fil sans commande"""
        thread = self.customer_service.open_thread(
            self.user_id,
            "General question"
        )
        
        self.assertEqual(thread.user_id, self.user_id)
        self.assertEqual(thread.subject, "General question")
        self.assertIsNone(thread.order_id)
    
    def test_post_message_from_user(self):
        """Test l'envoi d'un message par un utilisateur"""
        # Ouvrir un fil
        thread = self.customer_service.open_thread(self.user_id, "Test thread")
        
        # Poster un message
        message = self.customer_service.post_message(thread.id, self.user_id, "Hello, I need help")
        
        self.assertEqual(message.thread_id, thread.id)
        self.assertEqual(message.author_user_id, self.user_id)
        self.assertEqual(message.body, "Hello, I need help")
        self.assertIsNotNone(message.created_at)
        self.assertFalse(message.read_by_client)
        
        # Vérifier que le message est dans le fil
        updated_thread = self.thread_repo.get(thread.id)
        self.assertEqual(len(updated_thread.messages), 1)
        self.assertEqual(updated_thread.messages[0].id, message.id)
        self.assertEqual(updated_thread.unread_count, 0)  # Messages utilisateur ne comptent pas comme non lus
    
    def test_post_message_from_support(self):
        """Test l'envoi d'un message par le support"""
        # Ouvrir un fil
        thread = self.customer_service.open_thread(self.user_id, "Support thread")
        
        # Poster un message du support
        message = self.customer_service.post_message(thread.id, None, "Thank you for contacting us")
        
        self.assertEqual(message.thread_id, thread.id)
        self.assertIsNone(message.author_user_id)  # Support
        self.assertEqual(message.body, "Thank you for contacting us")
        
        # Vérifier que le compteur de messages non lus a augmenté
        updated_thread = self.thread_repo.get(thread.id)
        self.assertEqual(updated_thread.unread_count, 1)
        self.assertEqual(len(updated_thread.messages), 1)
    
    def test_post_message_to_nonexistent_thread(self):
        """Test l'envoi d'un message à un fil inexistant"""
        with self.assertRaises(ValueError) as context:
            self.customer_service.post_message("nonexistent-thread", self.user_id, "Hello")
        
        self.assertIn("Fil introuvable ou fermé", str(context.exception))
    
    def test_post_message_to_closed_thread(self):
        """Test l'envoi d'un message à un fil fermé"""
        # Ouvrir un fil
        thread = self.customer_service.open_thread(self.user_id, "Closed thread")
        
        # Fermer le fil
        thread.closed = True
        
        # Essayer de poster un message
        with self.assertRaises(ValueError) as context:
            self.customer_service.post_message(thread.id, self.user_id, "Hello")
        
        self.assertIn("Fil introuvable ou fermé", str(context.exception))
    
    def test_post_message_from_nonexistent_user(self):
        """Test l'envoi d'un message par un utilisateur inexistant"""
        thread = self.customer_service.open_thread(self.user_id, "Test thread")
        
        with self.assertRaises(ValueError) as context:
            self.customer_service.post_message(thread.id, "nonexistent-user", "Hello")
        
        self.assertIn("Auteur inconnu", str(context.exception))
    
    def test_mark_thread_as_read(self):
        """Test le marquage d'un fil comme lu"""
        # Ouvrir un fil et poster des messages du support
        thread = self.customer_service.open_thread(self.user_id, "Read test thread")
        
        # Poster un message du support
        self.customer_service.post_message(thread.id, None, "Support message 1")
        self.customer_service.post_message(thread.id, None, "Support message 2")
        
        # Vérifier que le compteur est à 2
        thread = self.thread_repo.get(thread.id)
        self.assertEqual(thread.unread_count, 2)
        
        # Marquer comme lu
        self.customer_service.mark_thread_as_read(thread.id, self.user_id)
        
        # Vérifier que le compteur est à 0
        updated_thread = self.thread_repo.get(thread.id)
        self.assertEqual(updated_thread.unread_count, 0)
        
        # Vérifier que les messages sont marqués comme lus
        for message in updated_thread.messages:
            if message.author_user_id is None:  # Messages du support
                self.assertTrue(message.read_by_client)
    
    def test_mark_nonexistent_thread_as_read(self):
        """Test le marquage d'un fil inexistant comme lu"""
        with self.assertRaises(ValueError) as context:
            self.customer_service.mark_thread_as_read("nonexistent-thread", self.user_id)
        
        self.assertIn("Fil introuvable", str(context.exception))
    
    def test_mark_thread_as_read_wrong_user(self):
        """Test le marquage d'un fil comme lu par le mauvais utilisateur"""
        other_user_id = str(uuid.uuid4())
        thread = self.customer_service.open_thread(self.user_id, "Access test thread")
        
        with self.assertRaises(PermissionError) as context:
            self.customer_service.mark_thread_as_read(thread.id, other_user_id)
        
        self.assertIn("Accès refusé", str(context.exception))
    
    def test_close_thread(self):
        """Test la fermeture d'un fil par un admin"""
        thread = self.customer_service.open_thread(self.user_id, "Thread to close")
        
        # Fermer le fil
        closed_thread = self.customer_service.close_thread(thread.id, self.admin_id)
        
        self.assertTrue(closed_thread.closed)
        
        # Vérifier dans le repository
        updated_thread = self.thread_repo.get(thread.id)
        self.assertTrue(updated_thread.closed)
    
    def test_close_thread_without_admin(self):
        """Test la fermeture d'un fil sans être admin"""
        thread = self.customer_service.open_thread(self.user_id, "Thread to close")
        
        with self.assertRaises(PermissionError) as context:
            self.customer_service.close_thread(thread.id, self.user_id)  # Utilisateur non-admin
        
        self.assertIn("Droits insuffisants", str(context.exception))
        
        # Vérifier que le fil n'est pas fermé
        updated_thread = self.thread_repo.get(thread.id)
        self.assertFalse(updated_thread.closed)
    
    def test_close_nonexistent_thread(self):
        """Test la fermeture d'un fil inexistant"""
        with self.assertRaises(ValueError) as context:
            self.customer_service.close_thread("nonexistent-thread", self.admin_id)
        
        self.assertIn("Fil introuvable", str(context.exception))


class TestSupportWorkflow(unittest.TestCase):
    """Tests pour les workflows complets du support"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.thread_repo = ThreadRepository()
        self.user_repo = UserRepository()
        self.customer_service = CustomerService(self.thread_repo, self.user_repo)
        
        self.user_id = str(uuid.uuid4())
        self.admin_id = str(uuid.uuid4())
        
        # Créer des utilisateurs
        user = User(
            id=self.user_id,
            email="user@example.com",
            password_hash="hash",
            first_name="Test",
            last_name="User",
            address="Test Address",
            is_admin=False
        )
        
        admin = User(
            id=self.admin_id,
            email="admin@support.com",
            password_hash="hash",
            first_name="Support",
            last_name="Admin",
            address="Admin Address",
            is_admin=True
        )
        
        self.user_repo.add(user)
        self.user_repo.add(admin)
    
    def test_complete_support_conversation(self):
        """Test une conversation complète de support"""
        # 1. L'utilisateur ouvre un fil
        thread = self.customer_service.open_thread(
            self.user_id, 
            "Order delivery issue",
            order_id=str(uuid.uuid4())
        )
        
        self.assertEqual(thread.subject, "Order delivery issue")
        self.assertFalse(thread.closed)
        self.assertEqual(thread.unread_count, 0)
        
        # 2. L'utilisateur envoie son premier message
        user_message = self.customer_service.post_message(
            thread.id, self.user_id, "My order hasn't arrived yet"
        )
        
        self.assertEqual(user_message.body, "My order hasn't arrived yet")
        self.assertEqual(user_message.author_user_id, self.user_id)
        
        # 3. Le support répond
        support_message1 = self.customer_service.post_message(
            thread.id, None, "I'll check the status of your order"
        )
        
        self.assertIsNone(support_message1.author_user_id)
        
        # Vérifier que le compteur de messages non lus a augmenté
        thread = self.thread_repo.get(thread.id)
        self.assertEqual(thread.unread_count, 1)
        
        # 4. L'utilisateur lit les messages
        self.customer_service.mark_thread_as_read(thread.id, self.user_id)
        
        thread = self.thread_repo.get(thread.id)
        self.assertEqual(thread.unread_count, 0)
        
        # 5. L'utilisateur répond
        user_reply = self.customer_service.post_message(
            thread.id, self.user_id, "Thank you, please let me know what you find"
        )
        
        # 6. Le support donne une réponse finale
        support_message2 = self.customer_service.post_message(
            thread.id, None, "Your order is on its way, tracking number: TRK123456"
        )
        
        # 7. Fermer le fil
        closed_thread = self.customer_service.close_thread(thread.id, self.admin_id)
        
        self.assertTrue(closed_thread.closed)
        
        # Vérifier le contenu final
        final_thread = self.thread_repo.get(thread.id)
        self.assertEqual(len(final_thread.messages), 4)
        self.assertTrue(final_thread.closed)
        self.assertEqual(final_thread.unread_count, 1)  # Le dernier message du support
    
    def test_multiple_threads_per_user(self):
        """Test plusieurs fils par utilisateur"""
        # Créer plusieurs fils pour le même utilisateur
        thread1 = self.customer_service.open_thread(self.user_id, "Order issue")
        thread2 = self.customer_service.open_thread(self.user_id, "Billing question")
        thread3 = self.customer_service.open_thread(self.user_id, "Product inquiry")
        
        # Ajouter des messages du support dans chaque fil
        self.customer_service.post_message(thread1.id, None, "Support response 1")
        self.customer_service.post_message(thread2.id, None, "Support response 2")
        self.customer_service.post_message(thread3.id, None, "Support response 3")
        
        # Récupérer tous les fils de l'utilisateur
        user_threads = self.thread_repo.list_by_user(self.user_id)
        
        self.assertEqual(len(user_threads), 3)
        
        # Vérifier que chaque fil a un message non lu
        for thread in user_threads:
            self.assertEqual(thread.unread_count, 1)
    
    def test_thread_with_mixed_messages(self):
        """Test un fil avec des messages mixtes (utilisateur et support)"""
        thread = self.customer_service.open_thread(self.user_id, "Mixed messages test")
        
        # Conversation mixte
        self.customer_service.post_message(thread.id, self.user_id, "Hello")
        self.customer_service.post_message(thread.id, None, "Hi, how can I help?")
        self.customer_service.post_message(thread.id, self.user_id, "I need assistance")
        self.customer_service.post_message(thread.id, None, "Of course, what's the issue?")
        self.customer_service.post_message(thread.id, self.user_id, "Never mind, I found the solution")
        self.customer_service.post_message(thread.id, None, "Great! Let me know if you need anything else")
        
        # Vérifier le fil final
        final_thread = self.thread_repo.get(thread.id)
        self.assertEqual(len(final_thread.messages), 6)
        self.assertEqual(final_thread.unread_count, 3)  # 3 messages du support
        
        # Marquer comme lu
        self.customer_service.mark_thread_as_read(thread.id, self.user_id)
        
        final_thread = self.thread_repo.get(thread.id)
        self.assertEqual(final_thread.unread_count, 0)


if __name__ == '__main__':
    print("=== Tests du support client ===")
    unittest.main(verbosity=2)
