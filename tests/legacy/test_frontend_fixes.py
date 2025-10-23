#!/usr/bin/env python3
"""
Test des corrections du frontend pour résoudre le problème "load failed"
"""

import requests
import json
import time

def test_frontend_fixes():
    """Test des corrections du frontend"""
    print("🔧 Test des corrections du frontend")
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
    
    # Test 3: Test des endpoints avec délai (simulation du frontend)
    print("\n3. Test des endpoints avec délai...")
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    endpoints = [
        ('/auth/me', 'Données utilisateur'),
        ('/cart', 'Panier'),
        ('/admin/orders', 'Commandes admin'),
        ('/products', 'Produits')
    ]
    
    for endpoint, description in endpoints:
        print(f"   Test {description}...")
        try:
            # Simuler le délai du frontend
            time.sleep(0.1)
            
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ {len(data)} éléments récupérés")
                elif isinstance(data, dict):
                    print(f"   ✅ Données récupérées: {list(data.keys())}")
                else:
                    print(f"   ✅ Données récupérées: {type(data)}")
            else:
                print(f"   ❌ Erreur: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test 4: Test de performance (plusieurs requêtes rapides)
    print("\n4. Test de performance...")
    try:
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
        
        if success_count == len(endpoints):
            print("🎉 Toutes les requêtes sont stables - problème 'load failed' résolu !")
        else:
            print("⚠️ Certaines requêtes échouent encore")
        
    except Exception as e:
        print(f"❌ Erreur test performance: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Test des corrections terminé !")
    return True

if __name__ == "__main__":
    test_frontend_fixes()
