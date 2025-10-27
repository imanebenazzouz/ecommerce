#!/usr/bin/env python3
"""
Test de validation des adresses - Rejet des symboles spéciaux
Vérifie que les adresses avec des symboles (@, #, $, %, etc.) sont rejetées
"""

import sys
import os

# Ajouter le chemin du backend (remonter de 2 niveaux depuis tests/unit/)
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))
sys.path.insert(0, backend_path)

from pydantic import ValidationError
from api import RegisterIn, UserUpdateIn

def test_address_symbols():
    """Test de validation des adresses avec symboles"""
    
    print("=" * 70)
    print("Test de validation des adresses - Rejet des symboles")
    print("=" * 70)
    
    # Test 1: Adresse valide
    print("\n1. Test avec une adresse valide...")
    try:
        valid_user = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12 Rue des Fleurs, 75001 Paris"
        )
        print("   ✅ PASS: Adresse valide acceptée")
        print(f"   - Adresse: {valid_user.address}")
    except ValidationError as e:
        print(f"   ❌ FAIL: {e}")
        return False
    
    # Test 2: Adresse avec @ (devrait échouer)
    print("\n2. Test avec une adresse contenant @...")
    try:
        invalid_address = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12 Rue des Fleurs @ Paris, 75001"
        )
        print("   ❌ FAIL: Adresse avec @ acceptée (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Adresse avec @ rejetée")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 3: Adresse avec # (devrait échouer)
    print("\n3. Test avec une adresse contenant #...")
    try:
        invalid_address = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12# Rue des Fleurs, 75001 Paris"
        )
        print("   ❌ FAIL: Adresse avec # acceptée (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Adresse avec # rejetée")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 4: Adresse avec $ (devrait échouer)
    print("\n4. Test avec une adresse contenant $...")
    try:
        invalid_address = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12 Rue des $Fleurs, 75001 Paris"
        )
        print("   ❌ FAIL: Adresse avec $ acceptée (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Adresse avec $ rejetée")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 5: Adresse avec % (devrait échouer)
    print("\n5. Test avec une adresse contenant %...")
    try:
        invalid_address = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12 Rue des Fleurs%, 75001 Paris"
        )
        print("   ❌ FAIL: Adresse avec % acceptée (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Adresse avec % rejetée")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 6: Adresse avec & (devrait échouer)
    print("\n6. Test avec une adresse contenant &...")
    try:
        invalid_address = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12 Rue des Fleurs & Jardins, 75001 Paris"
        )
        print("   ❌ FAIL: Adresse avec & acceptée (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Adresse avec & rejetée")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 7: Adresse avec * (devrait échouer)
    print("\n7. Test avec une adresse contenant *...")
    try:
        invalid_address = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12* Rue des Fleurs, 75001 Paris"
        )
        print("   ❌ FAIL: Adresse avec * acceptée (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Adresse avec * rejetée")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 8: Adresse avec parenthèses (devrait échouer)
    print("\n8. Test avec une adresse contenant des parenthèses...")
    try:
        invalid_address = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12 Rue des Fleurs (batiment A), 75001 Paris"
        )
        print("   ❌ FAIL: Adresse avec parenthèses acceptée (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Adresse avec parenthèses rejetée")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 9: Adresse avec caractères autorisés (virgule, point, tiret, apostrophe)
    print("\n9. Test avec une adresse contenant des caractères autorisés...")
    try:
        valid_address = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12 Rue St-Martin, Bât. B, 75001 Paris"
        )
        print("   ✅ PASS: Adresse avec caractères autorisés acceptée")
        print(f"   - Adresse: {valid_address.address}")
    except ValidationError as e:
        print(f"   ❌ FAIL: {e}")
        return False
    
    # Test 10: Adresse avec apostrophe (devrait passer)
    print("\n10. Test avec une adresse contenant une apostrophe...")
    try:
        valid_address = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name="Jean",
            last_name="Dupont",
            address="12 Rue de l'Église, 75001 Paris"
        )
        print("   ✅ PASS: Adresse avec apostrophe acceptée")
        print(f"   - Adresse: {valid_address.address}")
    except ValidationError as e:
        print(f"   ❌ FAIL: {e}")
        return False
    
    # Test 11: UserUpdateIn avec adresse contenant des symboles (devrait échouer)
    print("\n11. Test de mise à jour avec une adresse contenant @...")
    try:
        invalid_update = UserUpdateIn(
            address="12 Rue @ Paris, 75001"
        )
        print("   ❌ FAIL: Mise à jour avec @ acceptée (ne devrait pas)")
        return False
    except ValidationError as e:
        print("   ✅ PASS: Mise à jour avec @ rejetée")
        print(f"   - Erreur: {e.errors()[0]['msg']}")
    
    # Test 12: UserUpdateIn avec adresse valide (devrait passer)
    print("\n12. Test de mise à jour avec une adresse valide...")
    try:
        valid_update = UserUpdateIn(
            address="15 Avenue des Champs-Élysées, 75008 Paris"
        )
        print("   ✅ PASS: Mise à jour avec adresse valide acceptée")
        print(f"   - Adresse: {valid_update.address}")
    except ValidationError as e:
        print(f"   ❌ FAIL: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ TOUS LES TESTS SONT PASSÉS!")
    print("=" * 70)
    print("\n📋 Symboles testés et rejetés : @, #, $, %, &, *, ( )")
    print("✅ Caractères autorisés : lettres, chiffres, espaces, virgules, points, tirets, apostrophes")
    return True

if __name__ == "__main__":
    success = test_address_symbols()
    sys.exit(0 if success else 1)

