#!/usr/bin/env python3
"""
Test complet de l'authentification
"""

import requests
import json

def test_auth_flow():
    """Test complet du flux d'authentification"""
    base_url = "http://localhost:8000"
    
    print("🔐 Test du flux d'authentification complet")
    print("=" * 50)
    
    # 1. Test de connexion
    print("1️⃣ Test de connexion...")
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print(f"   ✅ Token reçu: {token[:10]}...")
        
        # 2. Test de l'endpoint /auth/me avec le token
        print("\n2️⃣ Test de l'endpoint /auth/me...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{base_url}/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Utilisateur: {user_data['first_name']} {user_data['last_name']}")
            print(f"   📧 Email: {user_data['email']}")
        else:
            print(f"   ❌ Erreur: {response.text}")
            
        # 3. Test des produits
        print("\n3️⃣ Test des produits...")
        response = requests.get(f"{base_url}/products")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            products = response.json()
            print(f"   ✅ {len(products)} produits disponibles")
            for product in products[:3]:  # Afficher les 3 premiers
                print(f"      - {product['name']}: {product['price_cents']/100:.2f}€")
        else:
            print(f"   ❌ Erreur: {response.text}")
            
        # 4. Test du panier
        print("\n4️⃣ Test du panier...")
        response = requests.get(f"{base_url}/cart", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            cart = response.json()
            print(f"   ✅ Panier: {len(cart.get('items', []))} articles")
        else:
            print(f"   ❌ Erreur: {response.text}")
            
    else:
        print(f"   ❌ Erreur de connexion: {response.text}")
        return False
        
    print("\n🎉 Test d'authentification terminé!")
    return True

if __name__ == "__main__":
    test_auth_flow()