"""
Configuration et initialisation des services métier.

Ce module centralise la création et la configuration de tous les services
métier, permettant une injection de dépendances propre et une réutilisation
facile dans l'API.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from database.repositories_simple import (
    PostgreSQLUserRepository, PostgreSQLProductRepository, 
    PostgreSQLCartRepository, PostgreSQLOrderRepository,
    PostgreSQLDeliveryRepository, PostgreSQLInvoiceRepository, 
    PostgreSQLPaymentRepository, PostgreSQLThreadRepository
)
from services import (
    AuthService, OrderService, PaymentService, DeliveryService,
    BillingService, CatalogService, CartService, CustomerService
)


class ServiceContainer:
    """Conteneur de services métier avec injection de dépendances."""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Initialiser les repositories
        self.user_repo = PostgreSQLUserRepository(db)
        self.product_repo = PostgreSQLProductRepository(db)
        self.cart_repo = PostgreSQLCartRepository(db)
        self.order_repo = PostgreSQLOrderRepository(db)
        self.delivery_repo = PostgreSQLDeliveryRepository(db)
        self.invoice_repo = PostgreSQLInvoiceRepository(db)
        self.payment_repo = PostgreSQLPaymentRepository(db)
        self.thread_repo = PostgreSQLThreadRepository(db)
        
        # Initialiser les services métier
        self.auth_service = AuthService(self.user_repo)
        self.payment_service = PaymentService(self.payment_repo, self.order_repo)
        self.delivery_service = DeliveryService(self.delivery_repo, self.order_repo, self.user_repo)
        self.billing_service = BillingService(self.invoice_repo, self.order_repo)
        self.catalog_service = CatalogService(self.product_repo)
        self.cart_service = CartService(self.cart_repo, self.product_repo)
        self.customer_service = CustomerService(self.thread_repo, self.user_repo)
        
        # Initialiser le service de commandes (qui dépend des autres services)
        self.order_service = OrderService(
            self.order_repo, self.product_repo, self.cart_repo,
            self.payment_repo, self.invoice_repo, self.user_repo,
            self.payment_service, self.delivery_service, self.billing_service
        )
    
    def get_auth_service(self) -> AuthService:
        """Récupère le service d'authentification."""
        return self.auth_service
    
    def get_order_service(self) -> OrderService:
        """Récupère le service de gestion des commandes."""
        return self.order_service
    
    def get_payment_service(self) -> PaymentService:
        """Récupère le service de paiement."""
        return self.payment_service
    
    def get_delivery_service(self) -> DeliveryService:
        """Récupère le service de livraison."""
        return self.delivery_service
    
    def get_billing_service(self) -> BillingService:
        """Récupère le service de facturation."""
        return self.billing_service
    
    def get_catalog_service(self) -> CatalogService:
        """Récupère le service de catalogue."""
        return self.catalog_service
    
    def get_cart_service(self) -> CartService:
        """Récupère le service de panier."""
        return self.cart_service
    
    def get_customer_service(self) -> CustomerService:
        """Récupère le service de support client."""
        return self.customer_service


def get_service_container(db: Session) -> ServiceContainer:
    """Factory function pour créer un conteneur de services."""
    return ServiceContainer(db)
