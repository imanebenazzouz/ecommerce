#!/usr/bin/env python3
"""
Test du remboursement automatique lors de l'annulation d'une commande payée.
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

def test_auto_refund_cancel():
    """Test du remboursement automatique lors de l'annulation"""
    print("🧪 Test du remboursement automatique lors de l'annulation")
    print("=" * 70)
    
    # 1. Connexion client
    print("1. Connexion client...")
    client_token = login(CLIENT_EMAIL, CLIENT_PASSWORD)
    if not client_token:
        return False
    
    # 2. Créer un produit avec stock limité
    print("2. Création d'un produit avec stock limité...")
    product_data = {
        "name": "Produit Test Remboursement Auto",
        "description": "Produit pour tester le remboursement automatique",
        "price_cents": 2500,  # 25€
        "stock_qty": 1,  # Stock limité à 1
        "active": True
    }
    
    response = requests.post(
        f"{BASE_URL}/admin/products",
        json=product_data,
        headers=get_headers(client_token)
    )
    
    if response.status_code != 201:
        print(f"❌ Erreur création produit: {response.text}")
        return False
    
    product = response.json()
    product_id = product["id"]
    print(f"✅ Produit créé: {product['name']} (Prix: {product['price_cents']/100:.2f}€, Stock: {product['stock_qty']})")
    
    # 3. Ajouter le produit au panier
    print("3. Ajout du produit au panier...")
    response = requests.post(
        f"{BASE_URL}/cart/add",
        json={"product_id": product_id, "qty": 1},
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur ajout panier: {response.text}")
        return False
    
    print("✅ Produit ajouté au panier")
    
    # 4. Passer la commande
    print("4. Passage de la commande...")
    response = requests.post(
        f"{BASE_URL}/orders/checkout",
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur checkout: {response.text}")
        return False
    
    order = response.json()
    order_id = order["order_id"]
    print(f"✅ Commande créée: {order_id}")
    print(f"   Montant total: {order['total_cents']/100:.2f}€")
    
    # 5. Payer la commande
    print("5. Paiement de la commande...")
    payment_data = {
        "card_number": "4242424242424242",
        "exp_month": 12,
        "exp_year": 2025,
        "cvc": "123"
    }
    
    response = requests.post(
        f"{BASE_URL}/orders/{order_id}/pay",
        json=payment_data,
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur paiement: {response.text}")
        return False
    
    payment_result = response.json()
    print(f"✅ Commande payée: {payment_result['payment_id']}")
    print(f"   Montant payé: {payment_result['amount_cents']/100:.2f}€")
    
    # 6. Vérifier le statut de la commande avant annulation
    print("6. Vérification du statut de la commande avant annulation...")
    response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=get_headers(client_token))
    if response.status_code == 200:
        order_info = response.json()
        print(f"   Statut avant annulation: {order_info['status']}")
    
    # 7. Annuler la commande (devrait déclencher le remboursement automatique)
    print("7. Annulation de la commande (remboursement automatique)...")
    response = requests.post(
        f"{BASE_URL}/orders/{order_id}/cancel",
        headers=get_headers(client_token)
    )
    
    if response.status_code != 200:
        print(f"❌ Erreur annulation: {response.text}")
        return False
    
    cancel_result = response.json()
    print(f"✅ Commande annulée: {cancel_result['message']}")
    
    # Vérifier les informations de remboursement
    if cancel_result.get('refunded'):
        print(f"💰 Remboursement automatique effectué!")
        print(f"   Montant remboursé: {cancel_result['amount_cents']/100:.2f}€")
        print(f"   Message: {cancel_result['message']}")
    else:
        print("ℹ️  Aucun remboursement nécessaire (commande non payée)")
    
    # 8. Vérifier le statut de la commande après annulation
    print("8. Vérification du statut de la commande après annulation...")
    response = requests.get(f"{BASE_URL}/orders/{order_id}", headers=get_headers(client_token))
    if response.status_code == 200:
        order_info = response.json()
        print(f"   Statut après annulation: {order_info['status']}")
    
    # 9. Vérifier que le produit est réactivé (stock restauré)
    print("9. Vérification que le produit est réactivé...")
    response = requests.get(f"{BASE_URL}/products", headers=get_headers(client_token))
    if response.status_code == 200:
        products = response.json()
        for p in products:
            if p["id"] == product_id:
                print(f"   Stock après annulation: {p['stock_qty']}")
                print(f"   Produit actif: {p['active']}")
                if p['stock_qty'] > 0 and p['active']:
                    print("✅ SUCCÈS: Le produit a été réactivé et le stock restauré!")
                else:
                    print("❌ ÉCHEC: Le produit n'a pas été réactivé correctement")
                break
    
    # 10. Test avec une commande non payée (pas de remboursement)
    print("\n10. Test avec une commande non payée (pas de remboursement)...")
    
    # Créer une nouvelle commande
    response = requests.post(
        f"{BASE_URL}/cart/add",
        json={"product_id": product_id, "qty": 1},
        headers=get_headers(client_token)
    )
    
    if response.status_code == 200:
        print("✅ Produit ajouté au panier")
        
        # Passer la commande
        response = requests.post(
            f"{BASE_URL}/orders/checkout",
            headers=get_headers(client_token)
        )
        
        if response.status_code == 200:
            order2 = response.json()
            order2_id = order2["order_id"]
            print(f"✅ Deuxième commande créée: {order2_id}")
            
            # Annuler sans payer (pas de remboursement)
            response = requests.post(
                f"{BASE_URL}/orders/{order2_id}/cancel",
                headers=get_headers(client_token)
            )
            
            if response.status_code == 200:
                cancel_result2 = response.json()
                print(f"✅ Commande non payée annulée: {cancel_result2['message']}")
                
                if not cancel_result2.get('refunded'):
                    print("✅ SUCCÈS: Aucun remboursement pour une commande non payée!")
                else:
                    print("❌ ÉCHEC: Remboursement inattendu pour une commande non payée")
    
    print("\n" + "=" * 70)
    print("🎯 Test de remboursement automatique terminé!")
    return True

if __name__ == "__main__":
    print("🚀 Démarrage du test de remboursement automatique")
    print("⚠️  Assurez-vous que l'API est démarrée sur http://localhost:8000")
    print("⚠️  Assurez-vous que les données d'exemple sont initialisées")
    print()
    
    # Attendre un peu pour que l'utilisateur puisse lire
    time.sleep(2)
    
    try:
        test_auto_refund_cancel()
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
