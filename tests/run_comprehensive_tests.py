#!/usr/bin/env python3
"""
Script de lancement des tests complets
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_section(title):
    """Affiche une section formatée"""
    print(f"\n📋 {title}")
    print("-" * 40)

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    start_time = time.time()
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} - Réussi ({duration:.2f}s)")
            if result.stdout:
                print(f"📄 Sortie: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - Échec ({duration:.2f}s)")
            if result.stderr:
                print(f"🚨 Erreur: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False
    
    return True

def check_dependencies():
    """Vérifie les dépendances"""
    print_section("Vérification des dépendances")
    
    dependencies = [
        ("python", "Python 3.8+"),
        ("pip", "Pip"),
        ("pytest", "Pytest"),
        ("requests", "Requests"),
        ("sqlalchemy", "SQLAlchemy"),
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
    ]
    
    for dep, description in dependencies:
        try:
            result = subprocess.run(f"python -c 'import {dep}'", shell=True, capture_output=True)
            if result.returncode == 0:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - Manquant")
                return False
        except:
            print(f"❌ {description} - Erreur de vérification")
            return False
    
    return True

def run_unit_tests():
    """Lance les tests unitaires"""
    print_section("Tests unitaires")
    
    test_files = [
        "tests/unit/test_auth_comprehensive.py",
        "tests/unit/test_cart_comprehensive.py", 
        "tests/unit/test_orders_comprehensive.py",
        "tests/unit/test_security_comprehensive.py",
        "tests/unit/test_performance_comprehensive.py",
        "tests/unit/test_api_endpoints.py",
        "tests/unit/test_auth_service.py",
        "tests/unit/test_products.py",
        "tests/unit/test_cart.py",
        "tests/unit/test_orders.py",
        "tests/unit/test_payments.py",
        "tests/unit/test_support.py",
    ]
    
    success_count = 0
    total_count = len(test_files)
    
    for test_file in test_files:
        if os.path.exists(test_file):
            command = f"python -m pytest {test_file} -v --tb=short"
            if run_command(command, f"Test {test_file}"):
                success_count += 1
        else:
            print(f"⚠️  Fichier de test non trouvé: {test_file}")
    
    print(f"\n📊 Tests unitaires: {success_count}/{total_count} réussis")
    return success_count == total_count

def run_integration_tests():
    """Lance les tests d'intégration"""
    print_section("Tests d'intégration")
    
    test_files = [
        "tests/integration/test_database_comprehensive.py",
        "tests/integration/test_database_integration.py",
    ]
    
    success_count = 0
    total_count = len(test_files)
    
    for test_file in test_files:
        if os.path.exists(test_file):
            command = f"python -m pytest {test_file} -v --tb=short"
            if run_command(command, f"Test {test_file}"):
                success_count += 1
        else:
            print(f"⚠️  Fichier de test non trouvé: {test_file}")
    
    print(f"\n📊 Tests d'intégration: {success_count}/{total_count} réussis")
    return success_count == total_count

def run_e2e_tests():
    """Lance les tests end-to-end"""
    print_section("Tests end-to-end")
    
    test_files = [
        "tests/e2e/test_user_journey_comprehensive.py",
        "tests/e2e/test_final.py",
        "tests/e2e/test_user_journey.py",
    ]
    
    success_count = 0
    total_count = len(test_files)
    
    for test_file in test_files:
        if os.path.exists(test_file):
            command = f"python -m pytest {test_file} -v --tb=short"
            if run_command(command, f"Test {test_file}"):
                success_count += 1
        else:
            print(f"⚠️  Fichier de test non trouvé: {test_file}")
    
    print(f"\n📊 Tests end-to-end: {success_count}/{total_count} réussis")
    return success_count == total_count

def run_all_tests():
    """Lance tous les tests"""
    print_section("Tous les tests")
    
    command = "python -m pytest tests/ -v --tb=short --maxfail=5"
    return run_command(command, "Tous les tests")

def run_specific_test_categories():
    """Lance des catégories spécifiques de tests"""
    print_section("Tests par catégorie")
    
    categories = [
        ("tests/unit/", "Tests unitaires", "unit"),
        ("tests/integration/", "Tests d'intégration", "integration"),
        ("tests/e2e/", "Tests end-to-end", "e2e"),
    ]
    
    results = {}
    
    for path, name, marker in categories:
        if os.path.exists(path):
            command = f"python -m pytest {path} -v --tb=short -m {marker}"
            success = run_command(command, name)
            results[name] = success
        else:
            print(f"⚠️  Répertoire non trouvé: {path}")
            results[name] = False
    
    return results

def run_performance_tests():
    """Lance les tests de performance"""
    print_section("Tests de performance")
    
    command = "python -m pytest tests/unit/test_performance_comprehensive.py -v --tb=short"
    return run_command(command, "Tests de performance")

def run_security_tests():
    """Lance les tests de sécurité"""
    print_section("Tests de sécurité")
    
    command = "python -m pytest tests/unit/test_security_comprehensive.py -v --tb=short"
    return run_command(command, "Tests de sécurité")

def generate_test_report():
    """Génère un rapport de tests"""
    print_section("Génération du rapport")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"test_report_{timestamp}.txt"
    
    command = f"python -m pytest tests/ -v --tb=short --html=test_report_{timestamp}.html --self-contained-html"
    success = run_command(command, "Génération du rapport HTML")
    
    if success:
        print(f"📄 Rapport généré: test_report_{timestamp}.html")
    
    return success

def check_code_quality():
    """Vérifie la qualité du code"""
    print_section("Vérification de la qualité du code")
    
    # Vérification de la syntaxe Python
    python_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    syntax_errors = 0
    for file in python_files:
        command = f"python -m py_compile {file}"
        if not run_command(command, f"Syntaxe {file}"):
            syntax_errors += 1
    
    if syntax_errors == 0:
        print("✅ Aucune erreur de syntaxe détectée")
    else:
        print(f"❌ {syntax_errors} erreurs de syntaxe détectées")
    
    return syntax_errors == 0

def main():
    """Fonction principale"""
    print_header("TESTS COMPLETS DU PROJET E-COMMERCE")
    print(f"🕐 Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérification des dépendances
    if not check_dependencies():
        print("❌ Dépendances manquantes. Veuillez les installer.")
        sys.exit(1)
    
    # Vérification de la qualité du code
    if not check_code_quality():
        print("❌ Erreurs de qualité du code détectées.")
        sys.exit(1)
    
    # Lancement des tests
    results = {}
    
    # Tests unitaires
    results["unit"] = run_unit_tests()
    
    # Tests d'intégration
    results["integration"] = run_integration_tests()
    
    # Tests end-to-end
    results["e2e"] = run_e2e_tests()
    
    # Tests de performance
    results["performance"] = run_performance_tests()
    
    # Tests de sécurité
    results["security"] = run_security_tests()
    
    # Tests par catégorie
    category_results = run_specific_test_categories()
    results.update(category_results)
    
    # Génération du rapport
    results["report"] = generate_test_report()
    
    # Résumé final
    print_header("RÉSUMÉ FINAL")
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    print(f"📊 Tests réussis: {passed_tests}/{total_tests}")
    print(f"📈 Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📋 Détail des résultats:")
    for test_name, success in results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}")
    
    if passed_tests == total_tests:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS!")
        print("✅ Le projet e-commerce est en excellent état")
        print("🚀 Prêt pour la production!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests ont échoué")
        print("🔧 Veuillez corriger les problèmes identifiés")
    
    print(f"\n🕐 Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
