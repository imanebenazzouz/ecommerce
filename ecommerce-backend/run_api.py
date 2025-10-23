#!/usr/bin/env python3
"""
Script de démarrage simple de l'API
"""

import sys
import os

# Ajouter le répertoire courant au path Python
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    """Démarre l'API"""
    print("🚀 Démarrage de l'API e-commerce...")
    
    try:
        # Importer et démarrer l'API
        import uvicorn
        from api import app
        
        print("📡 URL: http://localhost:8000")
        print("📚 Documentation: http://localhost:8000/docs")
        print("=" * 50)
        
        uvicorn.run(
            "api:app",  # Utiliser le format string pour éviter les problèmes d'import
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Erreur d'importation: {e}")
        print("💡 Assurez-vous d'être dans le bon répertoire et que l'environnement virtuel est activé")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
