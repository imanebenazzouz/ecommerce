#!/usr/bin/env python3
"""
Test direct de la génération PDF
"""

import sys
import os
sys.path.append('/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend')

from api import generate_invoice_pdf
import io

def test_pdf_generation():
    """Test direct de la génération PDF"""
    
    print("🧾 Test de génération PDF")
    print("=" * 40)
    
    # Données de test
    invoice_data = {
        'id': 'test-invoice-123',
        'number': 'INV-123',
        'issued_at': 1697462400.0,  # Timestamp fixe
        'lines': [
            {
                'product_id': 'prod-1',
                'name': 'T-Shirt Logo',
                'unit_price_cents': 1999,
                'quantity': 2,
                'line_total_cents': 3998
            },
            {
                'product_id': 'prod-2', 
                'name': 'Sweat Capuche',
                'unit_price_cents': 4999,
                'quantity': 1,
                'line_total_cents': 4999
            }
        ]
    }
    
    order_data = {
        'id': 'order-123',
        'total_cents': 8997
    }
    
    user_data = {
        'first_name': 'Alice',
        'last_name': 'Martin',
        'address': '12 Rue des Fleurs, 75001 Paris'
    }
    
    payment_data = {
        'amount_cents': 8997,
        'status': 'PAID',
        'created_at': 1697462400.0
    }
    
    delivery_data = {
        'transporteur': 'Colissimo',
        'tracking_number': 'TRK-ABC123',
        'delivery_status': 'EN_COURS'
    }
    
    try:
        print("📄 Génération du PDF...")
        pdf_buffer = generate_invoice_pdf(invoice_data, order_data, user_data, payment_data, delivery_data)
        
        # Sauvegarder le PDF
        filename = "test_invoice.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        file_size = len(pdf_buffer.getvalue())
        print(f"✅ PDF généré: {filename} ({file_size} bytes)")
        
        # Vérifications
        if file_size < 1000:
            print(f"❌ PDF trop petit: {file_size} bytes")
            return False
        
        print("✅ PDF semble valide")
        
        # Nettoyer
        os.remove(filename)
        print(f"✅ Fichier de test supprimé: {filename}")
        
        print("\n🎉 Test de génération PDF réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur génération PDF: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1)
