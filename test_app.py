#!/usr/bin/env python3
"""
Script de test principal pour l'application e-commerce
Utilise le test complet depuis le dossier tests/legacy
"""

import sys
import os
import subprocess

def main():
    """Lance le test complet de l'application"""
    print("🚀 Test de l'application e-commerce")
    print("=" * 50)
    
    # Chemin vers le test complet
    test_path = os.path.join(os.path.dirname(__file__), "tests", "legacy", "test_complete.py")
    
    if not os.path.exists(test_path):
        print("❌ Fichier de test non trouvé:", test_path)
        return 1
    
    try:
        # Exécuter le test
        result = subprocess.run([sys.executable, test_path], check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du test: {e}")
        return e.returncode
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
