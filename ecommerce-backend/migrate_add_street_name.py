#!/usr/bin/env python3
"""
Script de migration pour ajouter le champ street_name à la table payments
"""

import os
import sys
import psycopg2
from psycopg2 import sql

def migrate_add_street_name():
    """Ajoute la colonne street_name à la table payments"""
    
    # Configuration de la base de données
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce")
    
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("🔄 Migration: Ajout de la colonne street_name à la table payments...")
        
        # Vérifier si la colonne existe déjà
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='payments' AND column_name='street_name'
        """)
        
        if cursor.fetchone():
            print("✅ La colonne street_name existe déjà dans la table payments")
        else:
            # Ajouter la colonne street_name
            cursor.execute("""
                ALTER TABLE payments 
                ADD COLUMN street_name VARCHAR(100)
            """)
            
            conn.commit()
            print("✅ Colonne street_name ajoutée avec succès à la table payments")
        
        cursor.close()
        conn.close()
        print("🎉 Migration terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_add_street_name()

