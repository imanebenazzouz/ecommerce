#!/usr/bin/env python3
"""
Script pour vérifier l'état de la base de données PostgreSQL
"""

import os
import sys
import json
from sqlalchemy import text
from database.database import engine, SessionLocal
from database.models import User, Product, Order, Cart, CartItem, Delivery, Invoice, Payment, MessageThread, Message

def check_database_connection():
    """Vérifier la connexion à la base de données"""
    print("🔍 Vérification de la connexion à la base de données...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Connexion à la base de données réussie")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def check_tables_exist():
    """Vérifier que les tables existent"""
    print("\n📋 Vérification de l'existence des tables...")
    try:
        with engine.connect() as connection:
            # Vérifier les tables principales
            tables_to_check = [
                'users', 'products', 'orders', 'carts', 'cart_items',
                'order_items', 'deliveries', 'invoices', 'payments',
                'message_threads', 'messages'
            ]
            
            for table in tables_to_check:
                result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"✅ Table '{table}': {count} enregistrements")
            
            return True
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des tables: {e}")
        return False

def check_data_in_database():
    """Vérifier les données dans la base de données"""
    print("\n📊 Vérification des données dans la base de données...")
    
    db = SessionLocal()
    try:
        # Vérifier les utilisateurs
        users = db.query(User).all()
        print(f"👥 Utilisateurs: {len(users)}")
        for user in users:
            print(f"   - {user.email} ({'Admin' if user.is_admin else 'User'})")
        
        # Vérifier les produits
        products = db.query(Product).all()
        print(f"\n🛍️  Produits: {len(products)}")
        for product in products:
            print(f"   - {product.name} ({product.price_cents/100:.2f}€) - Stock: {product.stock_qty}")
        
        # Vérifier les commandes
        orders = db.query(Order).all()
        print(f"\n📦 Commandes: {len(orders)}")
        for order in orders:
            print(f"   - Commande {str(order.id)[:8]} - Statut: {order.status}")
        
        # Vérifier les paniers
        carts = db.query(Cart).all()
        print(f"\n🛒 Paniers: {len(carts)}")
        
        # Vérifier les factures
        invoices = db.query(Invoice).all()
        print(f"\n🧾 Factures: {len(invoices)}")
        
        # Vérifier les paiements
        payments = db.query(Payment).all()
        print(f"\n💳 Paiements: {len(payments)}")
        
        # Vérifier les threads de support
        threads = db.query(MessageThread).all()
        print(f"\n💬 Threads de support: {len(threads)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des données: {e}")
        return False
    finally:
        db.close()

def compare_with_json_files():
    """Comparer les données de la base avec les fichiers JSON"""
    print("\n📄 Comparaison avec les fichiers JSON...")
    
    # Lire les fichiers JSON
    json_files = {
        'users': 'data/users.json',
        'products': 'data/products.json',
        'orders': '../data/orders.json',
        'payments': '../data/payments.json',
        'invoices': '../data/invoices.json'
    }
    
    for data_type, file_path in json_files.items():
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"📁 {data_type}.json: {len(data)} enregistrements")
            else:
                print(f"❌ Fichier {data_type}.json non trouvé")
        except Exception as e:
            print(f"❌ Erreur lecture {data_type}.json: {e}")

def main():
    """Fonction principale"""
    print("🔍 Vérification de l'état de la base de données PostgreSQL")
    print("=" * 60)
    
    # Vérifier la connexion
    if not check_database_connection():
        print("\n❌ Impossible de se connecter à la base de données")
        print("💡 Vérifiez que PostgreSQL est démarré et que les paramètres de connexion sont corrects")
        return
    
    # Vérifier les tables
    if not check_tables_exist():
        print("\n❌ Problème avec les tables de la base de données")
        return
    
    # Vérifier les données
    check_data_in_database()
    
    # Comparer avec les fichiers JSON
    compare_with_json_files()
    
    print("\n" + "=" * 60)
    print("✅ Vérification terminée")

if __name__ == "__main__":
    main()
