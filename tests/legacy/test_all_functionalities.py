#!/usr/bin/env python3
"""
Test complet de toutes les fonctionnalités pour détecter les régressions
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000"

def test_all_functionalities():
    """Test complet de toutes les fonctionnalités"""
    print("🧪 TEST COMPLET - TOUTES LES FONCTIONNALITÉS")
    print("=" * 60)
    
    all_tests_passed = True
    test_results = {}
    
    # ==================== AUTHENTIFICATION ====================
    print("\n🔐 1. TEST AUTHENTIFICATION")
    print("-" * 30)
    
    # Test connexion utilisateur
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "user@example.com",
            "password": "user123"
        })
        if response.status_code == 200:
            user_token = response.json()["token"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
            print("   ✅ Connexion utilisateur réussie")
            test_results["user_login"] = True
        else:
            print(f"   ❌ Erreur connexion utilisateur: {response.status_code}")
            test_results["user_login"] = False
            all_tests_passed = False
    except Exception as e:
        print(f"   ❌ Erreur connexion utilisateur: {e}")
        test_results["user_login"] = False
        all_tests_passed = False
    
    # Test connexion admin
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@example.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            admin_token = response.json()["token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
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
    
    # ==================== PRODUITS ====================
    print("\n📦 2. TEST PRODUITS")
    print("-" * 30)
    
    # Test liste des produits
    try:
        response = requests.get(f"{BASE_URL}/products")
        if response.status_code == 200:
            products = response.json()
            print(f"   ✅ {len(products)} produits récupérés")
            test_results["list_products"] = True
            if products:
                test_product_id = products[0]["id"]
            else:
                test_product_id = None
        else:
            print(f"   ❌ Erreur liste produits: {response.status_code}")
            test_results["list_products"] = False
            all_tests_passed = False
            test_product_id = None
    except Exception as e:
        print(f"   ❌ Erreur liste produits: {e}")
        test_results["list_products"] = False
        all_tests_passed = False
        test_product_id = None
    
    # Test récupération d'un produit
    if test_product_id:
        try:
            response = requests.get(f"{BASE_URL}/products/{test_product_id}")
            if response.status_code == 200:
                product = response.json()
                print(f"   ✅ Produit récupéré: {product['name']}")
                test_results["get_product"] = True
            else:
                print(f"   ❌ Erreur récupération produit: {response.status_code}")
                test_results["get_product"] = False
                all_tests_passed = False
        except Exception as e:
            print(f"   ❌ Erreur récupération produit: {e}")
            test_results["get_product"] = False
            all_tests_passed = False
    
    # ==================== PANIER ====================
    print("\n🛒 3. TEST PANIER")
    print("-" * 30)
    
    # Test vue du panier
    try:
        response = requests.get(f"{BASE_URL}/cart", headers=user_headers)
        if response.status_code == 200:
            cart = response.json()
            print(f"   ✅ Panier récupéré: {len(cart.get('items', {}))} articles")
            test_results["view_cart"] = True
        else:
            print(f"   ❌ Erreur vue panier: {response.status_code}")
            test_results["view_cart"] = False
            all_tests_passed = False
    except Exception as e:
        print(f"   ❌ Erreur vue panier: {e}")
        test_results["view_cart"] = False
        all_tests_passed = False
    
    # Test ajout au panier
    if test_product_id:
        try:
            response = requests.post(f"{BASE_URL}/cart/add", json={
                "product_id": test_product_id,
                "quantity": 2
            }, headers=user_headers)
            if response.status_code == 200:
                print("   ✅ Produit ajouté au panier")
                test_results["add_to_cart"] = True
            else:
                print(f"   ❌ Erreur ajout panier: {response.status_code}")
                test_results["add_to_cart"] = False
                all_tests_passed = False
        except Exception as e:
            print(f"   ❌ Erreur ajout panier: {e}")
            test_results["add_to_cart"] = False
            all_tests_passed = False
    
    # ==================== COMMANDES ====================
    print("\n📋 4. TEST COMMANDES")
    print("-" * 30)
    
    # Test checkout
    try:
        response = requests.post(f"{BASE_URL}/checkout", headers=user_headers)
        if response.status_code == 200:
            order = response.json()
            test_order_id = order["id"]
            print(f"   ✅ Commande créée: {test_order_id}")
            test_results["checkout"] = True
        else:
            print(f"   ❌ Erreur checkout: {response.status_code}")
            test_results["checkout"] = False
            all_tests_passed = False
            test_order_id = None
    except Exception as e:
        print(f"   ❌ Erreur checkout: {e}")
        test_results["checkout"] = False
        all_tests_passed = False
        test_order_id = None
    
    # Test liste des commandes utilisateur
    try:
        response = requests.get(f"{BASE_URL}/orders", headers=user_headers)
        if response.status_code == 200:
            orders = response.json()
            print(f"   ✅ {len(orders)} commandes utilisateur récupérées")
            test_results["user_orders"] = True
        else:
            print(f"   ❌ Erreur commandes utilisateur: {response.status_code}")
            test_results["user_orders"] = False
            all_tests_passed = False
    except Exception as e:
        print(f"   ❌ Erreur commandes utilisateur: {e}")
        test_results["user_orders"] = False
        all_tests_passed = False
    
    # ==================== ADMIN PRODUITS ====================
    print("\n👨‍💼 5. TEST ADMIN PRODUITS")
    print("-" * 30)
    
    # Test liste produits admin
    try:
        response = requests.get(f"{BASE_URL}/admin/products", headers=admin_headers)
        if response.status_code == 200:
            admin_products = response.json()
            print(f"   ✅ {len(admin_products)} produits admin récupérés")
            test_results["admin_list_products"] = True
        else:
            print(f"   ❌ Erreur liste produits admin: {response.status_code}")
            test_results["admin_list_products"] = False
            all_tests_passed = False
    except Exception as e:
        print(f"   ❌ Erreur liste produits admin: {e}")
        test_results["admin_list_products"] = False
        all_tests_passed = False
    
    # Test création produit admin
    try:
        response = requests.post(f"{BASE_URL}/admin/products", json={
            "name": "Test Produit Admin",
            "description": "Produit de test créé par admin",
            "price_cents": 2999,
            "stock_qty": 10,
            "active": True
        }, headers=admin_headers)
        if response.status_code == 201:
            new_product = response.json()
            test_admin_product_id = new_product["id"]
            print(f"   ✅ Produit admin créé: {test_admin_product_id}")
            test_results["admin_create_product"] = True
        else:
            print(f"   ❌ Erreur création produit admin: {response.status_code}")
            test_results["admin_create_product"] = False
            all_tests_passed = False
            test_admin_product_id = None
    except Exception as e:
        print(f"   ❌ Erreur création produit admin: {e}")
        test_results["admin_create_product"] = False
        all_tests_passed = False
        test_admin_product_id = None
    
    # ==================== ADMIN COMMANDES ====================
    print("\n👨‍💼 6. TEST ADMIN COMMANDES")
    print("-" * 30)
    
    # Test liste commandes admin
    try:
        response = requests.get(f"{BASE_URL}/admin/orders", headers=admin_headers)
        if response.status_code == 200:
            admin_orders = response.json()
            print(f"   ✅ {len(admin_orders)} commandes admin récupérées")
            test_results["admin_list_orders"] = True
        else:
            print(f"   ❌ Erreur liste commandes admin: {response.status_code}")
            test_results["admin_list_orders"] = False
            all_tests_passed = False
    except Exception as e:
        print(f"   ❌ Erreur liste commandes admin: {e}")
        test_results["admin_list_orders"] = False
        all_tests_passed = False
    
    # ==================== SUPPORT CLIENT ====================
    print("\n🎧 7. TEST SUPPORT CLIENT")
    print("-" * 30)
    
    # Test création fil support
    try:
        response = requests.post(f"{BASE_URL}/support/threads", json={
            "subject": "Test support client",
            "order_id": test_order_id
        }, headers=user_headers)
        if response.status_code == 200:
            support_thread = response.json()
            test_thread_id = support_thread["id"]
            print(f"   ✅ Fil support créé: {test_thread_id}")
            test_results["create_support_thread"] = True
        else:
            print(f"   ❌ Erreur création fil support: {response.status_code}")
            test_results["create_support_thread"] = False
            all_tests_passed = False
            test_thread_id = None
    except Exception as e:
        print(f"   ❌ Erreur création fil support: {e}")
        test_results["create_support_thread"] = False
        all_tests_passed = False
        test_thread_id = None
    
    # Test ajout message support
    if test_thread_id:
        try:
            response = requests.post(f"{BASE_URL}/support/threads/{test_thread_id}/messages", json={
                "content": "Message de test support client"
            }, headers=user_headers)
            if response.status_code == 200:
                print("   ✅ Message support ajouté")
                test_results["add_support_message"] = True
            else:
                print(f"   ❌ Erreur ajout message support: {response.status_code}")
                test_results["add_support_message"] = False
                all_tests_passed = False
        except Exception as e:
            print(f"   ❌ Erreur ajout message support: {e}")
            test_results["add_support_message"] = False
            all_tests_passed = False
    
    # ==================== SUPPORT ADMIN ====================
    print("\n👨‍💼 8. TEST SUPPORT ADMIN")
    print("-" * 30)
    
    # Test liste fils admin
    try:
        response = requests.get(f"{BASE_URL}/admin/support/threads", headers=admin_headers)
        if response.status_code == 200:
            admin_threads = response.json()
            print(f"   ✅ {len(admin_threads)} fils support admin récupérés")
            test_results["admin_support_threads"] = True
        else:
            print(f"   ❌ Erreur fils support admin: {response.status_code}")
            test_results["admin_support_threads"] = False
            all_tests_passed = False
    except Exception as e:
        print(f"   ❌ Erreur fils support admin: {e}")
        test_results["admin_support_threads"] = False
        all_tests_passed = False
    
    # Test réponse admin
    if test_thread_id:
        try:
            response = requests.post(f"{BASE_URL}/admin/support/threads/{test_thread_id}/messages", json={
                "content": "Réponse admin de test"
            }, headers=admin_headers)
            if response.status_code == 200:
                print("   ✅ Réponse admin ajoutée")
                test_results["admin_support_response"] = True
            else:
                print(f"   ❌ Erreur réponse admin: {response.status_code}")
                test_results["admin_support_response"] = False
                all_tests_passed = False
        except Exception as e:
            print(f"   ❌ Erreur réponse admin: {e}")
            test_results["admin_support_response"] = False
            all_tests_passed = False
    
    # ==================== PERFORMANCE ====================
    print("\n⚡ 9. TEST PERFORMANCE")
    print("-" * 30)
    
    # Test performance générale
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/products")
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
    
    # ==================== RÉSUMÉ FINAL ====================
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ COMPLET")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    
    print(f"\n🎯 Tests exécutés: {total_tests}")
    print(f"✅ Tests réussis: {passed_tests}")
    print(f"❌ Tests échoués: {total_tests - passed_tests}")
    
    print(f"\n📋 Détail par catégorie:")
    categories = {
        "Authentification": ["user_login", "admin_login"],
        "Produits": ["list_products", "get_product"],
        "Panier": ["view_cart", "add_to_cart"],
        "Commandes": ["checkout", "user_orders"],
        "Admin Produits": ["admin_list_products", "admin_create_product"],
        "Admin Commandes": ["admin_list_orders"],
        "Support Client": ["create_support_thread", "add_support_message"],
        "Support Admin": ["admin_support_threads", "admin_support_response"],
        "Performance": ["performance"]
    }
    
    for category, tests in categories.items():
        category_passed = sum(1 for test in tests if test_results.get(test, False))
        category_total = len(tests)
        status = "✅" if category_passed == category_total else "❌"
        print(f"   {status} {category}: {category_passed}/{category_total}")
    
    if all_tests_passed:
        print(f"\n🎉 AUCUNE RÉGRESSION DÉTECTÉE !")
        print(f"   Toutes les fonctionnalités fonctionnent parfaitement !")
        return True
    else:
        print(f"\n⚠️ RÉGRESSIONS DÉTECTÉES")
        print(f"   {passed_tests}/{total_tests} tests réussis")
        return False

if __name__ == "__main__":
    success = test_all_functionalities()
    sys.exit(0 if success else 1)
