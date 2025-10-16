#!/usr/bin/env python3
"""
Tests pour la gestion des commandes
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

from backend_demo import (
    User, Product, Cart, CartItem, Order, OrderItem, OrderStatus, DeliveryStatus,
    Delivery, OrderRepository, ProductRepository, CartRepository, PaymentRepository,
    InvoiceRepository, BillingService, DeliveryService, PaymentGateway,
    OrderService, UserRepository
)
import uuid
import time


class TestOrderItem(unittest.TestCase):
    """Tests pour l'entité OrderItem"""
    
    def test_create_order_item(self):
        """Test la création d'un article de commande"""
        product_id = str(uuid.uuid4())
        order_item = OrderItem(
            product_id=product_id,
            name="Test Product",
            unit_price_cents=1999,
            quantity=2
        )
        
        self.assertEqual(order_item.product_id, product_id)
        self.assertEqual(order_item.name, "Test Product")
        self.assertEqual(order_item.unit_price_cents, 1999)
        self.assertEqual(order_item.quantity, 2)


class TestOrder(unittest.TestCase):
    """Tests pour l'entité Order"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.user_id = str(uuid.uuid4())
        self.order_items = [
            OrderItem(
                product_id=str(uuid.uuid4()),
                name="Product 1",
                unit_price_cents=1000,
                quantity=2
            ),
            OrderItem(
                product_id=str(uuid.uuid4()),
                name="Product 2",
                unit_price_cents=2000,
                quantity=1
            )
        ]
    
    def test_create_order(self):
        """Test la création d'une commande"""
        order = Order(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            items=self.order_items,
            status=OrderStatus.CREE,
            created_at=time.time()
        )
        
        self.assertEqual(order.user_id, self.user_id)
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.status, OrderStatus.CREE)
        self.assertIsNotNone(order.created_at)
        self.assertIsNone(order.validated_at)
        self.assertIsNone(order.paid_at)
        self.assertIsNone(order.shipped_at)
        self.assertIsNone(order.delivered_at)
        self.assertIsNone(order.cancelled_at)
        self.assertIsNone(order.refunded_at)
        self.assertIsNone(order.delivery)
        self.assertIsNone(order.invoice_id)
        self.assertIsNone(order.payment_id)
    
    def test_order_total(self):
        """Test le calcul du total d'une commande"""
        order = Order(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            items=self.order_items,
            status=OrderStatus.CREE,
            created_at=time.time()
        )
        
        # Total attendu: (2 * 1000) + (1 * 2000) = 4000 cents
        total = order.total_cents()
        self.assertEqual(total, 4000)
    
    def test_order_with_delivery(self):
        """Test une commande avec livraison"""
        order = Order(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            items=self.order_items,
            status=OrderStatus.CREE,
            created_at=time.time()
        )
        
        delivery = Delivery(
            id=str(uuid.uuid4()),
            order_id=order.id,
            transporteur="Colissimo",
            tracking_number="TRK123456",
            address="123 Main St",
            delivery_status=DeliveryStatus.PREPAREE
        )
        
        order.delivery = delivery
        
        self.assertEqual(order.delivery.transporteur, "Colissimo")
        self.assertEqual(order.delivery.tracking_number, "TRK123456")
        self.assertEqual(order.delivery.delivery_status, DeliveryStatus.PREPAREE)


