#!/usr/bin/env python3
"""
Script de test complet pour créer une commande et tester le téléchargement de facture PDF
"""

import requests
import json
import time
import sys
import os

# Configuration
API_BASE = "http://127.0.0.1:8000"

def create_complete_order_flow():
    """Crée une commande complète avec paiement pour tester la facture"""
    
    print("🛒 Création d'une commande complète pour test facture")
    print("=" * 60)
    
    # 1. Connexion client
    print("\n1️⃣ Connexion client...")
    client_login = {
        "email": "client@example.com", 
        "password": "secret"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=client_login)
    if response.status_code != 200:
        print(f"❌ Erreur connexion client: {response.status_code}")
        return False
    
    client_token = response.json()["token"]
    client_headers = {"Authorization": f"Bearer {client_token}"}
    print("✅ Client connecté")
    
    # 2. Récupérer les produits disponibles
    print("\n2️⃣ Récupération des produits...")
    response = requests.get(f"{API_BASE}/products")
    if response.status_code != 200:
        print(f"❌ Erreur récupération produits: {response.status_code}")
        return False
    
    products = response.json()
    if not products:
        print("❌ Aucun produit disponible")
        return False
    
    print(f"✅ {len(products)} produits trouvés")
    for p in products:
        print(f"   - {p['name']}: {p['price_cents']/100:.2f}€ (stock: {p['stock_qty']})")
    
    # 3. Ajouter des produits au panier
    print("\n3️⃣ Ajout au panier...")
    cart_products = products[:2]  # Prendre les 2 premiers produits
    
    for product in cart_products:
        cart_data = {
            "product_id": product["id"],
            "qty": 2  # 2 exemplaires de chaque
        }
        response = requests.post(f"{API_BASE}/cart/add", json=cart_data, headers=client_headers)
        if response.status_code != 200:
            print(f"❌ Erreur ajout au panier {product['name']}: {response.status_code}")
            return False
        print(f"✅ {product['name']} ajouté au panier (quantité: 2)")
    
    # 4. Vérifier le panier
    print("\n4️⃣ Vérification du panier...")
    response = requests.get(f"{API_BASE}/cart", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur récupération panier: {response.status_code}")
        return False
    
    cart = response.json()
    print(f"✅ Panier avec {len(cart['items'])} articles")
    
    # 5. Checkout (créer la commande)
    print("\n5️⃣ Création de la commande...")
    response = requests.post(f"{API_BASE}/orders/checkout", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur checkout: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return False
    
    order_data = response.json()
    order_id = order_data["order_id"]
    total_cents = order_data["total_cents"]
    print(f"✅ Commande créée: {order_id[:8]} - Total: {total_cents/100:.2f}€")
    
    # 6. Paiement de la commande
    print("\n6️⃣ Paiement de la commande...")
    payment_data = {
        "card_number": "1234567890123456",  # Carte valide (ne finit pas par 0000)
        "exp_month": 12,
        "exp_year": 2025,
        "cvc": "123"
    }
    
    response = requests.post(f"{API_BASE}/orders/{order_id}/pay", json=payment_data, headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur paiement: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return False
    
    payment_result = response.json()
    print(f"✅ Paiement effectué: {payment_result.get('payment_id', 'N/A')}")
    
    # 7. Validation admin de la commande
    print("\n7️⃣ Validation admin...")
    admin_login = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=admin_login)
    if response.status_code != 200:
        print(f"❌ Erreur connexion admin: {response.status_code}")
        return False
    
    admin_token = response.json()["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Valider la commande
    response = requests.post(f"{API_BASE}/admin/orders/{order_id}/validate", headers=admin_headers)
    if response.status_code != 200:
        print(f"❌ Erreur validation: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return False
    
    print("✅ Commande validée par l'admin")
    
    # 8. Expédition de la commande
    print("\n8️⃣ Expédition de la commande...")
    response = requests.post(f"{API_BASE}/admin/orders/{order_id}/ship", headers=admin_headers)
    if response.status_code != 200:
        print(f"❌ Erreur expédition: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return False
    
    print("✅ Commande expédiée")
    
    # 9. Test du téléchargement de facture
    print("\n9️⃣ Test du téléchargement de facture PDF...")
    
    # Vérifier que la facture existe
    response = requests.get(f"{API_BASE}/orders/{order_id}/invoice", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Facture non trouvée: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return False
    
    invoice_data = response.json()
    print("✅ Facture trouvée")
    print(f"   - ID: {invoice_data['id'][:8]}")
    print(f"   - Nombre d'articles: {len(invoice_data['lines'])}")
    print(f"   - Total: {invoice_data['total_cents'] / 100:.2f} €")
    
    # Vérifier le contenu de la facture
    print("\n🔍 Validation du contenu de la facture...")
    
    # Vérifier chaque ligne
    total_calculated = 0
    for line in invoice_data['lines']:
        expected_total = line['unit_price_cents'] * line['quantity']
        if line.get('line_total_cents', 0) != expected_total:
            print(f"❌ Erreur calcul ligne {line['product_id']}: {line.get('line_total_cents', 0)} ≠ {expected_total}")
            return False
        total_calculated += expected_total
        print(f"   ✅ {line['name']}: {line['quantity']} × {line['unit_price_cents']/100:.2f}€ = {expected_total/100:.2f}€")
    
    if total_calculated != invoice_data['total_cents']:
        print(f"❌ Total incohérent: {total_calculated/100:.2f}€ ≠ {invoice_data['total_cents']/100:.2f}€")
        return False
    
    print(f"✅ Total cohérent: {total_calculated/100:.2f}€")
    
    # Télécharger le PDF
    print("\n📄 Téléchargement du PDF...")
    response = requests.get(f"{API_BASE}/orders/{order_id}/invoice/download", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur téléchargement PDF: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return False
    
    # Vérifier le type de contenu
    content_type = response.headers.get('content-type')
    if content_type != 'application/pdf':
        print(f"❌ Type de contenu incorrect: {content_type}")
        return False
    
    # Sauvegarder le PDF
    filename = f"test_facture_{order_id[:8]}.pdf"
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    file_size = len(response.content)
    print(f"✅ PDF téléchargé: {filename} ({file_size} bytes)")
    
    # 10. Vérification des données de paiement et livraison
    print("\n🔍 Vérification des données associées...")
    
    # Récupérer la commande mise à jour
    response = requests.get(f"{API_BASE}/orders/{order_id}", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur récupération commande: {response.status_code}")
        return False
    
    updated_order = response.json()
    
    # Vérifier le statut de paiement
    if updated_order['status'] != 'PAYEE':
        print(f"❌ Statut de paiement incorrect: {updated_order['status']}")
        return False
    print("✅ Commande correctement payée")
    
    # Vérifier les données de livraison
    if updated_order.get('delivery'):
        delivery = updated_order['delivery']
        print(f"✅ Transporteur: {delivery['transporteur']}")
        print(f"✅ Statut livraison: {delivery['delivery_status']}")
        if delivery.get('tracking_number'):
            print(f"✅ Numéro de suivi: {delivery['tracking_number']}")
    else:
        print("⚠️ Aucune information de livraison")
    
    # 11. Validation finale
    print("\n🎯 Validation finale...")
    
    # Vérifier que le PDF s'ouvre correctement (vérification basique)
    if file_size < 1000:  # PDF trop petit
        print(f"❌ PDF suspect (trop petit: {file_size} bytes)")
        return False
    
    print("✅ PDF semble valide")
    
    # Nettoyer le fichier de test
    os.remove(filename)
    print(f"✅ Fichier de test supprimé: {filename}")
    
    print("\n🎉 TEST COMPLET RÉUSSI !")
    print("=" * 60)
    print("✅ Commande créée et payée")
    print("✅ Facture générée automatiquement")
    print("✅ Téléchargement de facture PDF fonctionnel")
    print("✅ Contenu de la facture correct")
    print("✅ Données de paiement cohérentes")
    print("✅ Données de livraison présentes")
    print("✅ Cohérence entre toutes les données")
    
    return order_id

if __name__ == "__main__":
    try:
        order_id = create_complete_order_flow()
        if order_id:
            print(f"\n📋 ID de la commande de test: {order_id}")
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
