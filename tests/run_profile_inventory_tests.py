#!/usr/bin/env python3
"""
Script pour exécuter les tests de profil utilisateur et gestion d'inventaire
"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

def main():
    """Exécute les tests de profil et inventaire"""
    
    print("=" * 80)
    print("🧪 Exécution des tests de profil utilisateur et gestion d'inventaire")
    print("=" * 80)
    print()
    
    # Définir les fichiers de test
    test_files = [
        "tests/unit/test_user_profile_advanced.py",
        "tests/integration/test_inventory_management.py"
    ]
    
    # Arguments pytest
    pytest_args = [
        "-v",  # Verbose
        "-s",  # Afficher les prints
        "--tb=short",  # Traceback court
        "-x",  # Arrêter au premier échec
        "--color=yes",  # Couleurs
    ]
    
    # Ajouter les fichiers de test
    pytest_args.extend(test_files)
    
    print("📋 Tests à exécuter:")
    for test_file in test_files:
        print(f"  ✓ {test_file}")
    print()
    
    # Exécuter les tests
    print("🚀 Lancement des tests...")
    print()
    
    exit_code = pytest.main(pytest_args)
    
    print()
    print("=" * 80)
    if exit_code == 0:
        print("✅ Tous les tests ont réussi!")
    else:
        print("❌ Certains tests ont échoué")
    print("=" * 80)
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

