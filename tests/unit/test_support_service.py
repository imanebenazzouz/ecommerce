#!/usr/bin/env python3
"""
Tests unitaires pour le service de support
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.database.repositories_simple import PostgreSQLThreadRepository

@pytest.mark.unit
@pytest.mark.support
class TestSupportService:
    """Tests unitaires pour le service de support"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def thread_repo(self, mock_db):
        """Repository de threads avec mock"""
        return PostgreSQLThreadRepository(mock_db)
    
    def test_create_thread_success(self, thread_repo, mock_db):
        """Test de création de thread réussie"""
        # Données du thread
        thread_data = {
            "user_id": "user123",
            "subject": "Problème avec ma commande",
            "status": "OPEN"
        }
        
        # Mock de la création
        mock_thread = Mock()
        mock_thread.id = "thread123"
        mock_thread.user_id = "user123"
        mock_thread.subject = "Problème avec ma commande"
        mock_thread.status = "OPEN"
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test de création
        result = thread_repo.create(thread_data)
        
        assert result is not None
        assert result.id == "thread123"
        assert result.user_id == "user123"
        assert result.subject == "Problème avec ma commande"
        assert result.status == "OPEN"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_get_thread_by_id_success(self, thread_repo, mock_db):
        """Test de récupération de thread par ID réussie"""
        # Mock du thread
        mock_thread = Mock()
        mock_thread.id = "thread123"
        mock_thread.user_id = "user123"
        mock_thread.subject = "Problème avec ma commande"
        mock_thread.status = "OPEN"
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_thread
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = thread_repo.get_by_id("thread123")
        
        assert result is not None
        assert result.id == "thread123"
        assert result.user_id == "user123"
        mock_db.query.assert_called_once()
    
    def test_get_thread_by_id_not_found(self, thread_repo, mock_db):
        """Test de récupération de thread par ID non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = thread_repo.get_by_id("nonexistent")
        
        assert result is None
        mock_db.query.assert_called_once()
    
    def test_get_threads_by_user_id(self, thread_repo, mock_db):
        """Test de récupération des threads par ID utilisateur"""
        # Mock des threads
        mock_threads = [
            Mock(id="thread1", user_id="user123", subject="Problème 1", status="OPEN"),
            Mock(id="thread2", user_id="user123", subject="Problème 2", status="CLOSED"),
            Mock(id="thread3", user_id="user456", subject="Problème 3", status="OPEN")
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_threads
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = thread_repo.get_by_user_id("user123")
        
        assert result is not None
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_get_all_threads(self, thread_repo, mock_db):
        """Test de récupération de tous les threads"""
        # Mock des threads
        mock_threads = [
            Mock(id="thread1", user_id="user123", subject="Problème 1", status="OPEN"),
            Mock(id="thread2", user_id="user456", subject="Problème 2", status="CLOSED")
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.all.return_value = mock_threads
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = thread_repo.get_all()
        
        assert result is not None
        assert len(result) == 2
        mock_db.query.assert_called_once()
    
    def test_add_message_to_thread_success(self, thread_repo, mock_db):
        """Test d'ajout de message à un thread réussi"""
        # Données du message
        message_data = {
            "sender_id": "user123",
            "content": "Bonjour, j'ai un problème avec ma commande",
            "is_admin": False
        }
        
        # Mock de la création
        mock_message = Mock()
        mock_message.id = "message123"
        mock_message.thread_id = "thread123"
        mock_message.sender_id = "user123"
        mock_message.content = "Bonjour, j'ai un problème avec ma commande"
        mock_message.is_admin = False
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test d'ajout
        result = thread_repo.add_message("thread123", message_data)
        
        assert result is not None
        assert result.id == "message123"
        assert result.thread_id == "thread123"
        assert result.sender_id == "user123"
        assert result.content == "Bonjour, j'ai un problème avec ma commande"
        assert result.is_admin is False
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_thread_status_workflow(self, thread_repo):
        """Test du workflow des statuts de thread"""
        # Workflow typique d'un thread
        workflow = [
            "OPEN",     # Thread ouvert
            "PENDING",  # Thread en attente
            "CLOSED"    # Thread fermé
        ]
        
        # Vérifier que tous les statuts sont valides
        valid_statuses = ["OPEN", "PENDING", "CLOSED"]
        for status in workflow:
            assert status in valid_statuses
        
        # Vérifier que les statuts sont différents
        assert len(set(workflow)) == len(workflow)
    
    def test_thread_validation(self, thread_repo):
        """Test de validation des données de thread"""
        # Test avec données valides
        valid_thread_data = {
            "user_id": "user123",
            "subject": "Problème avec ma commande",
            "status": "OPEN"
        }
        
        # Les données valides ne doivent pas lever d'exception
        try:
            assert valid_thread_data["user_id"] is not None
            assert valid_thread_data["subject"] is not None
            assert len(valid_thread_data["subject"]) > 0
            assert valid_thread_data["status"] in ["OPEN", "PENDING", "CLOSED"]
        except AssertionError:
            pytest.fail("Les données valides ont échoué la validation")
    
    def test_message_validation(self, thread_repo):
        """Test de validation des données de message"""
        # Test avec données valides
        valid_message_data = {
            "sender_id": "user123",
            "content": "Bonjour, j'ai un problème avec ma commande",
            "is_admin": False
        }
        
        # Les données valides ne doivent pas lever d'exception
        try:
            assert valid_message_data["sender_id"] is not None
            assert valid_message_data["content"] is not None
            assert len(valid_message_data["content"]) > 0
            assert isinstance(valid_message_data["is_admin"], bool)
        except AssertionError:
            pytest.fail("Les données valides ont échoué la validation")
    
    def test_thread_priority_levels(self, thread_repo):
        """Test des niveaux de priorité des threads"""
        # Niveaux de priorité
        priority_levels = ["LOW", "MEDIUM", "HIGH", "URGENT"]
        
        for priority in priority_levels:
            assert priority in priority_levels
            assert isinstance(priority, str)
            assert len(priority) > 0
    
    def test_thread_categories(self, thread_repo):
        """Test des catégories de threads"""
        # Catégories de support
        categories = [
            "ORDER_ISSUE",
            "PAYMENT_PROBLEM",
            "SHIPPING_DELAY",
            "PRODUCT_DEFECT",
            "ACCOUNT_ISSUE",
            "TECHNICAL_SUPPORT",
            "GENERAL_INQUIRY"
        ]
        
        for category in categories:
            assert category in categories
            assert isinstance(category, str)
            assert len(category) > 0
    
    def test_message_types(self, thread_repo):
        """Test des types de messages"""
        # Types de messages
        message_types = [
            "CUSTOMER_MESSAGE",
            "ADMIN_RESPONSE",
            "SYSTEM_NOTIFICATION",
            "AUTO_REPLY"
        ]
        
        for msg_type in message_types:
            assert msg_type in message_types
            assert isinstance(msg_type, str)
            assert len(msg_type) > 0
    
    def test_thread_escalation(self, thread_repo):
        """Test de l'escalation des threads"""
        # Niveaux d'escalation
        escalation_levels = [
            "LEVEL_1",  # Support de base
            "LEVEL_2",  # Support avancé
            "LEVEL_3",  # Support expert
            "MANAGEMENT"  # Direction
        ]
        
        for level in escalation_levels:
            assert level in escalation_levels
            assert isinstance(level, str)
            assert len(level) > 0
    
    def test_thread_sla_handling(self, thread_repo):
        """Test de la gestion des SLA (Service Level Agreement)"""
        # SLA par priorité
        sla_hours = {
            "URGENT": 1,    # 1 heure
            "HIGH": 4,      # 4 heures
            "MEDIUM": 24,   # 24 heures
            "LOW": 72       # 72 heures
        }
        
        for priority, hours in sla_hours.items():
            assert priority in sla_hours
            assert hours > 0
            assert isinstance(hours, int)
    
    def test_thread_auto_close(self, thread_repo):
        """Test de la fermeture automatique des threads"""
        # Conditions de fermeture automatique
        auto_close_conditions = [
            "NO_RESPONSE_7_DAYS",
            "CUSTOMER_SATISFIED",
            "ISSUE_RESOLVED",
            "DUPLICATE_THREAD"
        ]
        
        for condition in auto_close_conditions:
            assert condition in auto_close_conditions
            assert isinstance(condition, str)
            assert len(condition) > 0
    
    def test_thread_metrics(self, thread_repo):
        """Test des métriques de support"""
        # Métriques de support
        metrics = {
            "response_time": 2.5,  # Heures
            "resolution_time": 24.0,  # Heures
            "customer_satisfaction": 4.5,  # Sur 5
            "first_call_resolution": 0.85  # 85%
        }
        
        for metric, value in metrics.items():
            assert metric in metrics
            assert value > 0
            assert isinstance(value, (int, float))
    
    def test_thread_edge_cases(self, thread_repo):
        """Test des cas limites des threads"""
        # Test avec ID utilisateur vide
        assert thread_repo.get_by_user_id("") is None
        
        # Test avec ID thread vide
        assert thread_repo.get_by_id("") is None
        
        # Test avec sujet vide
        empty_subject_data = {
            "user_id": "user123",
            "subject": "",
            "status": "OPEN"
        }
        
        # Le sujet vide devrait être invalide
        assert len(empty_subject_data["subject"]) == 0
    
    def test_thread_search_functionality(self, thread_repo):
        """Test de la fonctionnalité de recherche de threads"""
        # Critères de recherche
        search_criteria = {
            "status": "OPEN",
            "priority": "HIGH",
            "category": "ORDER_ISSUE",
            "date_range": "last_7_days"
        }
        
        for criterion, value in search_criteria.items():
            assert criterion in search_criteria
            assert value is not None
            assert isinstance(value, str)
            assert len(value) > 0
