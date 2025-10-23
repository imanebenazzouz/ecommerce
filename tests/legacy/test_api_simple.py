#!/usr/bin/env python3
"""
Test simple de l'API pour vérifier qu'elle fonctionne
"""

import sys
import os
sys.path.append('ecommerce-backend')

def test_api_import():
    """Test d'import de l'API"""
    try:
        # Test d'import des modules de base
        from database.database import get_db, SessionLocal, create_tables
        print("✅ Module database importé avec succès")
        
        from database.models import User, Product, Order
        print("✅ Modèles de base de données importés avec succès")
        
        from services.auth_service import AuthService
        print("✅ Service d'authentification importé avec succès")
        
        # Test de création d'une instance AuthService
        from database.repositories_simple import PostgreSQLUserRepository
        from database.database import SessionLocal
        
        db = SessionLocal()
        user_repo = PostgreSQLUserRepository(db)
        auth_service = AuthService(user_repo)
        print("✅ Instance AuthService créée avec succès")
        
        db.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import: {e}")
        return False

def test_database_connection():
    """Test de connexion à la base de données"""
    try:
        from database.database import SessionLocal, create_tables
        
        # Test de création de session
        db = SessionLocal()
        print("✅ Connexion à la base de données réussie")
        
        # Test de création des tables
        create_tables()
        print("✅ Tables créées avec succès")
        
        db.close()
        print("✅ Connexion fermée avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return False

def test_auth_service():
    """Test du service d'authentification"""
    try:
        from services.auth_service import AuthService
        from database.repositories_simple import PostgreSQLUserRepository
        from database.database import SessionLocal
        
        db = SessionLocal()
        user_repo = PostgreSQLUserRepository(db)
        auth_service = AuthService(user_repo)
        
        # Test de hachage de mot de passe
        password = "test123"
        hashed = auth_service.hash_password(password)
        print("✅ Hachage de mot de passe réussi")
        
        # Test de vérification de mot de passe
        is_valid = auth_service.verify_password(password, hashed)
        if is_valid:
            print("✅ Vérification de mot de passe réussie")
        else:
            print("❌ Vérification de mot de passe échouée")
            return False
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le service d'authentification: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 TEST SIMPLE DE L'API")
    print("=" * 50)
    
    # Test 1: Import des modules
    print("\n📦 Test d'import des modules...")
    import_success = test_api_import()
    
    if not import_success:
        print("❌ Les tests s'arrêtent ici car les imports ont échoué")
        return False
    
    # Test 2: Connexion à la base de données
    print("\n🗄️  Test de connexion à la base de données...")
    db_success = test_database_connection()
    
    # Test 3: Service d'authentification
    print("\n🔐 Test du service d'authentification...")
    auth_success = test_auth_service()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    print(f"📦 Import des modules: {'✅ RÉUSSI' if import_success else '❌ ÉCHOUÉ'}")
    print(f"🗄️  Base de données: {'✅ RÉUSSI' if db_success else '❌ ÉCHOUÉ'}")
    print(f"🔐 Service d'auth: {'✅ RÉUSSI' if auth_success else '❌ ÉCHOUÉ'}")
    
    overall_success = import_success and db_success and auth_success
    
    if overall_success:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("🚀 L'API est prête à fonctionner!")
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Veuillez corriger les erreurs")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
