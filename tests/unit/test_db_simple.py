#!/usr/bin/env python3
"""
Test simple de connexion à la base de données PostgreSQL
"""

import psycopg2
import os
from datetime import datetime

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce")

def test_connection():
    """Test de connexion à la base de données"""
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("✅ Connexion à PostgreSQL réussie")
        
        # Test de création de table simple
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Test d'insertion
        cursor.execute("""
            INSERT INTO test_table (name) VALUES (%s)
        """, ("Test " + str(datetime.now()),))
        
        # Test de sélection
        cursor.execute("SELECT * FROM test_table ORDER BY created_at DESC LIMIT 5")
        results = cursor.fetchall()
        
        print(f"✅ Table créée et données insérées. {len(results)} enregistrements trouvés:")
        for row in results:
            print(f"  - ID: {row[0]}, Name: {row[1]}, Created: {row[2]}")
        
        # Test de création des tables principales
        create_main_tables(cursor)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Tous les tests de base de données ont réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def create_main_tables(cursor):
    """Créer les tables principales de l'application"""
    
    # Table des utilisateurs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            address TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table des produits
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price_cents INTEGER NOT NULL,
            stock_qty INTEGER NOT NULL DEFAULT 0,
            active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table des commandes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            status VARCHAR(50) NOT NULL DEFAULT 'CREE',
            total_cents INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table des articles de commande
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            order_id UUID NOT NULL REFERENCES orders(id),
            panier_id UUID NOT NULL REFERENCES carts(id),
            product_id UUID NOT NULL REFERENCES products(id),
            name VARCHAR(255) NOT NULL,
            unit_price_cents INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table des paniers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Table des articles de panier
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            cart_id UUID NOT NULL REFERENCES carts(id),
            product_id UUID NOT NULL REFERENCES products(id),
            quantity INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("✅ Tables principales créées avec succès")

def init_sample_data(cursor):
    """Initialiser les données d'exemple"""
    
    # Vérifier si des données existent déjà
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]
    
    if user_count == 0:
        # Créer des utilisateurs d'exemple
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, address, is_admin)
            VALUES 
                ('admin@example.com', 'admin', 'Admin', 'Root', '1 Rue du BO', TRUE),
                ('client@example.com', 'secret', 'Alice', 'Martin', '12 Rue des Fleurs', FALSE)
        """)
        print("✅ Utilisateurs d'exemple créés")
    
    if product_count == 0:
        # Créer des produits d'exemple
        cursor.execute("""
            INSERT INTO products (name, description, price_cents, stock_qty, active)
            VALUES 
                ('T-Shirt Logo', 'Coton bio', 1999, 100, TRUE),
                ('Sweat Capuche', 'Molleton', 4999, 50, TRUE)
        """)
        print("✅ Produits d'exemple créés")

if __name__ == "__main__":
    print("🧪 Test de connexion à la base de données PostgreSQL...")
    print(f"📡 URL de connexion: {DATABASE_URL}")
    
    if test_connection():
        print("\n🎉 La base de données est opérationnelle !")
        print("💾 Les données sont maintenant stockées dans PostgreSQL")
    else:
        print("\n💥 Échec du test de base de données")
