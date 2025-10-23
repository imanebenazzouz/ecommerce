#!/usr/bin/env python3
"""
Test de vérification de la modification de profil pour admin et clients
Vérifie que les modifications sont bien persistées en base de données
Inclut la création d'un client de test
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
CLIENT_EMAIL = f"client_test_{int(time.time())}@test.com"
CLIENT_PASSWORD = "client123"

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

def register_user(email, password, first_name, last_name, address):
    """Créer un nouvel utilisateur"""
    log(f"Création de l'utilisateur {email}...")
    response = make_request("POST", "/auth/register", {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "address": address
    })
    return response

def login_user(email, password):
    """Se connecter et récupérer le token"""
    log(f"Connexion de {email}...")
    response = make_request("POST", "/auth/login", {
        "email": email,
        "password": password
    })
    return response["token"]

def get_user_profile(token):
    """Récupérer le profil utilisateur"""
    return make_request("GET", "/auth/me", token=token)

def update_user_profile(token, first_name=None, last_name=None, address=None):
    """Mettre à jour le profil utilisateur"""
    update_data = {}
    if first_name is not None:
        update_data["first_name"] = first_name
    if last_name is not None:
        update_data["last_name"] = last_name
    if address is not None:
        update_data["address"] = address
    
    log(f"Mise à jour du profil avec: {update_data}")
    return make_request("PUT", "/auth/profile", update_data, token)

def test_admin_profile_update():
    """Tester la modification de profil pour l'admin"""
    log("=== TEST MODIFICATION PROFIL ADMIN ===")
    
    try:
        # Connexion admin
        admin_token = login_user(ADMIN_EMAIL, ADMIN_PASSWORD)
        log("✅ Connexion admin réussie")
        
        # Récupérer le profil initial
        initial_profile = get_user_profile(admin_token)
        log(f"Profil initial admin: {initial_profile}")
        
        # Vérifier que c'est bien un admin
        assert initial_profile["is_admin"] == True, "L'utilisateur devrait être admin"
        log("✅ Vérification rôle admin OK")
        
        # Modifier le profil
        new_first_name = f"Admin_Updated_{int(time.time())}"
        new_last_name = f"Test_{int(time.time())}"
        new_address = f"Adresse admin mise à jour {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        updated_profile = update_user_profile(
            admin_token,
            first_name=new_first_name,
            last_name=new_last_name,
            address=new_address
        )
        
        log(f"Profil mis à jour: {updated_profile}")
        
        # Vérifier que les modifications sont bien présentes
        assert updated_profile["first_name"] == new_first_name, "Prénom non mis à jour"
        assert updated_profile["last_name"] == new_last_name, "Nom non mis à jour"
        assert updated_profile["address"] == new_address, "Adresse non mise à jour"
        assert updated_profile["is_admin"] == True, "Le rôle admin ne devrait pas changer"
        log("✅ Vérification des modifications admin OK")
        
        # Vérifier la persistance en récupérant le profil à nouveau
        time.sleep(1)  # Attendre un peu pour s'assurer de la persistance
        final_profile = get_user_profile(admin_token)
        
        assert final_profile["first_name"] == new_first_name, "Prénom non persisté"
        assert final_profile["last_name"] == new_last_name, "Nom non persisté"
        assert final_profile["address"] == new_address, "Adresse non persistée"
        log("✅ Persistance des modifications admin vérifiée")
        
        return True
        
    except Exception as e:
        log(f"❌ Erreur test admin: {e}")
        return False

