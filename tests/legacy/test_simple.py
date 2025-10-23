#!/usr/bin/env python3
"""
Test simple et fiable de l'application e-commerce
"""

import subprocess
import time
import requests
import os

def run_command(cmd, cwd=None):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def test_database():
    """Teste la base de données"""
    print("🔍 Test de la base de données...")
    
    # Aller dans le répertoire backend et activer l'environnement virtuel
    cmd = "cd ecommerce-backend && source venv/bin/activate && python check_database.py"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Base de données OK")
        return True
    else:
        print(f"❌ Problème base de données: {stderr}")
        return False

def start_server():
    """Démarre le serveur"""
    print("🚀 Démarrage du serveur...")
    
    # Arrêter tout processus existant
    run_command("pkill -f 'python.*api' || true")
    time.sleep(2)
    
    # Démarrer le serveur
    cmd = "cd ecommerce-backend && source venv/bin/activate && python run_api.py"
    success, stdout, stderr = run_command(cmd, cwd="/Users/imanebenazzouz/Desktop/ecommerce")
    
    if success:
        print("✅ Serveur démarré")
        return True
    else:
        print(f"❌ Erreur démarrage serveur: {stderr}")
        return False

def test_api():
    """Teste l'API"""
    print("🔍 Test de l'API...")
    
    # Attendre que le serveur démarre
    print("⏳ Attente du démarrage du serveur...")
    time.sleep(5)
    
    try:
        # Test de santé
        response = requests.get('http://localhost:8000/', timeout=10)
        if response.status_code == 200:
            print("✅ API accessible")
            
            # Test des produits
            response = requests.get('http://localhost:8000/products', timeout=10)
            if response.status_code == 200:
                products = response.json()
                print(f"✅ Produits disponibles: {len(products)}")
                return True
            else:
                print(f"❌ Erreur produits: {response.status_code}")
                return False
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur test API: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Test simple de l'application e-commerce")
    print("=" * 50)
    
    # Test de la base de données
    if not test_database():
        print("\n❌ Problème avec la base de données")
        return
    
    # Démarrer le serveur
    if not start_server():
        print("\n❌ Impossible de démarrer le serveur")
        return
    
    # Tester l'API
    if not test_api():
        print("\n❌ Problème avec l'API")
        return
    
    print("\n" + "=" * 50)
    print("✅ TOUT FONCTIONNE!")
    print("🎉 Votre application e-commerce est opérationnelle!")
    print("\n📡 API: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
