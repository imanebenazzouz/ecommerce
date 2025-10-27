"""
Script de test pour vérifier que les données de paiement sont bien enregistrées
"""
import sys
import os

# Ajouter le chemin du backend (remonter de 2 niveaux depuis tests/unit/)
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../ecommerce-backend'))
sys.path.insert(0, backend_path)

from database.database import SessionLocal
from sqlalchemy import text

def test_payment_storage():
    print("🧪 Test : Vérification du stockage des données de paiement\n")
    
    db = SessionLocal()
    try:
        # Récupérer le dernier paiement
        result = db.execute(text("""
            SELECT 
                id, 
                order_id, 
                amount_cents, 
                status, 
                card_last4, 
                postal_code, 
                phone, 
                street_number,
                created_at
            FROM payments 
            ORDER BY created_at DESC 
            LIMIT 1
        """))
        
        payment = result.fetchone()
        
        if not payment:
            print("⚠️  Aucun paiement trouvé dans la base de données")
            print("   Effectuez un paiement de test via l'interface web")
            return
        
        print("✅ Dernier paiement trouvé :\n")
        print(f"  🆔 ID             : {payment[0]}")
        print(f"  📦 Commande       : {payment[1]}")
        print(f"  💰 Montant        : {payment[2] / 100:.2f} €")
        print(f"  📊 Statut         : {payment[3]}")
        print(f"  💳 Carte (4 der.) : {payment[4] or '❌ Non enregistré'}")
        print(f"  📮 Code postal    : {payment[5] or '❌ Non enregistré'}")
        print(f"  📞 Téléphone      : {payment[6] or '❌ Non enregistré'}")
        print(f"  🏠 N° de rue      : {payment[7] or '❌ Non enregistré'}")
        print(f"  📅 Date           : {payment[8]}")
        
        # Vérifier que les champs sont remplis
        print("\n" + "="*60)
        if payment[4] and payment[5] and payment[6] and payment[7]:
            print("✅ SUCCÈS : Toutes les données de paiement sont enregistrées !")
        else:
            print("⚠️  ATTENTION : Certaines données manquent")
            if not payment[4]:
                print("   ❌ Carte manquante")
            if not payment[5]:
                print("   ❌ Code postal manquant")
            if not payment[6]:
                print("   ❌ Téléphone manquant")
            if not payment[7]:
                print("   ❌ N° de rue manquant")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_payment_storage()

