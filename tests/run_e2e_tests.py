#!/usr/bin/env python3
"""
Script pour exécuter les tests end-to-end
"""
import subprocess
import sys
import os
import time

def main():
    print("🌐 EXÉCUTION DES TESTS END-TO-END")
    print("=" * 60)
    
    # Vérifier que l'API est disponible
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ L'API n'est pas disponible sur http://localhost:8000")
            print("💡 Démarrez l'API avec: cd ecommerce-backend && python3 api.py")
            return 1
        print("✅ L'API est disponible")
    except ImportError:
        print("❌ Le module 'requests' n'est pas installé")
        print("💡 Installez-le avec: pip install requests")
        return 1
    except Exception as e:
        print(f"❌ L'API n'est pas disponible: {e}")
        print("💡 Démarrez l'API avec: cd ecommerce-backend && python3 api.py")
        return 1
    
    # Vérifier que le frontend est disponible
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code != 200:
            print("❌ Le frontend n'est pas disponible sur http://localhost:5173")
            print("💡 Démarrez le frontend avec: cd ecommerce-front && npm run dev")
            return 1
        print("✅ Le frontend est disponible")
    except Exception as e:
        print(f"❌ Le frontend n'est pas disponible: {e}")
        print("💡 Démarrez le frontend avec: cd ecommerce-front && npm run dev")
        return 1
    
    # Exécuter les tests E2E
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'e2e')
    os.chdir(test_dir)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_final.py",
            "test_checkout_validation.py",
            "test_user_journey.py",
            "test_user_journey_comprehensive.py",
            "-v", "--tb=short"
        ])
        return result.returncode
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())