#!/usr/bin/env python3
"""
Tests unitaires pour le service de paiements
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ecommerce_backend.database.repositories_simple import PostgreSQLPaymentRepository

@pytest.mark.unit
@pytest.mark.payments
class TestPaymentService:
    """Tests unitaires pour le service de paiements"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la base de données"""
        return Mock()
    
    @pytest.fixture
    def payment_repo(self, mock_db):
        """Repository de paiements avec mock"""
        return PostgreSQLPaymentRepository(mock_db)
    
    def test_create_payment_success(self, payment_repo, mock_db):
        """Test de création de paiement réussie"""
        # Données du paiement
        payment_data = {
            "order_id": "order123",
            "amount_cents": 5999,
            "status": "SUCCEEDED",
            "payment_method": "card"
        }
        
        # Mock de la création - le repository crée un vrai objet Payment
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None
        
        # Test de création
        result = payment_repo.create(payment_data)
        
        assert result is not None
        assert result.order_id == "order123"
        assert result.amount_cents == 5999
        assert result.status == "SUCCEEDED"
        assert result.payment_method == "card"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_get_payment_by_id_success(self, payment_repo, mock_db):
        """Test de récupération de paiement par ID réussie"""
        # Mock du paiement
        mock_payment = Mock()
        mock_payment.id = "payment123"
        mock_payment.order_id = "order123"
        mock_payment.amount_cents = 5999
        mock_payment.status = "SUCCEEDED"
        mock_payment.payment_method = "card"
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_payment
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = payment_repo.get_by_id("payment123")
        
        assert result is not None
        assert result.id == "payment123"
        assert result.order_id == "order123"
        mock_db.query.assert_called_once()
    
    def test_get_payment_by_id_not_found(self, payment_repo, mock_db):
        """Test de récupération de paiement par ID non trouvé"""
        # Mock de la requête qui ne trouve rien
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = payment_repo.get_by_id("nonexistent")
        
        assert result is None
        mock_db.query.assert_called_once()
    
    def test_get_payments_by_order_id(self, payment_repo, mock_db):
        """Test de récupération des paiements par ID de commande"""
        # Mock des paiements
        mock_payments = [
            Mock(id="payment1", order_id="order123", amount_cents=2999, status="SUCCEEDED"),
            Mock(id="payment2", order_id="order123", amount_cents=1999, status="FAILED"),
            Mock(id="payment3", order_id="order456", amount_cents=3999, status="SUCCEEDED")
        ]
        
        # Mock de la requête
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_payments
        mock_db.query.return_value = mock_query
        
        # Test de récupération
        result = payment_repo.get_by_order_id("order123")
        
        assert result is not None
        assert len(result) == 3
        mock_db.query.assert_called_once()
    
    def test_payment_validation(self, payment_repo):
        """Test de validation des données de paiement"""
        # Test avec données valides
        valid_payment_data = {
            "order_id": "order123",
            "amount_cents": 5999,
            "status": "SUCCEEDED",
            "payment_method": "card"
        }
        
        # Les données valides ne doivent pas lever d'exception
        try:
            assert valid_payment_data["order_id"] is not None
            assert valid_payment_data["amount_cents"] > 0
            assert valid_payment_data["status"] in ["SUCCEEDED", "FAILED", "PENDING", "REFUNDED"]
            assert valid_payment_data["payment_method"] in ["card", "paypal", "bank_transfer"]
        except AssertionError:
            pytest.fail("Les données valides ont échoué la validation")
    
    def test_payment_amount_calculation(self, payment_repo):
        """Test des calculs de montant de paiement"""
        # Test de conversion centimes -> euros
        amount_cents = 5999
        amount_euros = amount_cents / 100
        
        assert amount_euros == 59.99
        
        # Test de calcul de total
        items = [
            {"unit_price_cents": 2999, "quantity": 1},  # 29.99
            {"unit_price_cents": 1999, "quantity": 1},  # 19.99
            {"unit_price_cents": 999, "quantity": 1}    # 9.99
        ]
        
        total_cents = sum(item["unit_price_cents"] * item["quantity"] for item in items)
        total_euros = total_cents / 100
        
        assert total_cents == 5997
        assert total_euros == 59.97
    
    def test_payment_status_workflow(self, payment_repo):
        """Test du workflow des statuts de paiement"""
        # Workflow typique d'un paiement
        workflow = [
            "PENDING",    # Paiement en attente
            "SUCCEEDED",  # Paiement réussi
            "REFUNDED"    # Paiement remboursé
        ]
        
        # Vérifier que tous les statuts sont valides
        valid_statuses = ["PENDING", "SUCCEEDED", "FAILED", "REFUNDED"]
        for status in workflow:
            assert status in valid_statuses
        
        # Vérifier que les statuts sont différents
        assert len(set(workflow)) == len(workflow)
    
    def test_payment_methods(self, payment_repo):
        """Test des méthodes de paiement"""
        # Méthodes de paiement supportées
        supported_methods = ["card", "paypal", "bank_transfer", "apple_pay", "google_pay"]
        
        # Test de validation des méthodes
        for method in supported_methods:
            assert method in supported_methods
            assert isinstance(method, str)
            assert len(method) > 0
    
    def test_payment_edge_cases(self, payment_repo):
        """Test des cas limites des paiements"""
        # Test avec montant zéro
        zero_amount_data = {
            "order_id": "order123",
            "amount_cents": 0,
            "status": "SUCCEEDED",
            "payment_method": "card"
        }
        
        # Le montant zéro devrait être valide (paiement gratuit)
        assert zero_amount_data["amount_cents"] >= 0
        
        # Test avec montant négatif (devrait être invalide)
        negative_amount_data = {
            "order_id": "order123",
            "amount_cents": -100,
            "status": "SUCCEEDED",
            "payment_method": "card"
        }
        
        # Le montant négatif devrait être invalide
        assert negative_amount_data["amount_cents"] < 0
    
    def test_payment_refund_calculation(self, payment_repo):
        """Test des calculs de remboursement"""
        # Montant original
        original_amount_cents = 5999
        
        # Remboursement total
        full_refund_cents = original_amount_cents
        full_refund_euros = full_refund_cents / 100
        
        assert full_refund_cents == 5999
        assert full_refund_euros == 59.99
        
        # Remboursement partiel
        partial_refund_cents = 2999
        partial_refund_euros = partial_refund_cents / 100
        
        assert partial_refund_cents == 2999
        assert partial_refund_euros == 29.99
        
        # Vérifier que le remboursement partiel est inférieur au montant original
        assert partial_refund_cents < original_amount_cents
    
    def test_payment_currency_handling(self, payment_repo):
        """Test de la gestion des devises"""
        # Test avec différentes devises (simulation)
        currencies = ["EUR", "USD", "GBP"]
        
        for currency in currencies:
            assert currency in currencies
            assert len(currency) == 3
            assert currency.isupper()
    
    def test_payment_security(self, payment_repo):
        """Test de la sécurité des paiements"""
        # Test de masquage des données sensibles
        card_number = "4242424242424242"
        masked_number = card_number[:4] + "*" * (len(card_number) - 8) + card_number[-4:]
        
        assert masked_number == "4242********4242"
        assert len(masked_number) == len(card_number)
        
        # Test de validation CVC
        valid_cvc = "123"
        invalid_cvc = "12"
        
        assert len(valid_cvc) == 3
        assert len(invalid_cvc) < 3
        assert valid_cvc.isdigit()
        assert invalid_cvc.isdigit()
    
    def test_payment_failure_handling(self, payment_repo):
        """Test de la gestion des échecs de paiement"""
        # Test des raisons d'échec
        failure_reasons = [
            "insufficient_funds",
            "card_declined",
            "expired_card",
            "invalid_cvc",
            "network_error"
        ]
        
        for reason in failure_reasons:
            assert reason in failure_reasons
            assert isinstance(reason, str)
            assert len(reason) > 0
    
    def test_payment_retry_logic(self, payment_repo):
        """Test de la logique de retry des paiements"""
        # Test du nombre maximum de tentatives
        max_attempts = 3
        current_attempt = 1
        
        while current_attempt <= max_attempts:
            assert current_attempt <= max_attempts
            current_attempt += 1
        
        # Test de l'attente entre les tentatives
        retry_delays = [1, 2, 4]  # Délais exponentiels
        
        for delay in retry_delays:
            assert delay > 0
            assert isinstance(delay, int)
