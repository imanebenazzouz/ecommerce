#!/usr/bin/env python3
"""
Script pour exécuter rapidement les tests qui fonctionnent
"""

import subprocess
import sys
import os
import time

def run_fast_tests():
    """Exécute rapidement les tests qui fonctionnent"""
    print("⚡ EXÉCUTION RAPIDE DES TESTS")
    print("=" * 50)
    
    start_time = time.time()
    
    # Changer vers le répertoire du projet
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Activer l'environnement virtuel
    venv_python = "ecommerce-backend/venv/bin/python"
    
    # Tests qui fonctionnent probablement
    test_commands = [
        # Test simple d'authentification
        f"{venv_python} -m pytest tests/unit/test_auth_simple.py -v",
        
        # Test des endpoints API (si corrigé)
        f"{venv_python} -m pytest tests/unit/test_api_endpoints.py -v --tb=short",
        
        # Test des services
        f"{venv_python} -m pytest tests/unit/test_auth_service.py -v --tb=short",
        
        # Test end-to-end simple
        f"{venv_python} tests/e2e/test_final.py",
    ]
    
    success_count = 0
    total_tests = len(test_commands)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n🧪 Test {i}/{total_tests}: {command.split()[-1]}")
        print("-" * 40)
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ RÉUSSI")
                success_count += 1
            else:
                print("❌ ÉCHOUÉ")
                if result.stderr:
                    print(f"Erreur: {result.stderr[:200]}...")
            
            # Afficher la sortie si elle est courte
            if result.stdout and len(result.stdout) < 500:
                print(result.stdout)
                
        except subprocess.TimeoutExpired:
            print("⏰ TIMEOUT (30s)")
        except Exception as e:
            print(f"💥 ERREUR: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*50}")
    print("📊 RÉSUMÉ RAPIDE")
    print(f"{'='*50}")
    print(f"⏱️  Durée totale: {duration:.2f} secondes")
    print(f"✅ Tests réussis: {success_count}/{total_tests}")
    print(f"❌ Tests échoués: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 TOUS LES TESTS RAPIDES SONT PASSÉS!")
    else:
        print(f"\n⚠️  {total_tests - success_count} tests ont échoué")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = run_fast_tests()
    sys.exit(0 if success else 1)
