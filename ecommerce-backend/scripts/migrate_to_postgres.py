#!/usr/bin/env python3
"""
Script de migration des données JSON vers PostgreSQL
"""

import sys
import os
import json
import uuid
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from database.database import engine, SessionLocal, create_tables
from database.models import (
    User, Product, Cart, CartItem, Order, OrderItem, 
    Delivery, Invoice, Payment, MessageThread, Message
)
from sqlalchemy.orm import Session

def load_json_data(file_path: str) -> dict:
    """Charge les données depuis un fichier JSON"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def migrate_users(db: Session, users_data: dict):
    """Migre les utilisateurs"""
    print(f"📊 Migration de {len(users_data)} utilisateurs...")
    
    for user_id, user_data in users_data.items():
        user = User(
            id=uuid.UUID(user_id),
            email=user_data['email'],
            password_hash=user_data['password_hash'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            address=user_data['address'],
            is_admin=user_data.get('is_admin', False)
        )
        db.add(user)
    
    db.commit()
    print("✅ Utilisateurs migrés avec succès")

def migrate_products(db: Session, products_data: dict):
    """Migre les produits"""
    print(f"📊 Migration de {len(products_data)} produits...")
    
    for product_id, product_data in products_data.items():
        product = Product(
            id=uuid.UUID(product_id),
            name=product_data['name'],
            description=product_data.get('description', ''),
            price_cents=product_data['price_cents'],
            stock_qty=product_data.get('stock_qty', 0),
            active=product_data.get('active', True)
        )
        db.add(product)
    
    db.commit()
    print("✅ Produits migrés avec succès")

def migrate_orders(db: Session, orders_data: dict):
    """Migre les commandes"""
    print(f"📊 Migration de {len(orders_data)} commandes...")
    
    for order_id, order_data in orders_data.items():
        # Créer la commande
        order = Order(
            id=uuid.UUID(order_id),
            user_id=uuid.UUID(order_data['user_id']),
            status=order_data['status'],
            created_at=datetime.fromtimestamp(order_data['created_at']) if order_data.get('created_at') else None,
            validated_at=datetime.fromtimestamp(order_data['validated_at']) if order_data.get('validated_at') else None,
            shipped_at=datetime.fromtimestamp(order_data['shipped_at']) if order_data.get('shipped_at') else None,
            delivered_at=datetime.fromtimestamp(order_data['delivered_at']) if order_data.get('delivered_at') else None,
            cancelled_at=datetime.fromtimestamp(order_data['cancelled_at']) if order_data.get('cancelled_at') else None,
            refunded_at=datetime.fromtimestamp(order_data['refunded_at']) if order_data.get('refunded_at') else None,
            payment_id=uuid.UUID(order_data['payment_id']) if order_data.get('payment_id') else None,
            invoice_id=uuid.UUID(order_data['invoice_id']) if order_data.get('invoice_id') else None
        )
        db.add(order)
        
        # Créer les articles de la commande
        for item_data in order_data.get('items', []):
            order_item = OrderItem(
                order_id=order.id,
                product_id=uuid.UUID(item_data['product_id']),
                name=item_data['name'],
                unit_price_cents=item_data['unit_price_cents'],
                quantity=item_data['quantity']
            )
            db.add(order_item)
        
        # Créer la livraison si elle existe
        if order_data.get('delivery'):
            delivery_data = order_data['delivery']
            delivery = Delivery(
                id=uuid.UUID(delivery_data['id']),
                order_id=order.id,
                transporteur=delivery_data['transporteur'],
                tracking_number=delivery_data['tracking_number'],
                address=delivery_data['address'],
                delivery_status=delivery_data['delivery_status']
            )
            db.add(delivery)
    
    db.commit()
    print("✅ Commandes migrées avec succès")

def migrate_payments(db: Session, payments_data: dict):
    """Migre les paiements"""
    print(f"📊 Migration de {len(payments_data)} paiements...")
    
    for payment_id, payment_data in payments_data.items():
        payment = Payment(
            id=uuid.UUID(payment_id),
            order_id=uuid.UUID(payment_data['order_id']),
            amount_cents=payment_data['amount_cents'],
            status=payment_data['status'],
            payment_method=payment_data['payment_method'],
            created_at=datetime.fromtimestamp(payment_data['created_at']) if payment_data.get('created_at') else None
        )
        db.add(payment)
    
    db.commit()
    print("✅ Paiements migrés avec succès")

def migrate_invoices(db: Session, invoices_data: dict):
    """Migre les factures"""
    print(f"📊 Migration de {len(invoices_data)} factures...")
    
    for invoice_id, invoice_data in invoices_data.items():
        invoice = Invoice(
            id=uuid.UUID(invoice_id),
            order_id=uuid.UUID(invoice_data['order_id']),
            user_id=uuid.UUID(invoice_data['user_id']),
            total_cents=invoice_data['total_cents'],
            created_at=datetime.fromtimestamp(invoice_data['created_at']) if invoice_data.get('created_at') else None
        )
        db.add(invoice)
    
    db.commit()
    print("✅ Factures migrées avec succès")

def main():
    """Fonction principale de migration"""
    print("🚀 Début de la migration vers PostgreSQL...")
    
    # Créer les tables
    print("📋 Création des tables...")
    create_tables()
    print("✅ Tables créées avec succès")
    
    # Charger les données JSON
    data_dir = Path(__file__).parent.parent / "data"
    
    users_data = load_json_data(data_dir / "users.json")
    products_data = load_json_data(data_dir / "products.json")
    orders_data = load_json_data(data_dir / "orders.json")
    payments_data = load_json_data(data_dir / "payments.json")
    invoices_data = load_json_data(data_dir / "invoices.json")
    
    # Créer une session de base de données
    db = SessionLocal()
    
    try:
        # Migrer les données
        if users_data:
            migrate_users(db, users_data)
        
        if products_data:
            migrate_products(db, products_data)
        
        if orders_data:
            migrate_orders(db, orders_data)
        
        if payments_data:
            migrate_payments(db, payments_data)
        
        if invoices_data:
            migrate_invoices(db, invoices_data)
        
        print("🎉 Migration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()