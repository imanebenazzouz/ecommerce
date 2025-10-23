#!/usr/bin/env python3
"""
Test de connexion à la base de données PostgreSQL
"""

import os
import sys
sys.path.append('ecommerce-backend')

# Définir les variables d'environnement
os.environ['DATABASE_URL'] = 'postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce'

from ecommerce_backend.database.database import engine, get_db
from sqlalchemy import text

def test_connection():
    """Test de connexion à la base de données"""
    try:
        print("🔍 Test de connexion à PostgreSQL...")
        
        # Test avec le moteur SQLAlchemy
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connexion réussie!")
            print(f"📊 Version PostgreSQL: {version}")
            
            # Test des tables
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 Tables disponibles: {tables}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    test_connection()
