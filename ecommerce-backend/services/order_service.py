"""
Service métier pour la gestion des commandes.

Ce service centralise toute la logique métier liée aux commandes :
- Création de commandes (checkout)
- Gestion des statuts
- Validation par les admins
- Annulation et remboursement
- Gestion du stock
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
import uuid
from database.models import Order, OrderItem, User, Product, Payment, Invoice
from database.repositories_simple import (
    PostgreSQLOrderRepository, PostgreSQLProductRepository, 
    PostgreSQLCartRepository, PostgreSQLPaymentRepository,
    PostgreSQLInvoiceRepository, PostgreSQLUserRepository
)
from enums import OrderStatus
from services.payment_service import PaymentService
from services.delivery_service import DeliveryService
from services.billing_service import BillingService


class OrderService:
    """Service métier pour la gestion des commandes."""
    
    def __init__(
        self,
        order_repo: PostgreSQLOrderRepository,
        product_repo: PostgreSQLProductRepository,
        cart_repo: PostgreSQLCartRepository,
        payment_repo: PostgreSQLPaymentRepository,
        invoice_repo: PostgreSQLInvoiceRepository,
        user_repo: PostgreSQLUserRepository,
        payment_service: PaymentService,
        delivery_service: DeliveryService,
        billing_service: BillingService
    ):
        self.order_repo = order_repo
        self.product_repo = product_repo
        self.cart_repo = cart_repo
        self.payment_repo = payment_repo
        self.invoice_repo = invoice_repo
        self.user_repo = user_repo
        self.payment_service = payment_service
        self.delivery_service = delivery_service
        self.billing_service = billing_service
    
    def checkout(self, user_id: str) -> Order:
        """Crée une commande depuis le panier de l'utilisateur."""
        # Récupérer le panier
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart or not cart.items:
            raise ValueError("Panier vide")
        
        # Vérifier et réserver le stock
        order_items = []
        for item in cart.items:
            product = self.product_repo.get_by_id(str(item.product_id))
            if not product or not product.active:
                raise ValueError(f"Produit indisponible: {product.name if product else 'ID inconnu'}")
            
            if product.stock_qty < item.quantity:
                raise ValueError(f"Stock insuffisant pour {product.name}")
            
            # Réserver le stock
            self.product_repo.reserve_stock(str(item.product_id), item.quantity)
            
            order_items.append({
                "product_id": str(item.product_id),
                "name": product.name,
                "unit_price_cents": product.price_cents,
                "quantity": item.quantity
            })
        
        # Créer la commande
        order_data = {
            "user_id": user_id,
            "status": OrderStatus.CREE,
            "items": order_items
        }
        
        order = self.order_repo.create(order_data)
        
        # Vider le panier
        self.cart_repo.clear(user_id)
        
        return order
    
    def pay_by_card(self, order_id: str, card_number: str, exp_month: int, exp_year: int, cvc: str, 
                   postal_code: str = None, phone: str = None, street_number: str = None, 
                   street_name: str = None) -> Payment:
        """Effectue le paiement d'une commande par carte."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Commande introuvable")
        
        if order.status not in [OrderStatus.CREE, OrderStatus.VALIDEE]:
            raise ValueError("Statut de commande incompatible avec le paiement")
        
        # Préparer les données de paiement
        payment_data = {
            "card_number": card_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvc,
            "postal_code": postal_code,
            "phone": phone,
            "street_number": street_number,
            "street_name": street_name
        }
        
        # Traiter le paiement
        payment = self.payment_service.process_payment(order_id, payment_data)
        
        if payment.status == "PAID":
            # Mettre à jour le statut de la commande
            order.status = OrderStatus.PAYEE
            order.paid_at = datetime.now(UTC)
            order.payment_id = payment.id
            self.order_repo.update(order)
            
            # Générer la facture
            invoice = self.billing_service.issue_invoice(order)
            order.invoice_id = invoice.id
            self.order_repo.update(order)
        
        return payment
    
    def view_orders(self, user_id: str) -> List[Order]:
        """Récupère toutes les commandes d'un utilisateur."""
        return self.order_repo.list_by_user(user_id)
    
    def request_cancellation(self, user_id: str, order_id: str) -> Order:
        """Demande d'annulation d'une commande par l'utilisateur."""
        order = self.order_repo.get_by_id(order_id)
        if not order or str(order.user_id) != user_id:
            raise ValueError("Commande introuvable")
        
        if order.status in [OrderStatus.EXPEDIEE, OrderStatus.LIVREE]:
            raise ValueError("Trop tard pour annuler : commande expédiée")
        
        order.status = OrderStatus.ANNULEE
        order.cancelled_at = datetime.now(UTC)
        
        # Restituer le stock
        for item in order.items:
            self.product_repo.release_stock(str(item.product_id), item.quantity)
        
        self.order_repo.update(order)
        return order
    
    # ========== FONCTIONS ADMIN ==========
    
    def backoffice_validate_order(self, admin_user_id: str, order_id: str) -> Order:
        """Valide une commande (admin)."""
        admin = self.user_repo.get_by_id(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants")
        
        order = self.order_repo.get_by_id(order_id)
        if not order or order.status != OrderStatus.CREE:
            raise ValueError("Commande introuvable ou mauvais statut")
        
        order.status = OrderStatus.VALIDEE
        order.validated_at = datetime.now(UTC)
        self.order_repo.update(order)
        
        return order
    
    def backoffice_ship_order(self, admin_user_id: str, order_id: str) -> Order:
        """Expédie une commande (admin)."""
        admin = self.user_repo.get_by_id(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants")
        
        order = self.order_repo.get_by_id(order_id)
        if not order or order.status != OrderStatus.PAYEE:
            raise ValueError("La commande doit être payée pour être expédiée")
        
        # Préparer la livraison
        delivery = self.delivery_service.prepare_delivery(order_id)
        delivery = self.delivery_service.ship_order(order_id)
        
        order.delivery_id = delivery.id
        order.status = OrderStatus.EXPEDIEE
        order.shipped_at = datetime.now(UTC)
        self.order_repo.update(order)
        
        return order
    
    def backoffice_mark_delivered(self, admin_user_id: str, order_id: str) -> Order:
        """Marque une commande comme livrée (admin)."""
        admin = self.user_repo.get_by_id(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants")
        
        order = self.order_repo.get_by_id(order_id)
        if not order or order.status != OrderStatus.EXPEDIEE:
            raise ValueError("Commande non expédiée")
        
        self.delivery_service.mark_delivered(order_id)
        
        order.status = OrderStatus.LIVREE
        order.delivered_at = datetime.now(UTC)
        self.order_repo.update(order)
        
        return order
    
    def backoffice_refund(self, admin_user_id: str, order_id: str, amount_cents: Optional[int] = None) -> Order:
        """Effectue un remboursement (admin)."""
        admin = self.user_repo.get_by_id(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants")
        
        order = self.order_repo.get_by_id(order_id)
        if not order or order.status not in [OrderStatus.PAYEE, OrderStatus.ANNULEE]:
            raise ValueError("Remboursement non autorisé au statut actuel")
        
        amount = amount_cents or order.total_cents()
        
        # Traiter le remboursement
        refund = self.payment_service.process_refund(order_id, amount)
        
        order.status = OrderStatus.REMBOURSEE
        order.refunded_at = datetime.now(UTC)
        
        # Restituer le stock si nécessaire
        for item in order.items:
            self.product_repo.release_stock(str(item.product_id), item.quantity)
        
        self.order_repo.update(order)
        return order
