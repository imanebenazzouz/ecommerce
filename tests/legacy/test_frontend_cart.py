#!/usr/bin/env python3
"""
Test du frontend pour vérifier les erreurs de panier
"""

import requests
import json
import time

def test_frontend_cart():
    """Test du frontend pour le panier"""
    print("🛒 Test du frontend - Panier")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    frontend_url = "http://localhost:5173"
    
    # Test 1: Vérifier que le frontend est accessible
    print("\n1. Vérification du frontend...")
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible")
        else:
            print(f"❌ Frontend non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur frontend: {e}")
        return False
    
    # Test 2: Vérifier que l'API est accessible
    print("\n2. Vérification de l'API...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ API accessible")
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False
    
    # Test 3: Test de login via API
    print("\n3. Test de login...")
    try:
        response = requests.post(f"{base_url}/auth/login", 
                               json={'email': 'admin@example.com', 'password': 'admin'})
        if response.status_code == 200:
            admin_data = response.json()
            admin_token = admin_data.get('token')
            print("✅ Login réussi")
            print(f"   - Token: {admin_token[:20]}...")
        else:
            print(f"❌ Erreur login: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur login: {e}")
        return False
    
    # Test 4: Test des endpoints de panier
    print("\n4. Test des endpoints de panier...")
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    endpoints = [
        ('/cart', 'GET', 'Récupération du panier'),
        ('/products', 'GET', 'Récupération des produits'),
        ('/cart/add', 'POST', 'Ajout au panier'),
        ('/cart/remove', 'POST', 'Retrait du panier')
    ]
    
    for endpoint, method, description in endpoints:
        print(f"   Test {description}...")
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
            elif method == 'POST':
                if endpoint == '/cart/add':
                    # Récupérer un produit d'abord
                    products_response = requests.get(f"{base_url}/products", headers=headers)
                    if products_response.status_code == 200:
                        products = products_response.json()
                        if products:
                            product_id = products[0]['id']
                            data = {"product_id": product_id, "qty": 1}
                        else:
                            print(f"   ⚠️ Aucun produit disponible")
                            continue
                    else:
                        print(f"   ❌ Erreur récupération produits")
                        continue
                elif endpoint == '/cart/remove':
                    # Récupérer le panier d'abord
                    cart_response = requests.get(f"{base_url}/cart", headers=headers)
                    if cart_response.status_code == 200:
                        cart = cart_response.json()
                        if cart.get('items'):
                            # Prendre le premier article
                            item_id = list(cart['items'].keys())[0]
                            data = {"product_id": item_id, "qty": 1}
                        else:
                            print(f"   ⚠️ Panier vide, retrait ignoré")
                            continue
                    else:
                        print(f"   ❌ Erreur récupération panier")
                        continue
                else:
                    data = {}
                
                response = requests.post(f"{base_url}{endpoint}", 
                                       json=data, headers=headers, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ {description} réussi")
            else:
                print(f"   ❌ {description} échoué: {response.status_code} - {response.text}")
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout pour {description}")
        except Exception as e:
            print(f"   ❌ Erreur {description}: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test du frontend terminé !")
    print("\n📋 Instructions pour tester manuellement :")
    print("1. Ouvrez http://localhost:5173 dans votre navigateur")
    print("2. Connectez-vous avec admin@example.com / admin")
    print("3. Allez sur la page Panier")
    print("4. Ajoutez des articles au panier")
    print("5. Vérifiez qu'il n'y a pas d'erreurs dans la console (F12)")
    return True

if __name__ == "__main__":
    test_frontend_cart()
