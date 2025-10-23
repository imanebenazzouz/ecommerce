#!/usr/bin/env python3
"""
Test de l'API avec la base de données
"""

import os
import sys
import requests
import time

def test_api_health():
    """Test de l'endpoint de santé de l'API"""
    try:
        print("🔍 Test de l'API...")
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False

def test_api_root():
    """Test de l'endpoint racine de l'API"""
    try:
        print("🔍 Test de l'endpoint racine...")
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False

def test_api_products():
    """Test de l'endpoint des produits"""
    try:
        print("🔍 Test de l'endpoint produits...")
        response = requests.get("http://localhost:8000/products", timeout=5)
        print(f"📊 Status Code: {response.status_code}")
        if response.status_code == 200:
            products = response.json()
            print(f"📋 Nombre de produits: {len(products)}")
        else:
            print(f"📋 Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test de l'API e-commerce")
    print("=" * 50)
    
    # Attendre que l'API démarre
    print("⏳ Attente du démarrage de l'API...")
    time.sleep(3)
    
    # Tests
    health_ok = test_api_health()
    root_ok = test_api_root()
    products_ok = test_api_products()
    
    print("\n📊 Résultats:")
    print(f"  Health: {'✅' if health_ok else '❌'}")
    print(f"  Root: {'✅' if root_ok else '❌'}")
    print(f"  Products: {'✅' if products_ok else '❌'}")
    
    if health_ok and root_ok and products_ok:
        print("\n🎉 L'API fonctionne correctement!")
    else:
        print("\n⚠️  L'API a des problèmes")
