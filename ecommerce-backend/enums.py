"""
Enums pour l'application e-commerce
"""

from enum import Enum

class OrderStatus(str, Enum):
    """Statuts des commandes"""
    CREE = "CREE"
    VALIDEE = "VALIDEE"
    PAYEE = "PAYEE"
    EXPEDIEE = "EXPEDIEE"
    LIVREE = "LIVREE"
    ANNULEE = "ANNULEE"
    REMBOURSEE = "REMBOURSEE"

class DeliveryStatus(str, Enum):
    """Statuts des livraisons"""
    PREPAREE = "PREPAREE"
    EN_COURS = "EN_COURS"
    LIVREE = "LIVREE"

class PaymentStatus(str, Enum):
    """Statuts des paiements"""
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class MessageThreadStatus(str, Enum):
    """Statuts des fils de discussion"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    PENDING = "PENDING"
