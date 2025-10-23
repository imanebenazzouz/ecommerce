#!/usr/bin/env python3
"""
Test de la fonctionnalité d'inactivation automatique des produits
quand le stock devient 0 après une commande.
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

def test_auto_inactive():
    """Test de l'inactivation automatique"""
    print("🧪 Test de l'inactivation automatique des produits")
    print("=" * 60)
    
    # 1. Connexion admin
    print("1. Connexion admin...")
    admin_token = login(ADMIN_EMAIL, ADMIN_PASSWORD)
    if not admin_token:
        return False
    
    # 2. Créer un produit avec stock limité
    print("2. Création d'un produit avec stock limité...")
    product_data = {
        "name": "Produit Test Stock",
        "description": "Produit pour tester l'inactivation automatique",
        "price_cents": 1000,  # 10€
        "stock_qty": 2,  # Stock limité à 2
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
    
    # 4. Ajouter le produit au panier (quantité 1)
    print("4. Ajout du produit au panier (quantité 1)...")
    response = requests.post(
        f"{BASE_URL}/cart/add",
        json={"product_id": product_id, "qty": 1},
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur ajout panier: {response.text}")
        return False
    
    print("✅ Produit ajouté au panier")
    
    # 5. Vérifier le stock avant commande
    print("5. Vérification du stock avant commande...")
    response = requests.get(f"{BASE_URL}/products", headers=get_headers(client_token))
    if response.status_code == 200:
        products = response.json()
        for p in products:
            if p["id"] == product_id:
                print(f"   Stock avant commande: {p['stock_qty']}")
                break
    
    # 6. Passer la commande
    print("6. Passage de la commande...")
    response = requests.post(
        f"{BASE_URL}/orders/checkout",
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur checkout: {response.text}")
        return False
    
    order = response.json()
    print(f"✅ Commande créée: {order['order_id']}")
    
    # 7. Vérifier le stock après commande
    print("7. Vérification du stock après commande...")
    response = requests.get(f"{BASE_URL}/products", headers=get_headers(client_token))
    if response.status_code == 200:
        products = response.json()
        for p in products:
            if p["id"] == product_id:
                print(f"   Stock après commande: {p['stock_qty']}")
                print(f"   Produit actif: {p['active']}")
                break
    
    # 8. Ajouter le même produit au panier (quantité 1) - devrait épuiser le stock
    print("8. Ajout du même produit au panier (quantité 1) - devrait épuiser le stock...")
    response = requests.post(
        f"{BASE_URL}/cart/add",
        json={"product_id": product_id, "qty": 1},
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur ajout panier: {response.text}")
        return False
    
    print("✅ Produit ajouté au panier")
    
    # 9. Passer la deuxième commande (devrait épuiser le stock)
    print("9. Passage de la deuxième commande (devrait épuiser le stock)...")
    response = requests.post(
        f"{BASE_URL}/orders/checkout",
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur checkout: {response.text}")
        return False
    
    order2 = response.json()
    print(f"✅ Deuxième commande créée: {order2['order_id']}")
    
    # 10. Vérifier que le produit est maintenant inactif
    print("10. Vérification que le produit est maintenant inactif...")
    response = requests.get(f"{BASE_URL}/products", headers=get_headers(client_token))
    if response.status_code == 200:
        products = response.json()
        product_found = False
        for p in products:
            if p["id"] == product_id:
                product_found = True
                print(f"   Stock final: {p['stock_qty']}")
                print(f"   Produit actif: {p['active']}")
                if p['stock_qty'] == 0 and not p['active']:
                    print("✅ SUCCÈS: Le produit a été automatiquement inactivé!")
                else:
                    print("❌ ÉCHEC: Le produit n'a pas été inactivé automatiquement")
                break
        
        if not product_found:
            print("❌ ÉCHEC: Le produit n'apparaît plus dans la liste (inactivé)")
    
    # 11. Test de réactivation via annulation de commande
    print("11. Test de réactivation via annulation de commande...")
    response = requests.post(
        f"{BASE_URL}/orders/{order2['order_id']}/cancel",
        headers=get_headers(client_token)
    )
    
    if response.status_code == 200:
        print("✅ Commande annulée")
        
        # Vérifier que le produit est réactivé
        response = requests.get(f"{BASE_URL}/products", headers=get_headers(client_token))
        if response.status_code == 200:
            products = response.json()
            for p in products:
                if p["id"] == product_id:
                    print(f"   Stock après annulation: {p['stock_qty']}")
                    print(f"   Produit actif: {p['active']}")
                    if p['stock_qty'] > 0 and p['active']:
                        print("✅ SUCCÈS: Le produit a été automatiquement réactivé!")
                    else:
                        print("❌ ÉCHEC: Le produit n'a pas été réactivé automatiquement")
                    break
    
    print("\n" + "=" * 60)
    print("🎯 Test terminé!")
    return True

if __name__ == "__main__":
    print("🚀 Démarrage du test d'inactivation automatique")
    print("⚠️  Assurez-vous que l'API est démarrée sur http://localhost:8000")
    print("⚠️  Assurez-vous que les données d'exemple sont initialisées")
    print()
    
    # Attendre un peu pour que l'utilisateur puisse lire
    time.sleep(2)
    
    try:
        test_auto_inactive()
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
