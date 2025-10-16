#!/usr/bin/env python3
"""
Tests pour la gestion des paiements
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

from backend_demo import (
    Payment, PaymentRepository, PaymentGateway, Order, OrderItem, OrderStatus,
    OrderRepository, ProductRepository, CartRepository, InvoiceRepository,
    BillingService, DeliveryService, OrderService, UserRepository, Product
)
import uuid
import time


class TestPayment(unittest.TestCase):
    """Tests pour l'entité Payment"""
    
    def test_create_payment(self):
        """Test la création d'un paiement"""
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            amount_cents=5000,
            provider="CB",
            provider_ref="TXN123456",
            succeeded=True,
            created_at=time.time(),
            idempotency_key="idempotency123",
            card_last4="1234"
        )
        
        self.assertEqual(payment.amount_cents, 5000)
        self.assertEqual(payment.provider, "CB")
        self.assertEqual(payment.provider_ref, "TXN123456")
        self.assertTrue(payment.succeeded)
        self.assertIsNotNone(payment.created_at)
        self.assertEqual(payment.idempotency_key, "idempotency123")
        self.assertEqual(payment.card_last4, "1234")
    
    def test_create_payment_minimal(self):
        """Test la création d'un paiement minimal"""
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            amount_cents=1000,
            provider="CB",
            provider_ref=None,
            succeeded=False,
            created_at=time.time()
        )
        
        self.assertEqual(payment.amount_cents, 1000)
        self.assertFalse(payment.succeeded)
        self.assertIsNone(payment.provider_ref)
        self.assertIsNone(payment.idempotency_key)
        self.assertIsNone(payment.card_last4)


class TestPaymentRepository(unittest.TestCase):
    """Tests pour le repository des paiements"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.repo = PaymentRepository()
    
    def test_add_payment(self):
        """Test l'ajout d'un paiement"""
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            amount_cents=3000,
            provider="CB",
            provider_ref="TXN789",
            succeeded=True,
            created_at=time.time(),
            idempotency_key="idem789"
        )
        
        self.repo.add(payment)
        
        # Vérifier que le paiement est récupérable
        retrieved = self.repo.get(payment.id)
        self.assertEqual(retrieved.id, payment.id)
        self.assertEqual(retrieved.amount_cents, 3000)
        self.assertTrue(retrieved.succeeded)
        self.assertEqual(retrieved.provider_ref, "TXN789")
    
    def test_get_nonexistent_payment(self):
        """Test la récupération d'un paiement inexistant"""
        self.assertIsNone(self.repo.get("nonexistent-id"))
    
    def test_get_by_idempotency_key(self):
        """Test la récupération par clé d'idempotence"""
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=str(uuid.uuid4()),
            user_id=str(uuid.uuid4()),
            amount_cents=2000,
            provider="CB",
            provider_ref="TXN456",
            succeeded=True,
            created_at=time.time(),
            idempotency_key="unique_key_123"
        )
        
        self.repo.add(payment)
        
        # Récupérer par clé d'idempotence
        retrieved = self.repo.get_by_idempotency_key("unique_key_123")
        self.assertEqual(retrieved.id, payment.id)
        self.assertEqual(retrieved.amount_cents, 2000)
    
    def test_get_by_nonexistent_idempotency_key(self):
        """Test la récupération par clé d'idempotence inexistante"""
        self.assertIsNone(self.repo.get_by_idempotency_key("nonexistent_key"))
    
    def test_multiple_payments_same_order(self):
        """Test plusieurs paiements pour la même commande"""
        order_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        payment1 = Payment(
            id=str(uuid.uuid4()),
            order_id=order_id,
            user_id=user_id,
            amount_cents=1000,
            provider="CB",
            provider_ref="TXN1",
            succeeded=True,
            created_at=time.time(),
            idempotency_key="key1"
        )
        
        payment2 = Payment(
            id=str(uuid.uuid4()),
            order_id=order_id,
            user_id=user_id,
            amount_cents=1000,
            provider="CB",
            provider_ref="TXN2",
            succeeded=False,
            created_at=time.time(),
            idempotency_key="key2"
        )
        
        self.repo.add(payment1)
        self.repo.add(payment2)
        
        # Vérifier que les deux paiements sont récupérables
        retrieved1 = self.repo.get(payment1.id)
        retrieved2 = self.repo.get(payment2.id)
        
        self.assertEqual(retrieved1.order_id, order_id)
        self.assertEqual(retrieved2.order_id, order_id)
        self.assertTrue(retrieved1.succeeded)
        self.assertFalse(retrieved2.succeeded)


