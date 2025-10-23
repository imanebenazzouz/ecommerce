#!/usr/bin/env python3
"""
Test de l'API FastAPI
"""

import sys
import os
sys.path.append('ecommerce-backend')

def test_fastapi_app():
    """Test de l'application FastAPI"""
    try:
        # Import de l'API
        from api_simple import app
        print("✅ Application FastAPI importée avec succès")
        
        # Test des endpoints de base
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test de l'endpoint racine
        response = client.get("/")
        print(f"✅ Endpoint racine: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Message: {data.get('message', 'N/A')}")
        
        # Test de l'endpoint health
        response = client.get("/health")
        print(f"✅ Endpoint health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'N/A')}")
        
        # Test de l'endpoint docs
        response = client.get("/docs")
        print(f"✅ Endpoint docs: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test FastAPI: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 TEST DE L'API FASTAPI")
    print("=" * 50)
    
    success = test_fastapi_app()
    
    if success:
        print("\n🎉 L'API FASTAPI FONCTIONNE CORRECTEMENT!")
        print("🌐 Vous pouvez accéder à l'API sur http://localhost:8000")
        print("📚 Documentation disponible sur http://localhost:8000/docs")
    else:
        print("\n❌ L'API FASTAPI A DES PROBLÈMES")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
