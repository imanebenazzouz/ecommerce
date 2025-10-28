#!/usr/bin/env python3
"""
Script de test pour vérifier que tous les services métier fonctionnent correctement.

Ce script teste :
- Initialisation des services
- Création d'utilisateurs
- Gestion des produits
- Gestion des paniers
- Gestion des commandes
- Gestion des paiements
- Gestion des livraisons
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, create_tables
from services import get_service_container
from enums import OrderStatus, DeliveryStatus


def test_services():
    """Teste tous les services métier."""
    print("🧪 Test des services métier...")
    
    # Créer les tables
    create_tables()
    
    # Créer une session de base de données
    db = SessionLocal()
    
    try:
        # Initialiser le conteneur de services
        services = get_service_container(db)
        print("✅ Conteneur de services initialisé")
        
        # Test du service d'authentification
        print("\n🔐 Test du service d'authentification...")
        auth_service = services.get_auth_service()
        
        # Créer un utilisateur de test
        user = auth_service.register(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            address="123 Test Street"
        )
        print(f"✅ Utilisateur créé: {user.email}")
        
        # Test de connexion
        token = auth_service.login("test@example.com", "password123")
        print(f"✅ Connexion réussie: {token}")
        
        # Test du service de catalogue
        print("\n📦 Test du service de catalogue...")
        catalog_service = services.get_catalog_service()
        
        # Créer un produit de test
        product_data = {
            "name": "Produit Test",
            "description": "Description du produit test",
            "price_cents": 1999,  # 19.99€
            "stock_qty": 10,
            "active": True
        }
        product = catalog_service.product_repo.create(product_data)
        print(f"✅ Produit créé: {product.name}")
        
        # Test du service de panier
        print("\n🛒 Test du service de panier...")
        cart_service = services.get_cart_service()
        
        # Ajouter un produit au panier
        cart_service.add_to_cart(str(user.id), str(product.id), 2)
        print("✅ Produit ajouté au panier")
        
        # Vérifier le total du panier
        total = cart_service.get_cart_total(str(user.id))
        print(f"✅ Total du panier: {total/100:.2f}€")
        
        # Test du service de commandes
        print("\n📋 Test du service de commandes...")
        order_service = services.get_order_service()
        
        # Créer une commande
        order = order_service.checkout(str(user.id))
        print(f"✅ Commande créée: {order.id}")
        
        # Test du service de paiement
        print("\n💳 Test du service de paiement...")
        payment_service = services.get_payment_service()
        
        # Simuler un paiement
        payment_data = {
            "card_number": "4242424242424242",
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0123456789",
            "street_number": "123",
            "street_name": "Test Street"
        }
        
        payment = order_service.pay_by_card(str(order.id), **payment_data)
        print(f"✅ Paiement traité: {payment.status}")
        
        # Test du service de livraison
        print("\n🚚 Test du service de livraison...")
        delivery_service = services.get_delivery_service()
        
        # Préparer la livraison
        delivery = delivery_service.prepare_delivery(str(order.id))
        print(f"✅ Livraison préparée: {delivery.id}")
        
        # Expédier la commande
        delivery = delivery_service.ship_order(str(order.id))
        print(f"✅ Commande expédiée: {delivery.tracking_number}")
        
        # Test du service de facturation
        print("\n🧾 Test du service de facturation...")
        billing_service = services.get_billing_service()
        
        # Récupérer la facture
        invoice = billing_service.get_invoice_by_order(str(order.id))
        print(f"✅ Facture récupérée: {invoice.id}")
        
        # Test du service de support client
        print("\n🎧 Test du service de support client...")
        customer_service = services.get_customer_service()
        
        # Créer un fil de support
        thread = customer_service.open_thread(
            str(user.id), 
            "Question sur ma commande", 
            str(order.id)
        )
        print(f"✅ Fil de support créé: {thread.id}")
        
        # Ajouter un message
        message = customer_service.post_message(
            str(thread.id), 
            str(user.id), 
            "Bonjour, j'ai une question sur ma commande."
        )
        print(f"✅ Message ajouté: {message.id}")
        
        print("\n🎉 Tous les tests sont passés avec succès !")
        print("\n📊 Résumé des fonctionnalités testées :")
        print("  ✅ Authentification et gestion des utilisateurs")
        print("  ✅ Gestion du catalogue de produits")
        print("  ✅ Gestion des paniers")
        print("  ✅ Création et gestion des commandes")
        print("  ✅ Traitement des paiements")
        print("  ✅ Gestion des livraisons")
        print("  ✅ Génération de factures")
        print("  ✅ Support client")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    success = test_services()
    sys.exit(0 if success else 1)