class TestPaymentGateway(unittest.TestCase):
    """Tests pour la passerelle de paiement"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.gateway = PaymentGateway()
    
    def test_successful_charge(self):
        """Test un paiement réussi"""
        result = self.gateway.charge_card("1234", 5000, "test_key_1")
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["transaction_id"])
        self.assertIsNone(result["failure_reason"])
    
    def test_failed_charge(self):
        """Test un paiement échoué (carte se terminant par 0000)"""
        result = self.gateway.charge_card("0000", 5000, "test_key_2")
        
        self.assertFalse(result["success"])
        self.assertIsNone(result["transaction_id"])
        self.assertEqual(result["failure_reason"], "CARTE_REFUSEE")
    
    def test_refund(self):
        """Test un remboursement"""
        # D'abord un paiement réussi
        charge_result = self.gateway.charge_card("1234", 3000, "test_key_3")
        self.assertTrue(charge_result["success"])
        
        # Puis un remboursement
        refund_result = self.gateway.refund(charge_result["transaction_id"], 3000)
        
        self.assertTrue(refund_result["success"])
        self.assertIsNotNone(refund_result["refund_id"])
    
    def test_refund_partial(self):
        """Test un remboursement partiel"""
        # Paiement de 5000
        charge_result = self.gateway.charge_card("1234", 5000, "test_key_4")
        
        # Remboursement de 2000
        refund_result = self.gateway.refund(charge_result["transaction_id"], 2000)
        
        self.assertTrue(refund_result["success"])
        self.assertIsNotNone(refund_result["refund_id"])
    
    def test_different_card_numbers(self):
        """Test avec différents numéros de carte"""
        # Cartes qui devraient réussir
        successful_cards = ["1234", "5678", "9999", "1111"]
        
        for card in successful_cards:
            result = self.gateway.charge_card(card, 1000, f"test_key_{card}")
            self.assertTrue(result["success"], f"Card {card} should succeed")
        
        # Carte qui devrait échouer
        failed_result = self.gateway.charge_card("0000", 1000, "test_key_0000")
        self.assertFalse(failed_result["success"])
    
    def test_idempotency_keys(self):
        """Test que les clés d'idempotence sont uniques"""
        # Même clé d'idempotence, résultats différents
        result1 = self.gateway.charge_card("1234", 1000, "same_key")
        result2 = self.gateway.charge_card("1234", 1000, "same_key")
        
        # Les deux devraient réussir mais avec des transaction_id différents
        self.assertTrue(result1["success"])
        self.assertTrue(result2["success"])
        self.assertNotEqual(result1["transaction_id"], result2["transaction_id"])


