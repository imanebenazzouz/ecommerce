#!/usr/bin/env python3
"""
Test simple et rapide - sans dépendances complexes
"""

import sys
import os
import time

def test_basic_imports():
    """Test des imports de base"""
    print("🔍 Test des imports de base...")
    
    try:
        import fastapi
        print("✅ FastAPI importé")
        
        import sqlalchemy
        print("✅ SQLAlchemy importé")
        
        import pydantic
        print("✅ Pydantic importé")
        
        import jwt
        print("✅ JWT importé")
        
        return True
    except Exception as e:
        print(f"❌ Import échoué: {e}")
        return False

def test_basic_functionality():
    """Test de fonctionnalités de base"""
    print("🔍 Test des fonctionnalités de base...")
    
    try:
        # Test de hachage simple
        import hashlib
        password = "test123"
        hashed = hashlib.sha256(password.encode()).hexdigest()
        
        if hashed:
            print("✅ Hachage SHA256 fonctionne")
        else:
            print("❌ Hachage SHA256 échoué")
            return False
        
        # Test de génération UUID
        import uuid
        test_uuid = str(uuid.uuid4())
        
        if test_uuid and len(test_uuid) == 36:
            print("✅ Génération UUID fonctionne")
        else:
            print("❌ Génération UUID échoué")
            return False
        
        # Test de validation email simple
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if re.match(email_pattern, "test@example.com"):
            print("✅ Validation email fonctionne")
        else:
            print("❌ Validation email échoué")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Fonctionnalités de base échouées: {e}")
        return False

def test_api_creation():
    """Test de création d'API FastAPI simple"""
    print("🔍 Test de création d'API...")
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Créer une API simple
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {"message": "Hello World"}
        
        @app.get("/health")
        def health_check():
            return {"status": "healthy"}
        
        # Tester avec TestClient
        client = TestClient(app)
        
        # Test endpoint racine
        response = client.get("/")
        if response.status_code == 200:
            print("✅ Endpoint racine fonctionne")
        else:
            print("❌ Endpoint racine échoué")
            return False
        
        # Test endpoint santé
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Endpoint santé fonctionne")
        else:
            print("❌ Endpoint santé échoué")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Création d'API échouée: {e}")
        return False

def test_database_connection():
    """Test de connexion à la base de données"""
    print("🔍 Test de connexion base de données...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Test avec une base de données en mémoire SQLite
        engine = create_engine("sqlite:///:memory:")
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                print("✅ Connexion base de données fonctionne")
                return True
            else:
                print("❌ Connexion base de données échoué")
                return False
                
    except Exception as e:
        print(f"❌ Connexion base de données échouée: {e}")
        return False

def main():
    """Fonction principale"""
    print("⚡ TEST SIMPLE ET RAPIDE")
    print("=" * 40)
    
    start_time = time.time()
    
    tests = [
        test_basic_imports,
        test_basic_functionality,
        test_api_creation,
        test_database_connection
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
        print("\n🎉 TOUS LES TESTS SIMPLES SONT PASSÉS!")
        print("✅ L'environnement de base fonctionne")
        print("🚀 Prêt pour des tests plus complexes")
    else:
        print(f"\n⚠️  {total_tests - success_count} tests ont échoué")
        print("🔧 Des corrections sont nécessaires")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
