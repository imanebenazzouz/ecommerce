#!/usr/bin/env python3
"""
Script de migration robuste des données JSON vers PostgreSQL
Gère les contraintes de clés étrangères et les données manquantes
"""

import json
import os
import uuid
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import sys

def load_json_data(file_path: str) -> dict:
    """Charge les données depuis un fichier JSON"""
    if os.path.exists(file_path):
        print(f"📁 Chargement du fichier: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print(f"⚠️  Fichier non trouvé: {file_path}")
        return {}

def get_db_connection():
    """Crée une connexion à la base de données PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'ecommerce'),
        user=os.getenv('DB_USER', 'ecommerce'),
        password=os.getenv('DB_PASSWORD', 'ecommerce123'),
        cursor_factory=RealDictCursor
    )

def create_missing_users(cursor, all_data: dict):
    """Crée les utilisateurs manquants basés sur les données des commandes et paiements"""
    print("🔍 Recherche d'utilisateurs manquants...")
    
    # Collecter tous les user_id des commandes et paiements
    user_ids = set()
    
    # Depuis les commandes
    orders_data = all_data.get('orders', {})
    for order_data in orders_data.values():
        if 'user_id' in order_data:
            user_ids.add(order_data['user_id'])
    
    # Depuis les paiements
    payments_data = all_data.get('payments', {})
    for payment_data in payments_data.values():
        if 'user_id' in payment_data:
            user_ids.add(payment_data['user_id'])
    
    # Depuis les factures
    invoices_data = all_data.get('invoices', {})
    for invoice_data in invoices_data.values():
        if 'user_id' in invoice_data:
            user_ids.add(invoice_data['user_id'])
    
    # Vérifier quels utilisateurs existent déjà
    existing_users = set()
    if user_ids:
        placeholders = ','.join(['%s'] * len(user_ids))
        cursor.execute(f"SELECT id FROM users WHERE id IN ({placeholders})", list(user_ids))
        for row in cursor.fetchall():
            existing_users.add(row['id'])
    
    # Créer les utilisateurs manquants
    missing_users = user_ids - existing_users
    if missing_users:
        print(f"👤 Création de {len(missing_users)} utilisateurs manquants...")
        for user_id in missing_users:
            try:
                cursor.execute("""
                    INSERT INTO users (id, email, password_hash, first_name, last_name, address, is_admin, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    user_id,
                    f"user_{user_id[:8]}@example.com",
                    "migrated_user_hash",
                    "Utilisateur",
                    "Migré",
                    "Adresse par défaut",
                    False,
                    datetime.now()
                ))
            except Exception as e:
                print(f"⚠️  Erreur lors de la création de l'utilisateur {user_id}: {e}")

def migrate_users(cursor, users_data: dict):
    """Migre les utilisateurs"""
    if not users_data:
        print("⚠️  Aucune donnée utilisateur à migrer")
        return
    
    print(f"📊 Migration de {len(users_data)} utilisateurs...")
    migrated_count = 0
    
    for user_id, user_data in users_data.items():
        try:
            cursor.execute("""
                INSERT INTO users (id, email, password_hash, first_name, last_name, address, is_admin, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                user_id,
                user_data['email'],
                user_data['password_hash'],
                user_data['first_name'],
                user_data['last_name'],
                user_data['address'],
                user_data.get('is_admin', False),
                datetime.fromtimestamp(user_data.get('created_at', 0)) if user_data.get('created_at') else datetime.now()
            ))
            migrated_count += 1
        except Exception as e:
            print(f"❌ Erreur lors de la migration de l'utilisateur {user_id}: {e}")
    
    print(f"✅ {migrated_count} utilisateurs migrés")

def migrate_products(cursor, products_data: dict):
    """Migre les produits"""
    if not products_data:
        print("⚠️  Aucune donnée produit à migrer")
        return
    
    print(f"📊 Migration de {len(products_data)} produits...")
    migrated_count = 0
    
    for product_id, product_data in products_data.items():
        try:
            cursor.execute("""
                INSERT INTO products (id, name, description, price_cents, stock_qty, active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                product_id,
                product_data['name'],
                product_data.get('description', ''),
                product_data['price_cents'],
                product_data.get('stock_qty', 0),
                product_data.get('active', True),
                datetime.fromtimestamp(product_data.get('created_at', 0)) if product_data.get('created_at') else datetime.now()
            ))
            migrated_count += 1
        except Exception as e:
            print(f"❌ Erreur lors de la migration du produit {product_id}: {e}")
    
    print(f"✅ {migrated_count} produits migrés")

