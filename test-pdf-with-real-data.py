#!/usr/bin/env python3
"""
Test de génération PDF avec des données réelles
"""

import requests
import json
import sys
import os
sys.path.append('/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend')

from api import generate_invoice_pdf

def test_pdf_with_real_data():
    """Test de génération PDF avec des données réelles"""
    
    print("🧾 Test génération PDF avec données réelles")
    print("=" * 50)
    
    # Configuration
    API_BASE = "http://127.0.0.1:8000"
    
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
    
    # 6. Récupérer la facture
    print("\n6️⃣ Récupération facture...")
    response = requests.get(f"{API_BASE}/orders/{order_id}/invoice", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur facture: {response.status_code}")
        return False
    
    invoice_data = response.json()
    print("✅ Facture récupérée")
    
    # 7. Récupérer l'utilisateur
    print("\n7️⃣ Récupération utilisateur...")
    response = requests.get(f"{API_BASE}/auth/me", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur utilisateur: {response.status_code}")
        return False
    
    user_data = response.json()
    print("✅ Utilisateur récupéré")
    
    # 8. Récupérer la commande pour les données de paiement/livraison
    print("\n8️⃣ Récupération commande...")
    response = requests.get(f"{API_BASE}/orders/{order_id}", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur commande: {response.status_code}")
        return False
    
    order_full_data = response.json()
    print("✅ Commande récupérée")
    
    # 9. Test génération PDF avec données réelles
    print("\n9️⃣ Test génération PDF avec données réelles...")
    
    try:
        # Préparer les données comme dans l'endpoint
        invoice_for_pdf = {
            'id': invoice_data['id'],
            'number': invoice_data['id'][:8],
            'issued_at': invoice_data['issued_at'],
            'lines': [
                {
                    'product_id': line['product_id'],
                    'name': line['name'],
                    'unit_price_cents': line['unit_price_cents'],
                    'quantity': line['quantity'],
                    'line_total_cents': line['line_total_cents']
                }
                for line in invoice_data['lines']
            ]
        }
        
        order_for_pdf = {
            'id': order_id,
            'total_cents': order_data['total_cents']
        }
        
        user_for_pdf = {
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'address': user_data['address']
        }
        
        payment_for_pdf = None  # Pas de données de paiement dans ce test
        delivery_for_pdf = None  # Pas de données de livraison dans ce test
        
        print(f"   Données préparées:")
        print(f"   - Invoice ID: {invoice_for_pdf['id'][:8]}")
        print(f"   - Order ID: {order_for_pdf['id'][:8]}")
        print(f"   - User: {user_for_pdf['first_name']} {user_for_pdf['last_name']}")
        print(f"   - Lines: {len(invoice_for_pdf['lines'])}")
        
        # Générer le PDF
        pdf_buffer = generate_invoice_pdf(
            invoice_for_pdf, 
            order_for_pdf, 
            user_for_pdf, 
            payment_for_pdf, 
            delivery_for_pdf
        )
        
        # Sauvegarder le PDF
        filename = f"test_real_data_{order_id[:8]}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        file_size = len(pdf_buffer.getvalue())
        print(f"✅ PDF généré avec données réelles: {filename} ({file_size} bytes)")
        
        # Nettoyer
        os.remove(filename)
        print(f"✅ Fichier supprimé: {filename}")
        
        print("\n🎉 Test avec données réelles réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur génération PDF avec données réelles: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = test_pdf_with_real_data()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
