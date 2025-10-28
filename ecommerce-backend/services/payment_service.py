"""
Service métier pour la gestion des paiements.

Ce service gère :
- Traitement des paiements par carte
- Simulation de gateway de paiement
- Gestion des remboursements
- Validation des données de paiement
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from database.models import Payment, Order
from database.repositories_simple import PostgreSQLPaymentRepository, PostgreSQLOrderRepository
from enums import OrderStatus


class PaymentGateway:
    """Simulation d'un prestataire de paiement (à remplacer par Stripe/Adyen/etc.)."""
    
    def charge_card(self, card_number: str, exp_month: int, exp_year: int, cvc: str,
                   amount_cents: int, idempotency_key: str) -> Dict[str, Any]:
        """Simule un paiement par carte."""
        # MOCK: succès si carte ne finit pas par '0000'
        ok = not card_number.endswith("0000")
        return {
            "success": ok,
            "transaction_id": str(uuid.uuid4()) if ok else None,
            "failure_reason": None if ok else "CARTE_REFUSEE"
        }
    
    def refund(self, transaction_id: str, amount_cents: int) -> Dict[str, Any]:
        """Simule un remboursement."""
        return {
            "success": True,
            "refund_id": str(uuid.uuid4())
        }


class PaymentService:
    """Service métier pour la gestion des paiements."""
    
    def __init__(self, payment_repo: PostgreSQLPaymentRepository, order_repo: PostgreSQLOrderRepository):
        self.payment_repo = payment_repo
        self.order_repo = order_repo
        self.gateway = PaymentGateway()
    
    def process_payment(self, order_id: str, payment_data: Dict[str, Any]) -> Payment:
        """Traite un paiement pour une commande."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Commande introuvable")
        
        if order.status not in [OrderStatus.CREE, OrderStatus.VALIDEE]:
            raise ValueError("Commande déjà payée ou traitée")
        
        amount = order.total_cents()
        
        # Simuler le paiement via le gateway
        result = self.gateway.charge_card(
            payment_data["card_number"],
            payment_data["exp_month"],
            payment_data["exp_year"],
            payment_data["cvc"],
            amount,
            idempotency_key=order_id
        )
        
        # Créer l'enregistrement de paiement
        payment_data_dict = {
            "order_id": order_id,
            "amount_cents": amount,
            "status": "PAID" if result["success"] else "FAILED",
            "payment_method": "CARD",
            "card_last4": payment_data["card_number"][-4:] if len(payment_data["card_number"]) >= 4 else None,
            "postal_code": payment_data.get("postal_code"),
            "phone": payment_data.get("phone"),
            "street_number": payment_data.get("street_number"),
            "street_name": payment_data.get("street_name")
        }
        
        payment = self.payment_repo.create(payment_data_dict)
        
        if not result["success"]:
            raise ValueError("Paiement refusé")
        
        return payment
    
    def process_refund(self, order_id: str, amount_cents: Optional[int] = None) -> Payment:
        """Traite un remboursement."""
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Commande introuvable")
        
        if order.status not in [OrderStatus.PAYEE, OrderStatus.ANNULEE]:
            raise ValueError("Remboursement non autorisé au statut actuel")
        
        amount = amount_cents or order.total_cents()
        
        # Récupérer le paiement initial
        initial_payment = None
        if order.payment_id:
            initial_payment = self.payment_repo.get_by_id(order.payment_id)
        
        if not initial_payment:
            raise ValueError("Aucun paiement initial trouvé")
        
        # Simuler le remboursement via le gateway
        refund_result = self.gateway.refund("mock_transaction_id", amount)
        
        if not refund_result["success"]:
            raise ValueError("Remboursement échoué")
        
        # Créer l'enregistrement de remboursement
        refund_data = {
            "order_id": order_id,
            "amount_cents": -amount,  # Montant négatif pour un remboursement
            "status": "REFUNDED",
            "payment_method": "REFUND"
        }
        
        refund = self.payment_repo.create(refund_data)
        return refund
    
    def get_payment_by_order(self, order_id: str) -> Optional[Payment]:
        """Récupère le paiement d'une commande."""
        return self.payment_repo.get_by_order_id(order_id)
