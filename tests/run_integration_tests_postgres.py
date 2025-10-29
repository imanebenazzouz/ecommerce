#!/usr/bin/env python3
"""
Script pour exécuter les tests d'intégration avec PostgreSQL
"""
import subprocess
import sys
import os

def main():
    print("🔗 EXÉCUTION DES TESTS D'INTÉGRATION AVEC POSTGRESQL")
    print("=" * 60)
    
    # Vérifier que PostgreSQL est disponible
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ PostgreSQL n'est pas disponible")
            return 1
        print("✅ PostgreSQL est disponible")
    except FileNotFoundError:
        print("❌ PostgreSQL n'est pas installé")
        return 1
    
    # Vérifier que la base de données de test existe
    try:
        result = subprocess.run([
            "psql", "-h", "localhost", "-U", "postgres", "-d", "ecommerce_test", 
            "-c", "SELECT 1;"
        ], capture_output=True, text=True, input="password\n")
        
        if result.returncode != 0:
            print("❌ Base de données de test 'ecommerce_test' n'existe pas")
            print("💡 Créez-la avec: createdb -U postgres ecommerce_test")
            return 1
        print("✅ Base de données de test 'ecommerce_test' est disponible")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la base de données: {e}")
        return 1
    
    # Exécuter les tests d'intégration
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'integration')
    os.chdir(test_dir)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_payment_validation.py",
            "test_database_comprehensive.py",
            "-v", "--tb=short"
        ])
        return result.returncode
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())