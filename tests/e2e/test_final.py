#!/usr/bin/env python3
"""
Test final de l'application e-commerce
"""

import requests
import json
import time
import sys

# Configuration
API_BASE = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_api_health():
    """Test de santé de l'API"""
    print("🏥 Test de santé de l'API...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API en ligne")
            return True
        else:
            print(f"❌ API répond avec le code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Impossible de contacter l'API: {e}")
        return False

def test_user_registration():
    """Test d'inscription d'utilisateur"""
    print("👤 Test d'inscription...")
    
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "address": "123 Test Street"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=user_data, timeout=10)
        if response.status_code == 200:
            print("✅ Inscription réussie")
            return response.json()
        else:
            print(f"❌ Échec inscription: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de l'inscription: {e}")
        return None

def test_user_login():
    """Test de connexion"""
    print("🔐 Test de connexion...")
    
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            print("✅ Connexion réussie")
            return response.json()
        else:
            print(f"❌ Échec connexion: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la connexion: {e}")
        return None

def test_products_listing(token):
    """Test de listing des produits"""
    print("🛍️ Test de listing des produits...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/products", headers=headers, timeout=10)
        if response.status_code == 200:
            products = response.json()
            print(f"✅ {len(products)} produits trouvés")
            return products
        else:
            print(f"❌ Échec listing produits: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors du listing: {e}")
        return None

def test_cart_operations(token, product_id):
    """Test des opérations de panier"""
    print("🛒 Test des opérations de panier...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Ajouter au panier
    cart_data = {"product_id": product_id, "qty": 2}
    try:
        response = requests.post(f"{API_BASE}/cart/add", json=cart_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Produit ajouté au panier")
        else:
            print(f"❌ Échec ajout panier: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur ajout panier: {e}")
        return False
    
    # Voir le panier
    try:
        response = requests.get(f"{API_BASE}/cart", headers=headers, timeout=10)
        if response.status_code == 200:
            cart = response.json()
            print(f"✅ Panier contient {len(cart['items'])} articles")
            return True
        else:
            print(f"❌ Échec récupération panier: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur récupération panier: {e}")
        return False

def test_order_creation(token):
    """Test de création de commande"""
    print("📦 Test de création de commande...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{API_BASE}/orders/checkout", headers=headers, timeout=10)
        if response.status_code == 200:
            order = response.json()
            print("✅ Commande créée")
            return order
        else:
            print(f"❌ Échec création commande: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur création commande: {e}")
        return None

def test_payment(token, order_id):
    """Test de paiement"""
    print("💳 Test de paiement...")
    
    headers = {"Authorization": f"Bearer {token}"}
    payment_data = {
        "card_number": "4242424242424242",
        "exp_month": 12,
        "exp_year": 2025,
        "cvc": "123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/orders/{order_id}/pay", json=payment_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Paiement effectué")
            return True
        else:
            print(f"❌ Échec paiement: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur paiement: {e}")
        return False

def test_orders_listing(token):
    """Test de listing des commandes"""
    print("📋 Test de listing des commandes...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/orders", headers=headers, timeout=10)
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ {len(orders)} commandes trouvées")
            return True
        else:
            print(f"❌ Échec listing commandes: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur listing commandes: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST FINAL DE L'APPLICATION E-COMMERCE")
    print("=" * 50)
    
    # Test 1: Santé de l'API
    if not test_api_health():
        print("❌ L'API n'est pas accessible. Veuillez démarrer le backend.")
        sys.exit(1)
    
    # Test 2: Inscription
    user_data = test_user_registration()
    if not user_data:
        print("❌ Échec de l'inscription")
        sys.exit(1)
    
    # Test 3: Connexion
    login_data = test_user_login()
    if not login_data:
        print("❌ Échec de la connexion")
        sys.exit(1)
    
    token = login_data["access_token"]
    
    # Test 4: Listing des produits
    products = test_products_listing(token)
    if not products:
        print("❌ Échec du listing des produits")
        sys.exit(1)
    
    # Prendre le premier produit pour les tests
    product_id = products[0]["id"]
    
    # Test 5: Opérations de panier
    if not test_cart_operations(token, product_id):
        print("❌ Échec des opérations de panier")
        sys.exit(1)
    
    # Test 6: Création de commande
    order = test_order_creation(token)
    if not order:
        print("❌ Échec de la création de commande")
        sys.exit(1)
    
    order_id = order["order_id"]
    
    # Test 7: Paiement
    if not test_payment(token, order_id):
        print("❌ Échec du paiement")
        sys.exit(1)
    
    # Test 8: Listing des commandes
    if not test_orders_listing(token):
        print("❌ Échec du listing des commandes")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
    print("✅ L'application e-commerce fonctionne correctement")
    print("🌐 Frontend: http://localhost:5173")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    main()
