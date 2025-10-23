#!/usr/bin/env python3
"""
Test complet de l'application e-commerce
"""

import requests
import time
import subprocess
import sys
import os

def test_database():
    """Teste la base de données"""
    print("🔍 Test de la base de données...")
    try:
        # Utiliser l'environnement virtuel
        result = subprocess.run([
            'bash', '-c', 'cd ecommerce-backend && source venv/bin/activate && python check_database.py'
        ], capture_output=True, text=True, cwd='/Users/imanebenazzouz/Desktop/ecommerce')
        
        if result.returncode == 0:
            print("✅ Base de données OK")
            return True
        else:
            print(f"❌ Problème base de données: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur test base de données: {e}")
        return False

def start_server():
    """Démarre le serveur"""
    print("🚀 Démarrage du serveur...")
    try:
        # Démarrer le serveur en arrière-plan
        process = subprocess.Popen([
            'bash', 'start_server.sh'
        ], cwd='/Users/imanebenazzouz/Desktop/ecommerce')
        
        # Attendre que le serveur démarre
        print("⏳ Attente du démarrage du serveur...")
        time.sleep(8)
        
        # Tester la connexion
        try:
            response = requests.get('http://localhost:8000/', timeout=5)
            if response.status_code == 200:
                print("✅ Serveur démarré avec succès")
                return process
            else:
                print(f"❌ Serveur ne répond pas: {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ Serveur non accessible")
            return None
            
    except Exception as e:
        print(f"❌ Erreur démarrage serveur: {e}")
        return None

def test_api():
    """Teste l'API"""
    print("🔍 Test de l'API...")
    
    try:
        # Test de santé
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code != 200:
            print(f"❌ Endpoint de santé échoué: {response.status_code}")
            return False
        
        print("✅ Endpoint de santé OK")
        
        # Test des produits
        response = requests.get('http://localhost:8000/products', timeout=5)
        if response.status_code != 200:
            print(f"❌ Endpoint produits échoué: {response.status_code}")
            return False
        
        products = response.json()
        print(f"✅ Endpoint produits OK - {len(products)} produits")
        
        # Test d'initialisation
        response = requests.post('http://localhost:8000/init-data', timeout=10)
        if response.status_code != 200:
            print(f"❌ Endpoint d'initialisation échoué: {response.status_code}")
            return False
        
        print("✅ Endpoint d'initialisation OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test complet de l'application e-commerce")
    print("=" * 60)
    
    # Test de la base de données
    if not test_database():
        print("\n❌ Problème avec la base de données")
        return
    
    # Démarrer le serveur
    server_process = start_server()
    if not server_process:
        print("\n❌ Impossible de démarrer le serveur")
        return
    
    try:
        # Tester l'API
        if not test_api():
            print("\n❌ Problème avec l'API")
            return
        
        print("\n" + "=" * 60)
        print("✅ TOUT FONCTIONNE PARFAITEMENT!")
        print("🎉 Votre application e-commerce est opérationnelle!")
        print("\n📡 API disponible sur: http://localhost:8000")
        print("📚 Documentation: http://localhost:8000/docs")
        print("📖 ReDoc: http://localhost:8000/redoc")
        print("\n💡 Pour arrêter le serveur, appuyez sur Ctrl+C")
        
        # Garder le serveur en vie
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Arrêt du serveur...")
            server_process.terminate()
            server_process.wait()
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    finally:
        if server_process:
            server_process.terminate()

if __name__ == "__main__":
    main()
