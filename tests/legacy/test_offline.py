#!/usr/bin/env python3
"""
Test offline rapide - sans dépendance API
"""

import sys
import os
import time
import unittest

# Ajouter le répertoire backend au path
backend_path = os.path.join(os.path.dirname(__file__), 'ecommerce-backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test des imports principaux"""
    print("🔍 Test des imports...")
    
    try:
        from ecommerce_backend.api import app
        print("✅ Import API réussi")
        return True
    except Exception as e:
        print(f"❌ Import API échoué: {e}")
        return False

def test_services():
    """Test des services"""
    print("🔍 Test des services...")
    
    try:
        from ecommerce_backend.services.auth_service import AuthService
        print("✅ Import AuthService réussi")
        
        # Test basique
        auth_service = AuthService(None)
        hashed = auth_service.hash_password("test123")
        verified = auth_service.verify_password("test123", hashed)
        
        if verified:
            print("✅ Hash/verify password fonctionne")
            return True
        else:
            print("❌ Hash/verify password échoué")
            return False
            
    except Exception as e:
        print(f"❌ Test services échoué: {e}")
        return False

def test_database_models():
    """Test des modèles de base de données"""
    print("🔍 Test des modèles...")
    
    try:
        from ecommerce_backend.database.models import User, Product, Order
        print("✅ Import modèles réussi")
        return True
    except Exception as e:
        print(f"❌ Import modèles échoué: {e}")
        return False

def test_repositories():
    """Test des repositories"""
    print("🔍 Test des repositories...")
    
    try:
        from ecommerce_backend.database.repositories_simple import (
            PostgreSQLUserRepository, 
            PostgreSQLProductRepository
        )
        print("✅ Import repositories réussi")
        return True
    except Exception as e:
        print(f"❌ Import repositories échoué: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 TEST OFFLINE RAPIDE")
    print("=" * 40)
    
    start_time = time.time()
    
    tests = [
        test_imports,
        test_services,
        test_database_models,
        test_repositories
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test in tests:
        if test():
            success_count += 1
        print()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("=" * 40)
    print("📊 RÉSUMÉ")
    print("=" * 40)
    print(f"⏱️  Durée: {duration:.2f} secondes")
    print(f"✅ Tests réussis: {success_count}/{total_tests}")
    print(f"❌ Tests échoués: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 TOUS LES TESTS OFFLINE SONT PASSÉS!")
        print("✅ L'architecture de base fonctionne")
    else:
        print(f"\n⚠️  {total_tests - success_count} tests ont échoué")
        print("🔧 Des corrections sont nécessaires")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
