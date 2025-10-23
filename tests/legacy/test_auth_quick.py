#!/usr/bin/env python3
"""
Test rapide de l'authentification
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_auth():
    print("🔐 Test de l'authentification")
    print("=" * 40)
    
    # Test connexion admin
    print("1. Test connexion admin...")
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={
            "email": "admin@example.com",
            "password": "admin"
        })
        if response.status_code == 200:
            admin_data = response.json()
            admin_token = admin_data["token"]
            print(f"✅ Admin connecté - Token: {admin_token[:20]}...")
        else:
            print(f"❌ Erreur admin: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur admin: {e}")
        return False
    
    # Test connexion client
    print("2. Test connexion client...")
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={
            "email": "client@example.com",
            "password": "secret"
        })
        if response.status_code == 200:
            client_data = response.json()
            client_token = client_data["token"]
            print(f"✅ Client connecté - Token: {client_token[:20]}...")
        else:
            print(f"❌ Erreur client: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur client: {e}")
        return False
    
    # Test récupération profil admin
    print("3. Test profil admin...")
    try:
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Profil admin: {profile['first_name']} {profile['last_name']} (admin: {profile['is_admin']})")
        else:
            print(f"❌ Erreur profil admin: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur profil admin: {e}")
        return False
    
    # Test récupération profil client
    print("4. Test profil client...")
    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{API_BASE}/auth/me", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print(f"✅ Profil client: {profile['first_name']} {profile['last_name']} (admin: {profile['is_admin']})")
        else:
            print(f"❌ Erreur profil client: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur profil client: {e}")
        return False
    
    # Test produits
    print("5. Test récupération produits...")
    try:
        response = requests.get(f"{API_BASE}/products")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits récupérés")
        else:
            print(f"❌ Erreur produits: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur produits: {e}")
        return False
    
    print("\n🎉 Tous les tests d'authentification sont passés !")
    print("\n🌐 URLs disponibles:")
    print("   Frontend: http://localhost:5173")
    print("   Backend: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("\n👤 Comptes de test:")
    print("   Admin: admin@example.com / admin")
    print("   Client: client@example.com / secret")
    
    return True

if __name__ == "__main__":
    test_auth()
