#!/usr/bin/env python3
"""
Script pour supprimer toutes les commandes de tous les utilisateurs.

Ce script supprime :
- Tous les paiements (Payments)
- Toutes les factures (Invoices)
- Toutes les livraisons (Deliveries)
- Met à NULL les références order_id dans les threads de support (MessageThread)
- Tous les éléments de commande (OrderItems) - en cascade avec Orders
- Toutes les commandes (Orders)

ATTENTION : Cette opération est IRRÉVERSIBLE !
"""

import sys
import os

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ecommerce-backend'))

from sqlalchemy.orm import Session
from database.database import SessionLocal
from database.models import Order, OrderItem, Payment, Invoice, Delivery, MessageThread

def delete_all_orders():
    """
    Supprime toutes les commandes et leurs données associées.
    
    Ordre de suppression pour respecter les contraintes de clés étrangères :
    1. Payments (référencent order_id)
    2. Invoices (référencent order_id)
    3. Deliveries (référencent order_id)
    4. MessageThread (mettre order_id à NULL plutôt que supprimer)
    5. OrderItems (seront supprimés en cascade, mais on les supprime explicitement pour être sûr)
    6. Orders (suppression finale)
    """
    db: Session = SessionLocal()
    
    try:
        print("🗑️  Suppression de toutes les commandes...")
        
        # 1. Supprimer tous les paiements
        payments_count = db.query(Payment).count()
        if payments_count > 0:
            print(f"  → Suppression de {payments_count} paiement(s)...")
            db.query(Payment).delete()
            db.commit()
            print(f"  ✅ {payments_count} paiement(s) supprimé(s)")
        else:
            print("  ℹ️  Aucun paiement à supprimer")
        
        # 2. Supprimer toutes les factures
        invoices_count = db.query(Invoice).count()
        if invoices_count > 0:
            print(f"  → Suppression de {invoices_count} facture(s)...")
            db.query(Invoice).delete()
            db.commit()
            print(f"  ✅ {invoices_count} facture(s) supprimée(s)")
        else:
            print("  ℹ️  Aucune facture à supprimer")
        
        # 3. Supprimer toutes les livraisons
        deliveries_count = db.query(Delivery).count()
        if deliveries_count > 0:
            print(f"  → Suppression de {deliveries_count} livraison(s)...")
            db.query(Delivery).delete()
            db.commit()
            print(f"  ✅ {deliveries_count} livraison(s) supprimée(s)")
        else:
            print("  ℹ️  Aucune livraison à supprimer")
        
        # 4. Mettre à NULL les références order_id dans les threads de support
        # (on ne supprime pas les threads, juste la référence à la commande)
        threads_with_order = db.query(MessageThread).filter(MessageThread.order_id.isnot(None)).count()
        if threads_with_order > 0:
            print(f"  → Mise à NULL de {threads_with_order} référence(s) order_id dans les threads de support...")
            db.query(MessageThread).filter(MessageThread.order_id.isnot(None)).update(
                {"order_id": None},
                synchronize_session=False
            )
            db.commit()
            print(f"  ✅ {threads_with_order} référence(s) mise(s) à NULL")
        else:
            print("  ℹ️  Aucune référence order_id dans les threads de support")
        
        # 5. Supprimer tous les éléments de commande (OrderItems)
        order_items_count = db.query(OrderItem).count()
        if order_items_count > 0:
            print(f"  → Suppression de {order_items_count} élément(s) de commande...")
            db.query(OrderItem).delete()
            db.commit()
            print(f"  ✅ {order_items_count} élément(s) de commande supprimé(s)")
        else:
            print("  ℹ️  Aucun élément de commande à supprimer")
        
        # 6. Supprimer toutes les commandes (Orders)
        orders_count = db.query(Order).count()
        if orders_count > 0:
            print(f"  → Suppression de {orders_count} commande(s)...")
            db.query(Order).delete()
            db.commit()
            print(f"  ✅ {orders_count} commande(s) supprimée(s)")
        else:
            print("  ℹ️  Aucune commande à supprimer")
        
        print("\n✅ Suppression terminée avec succès !")
        print(f"   {orders_count} commande(s) supprimée(s) au total")
        
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
    print("SUPPRESSION DE TOUTES LES COMMANDES")
    print("=" * 60)
    print()
    print("⚠️  ATTENTION : Cette opération est IRRÉVERSIBLE !")
    print("   Toutes les commandes seront définitivement supprimées.")
    print()
    
    # Demander confirmation
    response = input("Voulez-vous continuer ? (tapez 'OUI' pour confirmer) : ")
    
    if response != "OUI":
        print("❌ Opération annulée.")
        sys.exit(0)
    
    print()
    success = delete_all_orders()
    
    if success:
        print("\n✅ Script terminé avec succès")
        sys.exit(0)
    else:
        print("\n❌ Le script a rencontré une erreur")
        sys.exit(1)

