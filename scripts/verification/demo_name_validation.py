#!/usr/bin/env python3
"""
Démonstration interactive de la validation des noms et prénoms
Permet de tester différents noms en temps réel
"""

import sys
import os

# Ajouter le chemin du backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

from pydantic import ValidationError
from api import RegisterIn

def print_header():
    """Affiche l'en-tête du programme"""
    print("\n" + "=" * 70)
    print(" 🔍 DÉMONSTRATION - VALIDATION DES NOMS ET PRÉNOMS")
    print("=" * 70)
    print("\n📋 Règles de validation :")
    print("   ✅ Au moins 2 caractères")
    print("   ✅ Maximum 100 caractères")
    print("   ❌ AUCUN chiffre autorisé (0-9)")
    print("   ✅ Lettres, espaces, tirets (-) et apostrophes (') autorisés")
    print("   ✅ Accents français autorisés (é, è, ê, à, ç, etc.)")
    print("\n" + "-" * 70)

def test_name(first_name, last_name):
    """Teste un couple prénom/nom"""
    try:
        user = RegisterIn(
            email="test@example.com",
            password="Password123",
            first_name=first_name,
            last_name=last_name,
            address="12 Rue des Fleurs, 75001 Paris"
        )
        print(f"\n✅ VALIDE : {user.first_name} {user.last_name}")
        return True
    except ValidationError as e:
        print(f"\n❌ INVALIDE :")
        for error in e.errors():
            field = "Prénom" if error['loc'][0] == 'first_name' else "Nom"
            print(f"   - {field} : {error['msg']}")
        return False

def run_examples():
    """Exécute des exemples prédéfinis"""
    print("\n📝 Exemples de validation :\n")
    
    examples = [
        ("Jean", "Dupont", "Noms simples"),
        ("Jean-Claude", "O'Connor", "Noms composés avec tiret et apostrophe"),
        ("François", "Müller", "Noms avec accents"),
        ("Marie Anne", "Le Blanc", "Noms avec espaces"),
        ("Jean123", "Dupont", "❌ Prénom avec chiffres"),
        ("Marie", "Dubois99", "❌ Nom avec chiffres"),
        ("J", "Dupont", "❌ Prénom trop court"),
        ("Jean@", "Dupont", "❌ Prénom avec symbole interdit"),
    ]
    
    for first_name, last_name, description in examples:
        print(f"\n{description} : {first_name} {last_name}")
        test_name(first_name, last_name)

def interactive_mode():
    """Mode interactif pour tester ses propres noms"""
    print("\n" + "=" * 70)
    print(" 🎯 MODE INTERACTIF")
    print("=" * 70)
    print("\nTestez vos propres noms et prénoms !")
    print("(Tapez 'q' pour quitter)\n")
    
    while True:
        print("-" * 70)
        first_name = input("\nEntrez un prénom (ou 'q' pour quitter) : ").strip()
        
        if first_name.lower() == 'q':
            break
        
        if not first_name:
            print("⚠️  Le prénom ne peut pas être vide")
            continue
        
        last_name = input("Entrez un nom : ").strip()
        
        if not last_name:
            print("⚠️  Le nom ne peut pas être vide")
            continue
        
        test_name(first_name, last_name)

def main():
    """Point d'entrée principal"""
    print_header()
    
    print("\nChoisissez une option :")
    print("1. Voir des exemples de validation")
    print("2. Mode interactif (tester vos propres noms)")
    print("3. Voir les deux")
    print("q. Quitter")
    
    choice = input("\nVotre choix (1/2/3/q) : ").strip()
    
    if choice == '1':
        run_examples()
    elif choice == '2':
        interactive_mode()
    elif choice == '3':
        run_examples()
        interactive_mode()
    elif choice.lower() == 'q':
        print("\n👋 Au revoir !\n")
        return
    else:
        print("\n⚠️  Choix invalide")
        return
    
    print("\n" + "=" * 70)
    print(" ✅ Démonstration terminée")
    print("=" * 70)
    print("\n💡 Pour tester dans l'application :")
    print("   - Page d'inscription : http://localhost:5173/register")
    print("   - Page de profil : http://localhost:5173/profile")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programme interrompu. Au revoir !\n")
        sys.exit(0)

