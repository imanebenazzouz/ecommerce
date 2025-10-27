#!/usr/bin/env python3
"""
Test de validation des noms et prénoms
Vérifie que les noms/prénoms avec des chiffres sont rejetés
"""

import sys
import os

# Ajouter le chemin du backend (remonter de 2 niveaux depuis tests/integration/)
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))
sys.path.insert(0, backend_path)

from pydantic import ValidationError
from api import RegisterIn, UserUpdateIn

def test_name_validation():
    """Test de validation des noms/prénoms"""
    
    print("=" * 60)
    print("Test de validation des noms et prénoms")
    print("=" * 60)
    
    # Test 1: Noms valides
    print("\n1. Test avec des noms valides...")
    try:
        valid_user = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean-Claude",
            last_name="O'Connor",
            address="12 Rue des Fleurs, 75001 Paris"
        )
        print("   ✅ PASS: Noms valides acceptés")
        print(f"   - Prénom: {valid_user.first_name}")
        print(f"   - Nom: {valid_user.last_name}")
    except ValidationError as e:
        print(f"   ❌ FAIL: {e}")
        return False
    
    # Test 2: Prénom avec des chiffres (devrait échouer)
    print("\n2. Test avec un prénom contenant des chiffres...")
    try:
        invalid_first_name = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean123",
            last_name="Dupont",
            address="12 Rue des Fleurs, 75001 Paris"
        )
        print("   ❌ FAIL: Prénom avec chiffres accepté (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Prénom avec chiffres rejeté")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 3: Nom avec des chiffres (devrait échouer)
    print("\n3. Test avec un nom contenant des chiffres...")
    try:
        invalid_last_name = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont99",
            address="12 Rue des Fleurs, 75001 Paris"
        )
        print("   ❌ FAIL: Nom avec chiffres accepté (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Nom avec chiffres rejeté")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 4: Nom trop court (devrait échouer)
    print("\n4. Test avec un nom trop court...")
    try:
        short_name = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="J",
            last_name="Dupont",
            address="12 Rue des Fleurs, 75001 Paris"
        )
        print("   ❌ FAIL: Nom trop court accepté (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Nom trop court rejeté")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 5: Noms avec accents (devrait passer)
    print("\n5. Test avec des noms contenant des accents...")
    try:
        accented_names = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="François",
            last_name="Müller",
            address="12 Rue des Fleurs, 75001 Paris"
        )
        print("   ✅ PASS: Noms avec accents acceptés")
        print(f"   - Prénom: {accented_names.first_name}")
        print(f"   - Nom: {accented_names.last_name}")
    except ValidationError as e:
        print(f"   ❌ FAIL: {e}")
        return False
    
    # Test 6: UserUpdateIn avec nom valide
    print("\n6. Test de mise à jour du profil avec un nom valide...")
    try:
        valid_update = UserUpdateIn(
            first_name="Marie-Anne",
            last_name="Dubois"
        )
        print("   ✅ PASS: Mise à jour avec noms valides acceptée")
        print(f"   - Prénom: {valid_update.first_name}")
        print(f"   - Nom: {valid_update.last_name}")
    except ValidationError as e:
        print(f"   ❌ FAIL: {e}")
        return False
    
    # Test 7: UserUpdateIn avec nom contenant des chiffres (devrait échouer)
    print("\n7. Test de mise à jour du profil avec un nom contenant des chiffres...")
    try:
        invalid_update = UserUpdateIn(
            first_name="Marie123",
            last_name="Dubois"
        )
        print("   ❌ FAIL: Mise à jour avec prénom contenant des chiffres acceptée (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Mise à jour avec prénom contenant des chiffres rejetée")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    print("\n" + "=" * 60)
    print("✅ TOUS LES TESTS SONT PASSÉS!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_name_validation()
    sys.exit(0 if success else 1)

