"""
========================================
ENUMS - CONSTANTES DE L'APPLICATION
========================================

Ce fichier définit toutes les CONSTANTES de l'application sous forme d'Enums.

Pourquoi utiliser des Enums ?
- ✅ Évite les "magic strings" (chaînes en dur partout dans le code)
- ✅ Autocomplétion dans l'IDE
- ✅ Erreurs à la compilation si on fait une faute de frappe
- ✅ Facilite la maintenance (changer une valeur à un seul endroit)

Exemple d'utilisation :
    # ❌ Mauvais (magic string)
    order.status = "PAYEE"
    
    # ✅ Bon (Enum)
    order.status = OrderStatus.PAYEE
"""

# Import de la classe Enum du module enum de Python
from enum import Enum

# ========================================
# STATUTS DES COMMANDES
# ========================================
class OrderStatus(str, Enum):
    """
    Énumération des statuts possibles d'une commande.
    
    Cycle de vie normal d'une commande :
    CREE → VALIDEE → PAYEE → EXPEDIEE → LIVREE
    
    États alternatifs :
    - ANNULEE : Commande annulée par le client ou l'admin
    - REMBOURSEE : Commande remboursée
    """
    CREE = "CREE"              # Commande créée (checkout effectué)
    VALIDEE = "VALIDEE"        # Commande validée par l'admin (optionnel)
    PAYEE = "PAYEE"            # Paiement effectué avec succès
    EXPEDIEE = "EXPEDIEE"      # Colis expédié (tracking number généré)
    LIVREE = "LIVREE"          # Colis livré au client
    ANNULEE = "ANNULEE"        # Commande annulée (avant expédition)
    REMBOURSEE = "REMBOURSEE"  # Commande remboursée (après paiement)

# ========================================
# STATUTS DES LIVRAISONS
# ========================================
class DeliveryStatus(str, Enum):
    """
    Énumération des statuts possibles d'une livraison.
    
    Cycle de vie : PREPAREE → EN_COURS → LIVREE
    """
    PREPAREE = "PREPAREE"  # Colis préparé, en attente d'expédition
    EN_COURS = "EN_COURS"  # Colis en cours de livraison (transporteur)
    LIVREE = "LIVREE"      # Colis livré au client

# ========================================
# STATUTS DES PAIEMENTS
# ========================================
class PaymentStatus(str, Enum):
    """
    Énumération des statuts possibles d'un paiement.
    
    États possibles :
    - PENDING : Paiement en attente de traitement
    - SUCCEEDED : Paiement réussi
    - FAILED : Paiement échoué (carte refusée, fonds insuffisants, etc.)
    - REFUNDED : Paiement remboursé
    """
    PENDING = "PENDING"        # En attente (transaction en cours)
    SUCCEEDED = "SUCCEEDED"    # Paiement réussi (argent reçu)
    FAILED = "FAILED"          # Paiement échoué (erreur bancaire)
    REFUNDED = "REFUNDED"      # Paiement remboursé (argent rendu)

# ========================================
# STATUTS DES FILS DE DISCUSSION (SUPPORT)
# ========================================
class MessageThreadStatus(str, Enum):
    """
    Énumération des statuts possibles d'un fil de discussion du support client.
    
    États possibles :
    - OPEN : Conversation ouverte (en attente de réponse)
    - CLOSED : Conversation fermée (problème résolu)
    - PENDING : En attente de réponse du client ou de l'admin
    """
    OPEN = "OPEN"        # Fil ouvert (conversation active)
    CLOSED = "CLOSED"    # Fil fermé (problème résolu)
    PENDING = "PENDING"  # En attente de réponse
