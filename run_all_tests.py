#!/usr/bin/env python3
"""
Script principal pour exécuter tous les tests
Utilise la nouvelle structure organisée des tests
"""

import subprocess
import sys
import os
import time

def main():
    """Fonction principale pour exécuter tous les tests"""
    print("🧪 EXÉCUTION COMPLÈTE DE TOUS LES TESTS")
    print("=" * 60)
    print("📁 Utilisation de la structure organisée des tests")
    print("   - tests/unit/     : Tests unitaires")
    print("   - tests/integration/ : Tests d'intégration") 
    print("   - tests/e2e/      : Tests end-to-end")
    print("=" * 60)
    
    # Changer vers le répertoire des tests
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    
    if not os.path.exists(test_dir):
        print("❌ Dossier tests/ non trouvé. Veuillez exécuter depuis la racine du projet.")
        sys.exit(1)
    
    # Exécuter le script principal des tests
    script_path = os.path.join(test_dir, 'run_all_tests.py')
    
    if not os.path.exists(script_path):
        print("❌ Script tests/run_all_tests.py non trouvé.")
        sys.exit(1)
    
    try:
        # Exécuter le script des tests
        result = subprocess.run([sys.executable, script_path], cwd=test_dir)
        return result.returncode
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des tests: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
