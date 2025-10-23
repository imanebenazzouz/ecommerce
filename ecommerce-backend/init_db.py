#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
"""

import os
import sys
from database.database import create_tables, engine
from database.models import Base
from database.repositories_simple import PostgreSQLUserRepository, PostgreSQLProductRepository
from services.auth_service import AuthService
from sqlalchemy.orm import sessionmaker

def init_database():
    """Initialise la base de données avec les tables et données de base"""
    print("🚀 Initialisation de la base de données...")
    
    # Créer toutes les tables
    print("📋 Création des tables...")
    create_tables()
    print("✅ Tables créées avec succès")
    
    # Créer une session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Créer les repositories
        user_repo = PostgreSQLUserRepository(db)
        product_repo = PostgreSQLProductRepository(db)
        auth_service = AuthService(user_repo)
        
        # Vérifier si l'admin existe déjà
        admin = user_repo.get_by_email("admin@ecommerce.com")
        if not admin:
            print("👤 Création de l'utilisateur administrateur...")
            admin_data = {
                "email": "admin@ecommerce.com",
                "password_hash": auth_service.hash_password("admin123"),
                "first_name": "Admin",
                "last_name": "System",
                "address": "1 Admin Street, 75001 Paris",
                "is_admin": True
            }
            user_repo.create(admin_data)
            print("✅ Administrateur créé")
        else:
            print("ℹ️  Administrateur existe déjà")
        
        # Vérifier si des produits existent déjà
        products = product_repo.get_all()
        if not products:
            print("🛍️  Création des produits de démonstration...")
            demo_products = [
                {
                    "name": "T-Shirt Premium",
                    "description": "T-shirt en coton bio de haute qualité",
                    "price_cents": 2999,
                    "stock_qty": 100,
                    "active": True
                },
                {
                    "name": "Sweat Capuche",
                    "description": "Sweat-shirt à capuche confortable",
                    "price_cents": 4999,
                    "stock_qty": 50,
                    "active": True
                },
                {
                    "name": "Casquette Logo",
                    "description": "Casquette avec logo brodé",
                    "price_cents": 1999,
                    "stock_qty": 75,
                    "active": True
                },
                {
                    "name": "Jean Slim",
                    "description": "Jean slim en denim stretch",
                    "price_cents": 7999,
                    "stock_qty": 30,
                    "active": True
                },
                {
                    "name": "Veste Denim",
                    "description": "Veste en denim classique",
                    "price_cents": 8999,
                    "stock_qty": 25,
                    "active": True
                }
            ]
            
            for product_data in demo_products:
                product_repo.create(product_data)
            print("✅ Produits de démonstration créés")
        else:
            print("ℹ️  Produits existent déjà")
        
        print("🎉 Initialisation terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