class TestOrderServicePayment(unittest.TestCase):
    """Tests pour les paiements dans le service des commandes"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.users = UserRepository()
        self.products = ProductRepository()
        self.carts = CartRepository()
        self.orders = OrderRepository()
        self.payments = PaymentRepository()
        self.invoices = InvoiceRepository()
        self.billing = BillingService(self.invoices)
        self.delivery_svc = DeliveryService()
        self.gateway = PaymentGateway()
        
        self.order_service = OrderService(
            self.orders, self.products, self.carts, self.payments,
            self.invoices, self.billing, self.delivery_svc, self.gateway, self.users
        )
        
        self.user_id = str(uuid.uuid4())
        
        # Créer un produit
        self.product = Product(
            id=str(uuid.uuid4()),
            name="Payment Test Product",
            description="Product for payment tests",
            price_cents=2500,
            stock_qty=100,
            active=True
        )
        self.products.add(self.product)
    
    def test_process_payment_success(self):
        """Test un paiement réussi"""
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product, 2)  # 2 * 2500 = 5000 cents
        order = self.order_service.checkout(self.user_id)
        
        # Traiter le paiement
        payment = self.order_service.process_payment(order.id, "1234", "payment_key_1")
        
        # Vérifier le paiement
        self.assertEqual(payment.order_id, order.id)
        self.assertEqual(payment.amount_cents, 5000)
        self.assertTrue(payment.succeeded)
        self.assertEqual(payment.provider, "CB")
        self.assertEqual(payment.idempotency_key, "payment_key_1")
        self.assertEqual(payment.card_last4, "1234")
        
        # Vérifier que la commande a été mise à jour
        updated_order = self.orders.get(order.id)
        self.assertEqual(updated_order.status, OrderStatus.PAYEE)
        self.assertEqual(updated_order.payment_id, payment.id)
        self.assertIsNotNone(updated_order.paid_at)
        self.assertIsNotNone(updated_order.invoice_id)
    
    def test_process_payment_failure(self):
        """Test un paiement échoué"""
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product, 1)
        order = self.order_service.checkout(self.user_id)
        
        # Traiter un paiement qui échoue (carte 0000)
        payment = self.order_service.process_payment(order.id, "0000", "payment_key_2")
        
        # Vérifier le paiement
        self.assertFalse(payment.succeeded)
        self.assertEqual(payment.amount_cents, 2500)
        
        # Vérifier que la commande reste en statut CREE
        updated_order = self.orders.get(order.id)
        self.assertEqual(updated_order.status, OrderStatus.CREE)
        self.assertIsNone(updated_order.payment_id)
        self.assertIsNone(updated_order.paid_at)
        self.assertIsNone(updated_order.invoice_id)
    
    def test_process_payment_nonexistent_order(self):
        """Test un paiement pour une commande inexistante"""
        with self.assertRaises(ValueError) as context:
            self.order_service.process_payment("nonexistent-order", "1234", "payment_key_3")
        
        self.assertIn("Commande introuvable", str(context.exception))
    
    def test_process_payment_idempotency(self):
        """Test l'idempotence des paiements"""
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product, 1)
        order = self.order_service.checkout(self.user_id)
        
        idempotency_key = "idempotent_key_123"
        
        # Premier paiement
        payment1 = self.order_service.process_payment(order.id, "1234", idempotency_key)
        
        # Deuxième paiement avec la même clé d'idempotence
        payment2 = self.order_service.process_payment(order.id, "1234", idempotency_key)
        
        # Les deux paiements devraient être identiques
        self.assertEqual(payment1.id, payment2.id)
        self.assertEqual(payment1.amount_cents, payment2.amount_cents)
        self.assertEqual(payment1.succeeded, payment2.succeeded)
    
    def test_process_payment_wrong_order_status(self):
        """Test un paiement sur une commande avec un mauvais statut"""
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product, 1)
        order = self.order_service.checkout(self.user_id)
        
        # Modifier le statut de la commande pour qu'elle ne soit pas payable
        order.status = OrderStatus.EXPEDIEE
        self.orders.update(order)
        
        with self.assertRaises(ValueError) as context:
            self.order_service.process_payment(order.id, "1234", "payment_key_4")
        
        self.assertIn("Statut de commande incompatible", str(context.exception))
    
    def test_legacy_pay_by_card(self):
        """Test la méthode legacy pay_by_card"""
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product, 1)
        order = self.order_service.checkout(self.user_id)
        
        # Utiliser la méthode legacy
        payment = self.order_service.pay_by_card(
            order.id, "4111111111111111", 12, 2025, "123"
        )
        
        # Vérifier le paiement
        self.assertEqual(payment.order_id, order.id)
        self.assertEqual(payment.amount_cents, 2500)
        self.assertTrue(payment.succeeded)
        self.assertEqual(payment.card_last4, "1111")  # Derniers 4 chiffres
        self.assertIsNotNone(payment.idempotency_key)
    
    def test_payment_creates_invoice(self):
        """Test qu'un paiement réussi crée une facture"""
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product, 2)
        order = self.order_service.checkout(self.user_id)
        
        # Traiter le paiement
        payment = self.order_service.process_payment(order.id, "1234", "invoice_test_key")
        
        # Vérifier que la facture a été créée
        updated_order = self.orders.get(order.id)
        self.assertIsNotNone(updated_order.invoice_id)
        
        invoice = self.invoices.get(updated_order.invoice_id)
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.order_id, order.id)
        self.assertEqual(invoice.total_cents, 5000)
        self.assertEqual(len(invoice.lines), 1)
        self.assertEqual(invoice.lines[0].product_id, self.product.id)
        self.assertEqual(invoice.lines[0].quantity, 2)


