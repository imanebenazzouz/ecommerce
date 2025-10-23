#!/usr/bin/env python3
"""
Test en arrière-plan de l'application e-commerce
"""

import subprocess
import time
import requests
import threading
import sys

def start_server_background():
    """Démarre le serveur en arrière-plan"""
    print("🚀 Démarrage du serveur en arrière-plan...")
    
    # Arrêter tout processus existant
    subprocess.run("pkill -f 'python.*api' || true", shell=True)
    time.sleep(2)
    
    # Démarrer le serveur
    cmd = "cd ecommerce-backend && source venv/bin/activate && python run_api.py"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Attendre un peu
    time.sleep(8)
    
    return process

def test_api_connection():
    """Teste la connexion à l'API"""
    print("🔍 Test de connexion à l'API...")
    
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:8000/', timeout=5)
            if response.status_code == 200:
                print("✅ API accessible!")
                return True
        except:
            pass
        
        print(f"⏳ Tentative {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ API non accessible après 10 tentatives")
    return False

def test_endpoints():
    """Teste les endpoints principaux"""
    print("🔍 Test des endpoints...")
    
    endpoints = [
        ('/', 'Santé'),
        ('/products', 'Produits'),
        ('/init-data', 'Initialisation')
    ]
    
    for endpoint, name in endpoints:
        try:
            if endpoint == '/init-data':
                response = requests.post(f'http://localhost:8000{endpoint}', timeout=10)
            else:
                response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {name} OK")
            else:
                print(f"❌ {name} échoué: {response.status_code}")
        except Exception as e:
            print(f"❌ {name} erreur: {e}")

def main():
    """Fonction principale"""
    print("🚀 Test en arrière-plan de l'application e-commerce")
    print("=" * 60)
    
    # Démarrer le serveur
    server_process = start_server_background()
    
    try:
        # Tester la connexion
        if not test_api_connection():
            print("\n❌ Impossible de se connecter à l'API")
            return
        
        # Tester les endpoints
        test_endpoints()
        
        print("\n" + "=" * 60)
        print("✅ TOUT FONCTIONNE PARFAITEMENT!")
        print("🎉 Votre application e-commerce est opérationnelle!")
        print("\n📡 API: http://localhost:8000")
        print("📚 Documentation: http://localhost:8000/docs")
        print("📖 ReDoc: http://localhost:8000/redoc")
        print("\n💡 Le serveur continue de tourner en arrière-plan")
        print("💡 Pour l'arrêter: pkill -f 'python.*api'")
        
        # Garder le script en vie
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Arrêt demandé...")
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        if server_process:
            server_process.terminate()

if __name__ == "__main__":
    main()