def test_client_profile_update():
    """Tester la modification de profil pour un client"""
    log("=== TEST MODIFICATION PROFIL CLIENT ===")
    
    try:
        # Créer un client de test
        register_user(
            CLIENT_EMAIL,
            CLIENT_PASSWORD,
            "Client",
            "Test",
            "Adresse client initiale"
        )
        log("✅ Client de test créé")
        
        # Connexion client
        client_token = login_user(CLIENT_EMAIL, CLIENT_PASSWORD)
        log("✅ Connexion client réussie")
        
        # Récupérer le profil initial
        initial_profile = get_user_profile(client_token)
        log(f"Profil initial client: {initial_profile}")
        
        # Vérifier que c'est bien un client
        assert initial_profile["is_admin"] == False, "L'utilisateur devrait être client"
        log("✅ Vérification rôle client OK")
        
        # Modifier le profil
        new_first_name = f"Client_Updated_{int(time.time())}"
        new_last_name = f"Test_{int(time.time())}"
        new_address = f"Adresse client mise à jour {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        updated_profile = update_user_profile(
            client_token,
            first_name=new_first_name,
            last_name=new_last_name,
            address=new_address
        )
        
        log(f"Profil mis à jour: {updated_profile}")
        
        # Vérifier que les modifications sont bien présentes
        assert updated_profile["first_name"] == new_first_name, "Prénom non mis à jour"
        assert updated_profile["last_name"] == new_last_name, "Nom non mis à jour"
        assert updated_profile["address"] == new_address, "Adresse non mise à jour"
        assert updated_profile["is_admin"] == False, "Le rôle client ne devrait pas changer"
        log("✅ Vérification des modifications client OK")
        
        # Vérifier la persistance en récupérant le profil à nouveau
        time.sleep(1)  # Attendre un peu pour s'assurer de la persistance
        final_profile = get_user_profile(client_token)
        
        assert final_profile["first_name"] == new_first_name, "Prénom non persisté"
        assert final_profile["last_name"] == new_last_name, "Nom non persisté"
        assert final_profile["address"] == new_address, "Adresse non persistée"
        log("✅ Persistance des modifications client vérifiée")
        
        return True
        
    except Exception as e:
        log(f"❌ Erreur test client: {e}")
        return False

def test_partial_profile_update():
    """Tester la modification partielle du profil (un seul champ)"""
    log("=== TEST MODIFICATION PARTIELLE PROFIL ===")
    
    try:
        # Connexion admin
        admin_token = login_user(ADMIN_EMAIL, ADMIN_PASSWORD)
        
        # Récupérer le profil initial
        initial_profile = get_user_profile(admin_token)
        original_first_name = initial_profile["first_name"]
        original_last_name = initial_profile["last_name"]
        original_address = initial_profile["address"]
        
        # Modifier seulement l'adresse
        new_address = f"Adresse partielle {int(time.time())}"
        updated_profile = update_user_profile(
            admin_token,
            address=new_address
        )
        
        # Vérifier que seul l'adresse a changé
        assert updated_profile["first_name"] == original_first_name, "Le prénom ne devrait pas changer"
        assert updated_profile["last_name"] == original_last_name, "Le nom ne devrait pas changer"
        assert updated_profile["address"] == new_address, "L'adresse devrait être mise à jour"
        log("✅ Modification partielle OK")
        
        return True
        
    except Exception as e:
        log(f"❌ Erreur test modification partielle: {e}")
        return False

def test_database_persistence():
    """Tester la persistance en base de données avec reconnexion"""
    log("=== TEST PERSISTANCE BASE DE DONNÉES ===")
    
    try:
        # Créer un client de test
        client_email = f"persistence_test_{int(time.time())}@test.com"
        register_user(
            client_email,
            CLIENT_PASSWORD,
            "Persistence",
            "Test",
            "Adresse initiale"
        )
        log("✅ Client de test créé")
        
        # Connexion et modification
        client_token = login_user(client_email, CLIENT_PASSWORD)
        new_address = f"Adresse persistée {int(time.time())}"
        update_user_profile(client_token, address=new_address)
        log("✅ Profil modifié")
        
        # Déconnexion (simulation)
        # Pas de logout endpoint, on simule en perdant le token
        
        # Reconnexion et vérification
        time.sleep(1)
        new_token = login_user(client_email, CLIENT_PASSWORD)
        final_profile = get_user_profile(new_token)
        
        assert final_profile["address"] == new_address, "L'adresse n'a pas été persistée en base"
        log("✅ Persistance en base de données vérifiée")
        
        return True
        
    except Exception as e:
        log(f"❌ Erreur test persistance: {e}")
        return False

def main():
    """Fonction principale de test"""
    log("Démarrage des tests de modification de profil")
    log("=" * 50)
    
    # Vérifier que l'API est accessible
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code != 200:
            log("❌ L'API n'est pas accessible")
            return False
        log("✅ API accessible")
    except Exception as e:
        log(f"❌ Impossible d'accéder à l'API: {e}")
        return False
    
    # Tests
    tests = [
        ("Modification profil admin", test_admin_profile_update),
        ("Modification profil client", test_client_profile_update),
        ("Modification partielle", test_partial_profile_update),
        ("Persistance base de données", test_database_persistence),
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
    log("\n" + "=" * 50)
    log("RÉSUMÉ DES TESTS")
    log("=" * 50)
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for test_name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        log(f"{test_name}: {status}")
    
    log(f"\nTotal: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        log("🎉 TOUS LES TESTS SONT PASSÉS - Aucune régression détectée")
        return True
    else:
        log("⚠️  CERTAINS TESTS ONT ÉCHOUÉ - Vérification nécessaire")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