class TestOrderRepository(unittest.TestCase):
    """Tests pour le repository des commandes"""
    
    def setUp(self):
        """Setup avant chaque test"""
        self.repo = OrderRepository()
        self.user_id = str(uuid.uuid4())
        
        # Créer des commandes de test
        self.order1 = Order(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            items=[
                OrderItem(
                    product_id=str(uuid.uuid4()),
                    name="Test Product 1",
                    unit_price_cents=1000,
                    quantity=2
                )
            ],
            status=OrderStatus.CREE,
            created_at=time.time()
        )
        
        self.order2 = Order(
            id=str(uuid.uuid4()),
            user_id=self.user_id,
            items=[
                OrderItem(
                    product_id=str(uuid.uuid4()),
                    name="Test Product 2",
                    unit_price_cents=2000,
                    quantity=1
                )
            ],
            status=OrderStatus.PAYEE,
            created_at=time.time(),
            paid_at=time.time()
        )
    
    def test_add_order(self):
        """Test l'ajout d'une commande"""
        self.repo.add(self.order1)
        
        # Vérifier que la commande est récupérable
        retrieved = self.repo.get(self.order1.id)
        self.assertEqual(retrieved.id, self.order1.id)
        self.assertEqual(retrieved.user_id, self.order1.user_id)
        self.assertEqual(retrieved.status, OrderStatus.CREE)
    
    def test_get_nonexistent_order(self):
        """Test la récupération d'une commande inexistante"""
        self.assertIsNone(self.repo.get("nonexistent-id"))
    
    def test_list_orders_by_user(self):
        """Test la liste des commandes par utilisateur"""
        # Ajouter des commandes pour différents utilisateurs
        other_user_id = str(uuid.uuid4())
        other_order = Order(
            id=str(uuid.uuid4()),
            user_id=other_user_id,
            items=[],
            status=OrderStatus.CREE,
            created_at=time.time()
        )
        
        self.repo.add(self.order1)
        self.repo.add(self.order2)
        self.repo.add(other_order)
        
        # Récupérer les commandes de l'utilisateur principal
        user_orders = self.repo.list_by_user(self.user_id)
        
        self.assertEqual(len(user_orders), 2)
        order_ids = [o.id for o in user_orders]
        self.assertIn(self.order1.id, order_ids)
        self.assertIn(self.order2.id, order_ids)
        self.assertNotIn(other_order.id, order_ids)
    
    def test_update_order(self):
        """Test la mise à jour d'une commande"""
        self.repo.add(self.order1)
        
        # Modifier le statut
        self.order1.status = OrderStatus.PAYEE
        self.order1.paid_at = time.time()
        
        self.repo.update(self.order1)
        
        # Vérifier les modifications
        updated = self.repo.get(self.order1.id)
        self.assertEqual(updated.status, OrderStatus.PAYEE)
        self.assertIsNotNone(updated.paid_at)


