#!/usr/bin/env python3
"""
Script pour lister et rechercher des utilisateurs dans la base de données.

Usage:
    python list_users.py                    # Liste tous les utilisateurs
    python list_users.py --email imane      # Cherche par email
    python list_users.py --admin            # Liste seulement les admins
    python list_users.py --real             # Liste seulement les vrais users
"""

import sys
from database.database import SessionLocal
from database.models import User

def list_all_users():
    """Liste tous les utilisateurs."""
    db = SessionLocal()
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    print(f"\n📊 Total : {len(users)} utilisateurs\n")
    print("="*100)
    
    for u in users:
        admin_badge = "👑 ADMIN" if u.is_admin else "👤 Client"
        print(f"{admin_badge} | {u.email:45} | {u.first_name} {u.last_name}")
        print(f"{'':8} ID: {u.id}")
        print(f"{'':8} Adresse: {u.address}")
        print(f"{'':8} Créé: {u.created_at.strftime('%d/%m/%Y %H:%M')}")
        print()

def search_by_email(search_term):
    """Recherche des utilisateurs par email."""
    db = SessionLocal()
    users = db.query(User).filter(User.email.ilike(f"%{search_term}%")).all()
    
    print(f"\n🔍 Résultats pour '{search_term}' : {len(users)} utilisateur(s)\n")
    print("="*100)
    
    for u in users:
        admin_badge = "👑 ADMIN" if u.is_admin else "👤 Client"
        print(f"{admin_badge} | {u.email:45} | {u.first_name} {u.last_name}")
        print(f"{'':8} ID: {u.id}")
        print(f"{'':8} Adresse: {u.address}")
        print(f"{'':8} Créé: {u.created_at.strftime('%d/%m/%Y %H:%M')}")
        print()

def list_admins():
    """Liste uniquement les administrateurs."""
    db = SessionLocal()
    users = db.query(User).filter(User.is_admin == True).all()
    
    print(f"\n👑 Administrateurs : {len(users)}\n")
    print("="*100)
    
    for u in users:
        print(f"👑 {u.email:45} | {u.first_name} {u.last_name}")
        print(f"{'':8} ID: {u.id}")
        print(f"{'':8} Créé: {u.created_at.strftime('%d/%m/%Y %H:%M')}")
        print()

def list_real_users():
    """Liste uniquement les utilisateurs réels (non-test)."""
    db = SessionLocal()
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    # Filtrer les utilisateurs de test
    test_keywords = ['test', '@test.com', '_test_', 'example.com']
    real_users = []
    
    for u in users:
        is_real = True
        # Garder certains emails example.com comme réels
        if any(email in u.email for email in ['admin@example.com', 'client@example.com', 
                                                'imane@example.com', 'imane1@example.com', 
                                                'imane2@example.com']):
            real_users.append(u)
            continue
            
        # Filtrer les autres
        for keyword in test_keywords:
            if keyword in u.email.lower():
                is_real = False
                break
        
        if is_real:
            real_users.append(u)
    
    print(f"\n✅ Utilisateurs réels : {len(real_users)}\n")
    print("="*100)
    
    for u in real_users:
        admin_badge = "👑 ADMIN" if u.is_admin else "👤 Client"
        print(f"{admin_badge} | {u.email:45} | {u.first_name} {u.last_name}")
        print(f"{'':8} ID: {u.id}")
        print(f"{'':8} Adresse: {u.address}")
        print(f"{'':8} Créé: {u.created_at.strftime('%d/%m/%Y %H:%M')}")
        print()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Pas d'arguments : liste tous les users
        list_all_users()
    elif "--email" in sys.argv:
        # Recherche par email
        idx = sys.argv.index("--email")
        if idx + 1 < len(sys.argv):
            search_by_email(sys.argv[idx + 1])
        else:
            print("❌ Erreur : Veuillez fournir un terme de recherche")
    elif "--admin" in sys.argv:
        # Liste seulement les admins
        list_admins()
    elif "--real" in sys.argv:
        # Liste seulement les vrais users
        list_real_users()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
    else:
        print("❌ Argument inconnu. Utilisez --help pour l'aide.")

