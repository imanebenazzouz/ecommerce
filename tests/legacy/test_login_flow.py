#!/usr/bin/env python3
"""
Test du flux de connexion complet pour identifier les problèmes de "load failed"
"""

import requests
import json
import time

def test_login_flow():
    """Test du flux de connexion complet"""
    print("🔐 Test du flux de connexion complet")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Vérifier que l'API est accessible
    print("\n1. Test de connectivité API...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ API accessible")
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    
    # Test 2: Login admin
    print("\n2. Test login admin...")
    admin_token = None
    try:
        response = requests.post(f"{base_url}/auth/login", 
                               json={'email': 'admin@example.com', 'password': 'admin'})
        if response.status_code == 200:
            admin_data = response.json()
            admin_token = admin_data.get('token')
            print("✅ Login admin réussi")
            print(f"   - Token: {admin_token[:20]}...")
        else:
            print(f"❌ Erreur login admin: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur login admin: {e}")
        return False
    
    # Test 3: Vérifier les données admin
    print("\n3. Test /auth/me pour admin...")
    try:
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = requests.get(f"{base_url}/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Données admin récupérées")
            print(f"   - Email: {user_data.get('email')}")
            print(f"   - Admin: {user_data.get('is_admin')}")
        else:
            print(f"❌ Erreur /auth/me admin: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur /auth/me admin: {e}")
        return False
    
    # Test 4: Test des produits (endpoint public)
    print("\n4. Test des produits...")
    try:
        response = requests.get(f"{base_url}/products")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits récupérés")
            if len(products) > 0:
                print(f"   - Premier produit: {products[0].get('name', 'N/A')}")
        else:
            print(f"❌ Erreur produits: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur produits: {e}")
        return False
    
    # Test 5: Test du panier (avec authentification)
    print("\n5. Test du panier admin...")
    try:
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = requests.get(f"{base_url}/cart", headers=headers)
        if response.status_code == 200:
            cart = response.json()
            print("✅ Panier accessible")
            print(f"   - Items: {len(cart.get('items', {}))}")
        else:
            print(f"❌ Erreur panier: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur panier: {e}")
        return False
    
    # Test 6: Test des commandes admin
    print("\n6. Test des commandes admin...")
    try:
        headers = {'Authorization': f'Bearer {admin_token}'}
        response = requests.get(f"{base_url}/admin/orders", headers=headers)
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ {len(orders)} commandes récupérées (admin)")
        else:
            print(f"❌ Erreur commandes admin: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur commandes admin: {e}")
        return False
    
    # Test 7: Test de performance (plusieurs requêtes rapides)
    print("\n7. Test de performance...")
    try:
        headers = {'Authorization': f'Bearer {admin_token}'}
        start_time = time.time()
        
        # Faire plusieurs requêtes en parallèle
        import concurrent.futures
        
        def make_request(endpoint):
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
                return response.status_code == 200
            except:
                return False
        
        endpoints = ['/auth/me', '/cart', '/admin/orders', '/products']
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(make_request, endpoints))
        
        end_time = time.time()
        success_count = sum(results)
        
        print(f"✅ {success_count}/{len(endpoints)} requêtes réussies en {end_time - start_time:.2f}s")
        
        if success_count < len(endpoints):
            print("⚠️ Certaines requêtes ont échoué - possible cause du 'load failed'")
        
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test du flux de connexion terminé !")
    return True

if __name__ == "__main__":
    test_login_flow()
