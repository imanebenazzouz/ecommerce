#!/usr/bin/env python3
"""
Script de test pour vérifier la synchronisation des statuts de commande
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"

def login_admin():
    """Se connecter en tant qu'admin"""
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    
    if response.status_code != 200:
        print(f"❌ Erreur de connexion: {response.status_code}")
        print(response.text)
        return None
    
    data = response.json()
    return data["token"]

def get_orders(token):
    """Récupérer toutes les commandes"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/admin/orders", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Erreur récupération commandes: {response.status_code}")
        print(response.text)
        return []
    
    return response.json()

def get_order_status(token, order_id):
    """Récupérer le statut détaillé d'une commande"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE}/admin/orders/{order_id}/status", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Erreur statut commande {order_id}: {response.status_code}")
        print(response.text)
        return None
    
    return response.json()

def test_ship_order(token, order_id):
    """Tester l'expédition d'une commande"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Données de livraison
    delivery_data = {
        "transporteur": "Colissimo",
        "tracking_number": f"TRK{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "delivery_status": "PREPAREE"
    }
    
    response = requests.post(
        f"{API_BASE}/admin/orders/{order_id}/ship", 
        headers=headers,
        json=delivery_data
    )
    
    print(f"📦 Test expédition commande {order_id}:")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Succès: {response.json()}")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    return response.status_code == 200

def test_mark_delivered(token, order_id):
    """Tester le marquage comme livrée"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{API_BASE}/admin/orders/{order_id}/mark-delivered", 
        headers=headers
    )
    
    print(f"📦 Test livraison commande {order_id}:")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"   ✅ Succès: {response.json()}")
    else:
        print(f"   ❌ Erreur: {response.text}")
    
    return response.status_code == 200

def main():
    print("🔍 Test de synchronisation des statuts de commande")
    print("=" * 50)
    
    # Connexion admin
    print("1. Connexion admin...")
    token = login_admin()
    if not token:
        sys.exit(1)
    print("✅ Connexion réussie")
    
    # Récupérer les commandes
    print("\n2. Récupération des commandes...")
    orders = get_orders(token)
    print(f"✅ {len(orders)} commandes trouvées")
    
    if not orders:
        print("❌ Aucune commande trouvée. Créez d'abord une commande.")
        return
    
    # Afficher les commandes
    print("\n3. État des commandes:")
    for order in orders:
        print(f"   📋 Commande {order['id'][:8]}: {order['status']}")
        if order.get('delivery'):
            print(f"      📦 Livraison: {order['delivery']['transporteur']} - {order['delivery']['delivery_status']}")
    
    # Tester l'expédition sur une commande validée
    print("\n4. Test d'expédition...")
    valid_orders = [o for o in orders if o['status'] == 'VALIDEE']
    
    if valid_orders:
        order_to_ship = valid_orders[0]
        print(f"   Test sur commande {order_to_ship['id'][:8]}")
        
        # Vérifier le statut avant
        status_before = get_order_status(token, order_to_ship['id'])
        if status_before:
            print(f"   Statut avant: {status_before['status']}")
        
        # Tester l'expédition
        if test_ship_order(token, order_to_ship['id']):
            # Vérifier le statut après
            status_after = get_order_status(token, order_to_ship['id'])
            if status_after:
                print(f"   Statut après: {status_after['status']}")
                if status_after['delivery']:
                    print(f"   Livraison: {status_after['delivery']['transporteur']} - {status_after['delivery']['delivery_status']}")
        
        # Tester le marquage comme livrée
        print("\n5. Test de marquage comme livrée...")
        if test_mark_delivered(token, order_to_ship['id']):
            # Vérifier le statut final
            status_final = get_order_status(token, order_to_ship['id'])
            if status_final:
                print(f"   Statut final: {status_final['status']}")
    else:
        print("   ❌ Aucune commande validée trouvée pour le test")
    
    print("\n✅ Test terminé")

if __name__ == "__main__":
    main()
