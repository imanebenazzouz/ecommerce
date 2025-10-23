#!/usr/bin/env python3
"""
Script de migration simple des données JSON vers PostgreSQL
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
import psycopg2

def load_json_data(file_path: str) -> dict:
    """Charge les données depuis un fichier JSON"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def migrate_data():
    """Migre toutes les données JSON vers PostgreSQL"""
    
    # Connexion à PostgreSQL
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database='ecommerce',
        user='ecommerce',
        password='ecommerce123'
    )
    cursor = conn.cursor()
    
    try:
        # Charger les données JSON
        data_dir = Path(__file__).parent.parent / "data"
        
        # Migrer les utilisateurs
        users_data = load_json_data(data_dir / "users.json")
        if users_data:
            print(f"📊 Migration de {len(users_data)} utilisateurs...")
            for user_id, user_data in users_data.items():
                cursor.execute("""
                    INSERT INTO users (id, email, password_hash, first_name, last_name, address, is_admin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    user_id,
                    user_data['email'],
                    user_data['password_hash'],
                    user_data['first_name'],
                    user_data['last_name'],
                    user_data['address'],
                    user_data.get('is_admin', False)
                ))
            print("✅ Utilisateurs migrés")
        
        # Migrer les produits
        products_data = load_json_data(data_dir / "products.json")
        if products_data:
            print(f"📊 Migration de {len(products_data)} produits...")
            for product_id, product_data in products_data.items():
                cursor.execute("""
                    INSERT INTO products (id, name, description, price_cents, stock_qty, active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    product_id,
                    product_data['name'],
                    product_data.get('description', ''),
                    product_data['price_cents'],
                    product_data.get('stock_qty', 0),
                    product_data.get('active', True)
                ))
            print("✅ Produits migrés")
        
        # Migrer les commandes
        orders_data = load_json_data(data_dir / "orders.json")
        if orders_data:
            print(f"📊 Migration de {len(orders_data)} commandes...")
            for order_id, order_data in orders_data.items():
                # Insérer la commande
                cursor.execute("""
                    INSERT INTO orders (id, user_id, status, created_at, validated_at, shipped_at, 
                                     delivered_at, cancelled_at, refunded_at, payment_id, invoice_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    order_id,
                    order_data['user_id'],
                    order_data['status'],
                    datetime.fromtimestamp(order_data['created_at']) if order_data.get('created_at') else None,
                    datetime.fromtimestamp(order_data['validated_at']) if order_data.get('validated_at') else None,
                    datetime.fromtimestamp(order_data['shipped_at']) if order_data.get('shipped_at') else None,
                    datetime.fromtimestamp(order_data['delivered_at']) if order_data.get('delivered_at') else None,
                    datetime.fromtimestamp(order_data['cancelled_at']) if order_data.get('cancelled_at') else None,
                    datetime.fromtimestamp(order_data['refunded_at']) if order_data.get('refunded_at') else None,
                    order_data.get('payment_id'),
                    order_data.get('invoice_id')
                ))
                
                # Insérer les articles de la commande
                for item_data in order_data.get('items', []):
                    cursor.execute("""
                        INSERT INTO order_items (order_id, product_id, name, unit_price_cents, quantity)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        order_id,
                        item_data['product_id'],
                        item_data['name'],
                        item_data['unit_price_cents'],
                        item_data['quantity']
                    ))
                
                # Insérer la livraison si elle existe
                if order_data.get('delivery'):
                    delivery_data = order_data['delivery']
                    cursor.execute("""
                        INSERT INTO deliveries (id, order_id, transporteur, tracking_number, address, delivery_status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                    """, (
                        delivery_data['id'],
                        order_id,
                        delivery_data['transporteur'],
                        delivery_data['tracking_number'],
                        delivery_data['address'],
                        delivery_data['delivery_status']
                    ))
            
            print("✅ Commandes migrées")
        
        # Migrer les paiements
        payments_data = load_json_data(data_dir / "payments.json")
        if payments_data:
            print(f"📊 Migration de {len(payments_data)} paiements...")
            for payment_id, payment_data in payments_data.items():
                # Déterminer le statut basé sur 'succeeded'
                status = "SUCCEEDED" if payment_data.get('succeeded', False) else "PENDING"
                payment_method = payment_data.get('provider', 'UNKNOWN')
                
                cursor.execute("""
                    INSERT INTO payments (id, order_id, amount_cents, status, payment_method, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    payment_id,
                    payment_data['order_id'],
                    payment_data['amount_cents'],
                    status,
                    payment_method,
                    datetime.fromtimestamp(payment_data['created_at']) if payment_data.get('created_at') else None
                ))
            print("✅ Paiements migrés")
        
        # Migrer les factures
        invoices_data = load_json_data(data_dir / "invoices.json")
        if invoices_data:
            print(f"📊 Migration de {len(invoices_data)} factures...")
            for invoice_id, invoice_data in invoices_data.items():
                cursor.execute("""
                    INSERT INTO invoices (id, order_id, user_id, total_cents, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    invoice_id,
                    invoice_data['order_id'],
                    invoice_data['user_id'],
                    invoice_data['total_cents'],
                    datetime.fromtimestamp(invoice_data['created_at']) if invoice_data.get('created_at') else None
                ))
            print("✅ Factures migrées")
        
        conn.commit()
        print("🎉 Migration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_data()
