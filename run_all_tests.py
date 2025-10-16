#!/usr/bin/env python3
"""
Script pour exécuter tous les tests du backend
"""

import unittest
import sys
import os
import time

def run_test_suite(test_file, test_name):
    """Exécute une suite de tests spécifique"""
    print(f"\n{'='*60}")
    print(f"Exécution des tests: {test_name}")
    print(f"{'='*60}")
    
    # Ajouter le répertoire courant au path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Charger et exécuter les tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_file.replace('.py', ''))
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    return result

def main():
    """Fonction principale pour exécuter tous les tests"""
    print("🚀 DÉMARRAGE DES TESTS COMPLETS DU BACKEND ECOMMERCE")
    print("=" * 60)
    
    # Liste des fichiers de tests à exécuter
    test_files = [
        ("test_auth", "Authentification et sessions"),
        ("test_products", "Gestion des produits"),
        ("test_cart", "Gestion du panier"),
        ("test_orders", "Gestion des commandes"),
        ("test_payments", "Gestion des paiements"),
        ("test_support", "Support client"),
        ("test_storage", "Stockage persistant"),
        ("test_api_endpoints", "Endpoints API")
    ]
    
    start_time = time.time()
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    results = []
    
    for test_file, test_name in test_files:
        try:
            result = run_test_suite(test_file, test_name)
            results.append((test_name, result))
            
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution des tests {test_name}: {e}")
            total_errors += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Affichage du résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ FINAL DES TESTS")
    print(f"{'='*60}")
    
    print(f"⏱️  Durée totale: {duration:.2f} secondes")
    print(f"🧪 Tests exécutés: {total_tests}")
    print(f"✅ Tests réussis: {total_tests - total_failures - total_errors}")
    print(f"❌ Échecs: {total_failures}")
    print(f"💥 Erreurs: {total_errors}")
    
    # Détail par suite de tests
    print(f"\n📋 DÉTAIL PAR MODULE:")
    print("-" * 40)
    
    for test_name, result in results:
        status = "✅" if len(result.failures) == 0 and len(result.errors) == 0 else "❌"
        print(f"{status} {test_name:<25} | Tests: {result.testsRun:<3} | Échecs: {len(result.failures):<2} | Erreurs: {len(result.errors)}")
    
    # Affichage des échecs et erreurs
    if total_failures > 0 or total_errors > 0:
        print(f"\n🔍 DÉTAIL DES ÉCHECS ET ERREURS:")
        print("-" * 40)
        
        for test_name, result in results:
            if result.failures or result.errors:
                print(f"\n❌ {test_name}:")
                
                for test, traceback in result.failures:
                    print(f"  💥 ÉCHEC: {test}")
                    print(f"     {traceback.split('AssertionError:')[-1].strip()}")
                
                for test, traceback in result.errors:
                    print(f"  💥 ERREUR: {test}")
                    print(f"     {traceback.split('Exception:')[-1].strip()}")
    
    # Code de sortie
    exit_code = 0 if (total_failures == 0 and total_errors == 0) else 1
    
    print(f"\n{'='*60}")
    if exit_code == 0:
        print("🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("🚀 Le backend est prêt pour la production!")
    else:
        print("⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Veuillez corriger les erreurs avant de déployer")
    
    print(f"{'='*60}")
    
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
