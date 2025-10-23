#!/usr/bin/env python3
"""
Test final de vérification complète du système
Vérifie qu'il n'y a aucune régression et que la modification de profil fonctionne
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
ADMIN_EMAIL = "admin@ecommerce.com"
ADMIN_PASSWORD = "admin123"

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

def make_request(method, endpoint, data=None, token=None):
    """Faire une requête HTTP avec gestion d'erreurs"""
    url = f"{API_BASE}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        else:
            raise ValueError(f"Méthode HTTP non supportée: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        log(f"Erreur requête {method} {endpoint}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            log(f"Réponse: {e.response.text}")
        raise

def test_api_health():
    """Tester que l'API est accessible"""
    log("=== TEST SANTÉ API ===")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            data = response.json()
            log(f"✅ API accessible: {data}")
            return True
        else:
            log(f"❌ API non accessible: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Erreur API: {e}")
        return False

def test_admin_login():
    """Tester la connexion admin"""
    log("=== TEST CONNEXION ADMIN ===")
    try:
        response = make_request("POST", "/auth/login", {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if "token" in response:
            log("✅ Connexion admin réussie")
            return response["token"]
        else:
            log("❌ Token non reçu")
            return None
    except Exception as e:
        log(f"❌ Erreur connexion admin: {e}")
        return None

def test_admin_profile_operations():
    """Tester les opérations de profil admin"""
    log("=== TEST OPÉRATIONS PROFIL ADMIN ===")
    
    try:
        # Connexion
        token = test_admin_login()
        if not token:
            return False
        
        # Récupérer le profil
        profile = make_request("GET", "/auth/me", token=token)
        log(f"Profil initial: {profile}")
        
        # Vérifier que c'est un admin
        if not profile.get("is_admin"):
            log("❌ L'utilisateur n'est pas admin")
            return False
        
        # Modifier le profil
        new_data = {
            "first_name": f"Admin_Test_{int(time.time())}",
            "last_name": f"Verification_{int(time.time())}",
            "address": f"Adresse admin test {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        updated_profile = make_request("PUT", "/auth/profile", new_data, token)
        log(f"Profil mis à jour: {updated_profile}")
        
        # Vérifier les modifications
        for key, value in new_data.items():
            if updated_profile.get(key) != value:
                log(f"❌ {key} non mis à jour correctement")
                return False
        
        # Vérifier la persistance
        time.sleep(1)
        final_profile = make_request("GET", "/auth/me", token=token)
        for key, value in new_data.items():
            if final_profile.get(key) != value:
                log(f"❌ {key} non persisté")
                return False
        
        log("✅ Opérations profil admin réussies")
        return True
        
    except Exception as e:
        log(f"❌ Erreur opérations profil admin: {e}")
        return False

def test_client_profile_operations():
    """Tester les opérations de profil client"""
    log("=== TEST OPÉRATIONS PROFIL CLIENT ===")
    
    try:
        # Créer un client de test
        client_email = f"client_verification_{int(time.time())}@test.com"
        client_data = {
            "email": client_email,
            "password": "client123",
            "first_name": "Client",
            "last_name": "Test",
            "address": "Adresse client initiale"
        }
        
        make_request("POST", "/auth/register", client_data)
        log("✅ Client de test créé")
        
        # Connexion
        login_response = make_request("POST", "/auth/login", {
            "email": client_email,
            "password": "client123"
        })
        token = login_response["token"]
        
        # Récupérer le profil
        profile = make_request("GET", "/auth/me", token=token)
        log(f"Profil client: {profile}")
        
        # Vérifier que c'est un client
        if profile.get("is_admin"):
            log("❌ L'utilisateur ne devrait pas être admin")
            return False
        
        # Modifier le profil
        new_data = {
            "first_name": f"Client_Test_{int(time.time())}",
            "last_name": f"Verification_{int(time.time())}",
            "address": f"Adresse client test {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        updated_profile = make_request("PUT", "/auth/profile", new_data, token)
        log(f"Profil client mis à jour: {updated_profile}")
        
        # Vérifier les modifications
        for key, value in new_data.items():
            if updated_profile.get(key) != value:
                log(f"❌ {key} non mis à jour correctement")
                return False
        
        # Vérifier la persistance
        time.sleep(1)
        final_profile = make_request("GET", "/auth/me", token=token)
        for key, value in new_data.items():
            if final_profile.get(key) != value:
                log(f"❌ {key} non persisté")
                return False
        
        log("✅ Opérations profil client réussies")
        return True
        
    except Exception as e:
        log(f"❌ Erreur opérations profil client: {e}")
        return False

def test_partial_profile_update():
    """Tester la modification partielle du profil"""
    log("=== TEST MODIFICATION PARTIELLE ===")
    
    try:
        # Connexion admin
        token = test_admin_login()
        if not token:
            return False
        
        # Récupérer le profil initial
        initial_profile = make_request("GET", "/auth/me", token=token)
        original_first_name = initial_profile["first_name"]
        original_last_name = initial_profile["last_name"]
        original_address = initial_profile["address"]
        
        # Modifier seulement l'adresse
        new_address = f"Adresse partielle {int(time.time())}"
        updated_profile = make_request("PUT", "/auth/profile", {
            "address": new_address
        }, token)
        
        # Vérifier que seul l'adresse a changé
        if updated_profile["first_name"] != original_first_name:
            log("❌ Le prénom ne devrait pas changer")
            return False
        
        if updated_profile["last_name"] != original_last_name:
            log("❌ Le nom ne devrait pas changer")
            return False
        
        if updated_profile["address"] != new_address:
            log("❌ L'adresse devrait être mise à jour")
            return False
        
        log("✅ Modification partielle réussie")
        return True
        
    except Exception as e:
        log(f"❌ Erreur modification partielle: {e}")
        return False

def test_database_persistence():
    """Tester la persistance en base de données"""
    log("=== TEST PERSISTANCE BASE DE DONNÉES ===")
    
    try:
        # Créer un client pour le test
        client_email = f"persistence_test_{int(time.time())}@test.com"
        make_request("POST", "/auth/register", {
            "email": client_email,
            "password": "client123",
            "first_name": "Persistence",
            "last_name": "Test",
            "address": "Adresse initiale"
        })
        
        # Connexion et modification
        login_response = make_request("POST", "/auth/login", {
            "email": client_email,
            "password": "client123"
        })
        token = login_response["token"]
        
        new_address = f"Adresse persistée {int(time.time())}"
        make_request("PUT", "/auth/profile", {
            "address": new_address
        }, token)
        
        # Reconnexion pour vérifier la persistance
        time.sleep(1)
        new_login_response = make_request("POST", "/auth/login", {
            "email": client_email,
            "password": "client123"
        })
        new_token = new_login_response["token"]
        
        final_profile = make_request("GET", "/auth/me", token=new_token)
        
        if final_profile["address"] != new_address:
            log("❌ L'adresse n'a pas été persistée")
            return False
        
        log("✅ Persistance en base de données vérifiée")
        return True
        
    except Exception as e:
        log(f"❌ Erreur persistance: {e}")
        return False

def test_frontend_accessibility():
    """Tester l'accessibilité du frontend"""
    log("=== TEST ACCESSIBILITÉ FRONTEND ===")
    
    try:
        # Tester l'accès au frontend
        response = requests.get("http://localhost:5175/", timeout=5)
        if response.status_code == 200:
            log("✅ Frontend accessible")
            return True
        else:
            log(f"❌ Frontend non accessible: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Erreur accès frontend: {e}")
        return False

def main():
    """Fonction principale de test"""
    log("Démarrage de la vérification finale complète")
    log("=" * 60)
    
    # Tests
    tests = [
        ("Santé API", test_api_health),
        ("Connexion admin", test_admin_login),
        ("Opérations profil admin", test_admin_profile_operations),
        ("Opérations profil client", test_client_profile_operations),
        ("Modification partielle", test_partial_profile_update),
        ("Persistance base de données", test_database_persistence),
        ("Accessibilité frontend", test_frontend_accessibility),
    ]
    
    results = []
    for test_name, test_func in tests:
        log(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                log(f"✅ {test_name}: SUCCÈS")
            else:
                log(f"❌ {test_name}: ÉCHEC")
        except Exception as e:
            log(f"❌ {test_name}: ERREUR - {e}")
            results.append((test_name, False))
    
    # Résumé
    log("\n" + "=" * 60)
    log("RÉSUMÉ FINAL DE LA VÉRIFICATION")
    log("=" * 60)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        log(f"{test_name}: {status}")
    
    log(f"\nTotal: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        log("\n🎉 VÉRIFICATION COMPLÈTE RÉUSSIE")
        log("✅ Aucune régression détectée")
        log("✅ La modification de profil fonctionne pour admin et clients")
        log("✅ Les modifications sont bien persistées en base de données")
        log("✅ Le système est opérationnel")
        return True
    else:
        log(f"\n⚠️  VÉRIFICATION PARTIELLEMENT RÉUSSIE")
        log(f"❌ {total_count - success_count} test(s) ont échoué")
        log("🔍 Vérification manuelle nécessaire")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
