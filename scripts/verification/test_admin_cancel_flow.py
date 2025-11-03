#!/usr/bin/env python3
"""
Script de test du flux complet d'annulation admin:
Frontend → Backend → Base de données

Ce script vérifie:
1. L'endpoint /admin/orders/{order_id}/cancel est accessible
2. Le remboursement automatique fonctionne
3. Le stock est remis en place
4. Les statuts sont correctement mis à jour en base
"""

import requests
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_BASE = "http://localhost:8000"

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ecommerce'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_admin_token():
    """Connexion en tant qu'admin et récupération du token"""
    print("\n🔑 Connexion en tant qu'admin...")
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "admin@ecommerce.com",
        "password": "admin123"
    })
    if response.status_code != 200:
        print(f"❌ Erreur de connexion admin: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    print(f"✅ Admin connecté: {data.get('user', {}).get('email')}")
    return data["token"]

def get_db_connection():
    """Connexion à la base de données"""
    return psycopg2.connect(**DB_CONFIG)

def check_order_in_db(order_id):
    """Vérifie l'état d'une commande dans la base de données"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, user_id, status, cancelled_at, refunded_at, created_at
        FROM orders
        WHERE id = %s
    """, (order_id,))
    
    order = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if order:
        return {
            'id': str(order[0]),
            'user_id': str(order[1]),
            'status': order[2],
            'cancelled_at': order[3],
            'refunded_at': order[4],
            'created_at': order[5]
        }
    return None

def check_payments_in_db(order_id):
    """Vérifie les paiements d'une commande"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, order_id, status, amount_cents, created_at
        FROM payments
        WHERE order_id = %s
    """, (order_id,))
    
    payments = []
    for row in cursor.fetchall():
        payments.append({
            'id': str(row[0]),
            'order_id': str(row[1]),
            'status': row[2],
            'amount_cents': row[3],
            'created_at': row[4]
        })
    
    cursor.close()
    conn.close()
    return payments

def check_product_stock(product_id):
    """Vérifie le stock d'un produit"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, stock_qty, active
        FROM products
        WHERE id = %s
    """, (product_id,))
    
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if product:
        return {
            'id': str(product[0]),
            'name': product[1],
            'stock_qty': product[2],
            'active': product[3]
        }
    return None

