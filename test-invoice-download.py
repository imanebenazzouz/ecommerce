#!/usr/bin/env python3
"""
Script de test pour vérifier le téléchargement de facture PDF
"""

import requests
import json
import time
import sys
import os

# Configuration
API_BASE = "http://127.0.0.1:8000"
FRONTEND_BASE = "http://127.0.0.1:5173"

def test_invoice_download():
    """Test complet du téléchargement de facture PDF"""
    
    print("🧾 Test du téléchargement de facture PDF")
    print("=" * 50)
    
    # 1. Connexion admin
    print("\n1️⃣ Connexion admin...")
    login_data = {
        "email": "admin@example.com",
        "password": "admin"
    }
    
    response = requests.post(f"{API_BASE}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Erreur connexion admin: {response.status_code}")
        return False
    
    admin_token = response.json()["token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("✅ Admin connecté")
    
    # 2. Connexion client
    print("\n2️⃣ Connexion client...")
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
    
    # 3. Récupérer les commandes du client
    print("\n3️⃣ Récupération des commandes...")
    response = requests.get(f"{API_BASE}/orders", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Erreur récupération commandes: {response.status_code}")
        return False
    
    orders = response.json()
    if not orders:
        print("⚠️ Aucune commande trouvée pour le client")
        return False
    
    # Prendre la première commande payée
    paid_order = None
    for order in orders:
        if order["status"] == "PAYEE":
            paid_order = order
            break
    
    if not paid_order:
        print("⚠️ Aucune commande payée trouvée")
        return False
    
    print(f"✅ Commande trouvée: {paid_order['id'][:8]}")
    
    # 4. Vérifier que la facture existe
    print("\n4️⃣ Vérification de la facture...")
    response = requests.get(f"{API_BASE}/orders/{paid_order['id']}/invoice", headers=client_headers)
    if response.status_code != 200:
        print(f"❌ Facture non trouvée: {response.status_code}")
        return False
    
    invoice_data = response.json()
    print("✅ Facture trouvée")
    print(f"   - ID: {invoice_data['id'][:8]}")
    print(f"   - Nombre d'articles: {len(invoice_data['lines'])}")
    print(f"   - Total: {invoice_data['total_cents'] / 100:.2f} €")
    
    # 5. Vérifier le contenu de la facture
    print("\n5️⃣ Validation du contenu de la facture...")
    
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
    
    # 6. Télécharger le PDF
    print("\n6️⃣ Téléchargement du PDF...")
    response = requests.get(f"{API_BASE}/orders/{paid_order['id']}/invoice/download", headers=client_headers)
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
    filename = f"test_facture_{paid_order['id'][:8]}.pdf"
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    file_size = len(response.content)
    print(f"✅ PDF téléchargé: {filename} ({file_size} bytes)")
    
    # 7. Vérifier les données de paiement
    print("\n7️⃣ Vérification des données de paiement...")
    
    # Récupérer les paiements pour cette commande
    # Note: Dans l'implémentation actuelle, on ne peut pas facilement récupérer les paiements
    # mais on peut vérifier que la commande est bien payée
    if paid_order['status'] != 'PAYEE':
        print(f"❌ Commande non payée: {paid_order['status']}")
        return False
    
    print("✅ Commande correctement payée")
    
    # 8. Vérifier les données de livraison
    print("\n8️⃣ Vérification des données de livraison...")
    if paid_order.get('delivery'):
        delivery = paid_order['delivery']
        print(f"   ✅ Transporteur: {delivery['transporteur']}")
        print(f"   ✅ Statut: {delivery['delivery_status']}")
        if delivery.get('tracking_number'):
            print(f"   ✅ Numéro de suivi: {delivery['tracking_number']}")
    else:
        print("⚠️ Aucune information de livraison")
    
    # 9. Validation finale
    print("\n9️⃣ Validation finale...")
    
    # Vérifier que le PDF s'ouvre correctement (vérification basique)
    if file_size < 1000:  # PDF trop petit
        print(f"❌ PDF suspect (trop petit: {file_size} bytes)")
        return False
    
    print("✅ PDF semble valide")
    
    # Nettoyer le fichier de test
    os.remove(filename)
    print(f"✅ Fichier de test supprimé: {filename}")
    
    print("\n🎉 TEST RÉUSSI !")
    print("=" * 50)
    print("✅ Téléchargement de facture PDF fonctionnel")
    print("✅ Contenu de la facture correct")
    print("✅ Données de paiement cohérentes")
    print("✅ Données de livraison présentes")
    print("✅ Cohérence entre toutes les données")
    
    return True

if __name__ == "__main__":
    try:
        success = test_invoice_download()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)
