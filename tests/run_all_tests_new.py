#!/usr/bin/env python3
"""
Script principal pour exécuter tous les tests
"""
import subprocess
import sys
import os
import time

def main():
    print("🧪 EXÉCUTION COMPLÈTE DE TOUS LES TESTS")
    print("=" * 60)
    
    start_time = time.time()
    
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    os.chdir(test_dir)
    
    exe = sys.executable or "python3"
    
    # Tests unitaires
    print("\n🧪 TESTS UNITAIRES")
    print("-" * 30)
    unit_success = run_command(
        f"{exe} -m pytest unit/ -v --tb=short",
        "TESTS UNITAIRES"
    )
    
    # Tests d'intégration avec PostgreSQL
    print("\n🔗 TESTS D'INTÉGRATION (PostgreSQL)")
    print("-" * 30)
    integration_success = run_command(
        f"{exe} run_integration_tests_postgres.py",
        "TESTS D'INTÉGRATION"
    )
    
    # Tests end-to-end
    print("\n🌐 TESTS END-TO-END")
    print("-" * 30)
    e2e_success = run_command(
        f"{exe} run_e2e_tests.py",
        "TESTS END-TO-END"
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ FINAL DE TOUS LES TESTS")
    print(f"{'='*60}")
    print(f"⏱️  Durée totale: {duration:.2f} secondes")
    print(f"🧪 Tests unitaires: {'✅ RÉUSSIS' if unit_success else '❌ ÉCHOUÉS'}")
    print(f"🔗 Tests d'intégration: {'✅ RÉUSSIS' if integration_success else '❌ ÉCHOUÉS'}")
    print(f"🌐 Tests end-to-end: {'✅ RÉUSSIS' if e2e_success else '❌ ÉCHOUÉS'}")
    
    overall_success = unit_success and integration_success and e2e_success
    
    if overall_success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("🚀 L'application est prête pour la production!")
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Veuillez corriger les erreurs avant de déployer")
    
    print(f"{'='*60}")
    
    return 0 if overall_success else 1

def run_command(command, test_type):
    """Exécute une commande et retourne True si elle réussit"""
    try:
        print(f"Exécution: {command}")
        result = subprocess.run(command, shell=True)
        success = result.returncode == 0
        print(f"{'✅' if success else '❌'} {test_type}: {'RÉUSSIS' if success else 'ÉCHOUÉS'}")
        return success
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution de {test_type}: {e}")
        return False

if __name__ == "__main__":
    sys.exit(main())