def test_admin_cancel_order():
    """Test complet du flux d'annulation admin"""
    print("\n" + "="*70)
    print("🧪 TEST DU FLUX D'ANNULATION ADMIN")
    print("="*70)
    
    # 1. Connexion admin
    admin_token = get_admin_token()
    if not admin_token:
        print("❌ Impossible de se connecter en tant qu'admin")
        return False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # 2. Récupérer la liste des commandes
    print("\n📋 Récupération des commandes admin...")
    response = requests.get(f"{API_BASE}/admin/orders", headers=headers)
    if response.status_code != 200:
        print(f"❌ Erreur lors de la récupération des commandes: {response.status_code}")
        return False
    
    orders = response.json()
    print(f"✅ {len(orders)} commandes trouvées")
    
    # 3. Trouver une commande annulable (CREE, VALIDEE, ou PAYEE)
    cancellable_order = None
    for order in orders:
        if order['status'] in ['CREE', 'VALIDEE', 'PAYEE']:
            cancellable_order = order
            break
    
    if not cancellable_order:
        print("⚠️ Aucune commande annulable trouvée (statut CREE, VALIDEE ou PAYEE)")
        print("   Créez une commande de test d'abord!")
        return False
    
    order_id = cancellable_order['id']
    initial_status = cancellable_order['status']
    
    print(f"\n📦 Commande sélectionnée:")
    print(f"   ID: {order_id}")
    print(f"   Statut: {initial_status}")
    print(f"   Total: {cancellable_order.get('total_price_cents', 0)/100:.2f}€")
    
    # 4. Vérifier l'état initial en base de données
    print("\n🔍 Vérification de l'état initial en BDD...")
    initial_order_db = check_order_in_db(order_id)
    print(f"   Statut BDD: {initial_order_db['status']}")
    print(f"   cancelled_at: {initial_order_db.get('cancelled_at', 'NULL')}")
    print(f"   refunded_at: {initial_order_db.get('refunded_at', 'NULL')}")
    
    # 5. Vérifier les paiements initiaux
    initial_payments = check_payments_in_db(order_id)
    print(f"   Paiements: {len(initial_payments)}")
    for payment in initial_payments:
        print(f"      - {payment['status']}: {payment['amount_cents']/100:.2f}€")
    
    # 6. Récupérer le stock initial des produits
    print("\n📊 Stock initial des produits:")
    initial_stocks = {}
    for item in cancellable_order.get('items', []):
        product_id = item['product_id']
        product = check_product_stock(product_id)
        if product:
            initial_stocks[product_id] = product['stock_qty']
            print(f"   - {product['name']}: {product['stock_qty']} unités (quantité commande: {item['quantity']})")
    
    # 7. ANNULATION ADMIN
    print(f"\n❌ Annulation de la commande {order_id}...")
    response = requests.post(
        f"{API_BASE}/admin/orders/{order_id}/cancel",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur lors de l'annulation: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return False
    
    cancel_result = response.json()
    print(f"✅ Réponse backend:")
    print(f"   Message: {cancel_result.get('message')}")
    if cancel_result.get('refunded'):
        print(f"   ✅ Remboursement effectué: {cancel_result.get('amount_cents', 0)/100:.2f}€")
    
    # 8. Vérifier l'état final en base de données
    print("\n🔍 Vérification de l'état final en BDD...")
    final_order_db = check_order_in_db(order_id)
    print(f"   Statut BDD: {final_order_db['status']}")
    print(f"   cancelled_at: {final_order_db.get('cancelled_at', 'NULL')}")
    print(f"   refunded_at: {final_order_db.get('refunded_at', 'NULL')}")
    
    # Vérifications
    success = True
    
    # Vérif 1: Statut correct
    expected_status = 'REMBOURSEE' if initial_status == 'PAYEE' else 'ANNULEE'
    if final_order_db['status'] != expected_status:
        print(f"   ❌ Statut incorrect! Attendu: {expected_status}, Obtenu: {final_order_db['status']}")
        success = False
    else:
        print(f"   ✅ Statut correct: {expected_status}")
    
    # Vérif 2: cancelled_at rempli
    if not final_order_db.get('cancelled_at'):
        print("   ❌ cancelled_at non rempli!")
        success = False
    else:
        print(f"   ✅ cancelled_at rempli: {final_order_db['cancelled_at']}")
    
    # Vérif 3: refunded_at si payée
    if initial_status == 'PAYEE':
        if not final_order_db.get('refunded_at'):
            print("   ❌ refunded_at non rempli pour une commande payée!")
            success = False
        else:
            print(f"   ✅ refunded_at rempli: {final_order_db['refunded_at']}")
    
    # 9. Vérifier les paiements finaux
    final_payments = check_payments_in_db(order_id)
    if initial_status == 'PAYEE':
        print(f"\n💳 Vérification des paiements remboursés:")
        all_refunded = all(p['status'] == 'REFUNDED' for p in final_payments)
        if all_refunded:
            print(f"   ✅ Tous les paiements sont marqués REFUNDED")
        else:
            print(f"   ❌ Certains paiements ne sont pas remboursés!")
            for payment in final_payments:
                print(f"      - {payment['status']}: {payment['amount_cents']/100:.2f}€")
            success = False
    
    # 10. Vérifier le stock final
    print("\n📊 Vérification du stock final:")
    for item in cancellable_order.get('items', []):
        product_id = item['product_id']
        product = check_product_stock(product_id)
        if product:
            expected_stock = initial_stocks[product_id] + item['quantity']
            if product['stock_qty'] == expected_stock:
                print(f"   ✅ {product['name']}: {product['stock_qty']} unités (remis: +{item['quantity']})")
            else:
                print(f"   ❌ {product['name']}: {product['stock_qty']} unités (attendu: {expected_stock})")
                success = False
    
    # Résultat final
    print("\n" + "="*70)
    if success:
        print("🎉 ✅ TOUS LES TESTS SONT PASSÉS!")
        print("="*70)
        print("\n✅ Le flux complet fonctionne:")
        print("   1. ✅ Frontend → Backend: Endpoint accessible")
        print("   2. ✅ Backend: Traitement correct (remboursement, stock)")
        print("   3. ✅ Base de données: Toutes les données mises à jour")
        print("   4. ✅ Stock: Remis en place correctement")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("="*70)
    
    return success

if __name__ == "__main__":
    try:
        test_admin_cancel_order()
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

