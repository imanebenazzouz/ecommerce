#!/usr/bin/env python3
"""
Script de test pour vérifier tous les imports
"""

import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Teste tous les imports nécessaires"""
    print("🔍 Test des imports...")
    
    try:
        from sqlalchemy.orm import Session
        print("✅ SQLAlchemy import réussi")
    except ImportError as e:
        print(f"❌ Erreur import SQLAlchemy: {e}")
        return False
    
    try:
        from database.database import get_db, SessionLocal, create_tables
        print("✅ Database imports réussi")
    except ImportError as e:
        print(f"❌ Erreur import database: {e}")
        return False
    
    try:
        from database.models import User, Product, Order, OrderItem, Delivery, Invoice, Payment, MessageThread, Message
        print("✅ Models imports réussi")
    except ImportError as e:
        print(f"❌ Erreur import models: {e}")
        return False
    
    try:
        from database.repositories_simple import (
            PostgreSQLUserRepository, PostgreSQLProductRepository, 
            PostgreSQLCartRepository, PostgreSQLOrderRepository,
            PostgreSQLInvoiceRepository, PostgreSQLPaymentRepository,
            PostgreSQLThreadRepository
        )
        print("✅ Repositories imports réussi")
    except ImportError as e:
        print(f"❌ Erreur import repositories: {e}")
        return False
    
    try:
        from services.auth_service import AuthService
        print("✅ Services imports réussi")
    except ImportError as e:
        print(f"❌ Erreur import services: {e}")
        return False
    
    try:
        from enums import OrderStatus, DeliveryStatus
        print("✅ Enums imports réussi")
    except ImportError as e:
        print(f"❌ Erreur import enums: {e}")
        return False
    
    return True

def test_database_connection():
    """Teste la connexion à la base de données"""
    print("\n🔍 Test de la connexion à la base de données...")
    
    try:
        from database.database import engine, create_tables
        from sqlalchemy import text
        
        # Tester la connexion
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Connexion à la base de données réussie")
        
        # Créer les tables si nécessaire
        create_tables()
        print("✅ Tables créées/vérifiées")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def test_api_creation():
    """Teste la création de l'API FastAPI"""
    print("\n🔍 Test de la création de l'API...")
    
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        app = FastAPI(title="Test API")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        print("✅ API FastAPI créée avec succès")
        return True
    except Exception as e:
        print(f"❌ Erreur création API: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test complet de l'environnement")
    print("=" * 50)
    
    # Test des imports
    if not test_imports():
        print("\n❌ Échec des tests d'import")
        return
    
    # Test de la base de données
    if not test_database_connection():
        print("\n❌ Échec des tests de base de données")
        return
    
    # Test de l'API
    if not test_api_creation():
        print("\n❌ Échec des tests d'API")
        return
    
    print("\n" + "=" * 50)
    print("✅ Tous les tests sont passés avec succès!")
    print("🎉 L'environnement est prêt pour l'API")

if __name__ == "__main__":
    main()
