"""
Script de migration pour ajouter la colonne paid_at à la table orders.
Ce script vérifie d'abord si la colonne existe avant de l'ajouter.
"""

import psycopg2
import os

# Configuration de la base de données
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'ecommerce'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def column_exists(cursor, table_name, column_name):
    """Vérifie si une colonne existe dans une table."""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns 
            WHERE table_name = %s 
            AND column_name = %s
        );
    """, (table_name, column_name))
    return cursor.fetchone()[0]

def migrate():
    """Ajoute les colonnes manquantes à la table orders."""
    print("🔄 Connexion à la base de données PostgreSQL...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("✅ Connexion réussie!")
        print("\n🔍 Vérification des colonnes de la table orders...")
        
        # Colonnes à vérifier/ajouter
        columns_to_add = {
            'paid_at': 'TIMESTAMP WITH TIME ZONE',
            'validated_at': 'TIMESTAMP WITH TIME ZONE',
            'shipped_at': 'TIMESTAMP WITH TIME ZONE',
            'delivered_at': 'TIMESTAMP WITH TIME ZONE',
            'cancelled_at': 'TIMESTAMP WITH TIME ZONE',
            'refunded_at': 'TIMESTAMP WITH TIME ZONE',
            'payment_id': 'UUID',
            'invoice_id': 'UUID',
            'delivery_id': 'UUID'
        }
        
        added_columns = []
        existing_columns = []
        
        for column_name, column_type in columns_to_add.items():
            if column_exists(cursor, 'orders', column_name):
                existing_columns.append(column_name)
                print(f"   ✓ La colonne '{column_name}' existe déjà")
            else:
                print(f"   ➕ Ajout de la colonne '{column_name}' ({column_type})...")
                
                # Ajouter la colonne
                cursor.execute(f"""
                    ALTER TABLE orders 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_type};
                """)
                
                added_columns.append(column_name)
                print(f"   ✅ Colonne '{column_name}' ajoutée avec succès!")
        
        # Commit des changements
        conn.commit()
        
        print("\n" + "="*60)
        print("📊 RÉSUMÉ DE LA MIGRATION")
        print("="*60)
        print(f"✅ Colonnes existantes : {len(existing_columns)}")
        for col in existing_columns:
            print(f"   - {col}")
        
        if added_columns:
            print(f"\n➕ Colonnes ajoutées : {len(added_columns)}")
            for col in added_columns:
                print(f"   - {col}")
        else:
            print("\n✅ Aucune colonne à ajouter, la table est à jour!")
        
        print("="*60)
        print("✅ Migration terminée avec succès!")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n❌ Erreur PostgreSQL : {e}")
        print(f"   Code d'erreur : {e.pgcode}")
        return False
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("="*60)
    print("🔧 MIGRATION DE LA TABLE ORDERS")
    print("="*60)
    print()
    
    success = migrate()
    
    if success:
        print("\n✅ Vous pouvez maintenant relancer votre application!")
    else:
        print("\n❌ La migration a échoué. Vérifiez les erreurs ci-dessus.")

