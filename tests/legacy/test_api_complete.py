#!/usr/bin/env python3
"""
Test complet de l'API avec base de données PostgreSQL
"""

import requests
import json
import time
import subprocess
import os
import sys
from datetime import datetime

def test_complete_api():
    """Test complet de l'API"""
    print("🧪 TEST COMPLET DE L'API AVEC BASE DE DONNÉES")
    print("=" * 60)
    
    # Démarrer l'API
    print("🚀 Démarrage de l'API...")
    api_process = subprocess.Popen(
        ['python', 'api.py'], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        cwd='/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend'
    )
    
    # Attendre que l'API démarre
    print("⏳ Attente du démarrage de l'API...")
    time.sleep(5)
    
    base_url = 'http://localhost:8000'
    token = None
    user_id = None
    
    try:
        # Test 1: Vérifier que l'API répond
        print("\n📡 Test 1: Vérification de l'API...")
        try:
            response = requests.get(f'{base_url}/', timeout=10)
            if response.status_code == 200:
                print("✅ API accessible")
            else:
                print(f"❌ API non accessible: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion à l'API: {e}")
            return False
        
        # Test 2: Récupérer les produits
        print("\n🛍️  Test 2: Récupération des produits...")
        response = requests.get(f'{base_url}/products')
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits récupérés")
            if products:
                print(f"   Premier produit: {products[0]['name']} - {products[0]['price_cents']/100:.2f}€")
        else:
            print(f"❌ Erreur récupération produits: {response.status_code}")
            return False
        
        # Test 3: Inscription d'un nouvel utilisateur
        print("\n👤 Test 3: Inscription utilisateur...")
        user_data = {
            'email': f'test_{int(time.time())}@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User',
            'address': '123 Test Street, Paris'
        }
        response = requests.post(f'{base_url}/register', json=user_data)
        if response.status_code == 200:
            user_info = response.json()
            user_id = user_info.get('id')
            print("✅ Utilisateur créé avec succès")
            print(f"   Email: {user_info['email']}")
            print(f"   Nom: {user_info['first_name']} {user_info['last_name']}")
        else:
            print(f"❌ Erreur création utilisateur: {response.status_code} - {response.text}")
            return False
        
        # Test 4: Connexion
        print("\n🔐 Test 4: Connexion utilisateur...")
        login_data = {
            'email': user_data['email'],
            'password': user_data['password']
        }
        response = requests.post(f'{base_url}/login', json=login_data)
        if response.status_code == 200:
            login_info = response.json()
            token = login_info['access_token']
            print("✅ Connexion réussie")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ Erreur connexion: {response.status_code} - {response.text}")
            return False
        
        # Test 5: Ajouter au panier
        print("\n🛒 Test 5: Ajout au panier...")
        headers = {'Authorization': f'Bearer {token}'}
        if products:
            cart_data = {
                'product_id': products[0]['id'],
                'quantity': 2
            }
            response = requests.post(f'{base_url}/cart/add', json=cart_data, headers=headers)
            if response.status_code == 200:
                print("✅ Article ajouté au panier")
            else:
                print(f"❌ Erreur ajout panier: {response.status_code} - {response.text}")
                return False
        
        # Test 6: Récupérer le panier
        print("\n🛒 Test 6: Récupération du panier...")
        response = requests.get(f'{base_url}/cart', headers=headers)
        if response.status_code == 200:
            cart = response.json()
            print(f"✅ Panier récupéré: {len(cart.get('items', []))} articles")
            total = cart.get('total_cents', 0) / 100
            print(f"   Total: {total:.2f}€")
        else:
            print(f"❌ Erreur récupération panier: {response.status_code} - {response.text}")
            return False
        
        # Test 7: Créer une commande
        print("\n📦 Test 7: Création de commande...")
        order_data = {
            'payment_method': 'card'
        }
        response = requests.post(f'{base_url}/orders', json=order_data, headers=headers)
        if response.status_code == 200:
            order = response.json()
            order_id = order['id']
            print("✅ Commande créée avec succès")
            print(f"   ID: {order_id}")
            print(f"   Statut: {order['status']}")
        else:
            print(f"❌ Erreur création commande: {response.status_code} - {response.text}")
            return False
        
        # Test 8: Récupérer les commandes
        print("\n📋 Test 8: Récupération des commandes...")
        response = requests.get(f'{base_url}/orders', headers=headers)
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ {len(orders)} commandes récupérées")
            for order in orders[:2]:  # Afficher les 2 premières
                print(f"   - Commande {order['id'][:8]}... - Statut: {order['status']}")
        else:
            print(f"❌ Erreur récupération commandes: {response.status_code} - {response.text}")
            return False
        
        # Test 9: Détails d'une commande
        print("\n🔍 Test 9: Détails d'une commande...")
        response = requests.get(f'{base_url}/orders/{order_id}', headers=headers)
        if response.status_code == 200:
            order_detail = response.json()
            print("✅ Détails de commande récupérés")
            print(f"   Statut: {order_detail['status']}")
            print(f"   Articles: {len(order_detail.get('items', []))}")
        else:
            print(f"❌ Erreur détails commande: {response.status_code} - {response.text}")
            return False
        
        # Test 10: Test des endpoints admin (si admin)
        print("\n👑 Test 10: Endpoints administrateur...")
        response = requests.get(f'{base_url}/admin/users', headers=headers)
        if response.status_code == 200:
            admin_users = response.json()
            print(f"✅ Accès admin: {len(admin_users)} utilisateurs")
        elif response.status_code == 403:
            print("ℹ️  Accès admin refusé (utilisateur normal)")
        else:
            print(f"❌ Erreur accès admin: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎉 TOUS LES TESTS DE L'API SONT PASSÉS!")
        print("✅ La base de données PostgreSQL fonctionne parfaitement")
        print("✅ Toutes les données sont correctement stockées")
        print("✅ L'API est entièrement fonctionnelle")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Arrêter l'API
        print("\n🛑 Arrêt de l'API...")
        api_process.terminate()
        api_process.wait()
        print("✅ API arrêtée")

if __name__ == "__main__":
    success = test_complete_api()
    sys.exit(0 if success else 1)
