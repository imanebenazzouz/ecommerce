#!/usr/bin/env python3
"""
Test de la réactivation automatique des produits
via remboursement d'une commande.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"
CLIENT_EMAIL = "client@example.com"
CLIENT_PASSWORD = "secret"

def login(email, password):
    """Se connecter et récupérer le token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["token"]
    else:
        print(f"❌ Erreur de connexion: {response.text}")
        return None

def get_headers(token):
    """Créer les headers avec le token"""
    return {"Authorization": f"Bearer {token}"}

def test_reactivation_refund():
    """Test de la réactivation via remboursement"""
    print("🧪 Test de la réactivation via remboursement")
    print("=" * 60)
    
    # 1. Connexion admin
    print("1. Connexion admin...")
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not admin_token:
        return False
    
    # 2. Créer un produit avec stock limité
    print("2. Création d'un produit avec stock limité...")
    product_data = {
        "name": "Produit Test Remboursement",
        "description": "Produit pour tester la réactivation via remboursement",
        "price_cents": 1500,  # 15€
        "stock_qty": 1,  # Stock limité à 1
        "active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/products",
        json=product_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code != 201:
        print(f"❌ Erreur création produit: {response.text}")
        return False
    
    product = response.json()
    product_id = product["id"]
    print(f"✅ Produit créé: {product['name']} (Stock: {product['stock_qty']})")
    
    # 3. Connexion client
    print("3. Connexion client...")
    client_token = login(CLIENT_EMAIL, CLIENT_PASSWORD)
    if not client_token:
        return False
    
    # 4. Ajouter le produit au panier et passer commande
    print("4. Ajout du produit au panier et passage de commande...")
    response = requests.post(
        f"{BASE_URL}/cart/add",
        json={"product_id": product_id, "qty": 1},
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur ajout panier: {response.text}")
        return False
    
    # Passer la commande
    response = requests.post(
        f"{BASE_URL}/orders/checkout",
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur checkout: {response.text}")
        return False
    
    order = response.json()
    print(f"✅ Commande créée: {order['order_id']}")
    
    # 5. Payer la commande
    print("5. Paiement de la commande...")
    payment_data = {
        "card_number": "4242424242424242",
        "exp_month": 12,
        "exp_year": 2025,
        "cvc": "123"
    }
    
    response = requests.post(
        f"{BASE_URL}/orders/{order['order_id']}/pay",
        json=payment_data,
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur paiement: {response.text}")
        return False
    
    print("✅ Commande payée")
    
    # 6. Vérifier que le produit est inactif (stock épuisé)
    print("6. Vérification que le produit est inactif...")
    response = requests.get(f"{BASE_URL}/products", headers=get_headers(client_token))
    if response.status_code == 200:
        products = response.json()
        product_found = False
        for p in products:
            if p["id"] == product_id:
                product_found = True
                print(f"   Stock après commande: {p['stock_qty']}")
                print(f"   Produit actif: {p['active']}")
                break
        
        if not product_found:
            print("✅ Le produit est inactif (n'apparaît plus dans la liste)")
    
    # 7. Rembourser la commande (admin)
    print("7. Remboursement de la commande par l'admin...")
    refund_data = {"amount_cents": None}  # Remboursement complet
    
    response = requests.post(
        f"{BASE_URL}/admin/orders/{order['order_id']}/refund",
        json=refund_data,
        headers=get_headers(admin_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur remboursement: {response.text}")
        return False
    
    print("✅ Commande remboursée")
    
    # 8. Vérifier que le produit est réactivé
    print("8. Vérification que le produit est réactivé...")
    response = requests.get(f"{BASE_URL}/products", headers=get_headers(client_token))
    if response.status_code == 200:
        products = response.json()
        product_found = False
        for p in products:
            if p["id"] == product_id:
                product_found = True
                print(f"   Stock après remboursement: {p['stock_qty']}")
                print(f"   Produit actif: {p['active']}")
                if p['stock_qty'] > 0 and p['active']:
                    print("✅ SUCCÈS: Le produit a été automatiquement réactivé via remboursement!")
                else:
                    print("❌ ÉCHEC: Le produit n'a pas été réactivé automatiquement")
                break
        
        if not product_found:
            print("❌ ÉCHEC: Le produit n'apparaît toujours pas dans la liste")
    
    print("\n" + "=" * 60)
    print("🎯 Test de réactivation via remboursement terminé!")
    return True

if __name__ == "__main__":
    print("🚀 Démarrage du test de réactivation via remboursement")
    print("⚠️  Assurez-vous que l'API est démarrée sur http://localhost:8000")
    print("⚠️  Assurez-vous que les données d'exemple sont initialisées")
    print()
    
    # Attendre un peu pour que l'utilisateur puisse lire
    time.sleep(2)
    
    try:
        test_reactivation_refund()
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
