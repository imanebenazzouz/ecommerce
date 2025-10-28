#!/usr/bin/env python3
"""
Script principal pour exécuter tous les tests (unitaires, intégration, e2e)
"""

import subprocess
import sys
import os
import time

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        # Afficher la sortie
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution: {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 EXÉCUTION COMPLÈTE DE TOUS LES TESTS")
    print("=" * 60)
    
    start_time = time.time()
    
    # Changer vers le répertoire des tests
    test_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(test_dir)
    
    # Utiliser l'exécutable Python courant (compat macOS où 'python' peut être absent)
    exe = sys.executable or "python3"

    # Tests unitaires
    unit_success = run_command(
        f"{exe} run_unit_tests.py",
        "TESTS UNITAIRES"
    )
    
    # Tests d'intégration
    integration_success = run_command(
        f"{exe} run_integration_tests.py",
        "TESTS D'INTÉGRATION"
    )
    
    # Tests end-to-end
    e2e_success = run_command(
        f"{exe} run_e2e_tests.py",
        "TESTS END-TO-END"
    )
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Résumé final
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

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
