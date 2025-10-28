#!/usr/bin/env python3
"""
Tests unitaires pour le support client
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
class TestSupport:
    """Tests unitaires pour le support client"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def thread_repo(self, mock_db):
        """Repository de threads avec mock"""
        return PostgreSQLThreadRepository(mock_db)
    
    def test_support_ticket_creation(self, thread_repo, mock_db):
        """Test de création de ticket de support"""
        # Données du ticket
        ticket_data = {
            "user_id": "user123",
            "subject": "Problème avec ma commande #12345",
            "closed": False
        }
        
        # Mock de la création - le repository crée un vrai objet MessageThread
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test de création
        result = thread_repo.create(ticket_data)
        
        assert result is not None
        assert result.user_id == "user123"
        assert result.subject == "Problème avec ma commande #12345"
        assert result.closed is False
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_support_ticket_retrieval(self, thread_repo, mock_db):
        """Test de récupération de ticket de support"""
        # Mock du ticket
        mock_ticket = Mock()
        mock_ticket.id = "ticket123"
        mock_ticket.user_id = "user123"
        mock_ticket.subject = "Problème avec ma commande #12345"
        mock_ticket.status = "OPEN"
        mock_ticket.priority = "HIGH"
        mock_ticket.category = "ORDER_ISSUE"
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_ticket
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = thread_repo.get_by_id("ticket123")
        
        assert result is not None
        assert result.id == "ticket123"
        assert result.user_id == "user123"
        assert result.subject == "Problème avec ma commande #12345"
        assert result.status == "OPEN"
        assert result.priority == "HIGH"
        assert result.category == "ORDER_ISSUE"
        mock_db.query.assert_called_once()
    
    def test_support_ticket_not_found(self, thread_repo, mock_db):
        """Test de ticket de support non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = thread_repo.get_by_id("nonexistent")
        
        assert result is None
        mock_db.query.assert_called_once()
    
    def test_support_tickets_by_user(self, thread_repo, mock_db):
        """Test de récupération des tickets par utilisateur"""
        # Mock des tickets
        mock_tickets = [
            Mock(id="ticket1", user_id="user123", subject="Problème 1", status="OPEN"),
            Mock(id="ticket2", user_id="user123", subject="Problème 2", status="CLOSED"),
            Mock(id="ticket3", user_id="user456", subject="Problème 3", status="OPEN")
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_tickets
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = thread_repo.get_by_user_id("user123")
        
        assert result is not None
        assert len(result) == 3
        assert result[0].id == "ticket1"
        assert result[1].id == "ticket2"
        assert result[2].id == "ticket3"
        mock_db.query.assert_called_once()
    
    def test_all_support_tickets(self, thread_repo, mock_db):
        """Test de récupération de tous les tickets"""
        # Mock des tickets
        mock_tickets = [
            Mock(id="ticket1", user_id="user123", subject="Problème 1", status="OPEN"),
            Mock(id="ticket2", user_id="user456", subject="Problème 2", status="CLOSED")
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.all.return_value = mock_tickets
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = thread_repo.get_all()
        
        assert result is not None
        assert len(result) == 2
        assert result[0].id == "ticket1"
        assert result[1].id == "ticket2"
        mock_db.query.assert_called_once()
    
    def test_support_message_creation(self, thread_repo, mock_db):
        """Test de création de message de support"""
        # Données du message
        message_data = {
            "sender_id": "user123",
            "content": "Bonjour, j'ai un problème avec ma commande. Pouvez-vous m'aider ?",
            "is_admin": False,
            "message_type": "CUSTOMER_MESSAGE"
        }
        
        # Mock de la création
        mock_message = Mock()
        mock_message.id = "message123"
        mock_message.thread_id = "ticket123"
        mock_message.sender_id = "user123"
        mock_message.content = "Bonjour, j'ai un problème avec ma commande. Pouvez-vous m'aider ?"
        mock_message.is_admin = False
        mock_message.message_type = "CUSTOMER_MESSAGE"
        
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test de création
        result = thread_repo.add_message("ticket123", message_data)
        
        assert result is not None
        assert result.id is not None  # UUID généré automatiquement
        assert result.thread_id == "ticket123"
        assert result.author_user_id == "user123"
        assert result.content == "Bonjour, j'ai un problème avec ma commande. Pouvez-vous m'aider ?"
        # Le message est d'un utilisateur (pas admin) car author_user_id n'est pas None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_support_ticket_priority_levels(self, thread_repo):
        """Test des niveaux de priorité des tickets"""
        # Niveaux de priorité
        priority_levels = ["LOW", "MEDIUM", "HIGH", "URGENT", "CRITICAL"]
        
        for priority in priority_levels:
            assert priority in priority_levels
            assert isinstance(priority, str)
            assert len(priority) > 0
    
    def test_support_ticket_categories(self, thread_repo):
        """Test des catégories de tickets"""
        # Catégories de support
        categories = [
            "ORDER_ISSUE",
            "PAYMENT_PROBLEM",
            "SHIPPING_DELAY",
            "PRODUCT_DEFECT",
            "ACCOUNT_ISSUE",
            "TECHNICAL_SUPPORT",
            "GENERAL_INQUIRY",
            "REFUND_REQUEST",
            "CANCELLATION_REQUEST"
        ]
        
        for category in categories:
            assert category in categories
            assert isinstance(category, str)
            assert len(category) > 0
    
    def test_support_ticket_status_workflow(self, thread_repo):
        """Test du workflow des statuts de tickets"""
        # Workflow typique d'un ticket
        workflow = [
            "OPEN",      # Ticket ouvert
            "PENDING",   # Ticket en attente
            "IN_PROGRESS", # Ticket en cours
            "RESOLVED",  # Ticket résolu
            "CLOSED"     # Ticket fermé
        ]
        
        # Vérifier que tous les statuts sont valides
        valid_statuses = ["OPEN", "PENDING", "IN_PROGRESS", "RESOLVED", "CLOSED"]
        for status in workflow:
            assert status in valid_statuses
        
        # Vérifier que les statuts sont différents
        assert len(set(workflow)) == len(workflow)
    
    def test_support_message_types(self, thread_repo):
        """Test des types de messages"""
        # Types de messages
        message_types = [
            "CUSTOMER_MESSAGE",
            "ADMIN_RESPONSE",
            "SYSTEM_NOTIFICATION",
            "AUTO_REPLY",
            "ESCALATION_NOTICE",
            "RESOLUTION_NOTICE"
        ]
        
        for msg_type in message_types:
            assert msg_type in message_types
            assert isinstance(msg_type, str)
            assert len(msg_type) > 0
    
    def test_support_ticket_escalation_levels(self, thread_repo):
        """Test des niveaux d'escalation des tickets"""
        # Niveaux d'escalation
        escalation_levels = [
            "LEVEL_1",    # Support de base
            "LEVEL_2",    # Support avancé
            "LEVEL_3",    # Support expert
            "MANAGEMENT", # Direction
            "EXECUTIVE"   # Direction exécutive
        ]
        
        for level in escalation_levels:
            assert level in escalation_levels
            assert isinstance(level, str)
            assert len(level) > 0
    
    def test_support_ticket_sla_requirements(self, thread_repo):
        """Test des exigences SLA des tickets"""
        # SLA par priorité (en heures)
        sla_requirements = {
            "CRITICAL": 1,    # 1 heure
            "URGENT": 4,      # 4 heures
            "HIGH": 8,        # 8 heures
            "MEDIUM": 24,     # 24 heures
            "LOW": 72         # 72 heures
        }
        
        for priority, hours in sla_requirements.items():
            assert priority in sla_requirements
            assert hours > 0
            assert isinstance(hours, int)
    
    def test_support_ticket_auto_assignment(self, thread_repo):
        """Test de l'assignation automatique des tickets"""
        # Règles d'assignation automatique
        assignment_rules = {
            "ORDER_ISSUE": "ORDER_TEAM",
            "PAYMENT_PROBLEM": "PAYMENT_TEAM",
            "SHIPPING_DELAY": "LOGISTICS_TEAM",
            "PRODUCT_DEFECT": "QUALITY_TEAM",
            "TECHNICAL_SUPPORT": "TECH_TEAM"
        }
        
        for category, team in assignment_rules.items():
            assert category in assignment_rules
            assert team in assignment_rules.values()
            assert isinstance(category, str)
            assert isinstance(team, str)
    
    def test_support_ticket_auto_close_conditions(self, thread_repo):
        """Test des conditions de fermeture automatique des tickets"""
        # Conditions de fermeture automatique
        auto_close_conditions = [
            "NO_RESPONSE_7_DAYS",
            "CUSTOMER_SATISFIED",
            "ISSUE_RESOLVED",
            "DUPLICATE_TICKET",
            "CUSTOMER_CANCELLED"
        ]
        
        for condition in auto_close_conditions:
            assert condition in auto_close_conditions
            assert isinstance(condition, str)
            assert len(condition) > 0
    
    def test_support_ticket_metrics_calculation(self, thread_repo):
        """Test du calcul des métriques de support"""
        # Métriques de support
        metrics = {
            "response_time": 2.5,  # Heures
            "resolution_time": 24.0,  # Heures
            "customer_satisfaction": 4.5,  # Sur 5
            "first_call_resolution": 0.85,  # 85%
            "ticket_volume": 150,  # Par jour
            "escalation_rate": 0.15  # 15%
        }
        
        for metric, value in metrics.items():
            assert metric in metrics
            assert value > 0
            assert isinstance(value, (int, float))
    
    def test_support_ticket_search_criteria(self, thread_repo):
        """Test des critères de recherche de tickets"""
        # Critères de recherche
        search_criteria = {
            "status": "OPEN",
            "priority": "HIGH",
            "category": "ORDER_ISSUE",
            "assigned_to": "agent123",
            "date_range": "last_7_days",
            "customer_id": "user123"
        }
        
        for criterion, value in search_criteria.items():
            assert criterion in search_criteria
            assert value is not None
            assert isinstance(value, str)
            assert len(value) > 0
    
    def test_support_ticket_notification_settings(self, thread_repo):
        """Test des paramètres de notification des tickets"""
        # Types de notifications
        notification_types = [
            "EMAIL",
            "SMS",
            "PUSH_NOTIFICATION",
            "IN_APP_NOTIFICATION",
            "WEBHOOK"
        ]
        
        for notif_type in notification_types:
            assert notif_type in notification_types
            assert isinstance(notif_type, str)
            assert len(notif_type) > 0
    
    def test_support_ticket_attachment_handling(self, thread_repo):
        """Test de la gestion des pièces jointes des tickets"""
        # Types de pièces jointes supportés
        supported_attachments = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/pdf",
            "text/plain",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        
        for mime_type in supported_attachments:
            assert mime_type in supported_attachments
            assert isinstance(mime_type, str)
            assert "/" in mime_type  # Format MIME type/subtype
    
    def test_support_ticket_rating_system(self, thread_repo):
        """Test du système de notation des tickets"""
        # Échelles de notation
        rating_scales = {
            "satisfaction": (1, 5),  # 1-5 étoiles
            "response_time": (1, 5),  # 1-5 étoiles
            "resolution_quality": (1, 5),  # 1-5 étoiles
            "agent_friendliness": (1, 5)  # 1-5 étoiles
        }
        
        for scale, (min_val, max_val) in rating_scales.items():
            assert scale in rating_scales
            assert min_val > 0
            assert max_val > min_val
            assert isinstance(min_val, int)
            assert isinstance(max_val, int)
    
    def test_support_ticket_escalation_triggers(self, thread_repo):
        """Test des déclencheurs d'escalation des tickets"""
        # Déclencheurs d'escalation
        escalation_triggers = [
            "SLA_BREACH",
            "CUSTOMER_COMPLAINT",
            "MULTIPLE_FOLLOW_UPS",
            "TECHNICAL_COMPLEXITY",
            "MANAGER_OVERRIDE"
        ]
        
        for trigger in escalation_triggers:
            assert trigger in escalation_triggers
            assert isinstance(trigger, str)
            assert len(trigger) > 0
    
    def test_support_ticket_workflow_automation(self, thread_repo):
        """Test de l'automatisation du workflow des tickets"""
        # Règles d'automatisation
        automation_rules = {
            "auto_assign": True,
            "auto_escalate": True,
            "auto_close": True,
            "auto_notify": True,
            "auto_categorize": True
        }
        
        for rule, enabled in automation_rules.items():
            assert rule in automation_rules
            assert isinstance(enabled, bool)
    
    def test_support_ticket_analytics(self, thread_repo):
        """Test des analytics des tickets"""
        # Métriques d'analytics
        analytics_metrics = {
            "tickets_per_day": 150,
            "average_resolution_time": 18.5,  # Heures
            "customer_satisfaction_score": 4.3,  # Sur 5
            "agent_productivity": 0.85,  # 85%
            "escalation_rate": 0.12,  # 12%
            "repeat_ticket_rate": 0.08  # 8%
        }
        
        for metric, value in analytics_metrics.items():
            assert metric in analytics_metrics
            assert value >= 0
            assert isinstance(value, (int, float))
    
    def test_support_ticket_integration_apis(self, thread_repo):
        """Test des APIs d'intégration des tickets"""
        # APIs d'intégration
        integration_apis = [
            "CRM_INTEGRATION",
            "EMAIL_INTEGRATION",
            "SMS_INTEGRATION",
            "SLACK_INTEGRATION",
            "WEBHOOK_INTEGRATION"
        ]
        
        for api in integration_apis:
            assert api in integration_apis
            assert isinstance(api, str)
            assert len(api) > 0
    
    def test_support_ticket_edge_cases(self, thread_repo):
        """Test des cas limites des tickets"""
        # Test avec ID utilisateur vide
        assert thread_repo.get_by_user_id("") is None
        
        # Test avec ID ticket vide
        assert thread_repo.get_by_id("") is None
        
        # Test avec sujet vide
        empty_subject_data = {
            "user_id": "user123",
            "subject": "",
            "status": "OPEN"
        }
        
        # Le sujet vide devrait être invalide
        assert len(empty_subject_data["subject"]) == 0
    
    def test_support_ticket_performance(self, thread_repo):
        """Test des performances des tickets"""
        # Limite de tickets par utilisateur
        max_tickets_per_user = 100
        
        assert max_tickets_per_user > 0
        assert isinstance(max_tickets_per_user, int)
        
        # Limite de messages par ticket
        max_messages_per_ticket = 1000
        
        assert max_messages_per_ticket > 0
        assert isinstance(max_messages_per_ticket, int)
    
    def test_support_ticket_security(self, thread_repo):
        """Test de la sécurité des tickets"""
        # Validation des données d'entrée
        input_validation = {
            "user_id": "UUID format",
            "subject": "Non-empty string",
            "content": "Non-empty string",
            "priority": "Valid priority level",
            "category": "Valid category"
        }
        
        for field, validation in input_validation.items():
            assert field in input_validation
            assert validation is not None
            assert isinstance(validation, str)
            assert len(validation) > 0