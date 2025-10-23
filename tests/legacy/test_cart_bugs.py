#!/usr/bin/env python3
"""
Test approfondi pour identifier et corriger tous les bugs du panier
"""

import requests
import json
import time
import concurrent.futures

def test_cart_bugs():
    """Test approfondi du panier pour identifier les bugs"""
    print("🐛 Test approfondi du panier - Recherche de bugs")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Login
    print("\n1. Connexion...")
    try:
        response = requests.post(f"{base_url}/auth/login", 
                               json={'email': 'admin@example.com', 'password': 'admin'})
        if response.status_code == 200:
            admin_data = response.json()
            admin_token = admin_data.get('token')
            print("✅ Connexion réussie")
        else:
            print(f"❌ Erreur connexion: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test 2: Récupérer les produits
    print("\n2. Récupération des produits...")
    try:
        response = requests.get(f"{base_url}/products", headers=headers)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits récupérés")
            if len(products) < 2:
                print("⚠️ Moins de 2 produits disponibles pour les tests")
                return False
        else:
            print(f"❌ Erreur produits: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur produits: {e}")
        return False
    
    # Test 3: Vider le panier initial
    print("\n3. Nettoyage du panier initial...")
    try:
        # Récupérer le panier
        response = requests.get(f"{base_url}/cart", headers=headers)
        if response.status_code == 200:
            cart = response.json()
            # Retirer tous les articles existants
            for item_id in cart.get('items', {}):
                remove_data = {"product_id": item_id, "qty": 999}  # Retirer beaucoup
                requests.post(f"{base_url}/cart/remove", json=remove_data, headers=headers)
            print("✅ Panier nettoyé")
        else:
            print(f"❌ Erreur nettoyage: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur nettoyage: {e}")
    
    # Test 4: Tests de cas limites
    print("\n4. Tests de cas limites...")
    
    # Test 4.1: Ajout d'un produit inexistant
    print("   4.1. Test ajout produit inexistant...")
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        add_data = {"product_id": fake_id, "qty": 1}
        response = requests.post(f"{base_url}/cart/add", json=add_data, headers=headers)
        if response.status_code == 404:
            print("   ✅ Erreur 404 correcte pour produit inexistant")
        else:
            print(f"   ❌ Erreur inattendue: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4.2: Ajout avec quantité négative
    print("   4.2. Test quantité négative...")
    try:
        product_id = products[0]['id']
        add_data = {"product_id": product_id, "qty": -1}
        response = requests.post(f"{base_url}/cart/add", json=add_data, headers=headers)
        if response.status_code == 422:  # Validation error
            print("   ✅ Erreur de validation correcte pour quantité négative")
        else:
            print(f"   ⚠️ Réponse inattendue: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 4.3: Ajout avec quantité 0
    print("   4.3. Test quantité zéro...")
    try:
        add_data = {"product_id": product_id, "qty": 0}
        response = requests.post(f"{base_url}/cart/add", json=add_data, headers=headers)
        if response.status_code == 422:  # Validation error
            print("   ✅ Erreur de validation correcte pour quantité zéro")
        else:
            print(f"   ⚠️ Réponse inattendue: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test 5: Tests de concurrence
    print("\n5. Tests de concurrence...")
    try:
        def add_product_concurrent(product_id, quantity):
            try:
                add_data = {"product_id": product_id, "qty": quantity}
                response = requests.post(f"{base_url}/cart/add", json=add_data, headers=headers)
                return response.status_code == 200
            except:
                return False
        
        # Ajouter le même produit plusieurs fois en parallèle
        product_id = products[0]['id']
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(add_product_concurrent, product_id, 1) for _ in range(3)]
            results = [f.result() for f in futures]
        
        success_count = sum(results)
        print(f"   ✅ {success_count}/3 ajouts concurrents réussis")
        
        # Vérifier le panier après ajouts concurrents
        response = requests.get(f"{base_url}/cart", headers=headers)
        if response.status_code == 200:
            cart = response.json()
            if product_id in cart.get('items', {}):
                quantity = cart['items'][product_id]['quantity']
                print(f"   ✅ Quantité finale: {quantity}")
                if quantity >= 3:
                    print("   ✅ Ajouts concurrents gérés correctement")
                else:
                    print("   ⚠️ Possible perte de données lors d'ajouts concurrents")
            else:
                print("   ❌ Produit perdu après ajouts concurrents")
        else:
            print(f"   ❌ Erreur récupération panier: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur tests concurrence: {e}")
    
    # Test 6: Test de performance
    print("\n6. Test de performance...")
    try:
        start_time = time.time()
        
        # Faire plusieurs opérations de panier
        operations = []
        for i in range(5):
            product_id = products[i % len(products)]['id']
            operations.append(("add", product_id, 1))
        
        for operation, product_id, qty in operations:
            if operation == "add":
                add_data = {"product_id": product_id, "qty": qty}
                requests.post(f"{base_url}/cart/add", json=add_data, headers=headers)
        
        end_time = time.time()
        print(f"   ✅ 5 opérations en {end_time - start_time:.3f}s")
        
        # Vérifier le panier final
        response = requests.get(f"{base_url}/cart", headers=headers)
        if response.status_code == 200:
            cart = response.json()
            total_items = len(cart.get('items', {}))
            print(f"   ✅ Panier final: {total_items} articles différents")
        else:
            print(f"   ❌ Erreur récupération panier final: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur test performance: {e}")
    
    # Test 7: Test de checkout
    print("\n7. Test de checkout...")
    try:
        response = requests.post(f"{base_url}/orders/checkout", headers=headers)
        if response.status_code == 200:
            checkout_data = response.json()
            print("✅ Checkout réussi")
            print(f"   - Order ID: {checkout_data.get('order_id', 'N/A')}")
            print(f"   - Total: {checkout_data.get('total_cents', 0) / 100:.2f} €")
            
            # Vérifier que le panier est vide après checkout
            response = requests.get(f"{base_url}/cart", headers=headers)
            if response.status_code == 200:
                cart = response.json()
                if not cart.get('items'):
                    print("   ✅ Panier vidé après checkout")
                else:
                    print("   ⚠️ Panier non vidé après checkout")
        else:
            print(f"❌ Erreur checkout: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur checkout: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Tests approfondis terminés !")
    print("\n📋 Résumé des tests :")
    print("✅ Gestion des erreurs (produit inexistant, quantités invalides)")
    print("✅ Tests de concurrence")
    print("✅ Tests de performance")
    print("✅ Test de checkout")
    print("\n🔍 Si des bugs sont détectés, ils seront listés ci-dessus.")
    return True

if __name__ == "__main__":
    test_cart_bugs()
