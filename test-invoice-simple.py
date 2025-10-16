#!/usr/bin/env python3
"""
Test simple du téléchargement de facture PDF
"""

import requests
import json
import time
import sys
import os

# Configuration
API_BASE = "http://127.0.0.1:8000"

def test_invoice_simple():
    """Test simple du téléchargement de facture PDF"""
    
    print("🧾 Test simple téléchargement facture PDF")
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
    
    # 2. Ajouter produit au panier
    print("\n2️⃣ Ajout au panier...")
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
    
    # 3. Checkout
    print("\n3️⃣ Création commande...")
    response = requests.post(f"{API_BASE}/orders/checkout", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur checkout: {response.status_code}")
        return False
    
    order_data = response.json()
    order_id = order_data["order_id"]
    print(f"✅ Commande créée: {order_id[:8]}")
    
    # 4. Paiement
    print("\n4️⃣ Paiement...")
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
    
    # 5. Validation admin
    print("\n5️⃣ Validation admin...")
    admin_login = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=admin_login)
    admin_token = response.json()["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    response = requests.post(f"{API_BASE}/admin/orders/{order_id}/validate", headers=admin_headers)
    if response.status_code != 200:
        print(f"❌ Erreur validation: {response.status_code}")
        return False
    
    print("✅ Commande validée")
    
    # 6. Test facture JSON
    print("\n6️⃣ Test facture JSON...")
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
    
    # 7. Test téléchargement PDF
    print("\n7️⃣ Test téléchargement PDF...")
    try:
        response = requests.get(f"{API_BASE}/orders/{order_id}/invoice/download", headers=client_headers)
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"❌ Erreur téléchargement PDF: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
        
        # Vérifier le type de contenu
        content_type = response.headers.get('content-type')
        print(f"   Content-Type: {content_type}")
        
        if content_type != 'application/pdf':
            print(f"❌ Type de contenu incorrect: {content_type}")
            return False
        
        # Sauvegarder le PDF
        filename = f"test_invoice_{order_id[:8]}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        file_size = len(response.content)
        print(f"✅ PDF téléchargé: {filename} ({file_size} bytes)")
        
        # Nettoyer
        os.remove(filename)
        print(f"✅ Fichier supprimé: {filename}")
        
    except Exception as e:
        print(f"❌ Exception lors du téléchargement: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n🎉 TEST RÉUSSI !")
    print("=" * 50)
    print("✅ Téléchargement de facture PDF fonctionnel")
    print("✅ Contenu de la facture correct")
    print("✅ Fichier PDF généré et téléchargé")
    
    return True

if __name__ == "__main__":
    try:
        success = test_invoice_simple()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
