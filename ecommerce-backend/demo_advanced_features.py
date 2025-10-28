#!/usr/bin/env python3
"""
Script de démonstration des fonctionnalités avancées du squelette backend.

Ce script démontre toutes les fonctionnalités implémentées :
- Services métier avec architecture en couches
- Gestion avancée des paiements avec gateway
- Système de livraison avec tracking
- Facturation automatique
- Gestion des remboursements
- Support client complet
- Sécurité des mots de passe avec bcrypt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal, create_tables
from services import get_service_container
from enums import OrderStatus, DeliveryStatus


def demo_advanced_features():
    """Démonstration des fonctionnalités avancées."""
    print("🚀 DÉMONSTRATION DES FONCTIONNALITÉS AVANCÉES")
    print("=" * 60)
    
    # Créer les tables
    create_tables()
    
    # Créer une session de base de données
    db = SessionLocal()
    
    try:
        # Initialiser le conteneur de services
        services = get_service_container(db)
        print("✅ Architecture en services métier initialisée")
        
        # ========== DÉMONSTRATION 1: AUTHENTIFICATION SÉCURISÉE ==========
        print("\n🔐 1. AUTHENTIFICATION SÉCURISÉE")
        print("-" * 40)
        
        auth_service = services.get_auth_service()
        
        # Créer un utilisateur admin
        admin = auth_service.register(
            email="admin@ecommerce.com",
            password="admin123",
            first_name="Admin",
            last_name="User",
            address="1 Admin Street"
        )
        admin.is_admin = True
        services.user_repo.update(admin)
        print(f"✅ Admin créé: {admin.email}")
        
        # Créer un client
        client = auth_service.register(
            email="client@ecommerce.com",
            password="client123",
            first_name="Client",
            last_name="User",
            address="123 Client Street"
        )
        print(f"✅ Client créé: {client.email}")
        
        # ========== DÉMONSTRATION 2: CATALOGUE AVANCÉ ==========
        print("\n📦 2. GESTION DU CATALOGUE")
        print("-" * 40)
        
        catalog_service = services.get_catalog_service()
        
        # Créer plusieurs produits
        products_data = [
            {
                "name": "iPhone 15 Pro",
                "description": "Dernier iPhone avec caméra 48MP",
                "price_cents": 119900,  # 1199€
                "stock_qty": 5,
                "active": True
            },
            {
                "name": "MacBook Pro M3",
                "description": "Ordinateur portable professionnel",
                "price_cents": 249900,  # 2499€
                "stock_qty": 3,
                "active": True
            },
            {
                "name": "AirPods Pro",
                "description": "Écouteurs sans fil avec réduction de bruit",
                "price_cents": 27900,  # 279€
                "stock_qty": 20,
                "active": True
            }
        ]
        
        products = []
        for product_data in products_data:
            product = catalog_service.product_repo.create(product_data)
            products.append(product)
            print(f"✅ Produit créé: {product.name} - {product.price_cents/100:.2f}€")
        
        # ========== DÉMONSTRATION 3: PANIER INTELLIGENT ==========
        print("\n🛒 3. GESTION DU PANIER")
        print("-" * 40)
        
        cart_service = services.get_cart_service()
        
        # Ajouter des produits au panier
        cart_service.add_to_cart(str(client.id), str(products[0].id), 1)  # iPhone
        cart_service.add_to_cart(str(client.id), str(products[2].id), 2)  # AirPods x2
        print("✅ Produits ajoutés au panier")
        
        # Calculer le total
        total = cart_service.get_cart_total(str(client.id))
        print(f"✅ Total du panier: {total/100:.2f}€")
        
        # ========== DÉMONSTRATION 4: COMMANDE AVANCÉE ==========
        print("\n📋 4. GESTION DES COMMANDES")
        print("-" * 40)
        
        order_service = services.get_order_service()
        
        # Créer une commande
        order = order_service.checkout(str(client.id))
        print(f"✅ Commande créée: {str(order.id)[:8]}...")
        print(f"   Statut: {order.status}")
        print(f"   Total: {order.total_cents()/100:.2f}€")
        
        # ========== DÉMONSTRATION 5: PAIEMENT AVANCÉ ==========
        print("\n💳 5. SYSTÈME DE PAIEMENT")
        print("-" * 40)
        
        # Simuler un paiement réussi
        payment_data = {
            "card_number": "4242424242424242",  # Carte valide
            "exp_month": 12,
            "exp_year": 2030,
            "cvc": "123",
            "postal_code": "75001",
            "phone": "0123456789",
            "street_number": "123",
            "street_name": "Client Street"
        }
        
        payment = order_service.pay_by_card(str(order.id), **payment_data)
        print(f"✅ Paiement traité: {payment.status}")
        print(f"   Montant: {payment.amount_cents/100:.2f}€")
        print(f"   Méthode: {payment.payment_method}")
        
        # ========== DÉMONSTRATION 6: VALIDATION ADMIN ==========
        print("\n👨‍💼 6. VALIDATION ADMIN")
        print("-" * 40)
        
        # Valider la commande (admin)
        validated_order = order_service.backoffice_validate_order(str(admin.id), str(order.id))
        print(f"✅ Commande validée par admin")
        print(f"   Nouveau statut: {validated_order.status}")
        
        # ========== DÉMONSTRATION 7: LIVRAISON AVANCÉE ==========
        print("\n🚚 7. SYSTÈME DE LIVRAISON")
        print("-" * 40)
        
        delivery_service = services.get_delivery_service()
        
        # Préparer la livraison
        delivery = delivery_service.prepare_delivery(str(order.id), "DHL")
        print(f"✅ Livraison préparée avec {delivery.transporteur}")
        
        # Expédier la commande
        delivery = delivery_service.ship_order(str(order.id))
        print(f"✅ Commande expédiée")
        print(f"   Numéro de tracking: {delivery.tracking_number}")
        print(f"   Statut: {delivery.delivery_status}")
        
        # ========== DÉMONSTRATION 8: FACTURATION AUTOMATIQUE ==========
        print("\n🧾 8. FACTURATION AUTOMATIQUE")
        print("-" * 40)
        
        billing_service = services.get_billing_service()
        
        # Récupérer la facture
        invoice = billing_service.get_invoice_by_order(str(order.id))
        print(f"✅ Facture générée: {str(invoice.id)[:8]}...")
        print(f"   Total: {invoice.total_cents/100:.2f}€")
        
        # Afficher les lignes de facture
        lines = billing_service.get_invoice_lines(invoice)
        print("   Détail des lignes:")
        for line in lines:
            print(f"     - {line.name}: {line.quantity}x {line.unit_price_cents/100:.2f}€ = {line.line_total_cents/100:.2f}€")
        
        # ========== DÉMONSTRATION 9: SUPPORT CLIENT ==========
        print("\n🎧 9. SUPPORT CLIENT")
        print("-" * 40)
        
        customer_service = services.get_customer_service()
        
        # Créer un fil de support
        thread = customer_service.open_thread(
            str(client.id),
            "Question sur ma commande",
            str(order.id)
        )
        print(f"✅ Fil de support créé: {str(thread.id)[:8]}...")
        
        # Ajouter des messages
        customer_service.post_message(
            str(thread.id),
            str(client.id),
            "Bonjour, j'ai une question sur le délai de livraison."
        )
        print("✅ Message client ajouté")
        
        customer_service.post_message(
            str(thread.id),
            None,  # Message admin
            "Bonjour, votre commande sera livrée sous 2-3 jours ouvrés."
        )
        print("✅ Réponse admin ajoutée")
        
        # ========== DÉMONSTRATION 10: REMBOURSEMENT ==========
        print("\n💰 10. GESTION DES REMBOURSEMENTS")
        print("-" * 40)
        
        # Simuler une demande de remboursement
        refunded_order = order_service.backoffice_refund(str(admin.id), str(order.id))
        print(f"✅ Remboursement traité")
        print(f"   Nouveau statut: {refunded_order.status}")
        print(f"   Montant remboursé: {refunded_order.total_cents()/100:.2f}€")
        
        # ========== RÉSUMÉ FINAL ==========
        print("\n🎉 DÉMONSTRATION TERMINÉE AVEC SUCCÈS !")
        print("=" * 60)
        print("📊 FONCTIONNALITÉS DÉMONTRÉES :")
        print("  ✅ Architecture en services métier")
        print("  ✅ Authentification sécurisée avec bcrypt")
        print("  ✅ Gestion avancée du catalogue")
        print("  ✅ Panier intelligent avec calcul automatique")
        print("  ✅ Commandes avec gestion des statuts")
        print("  ✅ Système de paiement avec gateway")
        print("  ✅ Validation admin des commandes")
        print("  ✅ Livraison avec numéro de tracking")
        print("  ✅ Facturation automatique avec lignes détaillées")
        print("  ✅ Support client avec fils de discussion")
        print("  ✅ Gestion des remboursements")
        print("\n🚀 Votre site e-commerce est maintenant de niveau professionnel !")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la démonstration: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    success = demo_advanced_features()
    sys.exit(0 if success else 1)
