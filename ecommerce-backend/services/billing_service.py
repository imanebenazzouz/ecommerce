"""
Service métier pour la gestion de la facturation.

Ce service gère :
- Génération automatique de factures
- Création des lignes de facture
- Calcul des totaux
- Gestion des factures par commande
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid
from database.models import Invoice, Order, OrderItem
from database.repositories_simple import PostgreSQLInvoiceRepository, PostgreSQLOrderRepository


class InvoiceLine:
    """Représente une ligne de facture."""
    
    def __init__(self, product_id: str, name: str, unit_price_cents: int, quantity: int, line_total_cents: int):
        self.product_id = product_id
        self.name = name
        self.unit_price_cents = unit_price_cents
        self.quantity = quantity
        self.line_total_cents = line_total_cents


class BillingService:
    """Service métier pour la gestion de la facturation."""
    
    def __init__(self, invoice_repo: PostgreSQLInvoiceRepository, order_repo: PostgreSQLOrderRepository):
        self.invoice_repo = invoice_repo
        self.order_repo = order_repo
    
    def issue_invoice(self, order: Order) -> Invoice:
        """Génère une facture pour une commande."""
        # Vérifier si une facture existe déjà
        existing_invoice = self.invoice_repo.get_by_order_id(str(order.id))
        if existing_invoice:
            return existing_invoice
        
        # Créer les lignes de facture
        lines = []
        total_cents = 0
        
        for item in order.items:
            line_total = item.unit_price_cents * item.quantity
            lines.append(InvoiceLine(
                product_id=str(item.product_id),
                name=item.name,
                unit_price_cents=item.unit_price_cents,
                quantity=item.quantity,
                line_total_cents=line_total
            ))
            total_cents += line_total
        
        # Créer la facture
        invoice_data = {
            "order_id": str(order.id),
            "user_id": str(order.user_id),
            "total_cents": total_cents
        }
        
        invoice = self.invoice_repo.create(invoice_data)
        return invoice
    
    def get_invoice_by_order(self, order_id: str) -> Invoice:
        """Récupère la facture d'une commande."""
        invoice = self.invoice_repo.get_by_order_id(order_id)
        if not invoice:
            # Créer la facture si elle n'existe pas
            order = self.order_repo.get_by_id(order_id)
            if not order:
                raise ValueError("Commande introuvable")
            return self.issue_invoice(order)
        
        return invoice
    
    def get_invoice_lines(self, invoice: Invoice) -> List[InvoiceLine]:
        """Récupère les lignes d'une facture."""
        order = self.order_repo.get_by_id(str(invoice.order_id))
        if not order:
            return []
        
        lines = []
        for item in order.items:
            line_total = item.unit_price_cents * item.quantity
            lines.append(InvoiceLine(
                product_id=str(item.product_id),
                name=item.name,
                unit_price_cents=item.unit_price_cents,
                quantity=item.quantity,
                line_total_cents=line_total
            ))
        
        return lines
