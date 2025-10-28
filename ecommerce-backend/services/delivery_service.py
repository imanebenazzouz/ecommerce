"""
Service métier pour la gestion des livraisons.

Ce service gère :
- Préparation des livraisons
- Expédition avec numéro de tracking
- Suivi des livraisons
- Marquage comme livré
"""

from typing import Optional
from datetime import datetime
import uuid
from database.models import Delivery, Order
from database.repositories_simple import PostgreSQLDeliveryRepository, PostgreSQLOrderRepository, PostgreSQLUserRepository
from enums import DeliveryStatus


class DeliveryService:
    """Service métier pour la gestion des livraisons."""
    
    def __init__(
        self, 
        delivery_repo: PostgreSQLDeliveryRepository, 
        order_repo: PostgreSQLOrderRepository,
        user_repo: PostgreSQLUserRepository
    ):
        self.delivery_repo = delivery_repo
        self.order_repo = order_repo
        self.user_repo = user_repo
    
    def prepare_delivery(self, order_id: str, carrier: str = "POSTE") -> Delivery:
        """Prépare une livraison pour une commande."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Commande introuvable")
        
        user = self.user_repo.get_by_id(str(order.user_id))
        if not user:
            raise ValueError("Utilisateur introuvable")
        
        # Vérifier si une livraison existe déjà
        existing_delivery = self.delivery_repo.get_by_order_id(order_id)
        if existing_delivery:
            return existing_delivery
        
        # Créer une nouvelle livraison
        delivery_data = {
            "order_id": order_id,
            "transporteur": carrier,
            "address": user.address,
            "delivery_status": DeliveryStatus.PREPAREE
        }
        
        delivery = self.delivery_repo.create(delivery_data)
        return delivery
    
    def ship_order(self, order_id: str) -> Delivery:
        """Expédie une commande."""
        order = self.order_repo.get_by_id(order_id)
        if not order or order.status != "PAYEE":
            raise ValueError("Commande non payée")
        
        delivery = self.delivery_repo.get_by_order_id(order_id)
        if not delivery:
            delivery = self.prepare_delivery(order_id)
        
        # Générer un numéro de tracking
        tracking_number = f"TRK-{uuid.uuid4().hex[:10].upper()}"
        
        # Mettre à jour la livraison
        delivery.tracking_number = tracking_number
        delivery.delivery_status = DeliveryStatus.EN_COURS
        self.delivery_repo.update(delivery)
        
        return delivery
    
    def mark_delivered(self, order_id: str) -> Delivery:
        """Marque une commande comme livrée."""
        delivery = self.delivery_repo.get_by_order_id(order_id)
        if not delivery:
            raise ValueError("Livraison introuvable")
        
        delivery.delivery_status = DeliveryStatus.LIVREE
        self.delivery_repo.update(delivery)
        
        return delivery
    
    def get_delivery_by_order(self, order_id: str) -> Optional[Delivery]:
        """Récupère les informations de livraison d'une commande."""
        return self.delivery_repo.get_by_order_id(order_id)
    
    def update_tracking(self, order_id: str, tracking_number: str, carrier: str = None) -> Delivery:
        """Met à jour les informations de tracking."""
        delivery = self.delivery_repo.get_by_order_id(order_id)
        if not delivery:
            raise ValueError("Livraison introuvable")
        
        delivery.tracking_number = tracking_number
        if carrier:
            delivery.transporteur = carrier
        
        self.delivery_repo.update(delivery)
        return delivery
