#!/usr/bin/env python3
"""
Script de test complet de l'API
"""

import requests
import json
import time
import sys

def test_api_health():
    """Teste l'endpoint de santé"""
    print("🔍 Test de l'endpoint de santé...")
    try:
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint de santé OK")
            return True
        else:
            print(f"❌ Endpoint de santé échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur endpoint de santé: {e}")
        return False

def test_products_endpoint():
    """Teste l'endpoint des produits"""
    print("\n🔍 Test de l'endpoint des produits...")
    try:
        response = requests.get('http://localhost:8000/products', timeout=5)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Endpoint produits OK - {len(products)} produits trouvés")
            if products:
                print(f"   Premier produit: {products[0]['name']} - {products[0]['price_cents']/100:.2f}€")
            return True
        else:
            print(f"❌ Endpoint produits échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur endpoint produits: {e}")
        return False

def test_init_data_endpoint():
    """Teste l'endpoint d'initialisation des données"""
    print("\n🔍 Test de l'endpoint d'initialisation...")
    try:
        response = requests.post('http://localhost:8000/init-data', timeout=10)
        if response.status_code == 200:
            print("✅ Endpoint d'initialisation OK")
            return True
        else:
            print(f"❌ Endpoint d'initialisation échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur endpoint d'initialisation: {e}")
        return False

def test_auth_endpoints():
    """Teste les endpoints d'authentification"""
    print("\n🔍 Test des endpoints d'authentification...")
    
    # Test d'inscription
    try:
        register_data = {
            "email": "test@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "address": "123 Test Street"
        }
        response = requests.post('http://localhost:8000/auth/register', json=register_data, timeout=5)
        if response.status_code == 200:
            print("✅ Endpoint d'inscription OK")
        else:
            print(f"❌ Endpoint d'inscription échoué: {response.status_code}")
            print(f"   Réponse: {response.text}")
    except Exception as e:
        print(f"❌ Erreur endpoint d'inscription: {e}")
    
    # Test de connexion
    try:
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        response = requests.post('http://localhost:8000/auth/login', json=login_data, timeout=5)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Endpoint de connexion OK")
            return token_data.get('token')
        else:
            print(f"❌ Endpoint de connexion échoué: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erreur endpoint de connexion: {e}")
        return None

def test_protected_endpoints(token):
    """Teste les endpoints protégés"""
    if not token:
        print("\n❌ Pas de token, impossible de tester les endpoints protégés")
        return False
    
    print(f"\n🔍 Test des endpoints protégés avec token: {token[:20]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test du profil utilisateur
    try:
        response = requests.get('http://localhost:8000/auth/me', headers=headers, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Endpoint profil utilisateur OK")
            print(f"   Utilisateur: {user_data['first_name']} {user_data['last_name']}")
        else:
            print(f"❌ Endpoint profil utilisateur échoué: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur endpoint profil utilisateur: {e}")
    
    # Test du panier
    try:
        response = requests.get('http://localhost:8000/cart', headers=headers, timeout=5)
        if response.status_code == 200:
            cart_data = response.json()
            print("✅ Endpoint panier OK")
            print(f"   Panier: {len(cart_data['items'])} articles")
        else:
            print(f"❌ Endpoint panier échoué: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur endpoint panier: {e}")
    
    # Test des commandes
    try:
        response = requests.get('http://localhost:8000/orders', headers=headers, timeout=5)
        if response.status_code == 200:
            orders_data = response.json()
            print("✅ Endpoint commandes OK")
            print(f"   Commandes: {len(orders_data)} commandes")
        else:
            print(f"❌ Endpoint commandes échoué: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur endpoint commandes: {e}")

def test_admin_endpoints():
    """Teste les endpoints d'administration"""
    print("\n🔍 Test des endpoints d'administration...")
    
    # Test de connexion admin
    try:
        admin_login_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        response = requests.post('http://localhost:8000/auth/login', json=admin_login_data, timeout=5)
        if response.status_code == 200:
            admin_token = response.json().get('token')
            print("✅ Connexion admin OK")
            
            headers = {"Authorization": f"Bearer {admin_token}"}
            
            # Test des produits admin
            response = requests.get('http://localhost:8000/admin/products', headers=headers, timeout=5)
            if response.status_code == 200:
                products = response.json()
                print(f"✅ Endpoint produits admin OK - {len(products)} produits")
            else:
                print(f"❌ Endpoint produits admin échoué: {response.status_code}")
            
            # Test des commandes admin
            response = requests.get('http://localhost:8000/admin/orders', headers=headers, timeout=5)
            if response.status_code == 200:
                orders = response.json()
                print(f"✅ Endpoint commandes admin OK - {len(orders)} commandes")
            else:
                print(f"❌ Endpoint commandes admin échoué: {response.status_code}")
                
        else:
            print(f"❌ Connexion admin échouée: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur endpoints admin: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test complet de l'API e-commerce")
    print("=" * 60)
    
    # Attendre que le serveur soit prêt
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(2)
    
    # Test de santé
    if not test_api_health():
        print("\n❌ L'API n'est pas accessible. Vérifiez que le serveur est démarré.")
        return
    
    # Test d'initialisation des données
    test_init_data_endpoint()
    
    # Test des produits
    test_products_endpoint()
    
    # Test de l'authentification
    token = test_auth_endpoints()
    
    # Test des endpoints protégés
    test_protected_endpoints(token)
    
    # Test des endpoints admin
    test_admin_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés!")
    print("🎉 L'API fonctionne correctement")

if __name__ == "__main__":
    main()
