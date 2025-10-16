#!/usr/bin/env python3
"""
Test final du téléchargement de facture PDF - tout en une fois
"""

import requests
import json
import time
import sys
import os

# Configuration
API_BASE = "http://127.0.0.1:8000"

def test_invoice_final():
    """Test final du téléchargement de facture PDF"""
    
    print("🧾 Test final téléchargement facture PDF")
    print("=" * 50)
    
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
    
    # 2. Connexion admin
    print("\n2️⃣ Connexion admin...")
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
    print("✅ Admin connecté")
    
    # 3. Ajouter produit au panier
    print("\n3️⃣ Ajout au panier...")
    response = requests.get(f"{API_BASE}/products")
    products = response.json()
    
    if not products:
        print("❌ Aucun produit disponible")
        return False
    
    product = products[0]  # Premier produit
    cart_data = {
        "product_id": product["id"],
        "qty": 1
    }
    
    response = requests.post(f"{API_BASE}/cart/add", json=cart_data, headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur ajout au panier: {response.status_code}")
        return False
    
    print(f"✅ {product['name']} ajouté au panier")
    
    # 4. Checkout
    print("\n4️⃣ Création commande...")
    response = requests.post(f"{API_BASE}/orders/checkout", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur checkout: {response.status_code}")
        return False
    
    order_data = response.json()
    order_id = order_data["order_id"]
    print(f"✅ Commande créée: {order_id[:8]}")
    
    # 5. Paiement
    print("\n5️⃣ Paiement...")
    payment_data = {
        "card_number": "1234567890123456",
        "exp_month": 12,
        "exp_year": 2025,
        "cvc": "123"
    }
    
    response = requests.post(f"{API_BASE}/orders/{order_id}/pay", json=payment_data, headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur paiement: {response.status_code}")
        return False
    
    print("✅ Paiement effectué")
    
    # 6. Validation admin
    print("\n6️⃣ Validation admin...")
    response = requests.post(f"{API_BASE}/admin/orders/{order_id}/validate", headers=admin_headers)
    if response.status_code != 200:
        print(f"❌ Erreur validation: {response.status_code}")
        return False
    
    print("✅ Commande validée")
    
    # 7. Test facture JSON
    print("\n7️⃣ Test facture JSON...")
    response = requests.get(f"{API_BASE}/orders/{order_id}/invoice", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur facture JSON: {response.status_code}")
        print(f"   Réponse: {response.text}")
        return False
    
    invoice_data = response.json()
    print("✅ Facture JSON récupérée")
    print(f"   - ID: {invoice_data['id'][:8]}")
    print(f"   - Articles: {len(invoice_data['lines'])}")
    print(f"   - Total: {invoice_data['total_cents']/100:.2f}€")
    
    # Vérifier le contenu de la facture
    print("\n🔍 Validation du contenu de la facture...")
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
    
    # 8. Test téléchargement PDF IMMÉDIATEMENT
    print("\n8️⃣ Test téléchargement PDF...")
    try:
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
        filename = f"test_invoice_{order_id[:8]}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        file_size = len(response.content)
        print(f"✅ PDF téléchargé: {filename} ({file_size} bytes)")
        
        # Vérifications finales
        if file_size < 1000:
            print(f"❌ PDF trop petit: {file_size} bytes")
            return False
        
        print("✅ PDF semble valide")
        
        # Nettoyer
        os.remove(filename)
        print(f"✅ Fichier supprimé: {filename}")
        
    except Exception as e:
        print(f"❌ Exception lors du téléchargement: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 9. Vérification des données de paiement et livraison
    print("\n9️⃣ Vérification des données associées...")
    
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
    
    # Vérifier les données de livraison (peuvent être nulles si pas encore expédiée)
    if updated_order.get('delivery'):
        delivery = updated_order['delivery']
        print(f"✅ Transporteur: {delivery['transporteur']}")
        print(f"✅ Statut livraison: {delivery['delivery_status']}")
        if delivery.get('tracking_number'):
            print(f"✅ Numéro de suivi: {delivery['tracking_number']}")
    else:
        print("ℹ️ Pas encore d'informations de livraison (normal si pas expédiée)")
    
    print("\n🎉 TEST COMPLET RÉUSSI !")
    print("=" * 60)
    print("✅ Commande créée et payée")
    print("✅ Facture générée automatiquement")
    print("✅ Téléchargement de facture PDF fonctionnel")
    print("✅ Contenu de la facture correct")
    print("✅ Données de paiement cohérentes")
    print("✅ Fichier PDF généré et téléchargé")
    print("✅ Toutes les validations passées")
    
    return True

if __name__ == "__main__":
    try:
        success = test_invoice_final()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
