#!/usr/bin/env python3
"""
Test minimal de génération PDF pour isoler le problème
"""

import sys
import os
sys.path.append('/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend')

def test_minimal_pdf():
    """Test minimal de génération PDF"""
    
    print("🧾 Test minimal génération PDF")
    print("=" * 40)
    
    try:
        # Test des imports
        print("1️⃣ Test des imports...")
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        print("✅ Imports reportlab OK")
        
        import io
        from datetime import datetime
        print("✅ Imports standard OK")
        
        # Test génération PDF simple
        print("\n2️⃣ Test génération PDF simple...")
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Ajouter un paragraphe simple
        story.append(Paragraph("Test PDF", styles['Title']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Ceci est un test de génération PDF.", styles['Normal']))
        
        # Construire le PDF
        doc.build(story)
        buffer.seek(0)
        
        content = buffer.getvalue()
        file_size = len(content)
        
        print(f"✅ PDF généré: {file_size} bytes")
        
        # Sauvegarder pour vérification
        filename = "test_minimal.pdf"
        with open(filename, 'wb') as f:
            f.write(content)
        
        print(f"✅ PDF sauvegardé: {filename}")
        
        # Nettoyer
        os.remove(filename)
        print(f"✅ Fichier supprimé: {filename}")
        
        print("\n🎉 Test minimal réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal_pdf()
    sys.exit(0 if success else 1)
