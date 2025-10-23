#!/usr/bin/env python3
"""
Test du support client
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_support():
    print("💬 Test du support client")
    print("=" * 40)
    
    # Connexion client
    print("1. Connexion client...")
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={
            "email": "client@example.com",
            "password": "secret"
        })
        if response.status_code == 200:
            client_data = response.json()
            client_token = client_data["token"]
            print(f"✅ Client connecté - Token: {client_token[:20]}...")
        else:
            print(f"❌ Erreur connexion client: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion client: {e}")
        return False
    
    # Test récupération des threads
    print("2. Test récupération des threads...")
    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{API_BASE}/support/threads", headers=headers)
        if response.status_code == 200:
            threads = response.json()
            print(f"✅ {len(threads)} threads récupérés")
            for thread in threads:
                print(f"   - {thread['subject']} ({'Fermé' if thread['closed'] else 'Ouvert'})")
        else:
            print(f"❌ Erreur threads: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur threads: {e}")
        return False
    
    # Test création d'un nouveau thread
    print("3. Test création d'un nouveau thread...")
    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(f"{API_BASE}/support/threads", 
            headers=headers,
            json={
                "subject": "Test de support automatique",
                "order_id": None
            }
        )
        if response.status_code == 200:
            thread = response.json()
            print(f"✅ Thread créé: {thread['subject']}")
            thread_id = thread['id']
        else:
            print(f"❌ Erreur création thread: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur création thread: {e}")
        return False
    
    # Test récupération du thread
    print("4. Test récupération du thread...")
    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.get(f"{API_BASE}/support/threads/{thread_id}", headers=headers)
        if response.status_code == 200:
            thread_detail = response.json()
            print(f"✅ Thread récupéré: {thread_detail['subject']}")
            print(f"   Messages: {len(thread_detail.get('messages', []))}")
        else:
            print(f"❌ Erreur récupération thread: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur récupération thread: {e}")
        return False
    
    # Test envoi d'un message
    print("5. Test envoi d'un message...")
    try:
        headers = {"Authorization": f"Bearer {client_token}"}
        response = requests.post(f"{API_BASE}/support/threads/{thread_id}/messages", 
            headers=headers,
            json={
                "content": "Ceci est un message de test automatique"
            }
        )
        if response.status_code == 200:
            message = response.json()
            print(f"✅ Message envoyé: {message['content'][:50]}...")
        else:
            print(f"❌ Erreur envoi message: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur envoi message: {e}")
        return False
    
    # Test admin support
    print("6. Test support admin...")
    try:
        # Connexion admin
        admin_response = requests.post(f"{API_BASE}/auth/login", json={
            "email": "admin@example.com",
            "password": "admin"
        })
        if admin_response.status_code == 200:
            admin_data = admin_response.json()
            admin_token = admin_data["token"]
            print(f"✅ Admin connecté - Token: {admin_token[:20]}...")
            
            # Récupération des threads admin
            headers = {"Authorization": f"Bearer {admin_token}"}
            response = requests.get(f"{API_BASE}/admin/support/threads", headers=headers)
            if response.status_code == 200:
                admin_threads = response.json()
                print(f"✅ {len(admin_threads)} threads admin récupérés")
            else:
                print(f"❌ Erreur threads admin: {response.status_code}")
                return False
        else:
            print(f"❌ Erreur connexion admin: {admin_response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur support admin: {e}")
        return False
    
    print("\n🎉 Tous les tests du support sont passés !")
    print("\n🌐 URLs disponibles:")
    print("   Frontend: http://localhost:5174")
    print("   Support client: http://localhost:5174/support")
    print("   Support admin: http://localhost:5174/admin/support")
    
    return True

if __name__ == "__main__":
    test_support()
