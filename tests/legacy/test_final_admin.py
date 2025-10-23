#!/usr/bin/env python3
"""
Test final complet du support admin - Validation finale
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_final_admin():
    """Test final complet du support admin"""
    print("🎯 TEST FINAL - SUPPORT ADMIN")
    print("=" * 50)
    
    all_tests_passed = True
    test_results = {}
    
    # Test 1: Connexion admin
    print("\n1. 🔐 Test de connexion admin...")
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@example.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            admin_token = response.json()["token"]
            print("   ✅ Connexion admin réussie")
            test_results["admin_login"] = True
        else:
            print(f"   ❌ Erreur connexion admin: {response.status_code}")
            test_results["admin_login"] = False
            all_tests_passed = False
    except Exception as e:
        print(f"   ❌ Erreur connexion admin: {e}")
        test_results["admin_login"] = False
        all_tests_passed = False
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Test 2: Récupération des fils admin
    print("\n2. 📋 Test de récupération des fils admin...")
    try:
        response = requests.get(f"{BASE_URL}/admin/support/threads", headers=headers)
        if response.status_code == 200:
            threads = response.json()
            print(f"   ✅ {len(threads)} fils récupérés avec succès")
            test_results["admin_list_threads"] = True
            if threads:
                test_thread_id = threads[0]["id"]
                print(f"   📝 Fil de test: {test_thread_id}")
            else:
                test_thread_id = None
                print("   ℹ️ Aucun fil disponible pour les tests")
        else:
            print(f"   ❌ Erreur récupération fils: {response.status_code}")
            test_results["admin_list_threads"] = False
            all_tests_passed = False
            test_thread_id = None
    except Exception as e:
        print(f"   ❌ Erreur récupération fils: {e}")
        test_results["admin_list_threads"] = False
        all_tests_passed = False
        test_thread_id = None
    
    # Test 3: Récupération d'un fil spécifique
    if test_thread_id:
        print(f"\n3. 🔍 Test de récupération du fil {test_thread_id}...")
        try:
            response = requests.get(f"{BASE_URL}/admin/support/threads/{test_thread_id}", headers=headers)
            if response.status_code == 200:
                thread_detail = response.json()
                print(f"   ✅ Fil récupéré: {thread_detail['subject']}")
                print(f"   📨 Messages: {len(thread_detail.get('messages', []))}")
                test_results["admin_get_thread"] = True
            else:
                print(f"   ❌ Erreur récupération fil: {response.status_code}")
                test_results["admin_get_thread"] = False
                all_tests_passed = False
        except Exception as e:
            print(f"   ❌ Erreur récupération fil: {e}")
            test_results["admin_get_thread"] = False
            all_tests_passed = False
    
    # Test 4: Création d'un fil de test complet
    print("\n4. 🆕 Test de création d'un fil complet...")
    try:
        # Connexion utilisateur
        user_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "user@example.com",
            "password": "user123"
        })
        if user_response.status_code == 200:
            user_token = user_response.json()["token"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
            
            # Créer un fil
            thread_response = requests.post(f"{BASE_URL}/support/threads", json={
                "subject": "Test final support admin",
                "order_id": None
            }, headers=user_headers)
            
            if thread_response.status_code == 200:
                new_thread = thread_response.json()
                new_thread_id = new_thread["id"]
                print(f"   ✅ Fil créé: {new_thread_id}")
                
                # Ajouter un message utilisateur
                message_response = requests.post(f"{BASE_URL}/support/threads/{new_thread_id}/messages", json={
                    "content": "Message de test utilisateur pour validation finale"
                }, headers=user_headers)
                
                if message_response.status_code == 200:
                    print("   ✅ Message utilisateur ajouté")
                    
                    # Réponse admin
                    admin_message_response = requests.post(f"{BASE_URL}/admin/support/threads/{new_thread_id}/messages", json={
                        "content": "Réponse admin - Test final réussi !"
                    }, headers=headers)
                    
                    if admin_message_response.status_code == 200:
                        print("   ✅ Réponse admin ajoutée")
                        
                        # Fermer le fil
                        close_response = requests.post(f"{BASE_URL}/admin/support/threads/{new_thread_id}/close", headers=headers)
                        if close_response.status_code == 200:
                            print("   ✅ Fil fermé avec succès")
                            test_results["complete_thread_flow"] = True
                        else:
                            print(f"   ❌ Erreur fermeture fil: {close_response.status_code}")
                            test_results["complete_thread_flow"] = False
                            all_tests_passed = False
                    else:
                        print(f"   ❌ Erreur réponse admin: {admin_message_response.status_code}")
                        test_results["complete_thread_flow"] = False
                        all_tests_passed = False
                else:
                    print(f"   ❌ Erreur message utilisateur: {message_response.status_code}")
                    test_results["complete_thread_flow"] = False
                    all_tests_passed = False
            else:
                print(f"   ❌ Erreur création fil: {thread_response.status_code}")
                test_results["complete_thread_flow"] = False
                all_tests_passed = False
        else:
            print(f"   ❌ Erreur connexion utilisateur: {user_response.status_code}")
            test_results["complete_thread_flow"] = False
            all_tests_passed = False
    except Exception as e:
        print(f"   ❌ Erreur test complet: {e}")
        test_results["complete_thread_flow"] = False
        all_tests_passed = False
    
    # Test 5: Test de performance
    print("\n5. ⚡ Test de performance...")
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/admin/support/threads", headers=headers)
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = end_time - start_time
            print(f"   ✅ Temps de réponse: {response_time:.3f}s")
            if response_time < 1.0:
                print("   🚀 Performance excellente")
                test_results["performance"] = True
            elif response_time < 2.0:
                print("   ✅ Performance acceptable")
                test_results["performance"] = True
            else:
                print("   ⚠️ Performance lente")
                test_results["performance"] = False
        else:
            print(f"   ❌ Erreur test performance: {response.status_code}")
            test_results["performance"] = False
            all_tests_passed = False
    except Exception as e:
        print(f"   ❌ Erreur test performance: {e}")
        test_results["performance"] = False
        all_tests_passed = False
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 50)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print(f"\n🎯 Tests exécutés: {total_tests}")
    print(f"✅ Tests réussis: {passed_tests}")
    print(f"❌ Tests échoués: {total_tests - passed_tests}")
    
    print(f"\n📋 Détail des tests:")
    for test_name, result in test_results.items():
        status = "✅" if result else "❌"
        test_display = test_name.replace("_", " ").title()
        print(f"   {status} {test_display}")
    
    if all_tests_passed:
        print(f"\n🎉 SUCCÈS COMPLET !")
        print(f"   Le support admin fonctionne parfaitement !")
        print(f"   Toutes les fonctionnalités sont opérationnelles.")
        return True
    else:
        print(f"\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print(f"   {passed_tests}/{total_tests} tests réussis")
        return False

if __name__ == "__main__":
    success = test_final_admin()
    sys.exit(0 if success else 1)