def migrate_orders(cursor, orders_data: dict):
    """Migre les commandes"""
    if not orders_data:
        print("⚠️  Aucune donnée commande à migrer")
        return
    
    print(f"📊 Migration de {len(orders_data)} commandes...")
    migrated_count = 0
    
    for order_id, order_data in orders_data.items():
        try:
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
                    INSERT INTO order_items (id, order_id, product_id, name, unit_price_cents, quantity)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    str(uuid.uuid4()),  # Générer un nouvel ID pour chaque article
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
                    INSERT INTO deliveries (id, order_id, transporteur, tracking_number, address, delivery_status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    delivery_data.get('id', str(uuid.uuid4())),
                    order_id,
                    delivery_data['transporteur'],
                    delivery_data.get('tracking_number'),
                    delivery_data['address'],
                    delivery_data['delivery_status'],
                    datetime.fromtimestamp(delivery_data.get('created_at', 0)) if delivery_data.get('created_at') else datetime.now()
                ))
            
            migrated_count += 1
        except Exception as e:
            print(f"❌ Erreur lors de la migration de la commande {order_id}: {e}")
    
    print(f"✅ {migrated_count} commandes migrées")

def migrate_payments(cursor, payments_data: dict):
    """Migre les paiements"""
    if not payments_data:
        print("⚠️  Aucune donnée paiement à migrer")
        return
    
    print(f"📊 Migration de {len(payments_data)} paiements...")
    migrated_count = 0
    
    for payment_id, payment_data in payments_data.items():
        try:
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
            migrated_count += 1
        except Exception as e:
            print(f"❌ Erreur lors de la migration du paiement {payment_id}: {e}")
    
    print(f"✅ {migrated_count} paiements migrés")

def migrate_invoices(cursor, invoices_data: dict):
    """Migre les factures"""
    if not invoices_data:
        print("⚠️  Aucune donnée facture à migrer")
        return
    
    print(f"📊 Migration de {len(invoices_data)} factures...")
    migrated_count = 0
    
    for invoice_id, invoice_data in invoices_data.items():
        try:
            cursor.execute("""
                INSERT INTO invoices (id, order_id, user_id, total_cents, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                invoice_id,
                invoice_data['order_id'],
                invoice_data['user_id'],
                invoice_data['total_cents'],
                datetime.fromtimestamp(invoice_data['issued_at']) if invoice_data.get('issued_at') else datetime.now()
            ))
            migrated_count += 1
        except Exception as e:
            print(f"❌ Erreur lors de la migration de la facture {invoice_id}: {e}")
    
    print(f"✅ {migrated_count} factures migrées")

def migrate_all_data():
    """Migre toutes les données JSON vers PostgreSQL"""
    
    # Connexion à PostgreSQL
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🚀 Début de la migration complète des données...")
        
        # Charger toutes les données JSON
        data_dir = Path(__file__).parent.parent / "data"
        
        all_data = {
            'users': load_json_data(data_dir / "users.json"),
            'products': load_json_data(data_dir / "products.json"),
            'orders': load_json_data(data_dir / "orders.json"),
            'payments': load_json_data(data_dir / "payments.json"),
            'invoices': load_json_data(data_dir / "invoices.json")
        }
        
        # Créer les utilisateurs manquants d'abord
        create_missing_users(cursor, all_data)
        
        # Migrer les utilisateurs
        migrate_users(cursor, all_data['users'])
        
        # Migrer les produits
        migrate_products(cursor, all_data['products'])
        
        # Migrer les commandes
        migrate_orders(cursor, all_data['orders'])
        
        # Migrer les paiements
        migrate_payments(cursor, all_data['payments'])
        
        # Migrer les factures
        migrate_invoices(cursor, all_data['invoices'])
        
        conn.commit()
        print("🎉 Migration terminée avec succès!")
        
        # Afficher un résumé
        print("\n📊 Résumé de la migration:")
        try:
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()['count']
            print(f"👥 Utilisateurs: {user_count}")
        except:
            print("👥 Utilisateurs: 0")
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM products")
            product_count = cursor.fetchone()['count']
            print(f"📦 Produits: {product_count}")
        except:
            print("📦 Produits: 0")
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            order_count = cursor.fetchone()['count']
            print(f"🛒 Commandes: {order_count}")
        except:
            print("🛒 Commandes: 0")
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM payments")
            payment_count = cursor.fetchone()['count']
            print(f"💳 Paiements: {payment_count}")
        except:
            print("💳 Paiements: 0")
        
        try:
            cursor.execute("SELECT COUNT(*) as count FROM invoices")
            invoice_count = cursor.fetchone()['count']
            print(f"🧾 Factures: {invoice_count}")
        except:
            print("🧾 Factures: 0")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_all_data()