class TestOrderService(unittest.TestCase):
    """Tests pour le service des commandes"""
    
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
        self.admin_id = str(uuid.uuid4())
        
        # Créer un utilisateur admin
        admin_user = User(
            id=self.admin_id,
            email="admin@test.com",
            password_hash="hash",
            first_name="Admin",
            last_name="User",
            address="Admin Address",
            is_admin=True
        )
        self.users.add(admin_user)
        
        # Créer des produits de test
        self.product1 = Product(
            id=str(uuid.uuid4()),
            name="Service Product 1",
            description="Product for order service tests",
            price_cents=1000,
            stock_qty=100,
            active=True
        )
        
        self.product2 = Product(
            id=str(uuid.uuid4()),
            name="Service Product 2",
            description="Another product for tests",
            price_cents=2000,
            stock_qty=50,
            active=True
        )
        
        self.products.add(self.product1)
        self.products.add(self.product2)
    
    def test_checkout_empty_cart(self):
        """Test le checkout avec un panier vide"""
        with self.assertRaises(ValueError) as context:
            self.order_service.checkout(self.user_id)
        
        self.assertIn("Panier vide", str(context.exception))
    
    def test_checkout_success(self):
        """Test un checkout réussi"""
        # Ajouter des produits au panier
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product1, 2)
        cart.add(self.product2, 1)
        
        # Effectuer le checkout
        order = self.order_service.checkout(self.user_id)
        
        # Vérifier la commande
        self.assertEqual(order.user_id, self.user_id)
        self.assertEqual(order.status, OrderStatus.CREE)
        self.assertEqual(len(order.items), 2)
        self.assertIsNotNone(order.created_at)
        
        # Vérifier que le panier est vidé
        empty_cart = self.carts.get_or_create(self.user_id)
        self.assertEqual(len(empty_cart.items), 0)
        
        # Vérifier que le stock a été réservé
        updated_product1 = self.products.get(self.product1.id)
        updated_product2 = self.products.get(self.product2.id)
        self.assertEqual(updated_product1.stock_qty, 98)  # 100 - 2
        self.assertEqual(updated_product2.stock_qty, 49)  # 50 - 1
    
    def test_checkout_insufficient_stock(self):
        """Test le checkout avec stock insuffisant"""
        # Ajouter un produit puis réduire artificiellement le stock pour simuler une rupture au checkout
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product1, 2)
        # Simuler une baisse de stock ailleurs
        self.product1.stock_qty = 1
        with self.assertRaises(ValueError) as context:
            self.order_service.checkout(self.user_id)
        self.assertIn("Stock insuffisant", str(context.exception))
        # Vérifier que le stock n'a pas été réservé négativement
        unchanged_product = self.products.get(self.product1.id)
        self.assertEqual(unchanged_product.stock_qty, 1)
    
    def test_checkout_inactive_product(self):
        """Test le checkout avec un produit devenu inactif"""
        # Ajouter un produit au panier
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product1, 2)
        
        # Désactiver le produit
        self.product1.active = False
        
        with self.assertRaises(ValueError) as context:
            self.order_service.checkout(self.user_id)
        
        self.assertIn("Produit indisponible", str(context.exception))
    
    def test_view_orders(self):
        """Test la visualisation des commandes d'un utilisateur"""
        # Créer des commandes
        cart1 = self.carts.get_or_create(self.user_id)
        cart1.add(self.product1, 1)
        order1 = self.order_service.checkout(self.user_id)
        
        cart2 = self.carts.get_or_create(self.user_id)
        cart2.add(self.product2, 1)
        order2 = self.order_service.checkout(self.user_id)
        
        # Récupérer les commandes
        orders = self.order_service.view_orders(self.user_id)
        
        self.assertEqual(len(orders), 2)
        order_ids = [o.id for o in orders]
        self.assertIn(order1.id, order_ids)
        self.assertIn(order2.id, order_ids)
    
    def test_request_cancellation(self):
        """Test la demande d'annulation d'une commande"""
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product1, 2)
        order = self.order_service.checkout(self.user_id)
        
        # Annuler la commande
        cancelled_order = self.order_service.request_cancellation(self.user_id, order.id)
        
        self.assertEqual(cancelled_order.status, OrderStatus.ANNULEE)
        self.assertIsNotNone(cancelled_order.cancelled_at)
        
        # Vérifier que le stock a été restitué
        restored_product = self.products.get(self.product1.id)
        self.assertEqual(restored_product.stock_qty, 100)  # Restauré
    
    def test_cancel_shipped_order(self):
        """Test l'annulation d'une commande déjà expédiée"""
        # Créer et payer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product1, 2)
        order = self.order_service.checkout(self.user_id)
        
        # Simuler le paiement
        order.status = OrderStatus.PAYEE
        order.paid_at = time.time()
        self.orders.update(order)
        
        # Valider et expédier la commande
        validated_order = self.order_service.backoffice_validate_order(self.admin_id, order.id)
        shipped_order = self.order_service.backoffice_ship_order(self.admin_id, order.id)
        
        # Essayer d'annuler
        with self.assertRaises(ValueError) as context:
            self.order_service.request_cancellation(self.user_id, order.id)
        
        self.assertIn("Trop tard pour annuler", str(context.exception))
    
    def test_backoffice_validate_order(self):
        """Test la validation d'une commande par l'admin"""
        # Créer et payer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product1, 2)
        order = self.order_service.checkout(self.user_id)
        
        # Simuler le paiement
        order.status = OrderStatus.PAYEE
        order.paid_at = time.time()
        self.orders.update(order)
        
        # Valider la commande
        validated_order = self.order_service.backoffice_validate_order(self.admin_id, order.id)
        
        self.assertEqual(validated_order.status, OrderStatus.VALIDEE)
        self.assertIsNotNone(validated_order.validated_at)
        self.assertIsNotNone(validated_order.delivery)
        self.assertEqual(validated_order.delivery.delivery_status, DeliveryStatus.PREPAREE)
    
    def test_backoffice_validate_without_admin(self):
        """Test la validation sans droits admin"""
        # Créer un utilisateur non-admin
        regular_user = User(
            id=str(uuid.uuid4()),
            email="regular@test.com",
            password_hash="hash",
            first_name="Regular",
            last_name="User",
            address="Regular Address",
            is_admin=False
        )
        self.users.add(regular_user)
        
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product1, 2)
        order = self.order_service.checkout(self.user_id)
        
        # Essayer de valider sans être admin
        with self.assertRaises(PermissionError) as context:
            self.order_service.backoffice_validate_order(regular_user.id, order.id)
        
        self.assertIn("Droits insuffisants", str(context.exception))
    
    def test_backoffice_ship_order(self):
        """Test l'expédition d'une commande"""
        # Créer, payer et valider une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product1, 2)
        order = self.order_service.checkout(self.user_id)
        
        order.status = OrderStatus.PAYEE
        order.paid_at = time.time()
        self.orders.update(order)
        
        validated_order = self.order_service.backoffice_validate_order(self.admin_id, order.id)
        
        # Expédier la commande
        shipped_order = self.order_service.backoffice_ship_order(self.admin_id, order.id)
        
        self.assertEqual(shipped_order.status, OrderStatus.EXPEDIEE)
        self.assertIsNotNone(shipped_order.shipped_at)
        self.assertIsNotNone(shipped_order.delivery)
        self.assertEqual(shipped_order.delivery.delivery_status, DeliveryStatus.EN_COURS)
        self.assertIsNotNone(shipped_order.delivery.tracking_number)
    
    def test_backoffice_mark_delivered(self):
        """Test la marque de livraison"""
        # Créer une commande complète
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product1, 2)
        order = self.order_service.checkout(self.user_id)
        
        order.status = OrderStatus.PAYEE
        order.paid_at = time.time()
        self.orders.update(order)
        
        validated_order = self.order_service.backoffice_validate_order(self.admin_id, order.id)
        shipped_order = self.order_service.backoffice_ship_order(self.admin_id, order.id)
        
        # Marquer comme livré
        delivered_order = self.order_service.backoffice_mark_delivered(self.admin_id, order.id)
        
        self.assertEqual(delivered_order.status, OrderStatus.LIVREE)
        self.assertIsNotNone(delivered_order.delivered_at)
        self.assertEqual(delivered_order.delivery.delivery_status, DeliveryStatus.LIVREE)


