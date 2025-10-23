#!/usr/bin/env python3
"""
Script de test complet pour vérifier toutes les fonctionnalités de l'application e-commerce
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
TEST_EMAIL_ADMIN = "admin@example.com"
TEST_PASSWORD_ADMIN = "admin"
TEST_EMAIL_USER = "client@example.com"
TEST_PASSWORD_USER = "secret"

class EcommerceTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.user_token = None
        self.admin_user = None
        self.user_user = None
        self.products = []
        self.orders = []
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        
    def test_api_health(self):
        """Test de santé de l'API"""
        try:
            response = self.session.get(f"{API_BASE}/health")
            if response.status_code == 200:
                self.log("✅ API en ligne")
                return True
            else:
                self.log(f"❌ API non accessible: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Erreur de connexion à l'API: {e}", "ERROR")
            return False
    
    def test_init_data(self):
        """Initialise les données de test"""
        try:
            response = self.session.post(f"{API_BASE}/init-data")
            if response.status_code == 200:
                self.log("✅ Données d'exemple initialisées")
                return True
            else:
                self.log(f"❌ Erreur initialisation: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Erreur initialisation: {e}", "ERROR")
            return False
    
    def test_admin_login(self):
        """Test de connexion admin"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL_ADMIN,
                "password": TEST_PASSWORD_ADMIN
            })
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["token"]
                self.log("✅ Connexion admin réussie")
                
                # Récupérer les infos utilisateur
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                user_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                if user_response.status_code == 200:
                    self.admin_user = user_response.json()
                    self.log(f"✅ Utilisateur admin: {self.admin_user['first_name']} {self.admin_user['last_name']}")
                    return True
                else:
                    self.log("❌ Erreur récupération infos admin", "ERROR")
                    return False
            else:
                self.log(f"❌ Erreur connexion admin: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Erreur connexion admin: {e}", "ERROR")
            return False
    
    def test_user_login(self):
        """Test de connexion utilisateur"""
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json={
                "email": TEST_EMAIL_USER,
                "password": TEST_PASSWORD_USER
            })
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["token"]
                self.log("✅ Connexion utilisateur réussie")
                
                # Récupérer les infos utilisateur
                headers = {"Authorization": f"Bearer {self.user_token}"}
                user_response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                if user_response.status_code == 200:
                    self.user_user = user_response.json()
                    self.log(f"✅ Utilisateur: {self.user_user['first_name']} {self.user_user['last_name']}")
                    return True
                else:
                    self.log("❌ Erreur récupération infos utilisateur", "ERROR")
                    return False
            else:
                self.log(f"❌ Erreur connexion utilisateur: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Erreur connexion utilisateur: {e}", "ERROR")
            return False
    
    def test_products_list(self):
        """Test de récupération des produits"""
        try:
            response = self.session.get(f"{API_BASE}/products")
            if response.status_code == 200:
                self.products = response.json()
                self.log(f"✅ {len(self.products)} produits récupérés")
                return True
            else:
                self.log(f"❌ Erreur récupération produits: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Erreur récupération produits: {e}", "ERROR")
            return False
    
    def test_cart_operations(self):
        """Test des opérations de panier"""
        if not self.products:
            self.log("❌ Aucun produit disponible pour tester le panier", "ERROR")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            
            # Ajouter un produit au panier
            product = self.products[0]
            response = self.session.post(f"{API_BASE}/cart/add", 
                headers=headers,
                json={"product_id": product["id"], "qty": 2}
            )
            if response.status_code == 200:
                self.log("✅ Produit ajouté au panier")
            else:
                self.log(f"❌ Erreur ajout panier: {response.status_code}", "ERROR")
                return False
            
            # Voir le panier
            response = self.session.get(f"{API_BASE}/cart", headers=headers)
            if response.status_code == 200:
                cart = response.json()
                self.log(f"✅ Panier récupéré: {len(cart['items'])} articles")
                return True
            else:
                self.log(f"❌ Erreur récupération panier: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Erreur opérations panier: {e}", "ERROR")
            return False
    
    def test_checkout(self):
        """Test de checkout"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.post(f"{API_BASE}/orders/checkout", headers=headers)
            if response.status_code == 200:
                order_data = response.json()
                self.orders.append(order_data)
                self.log(f"✅ Commande créée: {order_data['order_id']}")
                return order_data
            else:
                self.log(f"❌ Erreur checkout: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Erreur checkout: {e}", "ERROR")
            return None
    
    def test_payment(self, order_id):
        """Test de paiement"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.post(f"{API_BASE}/orders/{order_id}/pay", 
                headers=headers,
                json={
                    "card_number": "1234567890123456",  # Carte valide (ne finit pas par 0000)
                    "exp_month": 12,
                    "exp_year": 2025,
                    "cvc": "123"
                }
            )
            if response.status_code == 200:
                self.log("✅ Paiement réussi")
                return True
            else:
                self.log(f"❌ Erreur paiement: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Erreur paiement: {e}", "ERROR")
            return False
    
    def test_admin_validate_order(self, order_id):
        """Test de validation de commande par admin"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{API_BASE}/admin/orders/{order_id}/validate", headers=headers)
            if response.status_code == 200:
                self.log("✅ Commande validée par admin")
                return True
            else:
                self.log(f"❌ Erreur validation: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Erreur validation: {e}", "ERROR")
            return False
    
    def test_admin_ship_order(self, order_id):
        """Test d'expédition de commande par admin"""
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = self.session.post(f"{API_BASE}/admin/orders/{order_id}/ship", 
                headers=headers,
                json={
                    "transporteur": "Colissimo",
                    "tracking_number": "TRK123456789",
                    "delivery_status": "PREPAREE"
                }
            )
            if response.status_code == 200:
                self.log("✅ Commande expédiée par admin")
                return True
            else:
                self.log(f"❌ Erreur expédition: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Erreur expédition: {e}", "ERROR")
            return False
    
    def test_support_thread(self):
        """Test de création de fil de support"""
        try:
            headers = {"Authorization": f"Bearer {self.user_token}"}
            response = self.session.post(f"{API_BASE}/support/threads", 
                headers=headers,
                json={
                    "subject": "Test de support",
                    "order_id": self.orders[0]["order_id"] if self.orders else None
                }
            )
            if response.status_code == 200:
                self.log("✅ Fil de support créé")
                return True
            else:
                self.log(f"❌ Erreur création support: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Erreur création support: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        self.log("🚀 Démarrage des tests complets de l'application e-commerce")
        
        tests = [
            ("Santé de l'API", self.test_api_health),
            ("Initialisation des données", self.test_init_data),
            ("Connexion admin", self.test_admin_login),
            ("Connexion utilisateur", self.test_user_login),
            ("Récupération des produits", self.test_products_list),
            ("Opérations de panier", self.test_cart_operations),
        ]
        
        # Tests de base
        for test_name, test_func in tests:
            self.log(f"🧪 Test: {test_name}")
            if not test_func():
                self.log(f"❌ Test échoué: {test_name}", "ERROR")
                return False
        
        # Test de checkout et paiement
        self.log("🧪 Test: Checkout et paiement")
        order = self.test_checkout()
        if order:
            self.test_payment(order["order_id"])
        
        # Tests admin
        if self.orders:
            self.log("🧪 Test: Validation de commande par admin")
            self.test_admin_validate_order(self.orders[0]["order_id"])
            
            self.log("🧪 Test: Expédition de commande par admin")
            self.test_admin_ship_order(self.orders[0]["order_id"])
        
        # Test support
        self.log("🧪 Test: Support client")
        self.test_support_thread()
        
        self.log("✅ Tous les tests sont passés avec succès !")
        return True

def main():
    print("🛒 Test complet de l'application e-commerce")
    print("=" * 50)
    
    tester = EcommerceTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            print("\n🎉 Tous les tests sont passés avec succès !")
            print("✅ L'application e-commerce fonctionne correctement")
            sys.exit(0)
        else:
            print("\n❌ Certains tests ont échoué")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
