#!/usr/bin/env python3
"""
Test simple du remboursement automatique lors de l'annulation.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_simple_refund():
    """Test simple du remboursement automatique"""
    print("🧪 Test simple du remboursement automatique")
    print("=" * 50)
    
    # 1. Connexion client
    print("1. Connexion client...")
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "client@example.com",
        "password": "secret"
    })
    
    if response.status_code != 200:
        print(f"❌ Erreur de connexion: {response.text}")
        return False
    
    client_token = response.json()["token"]
    headers = {"Authorization": f"Bearer {client_token}"}
    print("✅ Connexion réussie")
    
    # 2. Créer un produit
    print("2. Création d'un produit...")
    product_data = {
        "name": "Test Remboursement",
        "description": "Produit test",
        "price_cents": 1500,  # 15€
        "stock_qty": 1,
        "active": True
    }
    
    response = requests.post(f"{BASE_URL}/admin/products", json=product_data, headers=headers)
    if response.status_code != 201:
        print(f"❌ Erreur création produit: {response.text}")
        return False
    
    product = response.json()
    product_id = product["id"]
    print(f"✅ Produit créé: {product['name']} ({product['price_cents']/100:.2f}€)")
    
    # 3. Ajouter au panier et commander
    print("3. Ajout au panier et commande...")
    response = requests.post(f"{BASE_URL}/cart/add", json={"product_id": product_id, "qty": 1}, headers=headers)
    if response.status_code != 200:
        print(f"❌ Erreur ajout panier: {response.text}")
        return False
    
    response = requests.post(f"{BASE_URL}/orders/checkout", headers=headers)
    if response.status_code != 200:
        print(f"❌ Erreur checkout: {response.text}")
        return False
    
    order = response.json()
    order_id = order["order_id"]
    print(f"✅ Commande créée: {order_id}")
    
    # 4. Payer la commande
    print("4. Paiement de la commande...")
    payment_data = {
        "card_number": "4242424242424242",
        "exp_month": 12,
        "exp_year": 2025,
        "cvc": "123"
    }
    
    response = requests.post(f"{BASE_URL}/orders/{order_id}/pay", json=payment_data, headers=headers)
    if response.status_code != 200:
        print(f"❌ Erreur paiement: {response.text}")
        return False
    
    payment_result = response.json()
    print(f"✅ Commande payée: {payment_result['amount_cents']/100:.2f}€")
    
    # 5. Annuler la commande (remboursement automatique)
    print("5. Annulation avec remboursement automatique...")
    response = requests.post(f"{BASE_URL}/orders/{order_id}/cancel", headers=headers)
    if response.status_code != 200:
        print(f"❌ Erreur annulation: {response.text}")
        return False
    
    cancel_result = response.json()
    print(f"✅ Annulation réussie: {cancel_result['message']}")
    
    # Vérifier le remboursement
    if cancel_result.get('refunded'):
        print(f"💰 Remboursement automatique: {cancel_result['amount_cents']/100:.2f}€")
        print("✅ SUCCÈS: Remboursement automatique fonctionne!")
    else:
        print("❌ ÉCHEC: Pas de remboursement automatique")
    
    print("\n🎯 Test terminé!")
    return True

if __name__ == "__main__":
    try:
        test_simple_refund()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
