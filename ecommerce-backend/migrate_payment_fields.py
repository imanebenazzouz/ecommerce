"""
Script de migration pour ajouter les champs de détails de paiement
"""
from database.database import engine
from sqlalchemy import text

def migrate():
    print("🔄 Migration : Ajout des champs de paiement...")
    
    with engine.connect() as connection:
        try:
            # Vérifier si les colonnes existent déjà
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'payments' 
                AND column_name IN ('card_last4', 'postal_code', 'phone', 'street_number')
            """))
            
            existing_columns = {row[0] for row in result}
            
            # Ajouter les colonnes manquantes
            columns_to_add = {
                'card_last4': 'VARCHAR(4)',
                'postal_code': 'VARCHAR(5)',
                'phone': 'VARCHAR(10)',
                'street_number': 'VARCHAR(10)'
            }
            
            for col_name, col_type in columns_to_add.items():
                if col_name not in existing_columns:
                    print(f"  ➕ Ajout de la colonne {col_name}...")
                    connection.execute(text(f"""
                        ALTER TABLE payments 
                        ADD COLUMN {col_name} {col_type}
                    """))
                    connection.commit()
                else:
                    print(f"  ✅ Colonne {col_name} déjà présente")
            
            print("✅ Migration terminée avec succès !")
            
        except Exception as e:
            print(f"❌ Erreur lors de la migration : {e}")
            connection.rollback()
            raise

if __name__ == "__main__":
    migrate()

