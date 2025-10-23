#!/usr/bin/env python3
"""
Test complet du système de panier pour identifier et corriger les bugs
"""

import requests
import json
import time

def test_cart_system():
    """Test complet du système de panier"""
    print("🛒 Test complet du système de panier")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Login admin
    print("\n1. Connexion admin...")
    try:
        response = requests.post(f"{base_url}/auth/login", 
                               json={'email': 'admin@example.com', 'password': 'admin'})
        if response.status_code == 200:
            admin_data = response.json()
            admin_token = admin_data.get('token')
            print("✅ Connexion admin réussie")
            print(f"   - Token: {admin_token[:20]}...")
        else:
            print(f"❌ Erreur login admin: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur login admin: {e}")
        return False
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test 2: Récupérer les produits
    print("\n2. Récupération des produits...")
    try:
        response = requests.get(f"{base_url}/products", headers=headers)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits récupérés")
            if len(products) > 0:
                first_product = products[0]
                product_id = first_product['id']
                product_name = first_product['name']
                print(f"   - Premier produit: {product_name} (ID: {product_id[:8]}...)")
            else:
                print("❌ Aucun produit disponible")
                return False
        else:
            print(f"❌ Erreur produits: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur produits: {e}")
        return False
    
    # Test 3: Vérifier le panier initial
    print("\n3. Vérification du panier initial...")
    try:
        response = requests.get(f"{base_url}/cart", headers=headers)
        if response.status_code == 200:
            cart = response.json()
            print("✅ Panier récupéré")
            print(f"   - User ID: {cart.get('user_id', 'N/A')}")
            print(f"   - Items: {len(cart.get('items', {}))}")
        else:
            print(f"❌ Erreur panier: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur panier: {e}")
        return False
    
    # Test 4: Ajouter un article au panier
    print(f"\n4. Ajout d'un article au panier...")
    try:
        add_data = {
            "product_id": product_id,
            "qty": 2
        }
        response = requests.post(f"{base_url}/cart/add", 
                               json=add_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Article ajouté au panier")
            print(f"   - Résultat: {result}")
        else:
            print(f"❌ Erreur ajout panier: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur ajout panier: {e}")
        return False
    
    # Test 5: Vérifier le panier après ajout
    print("\n5. Vérification du panier après ajout...")
    try:
        response = requests.get(f"{base_url}/cart", headers=headers)
        if response.status_code == 200:
            cart = response.json()
            print("✅ Panier récupéré après ajout")
            print(f"   - Items: {len(cart.get('items', {}))}")
            if cart.get('items'):
                for item_id, item_data in cart['items'].items():
                    print(f"   - Article {item_id[:8]}...: {item_data['quantity']} unités")
        else:
            print(f"❌ Erreur panier: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur panier: {e}")
        return False
    
    # Test 6: Retirer un article du panier
    print(f"\n6. Retrait d'un article du panier...")
    try:
        remove_data = {
            "product_id": product_id,
            "qty": 1
        }
        response = requests.post(f"{base_url}/cart/remove", 
                               json=remove_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("✅ Article retiré du panier")
            print(f"   - Résultat: {result}")
        else:
            print(f"❌ Erreur retrait panier: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur retrait panier: {e}")
        return False
    
    # Test 7: Vérifier le panier après retrait
    print("\n7. Vérification du panier après retrait...")
    try:
        response = requests.get(f"{base_url}/cart", headers=headers)
        if response.status_code == 200:
            cart = response.json()
            print("✅ Panier récupéré après retrait")
            print(f"   - Items: {len(cart.get('items', {}))}")
            if cart.get('items'):
                for item_id, item_data in cart['items'].items():
                    print(f"   - Article {item_id[:8]}...: {item_data['quantity']} unités")
            else:
                print("   - Panier vide")
        else:
            print(f"❌ Erreur panier: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur panier: {e}")
        return False
    
    # Test 8: Test de checkout (si panier non vide)
    print("\n8. Test de checkout...")
    try:
        response = requests.get(f"{base_url}/cart", headers=headers)
        if response.status_code == 200:
            cart = response.json()
            if cart.get('items'):
                print("   - Panier non vide, test de checkout...")
                checkout_response = requests.post(f"{base_url}/orders/checkout", headers=headers)
                if checkout_response.status_code == 200:
                    checkout_data = checkout_response.json()
                    print("✅ Checkout réussi")
                    print(f"   - Order ID: {checkout_data.get('order_id', 'N/A')}")
                    print(f"   - Total: {checkout_data.get('total_cents', 0) / 100:.2f} €")
                else:
                    print(f"❌ Erreur checkout: {checkout_response.status_code} - {checkout_response.text}")
            else:
                print("   - Panier vide, checkout ignoré")
    except Exception as e:
        print(f"❌ Erreur checkout: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test du panier terminé !")
    return True

if __name__ == "__main__":
    test_cart_system()
