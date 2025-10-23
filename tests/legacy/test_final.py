#!/usr/bin/env python3
"""
Script de test final pour vérifier que tout fonctionne
"""

import subprocess
import time
import requests
import sys
import os

def check_database():
    """Vérifie l'état de la base de données"""
    print("🔍 Vérification de la base de données...")
    try:
        result = subprocess.run([
            'python3', 'ecommerce-backend/check_database.py'
        ], capture_output=True, text=True, cwd='/Users/imanebenazzouz/Desktop/ecommerce')
        
        if result.returncode == 0:
            print("✅ Base de données OK")
            return True
        else:
            print(f"❌ Problème avec la base de données: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur vérification base de données: {e}")
        return False

def start_api_server():
    """Démarre le serveur API en arrière-plan"""
    print("🚀 Démarrage du serveur API...")
    try:
        # Démarrer le serveur en arrière-plan
        process = subprocess.Popen([
            'python3', 'ecommerce-backend/start_api.py'
        ], cwd='/Users/imanebenazzouz/Desktop/ecommerce')
        
        # Attendre que le serveur démarre
        time.sleep(5)
        
        # Vérifier que le serveur répond
        try:
            response = requests.get('http://localhost:8000/', timeout=5)
            if response.status_code == 200:
                print("✅ Serveur API démarré avec succès")
                return process
            else:
                print(f"❌ Serveur API ne répond pas correctement: {response.status_code}")
                return None
        except requests.exceptions.RequestException:
            print("❌ Serveur API non accessible")
            return None
            
    except Exception as e:
        print(f"❌ Erreur démarrage serveur: {e}")
        return None

def test_api_endpoints():
    """Teste les endpoints de l'API"""
    print("🔍 Test des endpoints de l'API...")
    
    try:
        # Test de santé
        response = requests.get('http://localhost:8000/', timeout=5)
        if response.status_code != 200:
            print(f"❌ Endpoint de santé échoué: {response.status_code}")
            return False
        
        # Test des produits
        response = requests.get('http://localhost:8000/products', timeout=5)
        if response.status_code != 200:
            print(f"❌ Endpoint produits échoué: {response.status_code}")
            return False
        
        products = response.json()
        print(f"✅ {len(products)} produits disponibles")
        
        # Test d'initialisation des données
        response = requests.post('http://localhost:8000/init-data', timeout=10)
        if response.status_code != 200:
            print(f"❌ Endpoint d'initialisation échoué: {response.status_code}")
            return False
        
        print("✅ Tous les endpoints fonctionnent correctement")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test endpoints: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test final de l'application e-commerce")
    print("=" * 60)
    
    # Vérifier la base de données
    if not check_database():
        print("\n❌ Problème avec la base de données")
        return
    
    # Démarrer le serveur API
    server_process = start_api_server()
    if not server_process:
        print("\n❌ Impossible de démarrer le serveur API")
        return
    
    try:
        # Tester les endpoints
        if not test_api_endpoints():
            print("\n❌ Problème avec les endpoints de l'API")
            return
        
        print("\n" + "=" * 60)
        print("✅ TOUT FONCTIONNE CORRECTEMENT!")
        print("🎉 Votre application e-commerce est prête!")
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
        print(f"\n❌ Erreur lors des tests: {e}")
    finally:
        if server_process:
            server_process.terminate()

if __name__ == "__main__":
    main()