class TestPaymentEdgeCases(unittest.TestCase):
    """Tests pour les cas limites des paiements"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.users = UserRepository()
        self.products = ProductRepository()
        self.carts = CartRepository()
        self.orders = OrderRepository()
        self.payments = PaymentRepository()
        self.invoices = InvoiceRepository()
        self.billing = BillingService(self.invoices)
        self.delivery_svc = DeliveryService()
        self.gateway = PaymentGateway()
        
        self.order_service = OrderService(
            self.orders, self.products, self.carts, self.payments,
            self.invoices, self.billing, self.delivery_svc, self.gateway, self.users
        )
        
        self.user_id = str(uuid.uuid4())
    
    def test_zero_amount_payment(self):
        """Test un paiement de montant zéro"""
        # Créer un produit gratuit
        free_product = Product(
            id=str(uuid.uuid4()),
            name="Free Product",
            description="A free product",
            price_cents=0,
            stock_qty=100,
            active=True
        )
        self.products.add(free_product)
        
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(free_product, 1)
        order = self.order_service.checkout(self.user_id)
        
        # Traiter le paiement
        payment = self.order_service.process_payment(order.id, "1234", "zero_amount_key")
        
        self.assertEqual(payment.amount_cents, 0)
        self.assertTrue(payment.succeeded)
    
    def test_large_amount_payment(self):
        """Test un paiement avec un montant élevé"""
        # Créer un produit cher
        expensive_product = Product(
            id=str(uuid.uuid4()),
            name="Expensive Product",
            description="A very expensive product",
            price_cents=999999,  # 9999.99€
            stock_qty=1,
            active=True
        )
        self.products.add(expensive_product)
        
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(expensive_product, 1)
        order = self.order_service.checkout(self.user_id)
        
        # Traiter le paiement
        payment = self.order_service.process_payment(order.id, "1234", "large_amount_key")
        
        self.assertEqual(payment.amount_cents, 999999)
        self.assertTrue(payment.succeeded)
    
    def test_multiple_payments_same_order(self):
        """Test plusieurs tentatives de paiement pour la même commande"""
        # Créer un produit
        product = Product(
            id=str(uuid.uuid4()),
            name="Multi Payment Product",
            description="Product for multiple payment tests",
            price_cents=1000,
            stock_qty=100,
            active=True
        )
        self.products.add(product)
        
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(product, 1)
        order = self.order_service.checkout(self.user_id)
        
        # Premier paiement qui échoue
        failed_payment = self.order_service.process_payment(order.id, "0000", "first_key")
        self.assertFalse(failed_payment.succeeded)
        
        # Deuxième paiement qui réussit
        successful_payment = self.order_service.process_payment(order.id, "1234", "second_key")
        self.assertTrue(successful_payment.succeeded)
        
        # Vérifier que la commande est maintenant payée
        updated_order = self.orders.get(order.id)
        self.assertEqual(updated_order.status, OrderStatus.PAYEE)
        self.assertEqual(updated_order.payment_id, successful_payment.id)


if __name__ == '__main__':
    print("=== Tests des paiements ===")
    unittest.main(verbosity=2)
