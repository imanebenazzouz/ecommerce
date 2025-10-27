#!/usr/bin/env python3
"""
Script de test manuel pour la validation des adresses
Lance une série de tests interactifs pour vérifier la validation des adresses
"""

import sys
import os

# Ajouter le chemin du backend (remonter de 2 niveaux depuis tests/integration/)
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))
sys.path.insert(0, backend_path)

from api import RegisterIn, UserUpdateIn
from pydantic import ValidationError


def test_address(address, description):
    """Teste une adresse et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"Test : {description}")
    print(f"Adresse : '{address}'")
    print(f"{'-'*60}")
    
    try:
        # Test avec RegisterIn
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "address": address
        }
        user = RegisterIn(**data)
        print(f"✅ VALIDE : '{user.address}'")
        
    except ValidationError as e:
        print(f"❌ INVALIDE")
        for error in e.errors():
            if 'address' in error['loc']:
                print(f"   Erreur : {error['msg']}")


def main():
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "TEST DE VALIDATION DES ADRESSES" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    
    # Tests d'adresses valides
    print("\n\n🟢 ADRESSES VALIDES")
    test_address("12 Rue des Fleurs, 75001 Paris", "Adresse parisienne classique")
    test_address("45 Avenue Victor Hugo, 69003 Lyon", "Adresse lyonnaise")
    test_address("3 Boulevard Gambetta, 31000 Toulouse", "Adresse toulousaine")
    test_address("100 Rue de la République 13001 Marseille", "Sans virgule")
    test_address("7 Place du Marché, Bordeaux 33000", "Code postal à la fin")
    test_address("  12 Rue des Fleurs, 75001 Paris  ", "Avec espaces (trimming)")
    
    # Tests d'adresses invalides
    print("\n\n🔴 ADRESSES INVALIDES")
    test_address("Paris", "Trop courte, pas de numéro")
    test_address("Rue Paris", "Pas de numéro")
    test_address("123", "Pas de lettres")
    test_address("123 456 789", "Que des chiffres")
    test_address("Rue des Fleurs Paris France", "Pas de numéro")
    test_address("12 Rue", "Trop courte")
    
    # Test avec UserUpdateIn (optionnel)
    print("\n\n🔵 TEST MISE À JOUR (OPTIONNEL)")
    print(f"\n{'='*60}")
    print(f"Test : Adresse None (doit être accepté)")
    print(f"Adresse : None")
    print(f"{'-'*60}")
    try:
        update = UserUpdateIn(address=None)
        print(f"✅ VALIDE : None est accepté pour la mise à jour")
    except ValidationError as e:
        print(f"❌ INVALIDE (ne devrait pas arriver)")
        for error in e.errors():
            print(f"   Erreur : {error['msg']}")
    
    # Résumé
    print("\n\n╔" + "="*58 + "╗")
    print("║" + " "*22 + "RÉSUMÉ" + " "*30 + "║")
    print("╚" + "="*58 + "╝")
    print("\nRègles de validation :")
    print("  ✓ Minimum 10 caractères")
    print("  ✓ Au moins 1 chiffre (numéro de rue ou code postal)")
    print("  ✓ Au moins 5 lettres (nom de rue et ville)")
    print("  ✓ Trimming automatique des espaces")
    print("\nFormat recommandé :")
    print("  [Numéro] [Nom de rue], [Code postal] [Ville]")
    print("\nExemple : 12 Rue des Fleurs, 75001 Paris")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrompu par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nErreur inattendue : {e}")
        sys.exit(1)

