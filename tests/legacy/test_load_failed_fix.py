#!/usr/bin/env python3
"""
Test pour vérifier que les corrections du problème "Load failed" fonctionnent
"""
import requests
import json
import time

def test_backend_endpoints():
    """Test des endpoints du backend"""
    base_url = "http://localhost:8000"
    
    print("🔍 Test des endpoints backend...")
    
    # Test de l'endpoint de santé
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ /health - OK")
        else:
            print(f"❌ /health - Erreur {response.status_code}")
    except Exception as e:
        print(f"❌ /health - Erreur: {e}")
    
    # Test de l'endpoint racine
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ / - OK")
        else:
            print(f"❌ / - Erreur {response.status_code}")
    except Exception as e:
        print(f"❌ / - Erreur: {e}")
    
    # Test de l'endpoint des produits
    try:
        response = requests.get(f"{base_url}/products", timeout=5)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ /products - OK ({len(products)} produits)")
        else:
            print(f"❌ /products - Erreur {response.status_code}")
    except Exception as e:
        print(f"❌ /products - Erreur: {e}")

def test_authentication():
    """Test de l'authentification"""
    base_url = "http://localhost:8000"
    
    print("\n🔐 Test de l'authentification...")
    
    # Test de connexion
    try:
        login_data = {
            "email": "admin@example.com",
            "password": "admin"
        }
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("token")
            print("✅ /auth/login - OK")
            
            # Test de l'endpoint /auth/me
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(f"{base_url}/auth/me", headers=headers, timeout=5)
            if me_response.status_code == 200:
                user_data = me_response.json()
                print(f"✅ /auth/me - OK (utilisateur: {user_data.get('email')})")
            else:
                print(f"❌ /auth/me - Erreur {me_response.status_code}")
        else:
            print(f"❌ /auth/login - Erreur {response.status_code}")
    except Exception as e:
        print(f"❌ Authentification - Erreur: {e}")

def test_frontend_connectivity():
    """Test de la connectivité frontend"""
    print("\n🌐 Test de la connectivité frontend...")
    
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible")
        else:
            print(f"❌ Frontend - Erreur {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend - Erreur: {e}")

def test_concurrent_requests():
    """Test de requêtes concurrentes pour détecter les problèmes de timing"""
    print("\n⚡ Test de requêtes concurrentes...")
    
    base_url = "http://localhost:8000"
    
    # Test de plusieurs requêtes simultanées
    import concurrent.futures
    
    def make_request(url):
        try:
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    urls = [f"{base_url}/products" for _ in range(5)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(make_request, urls))
    
    success_count = sum(results)
    print(f"✅ Requêtes concurrentes: {success_count}/5 réussies")
    
    if success_count < 5:
        print("⚠️  Problème potentiel de concurrence détecté")

def main():
    """Fonction principale de test"""
    print("🚀 Test des corrections du problème 'Load failed'")
    print("=" * 50)
    
    test_backend_endpoints()
    test_authentication()
    test_frontend_connectivity()
    test_concurrent_requests()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés")
    print("\n📋 Instructions pour tester manuellement:")
    print("1. Ouvrez http://localhost:5173 dans votre navigateur")
    print("2. Connectez-vous avec admin@example.com / admin")
    print("3. Vérifiez que la page se charge sans 'Load failed'")
    print("4. Testez l'ajout d'articles au panier")
    print("5. Vérifiez la console du navigateur (F12) pour les erreurs")

if __name__ == "__main__":
    main()
