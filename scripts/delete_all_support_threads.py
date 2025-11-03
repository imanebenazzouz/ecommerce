#!/usr/bin/env python3
"""
Script pour supprimer toutes les conversations de support.

Ce script supprime :
- Tous les messages (Messages)
- Tous les fils de discussion (MessageThread)

ATTENTION : Cette opération est IRRÉVERSIBLE !
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ecommerce-backend'))

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Message, MessageThread

def delete_all_support_threads():
    """
    Supprime toutes les conversations de support et leurs messages.
    
    Ordre de suppression pour respecter les contraintes de clés étrangères :
    1. Messages (référencent message_threads.id)
    2. MessageThread (fils de discussion)
    """
    db: Session = SessionLocal()
    
    try:
        print("🗑️  Suppression de toutes les conversations de support...")
        
        # 1. Supprimer tous les messages
        messages_count = db.query(Message).count()
        if messages_count > 0:
            print(f"  → Suppression de {messages_count} message(s)...")
            db.query(Message).delete()
            db.commit()
            print(f"  ✅ {messages_count} message(s) supprimé(s)")
        else:
            print("  ℹ️  Aucun message à supprimer")
        
        # 2. Supprimer tous les fils de discussion
        threads_count = db.query(MessageThread).count()
        if threads_count > 0:
            print(f"  → Suppression de {threads_count} fil(s) de discussion...")
            db.query(MessageThread).delete()
            db.commit()
            print(f"  ✅ {threads_count} fil(s) de discussion supprimé(s)")
        else:
            print("  ℹ️  Aucun fil de discussion à supprimer")
        
        print("\n✅ Suppression terminée avec succès !")
        print(f"   {threads_count} conversation(s) supprimée(s) au total")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erreur lors de la suppression : {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("SUPPRESSION DE TOUTES LES CONVERSATIONS DE SUPPORT")
    print("=" * 60)
    print()
    print("⚠️  ATTENTION : Cette opération est IRRÉVERSIBLE !")
    print("   Toutes les conversations seront définitivement supprimées.")
    print()
    
    # Demander confirmation
    response = input("Voulez-vous continuer ? (tapez 'OUI' pour confirmer) : ")
    
    if response != "OUI":
        print("❌ Opération annulée.")
        sys.exit(0)
    
    print()
    success = delete_all_support_threads()
    
    if success:
        print("\n✅ Script terminé avec succès")
        sys.exit(0)
    else:
        print("\n❌ Le script a rencontré une erreur")
        sys.exit(1)

