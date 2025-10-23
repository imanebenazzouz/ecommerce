#!/usr/bin/env python3
"""
Script de test pour vérifier que toutes les corrections ont été appliquées
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'ecommerce-backend'))

def test_imports():
    """Test que tous les imports fonctionnent"""
    try:
        from ecommerce_backend.database.models import User, Product, Order, OrderItem, Delivery, Invoice, Payment, MessageThread, Message
        from ecommerce_backend.database.repositories_simple import (
            PostgreSQLUserRepository, PostgreSQLProductRepository, 
            PostgreSQLCartRepository, PostgreSQLOrderRepository,
            PostgreSQLInvoiceRepository, PostgreSQLPaymentRepository,
            PostgreSQLThreadRepository
        )
        from ecommerce_backend.services.auth_service import AuthService
        from ecommerce_backend.enums import OrderStatus, DeliveryStatus
        print("✅ Tous les imports fonctionnent")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_models():
    """Test que les modèles sont correctement définis"""
    try:
        from ecommerce_backend.database.models import User, Product, Order, MessageThread, Message
        
        # Test que les champs optionnels sont bien optionnels
        user = User()
        assert hasattr(user, 'id')
        assert hasattr(user, 'email')
        assert hasattr(user, 'password_hash')
        
        # Test MessageThread avec order_id optionnel
        thread = MessageThread()
        assert hasattr(thread, 'order_id')
        assert hasattr(thread, 'closed')
        
        # Test Message avec author_user_id optionnel
        message = Message()
        assert hasattr(message, 'author_user_id')
        
        print("✅ Modèles correctement définis")
        return True
    except Exception as e:
        print(f"❌ Erreur dans les modèles: {e}")
        return False

def test_auth_service():
    """Test que le service d'authentification fonctionne"""
    try:
        from ecommerce_backend.services.auth_service import AuthService
        
        # Vérifier que la méthode register existe
        assert hasattr(AuthService, 'register')
        assert hasattr(AuthService, 'authenticate_user')
        assert hasattr(AuthService, 'create_access_token')
        assert hasattr(AuthService, 'verify_token')
        
        print("✅ Service d'authentification correct")
        return True
    except Exception as e:
        print(f"❌ Erreur dans le service d'authentification: {e}")
        return False

def test_repositories():
    """Test que les repositories sont correctement définis"""
    try:
        from ecommerce_backend.database.repositories_simple import PostgreSQLProductRepository
        
        # Vérifier que la méthode update prend un objet Product
        import inspect
        sig = inspect.signature(PostgreSQLProductRepository.update)
        params = list(sig.parameters.keys())
        assert 'product' in params
        
        print("✅ Repositories correctement définis")
        return True
    except Exception as e:
        print(f"❌ Erreur dans les repositories: {e}")
        return False

def test_enums():
    """Test que les enums sont correctement définis"""
    try:
        from ecommerce_backend.enums import OrderStatus, DeliveryStatus
        
        # Vérifier que les statuts existent
        assert OrderStatus.CREE == "CREE"
        assert OrderStatus.VALIDEE == "VALIDEE"
        assert OrderStatus.PAYEE == "PAYEE"
        assert OrderStatus.EXPEDIEE == "EXPEDIEE"
        assert OrderStatus.LIVREE == "LIVREE"
        assert OrderStatus.ANNULEE == "ANNULEE"
        assert OrderStatus.REMBOURSEE == "REMBOURSEE"
        
        assert DeliveryStatus.PREPAREE == "PREPAREE"
        assert DeliveryStatus.EN_COURS == "EN_COURS"
        assert DeliveryStatus.LIVREE == "LIVREE"
        
        print("✅ Enums correctement définis")
        return True
    except Exception as e:
        print(f"❌ Erreur dans les enums: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🧪 Test des corrections appliquées...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_models,
        test_auth_service,
        test_repositories,
        test_enums
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Toutes les corrections ont été appliquées avec succès!")
        return True
    else:
        print("⚠️  Certaines corrections nécessitent encore du travail")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