class TestOrderStatusFlow(unittest.TestCase):
    """Tests pour le flux des statuts de commande"""
    
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
        self.admin_id = str(uuid.uuid4())
        
        # Créer un admin
        admin_user = User(
            id=self.admin_id,
            email="admin@test.com",
            password_hash="hash",
            first_name="Admin",
            last_name="User",
            address="Admin Address",
            is_admin=True
        )
        self.users.add(admin_user)
        
        # Créer un produit
        self.product = Product(
            id=str(uuid.uuid4()),
            name="Flow Test Product",
            description="Product for status flow tests",
            price_cents=1000,
            stock_qty=100,
            active=True
        )
        self.products.add(self.product)
    
    def test_complete_order_flow(self):
        """Test le flux complet d'une commande"""
        # 1. Création de la commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product, 2)
        order = self.order_service.checkout(self.user_id)
        
        self.assertEqual(order.status, OrderStatus.CREE)
        self.assertIsNotNone(order.created_at)
        
        # 2. Paiement (simulé)
        order.status = OrderStatus.PAYEE
        order.paid_at = time.time()
        self.orders.update(order)
        
        # 3. Validation par l'admin
        validated_order = self.order_service.backoffice_validate_order(self.admin_id, order.id)
        self.assertEqual(validated_order.status, OrderStatus.VALIDEE)
        self.assertIsNotNone(validated_order.validated_at)
        
        # 4. Expédition
        shipped_order = self.order_service.backoffice_ship_order(self.admin_id, order.id)
        self.assertEqual(shipped_order.status, OrderStatus.EXPEDIEE)
        self.assertIsNotNone(shipped_order.shipped_at)
        
        # 5. Livraison
        delivered_order = self.order_service.backoffice_mark_delivered(self.admin_id, order.id)
        self.assertEqual(delivered_order.status, OrderStatus.LIVREE)
        self.assertIsNotNone(delivered_order.delivered_at)
    
    def test_cancellation_flow(self):
        """Test le flux d'annulation"""
        # Créer une commande
        cart = self.carts.get_or_create(self.user_id)
        cart.add(self.product, 2)
        order = self.order_service.checkout(self.user_id)
        
        self.assertEqual(order.status, OrderStatus.CREE)
        
        # Annuler la commande
        cancelled_order = self.order_service.request_cancellation(self.user_id, order.id)
        self.assertEqual(cancelled_order.status, OrderStatus.ANNULEE)
        self.assertIsNotNone(cancelled_order.cancelled_at)


if __name__ == '__main__':
    print("=== Tests des commandes ===")
    unittest.main(verbosity=2)
