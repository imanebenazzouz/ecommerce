#!/usr/bin/env python3
"""
Script de démarrage de l'API e-commerce
"""

import uvicorn
import sys
import os

# Ajouter le répertoire courant au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_api():
    """Démarre l'API FastAPI"""
    print("🚀 Démarrage de l'API e-commerce...")
    print("📡 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("=" * 50)
    
    try:
        # Importer l'API
        from api import app
        
        # Démarrer le serveur
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur demandé par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    start_api()
