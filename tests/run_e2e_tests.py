#!/usr/bin/env python3
"""
Script pour exécuter tous les tests end-to-end
"""

import unittest
import sys
import os
import time

def run_e2e_tests():
    """Exécute tous les tests end-to-end"""
    print("🌐 EXÉCUTION DES TESTS END-TO-END")
    print("=" * 50)
    
    # Ajouter le répertoire courant au path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Découvrir et exécuter tous les tests e2e
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'e2e')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Affichage du résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS END-TO-END")
    print("=" * 50)
    print(f"🧪 Tests exécutés: {result.testsRun}")
    print(f"✅ Tests réussis: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Échecs: {len(result.failures)}")
    print(f"💥 Erreurs: {len(result.errors)}")
    
    if result.failures:
        print("\n🔍 DÉTAIL DES ÉCHECS:")
        for test, traceback in result.failures:
            print(f"  ❌ {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n🔍 DÉTAIL DES ERREURS:")
        for test, traceback in result.errors:
            print(f"  💥 {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return len(result.failures) + len(result.errors) == 0

if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
