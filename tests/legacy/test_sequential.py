#!/usr/bin/env python3
"""
Test séquentiel pour éviter les problèmes de concurrence
"""

import requests
import json
import time

def test_sequential():
    """Test séquentiel des requêtes"""
    print("🔄 Test séquentiel des requêtes")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Login d'abord
    print("\n1. Login...")
    try:
        response = requests.post(f"{base_url}/auth/login", 
                               json={'email': 'admin@example.com', 'password': 'admin'})
        if response.status_code == 200:
            admin_data = response.json()
            admin_token = admin_data.get('token')
            print(f"✅ Login réussi, token: {admin_token[:20]}...")
        else:
            print(f"❌ Erreur login: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Erreur login: {e}")
        return
    
    headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test séquentiel des endpoints
    print("\n2. Test séquentiel des endpoints...")
    endpoints = [
        ('/auth/me', 'Données utilisateur'),
        ('/cart', 'Panier'),
        ('/admin/orders', 'Commandes admin'),
        ('/products', 'Produits'),
        ('/orders', 'Commandes utilisateur')
    ]
    
    success_count = 0
    total_time = 0
    
    for endpoint, description in endpoints:
        print(f"\n   Test {description} ({endpoint})...")
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            end_time = time.time()
            
            request_time = end_time - start_time
            total_time += request_time
            
            print(f"   Status: {response.status_code}")
            print(f"   Temps: {request_time:.3f}s")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ {len(data)} éléments récupérés")
                elif isinstance(data, dict):
                    print(f"   ✅ Données récupérées: {list(data.keys())}")
                else:
                    print(f"   ✅ Données récupérées: {type(data)}")
                success_count += 1
            else:
                print(f"   ❌ Erreur: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout pour {endpoint}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    print(f"\n3. Résumé:")
    print(f"   ✅ {success_count}/{len(endpoints)} requêtes réussies")
    print(f"   ⏱️ Temps total: {total_time:.3f}s")
    print(f"   📊 Temps moyen: {total_time/len(endpoints):.3f}s")
    
    if success_count == len(endpoints):
        print("\n🎉 Toutes les requêtes séquentielles réussissent !")
        print("   Le problème 'load failed' vient probablement des requêtes en parallèle.")
        print("   Solution: Éviter les requêtes simultanées dans le frontend.")
    else:
        print(f"\n⚠️ {len(endpoints) - success_count} requêtes échouent encore")

if __name__ == "__main__":
    test_sequential()
