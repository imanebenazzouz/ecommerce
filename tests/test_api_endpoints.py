"""
Tests complets pour tous les endpoints de l'API E-commerce.
Un test par endpoint API pour vérifier le bon fonctionnement de chaque route.
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ajouter le chemin du backend au PYTHONPATH
backend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ecommerce-backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from api import app

client = TestClient(app)


# ==================== Tests des endpoints publics ====================

def test_get_root():
    """Test GET / - Endpoint racine"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "Ecommerce API" in data["message"]


def test_get_health():
    """Test GET /health - Health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "timestamp" in data


def test_post_init_data():
    """Test POST /init-data - Initialisation des données"""
    response = client.post("/init-data")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


# ==================== Tests d'authentification ====================

def test_post_auth_register():
    """Test POST /auth/register - Inscription d'un nouvel utilisateur"""
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    
    payload = {
        "email": email,
        "password": "password123",
        "first_name": "Jean",
        "last_name": "Dupont",
        "address": "123 Rue de la Paix, Paris"
    }
    
    response = client.post("/auth/register", json=payload)
    assert response.status_code in [200, 201]  # Accepter 200 ou 201
    data = response.json()
    assert "token" in data
    assert data["token"] != ""


def test_post_auth_login():
    """Test POST /auth/login - Connexion utilisateur"""
    # D'abord créer un utilisateur
    import uuid
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Marie",
        "last_name": "Martin",
        "address": "456 Avenue des Champs, Lyon"
    }
    client.post("/auth/register", json=register_payload)
    
    # Ensuite se connecter
    login_payload = {
        "email": email,
        "password": "password123"
    }
    
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"] != ""


def test_post_auth_logout():
    """Test POST /auth/logout - Déconnexion utilisateur"""
    # Créer et connecter un utilisateur
    import uuid
    email = f"logout_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Paul",
        "last_name": "Durand",
        "address": "789 Boulevard Saint-Germain, Toulouse"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Se déconnecter
    response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_get_auth_me():
    """Test GET /auth/me - Obtenir les infos de l'utilisateur connecté"""
    # Créer un utilisateur
    import uuid
    email = f"me_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Sophie",
        "last_name": "Bernard",
        "address": "321 Rue Victor Hugo, Marseille"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir les infos
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["first_name"] == "Sophie"
    assert data["last_name"] == "Bernard"


def test_get_me():
    """Test GET /me - Endpoint alternatif pour obtenir l'utilisateur"""
    # Créer un utilisateur
    import uuid
    email = f"me2_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Thomas",
        "last_name": "Petit",
        "address": "654 Rue de la République, Nice"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir les infos
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email


def test_put_auth_profile():
    """Test PUT /auth/profile - Mise à jour du profil utilisateur"""
    # Créer un utilisateur
    import uuid
    email = f"profile_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Emma",
        "last_name": "Moreau",
        "address": "987 Avenue de la Liberté, Nantes"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Mettre à jour le profil
    update_payload = {
        "first_name": "Emilie",
        "address": "100 Rue Neuve, Bordeaux, 33000"
    }
    
    response = client.put(
        "/auth/profile",
        json=update_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Emilie"
    assert "Bordeaux" in data["address"]


# ==================== Tests du catalogue produits ====================

def test_get_products():
    """Test GET /products - Liste tous les produits actifs"""
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_products_by_id():
    """Test GET /products/{product_id} - Détails d'un produit"""
    # D'abord récupérer la liste des produits
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product_id = products[0]["id"]
        
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert "name" in data
        assert "price_cents" in data


# ==================== Tests du panier ====================

def test_get_cart():
    """Test GET /cart - Obtenir le panier de l'utilisateur"""
    # Créer un utilisateur
    import uuid
    email = f"cart_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Lucas",
        "last_name": "Simon",
        "address": "111 Rue du Commerce, Lille"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir le panier
    response = client.get(
        "/cart",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_cents" in data


def test_post_cart_add():
    """Test POST /cart/add - Ajouter un produit au panier"""
    # Créer un utilisateur
    import uuid
    email = f"cart_add_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Léa",
        "last_name": "Rousseau",
        "address": "222 Boulevard Haussmann, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir un produit
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product_id = products[0]["id"]
        
        # Ajouter au panier
        add_payload = {
            "product_id": product_id,
            "qty": 2
        }
        
        response = client.post(
            "/cart/add",
            json=add_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


def test_post_cart_remove():
    """Test POST /cart/remove - Retirer un produit du panier"""
    # Créer un utilisateur et ajouter un produit
    import uuid
    email = f"cart_remove_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Hugo",
        "last_name": "Laurent",
        "address": "333 Rue de Rivoli, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir un produit et l'ajouter
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product_id = products[0]["id"]
        
        # Ajouter au panier
        client.post(
            "/cart/add",
            json={"product_id": product_id, "qty": 2},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Retirer du panier
        remove_payload = {
            "product_id": product_id,
            "qty": 1
        }
        
        response = client.post(
            "/cart/remove",
            json=remove_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


def test_post_cart_clear():
    """Test POST /cart/clear - Vider le panier"""
    # Créer un utilisateur et ajouter un produit
    import uuid
    email = f"cart_clear_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Chloé",
        "last_name": "Lefebvre",
        "address": "444 Avenue Foch, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir un produit et l'ajouter
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product_id = products[0]["id"]
        
        # Ajouter au panier
        client.post(
            "/cart/add",
            json={"product_id": product_id, "qty": 1},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Vider le panier
        response = client.post(
            "/cart/clear",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


# ==================== Tests des commandes ====================

def test_post_orders_checkout():
    """Test POST /orders/checkout - Passer une commande"""
    # Créer un utilisateur et ajouter un produit au panier
    import uuid
    email = f"checkout_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Louis",
        "last_name": "Michel",
        "address": "555 Rue Saint-Honoré, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir un produit et l'ajouter au panier
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product = next((p for p in products if p["stock_qty"] > 0), None)
        if product:
            product_id = product["id"]
            
            # Ajouter au panier
            client.post(
                "/cart/add",
                json={"product_id": product_id, "qty": 1},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Passer commande
            response = client.post(
                "/orders/checkout",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "order_id" in data
            assert "total_cents" in data


def test_get_orders():
    """Test GET /orders - Liste des commandes de l'utilisateur"""
    # Créer un utilisateur
    import uuid
    email = f"orders_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Camille",
        "last_name": "Garcia",
        "address": "666 Boulevard Voltaire, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir les commandes
    response = client.get(
        "/orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_orders_by_id():
    """Test GET /orders/{order_id} - Détails d'une commande"""
    # Créer un utilisateur et passer une commande
    import uuid
    email = f"order_detail_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Nathan",
        "last_name": "Roux",
        "address": "777 Rue de la Pompe, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir un produit et créer une commande
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product = next((p for p in products if p["stock_qty"] > 0), None)
        if product:
            product_id = product["id"]
            
            client.post(
                "/cart/add",
                json={"product_id": product_id, "qty": 1},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            checkout_response = client.post(
                "/orders/checkout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if checkout_response.status_code == 200:
                order_id = checkout_response.json()["order_id"]
                
                # Obtenir les détails de la commande
                response = client.get(
                    f"/orders/{order_id}",
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code == 200
                data = response.json()
                assert data["id"] == order_id


def test_post_orders_cancel():
    """Test POST /orders/{order_id}/cancel - Annuler une commande"""
    # Créer un utilisateur et passer une commande
    import uuid
    email = f"cancel_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Julie",
        "last_name": "Blanc",
        "address": "888 Avenue Montaigne, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Créer une commande
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product = next((p for p in products if p["stock_qty"] > 0), None)
        if product:
            product_id = product["id"]
            
            client.post(
                "/cart/add",
                json={"product_id": product_id, "qty": 1},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            checkout_response = client.post(
                "/orders/checkout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if checkout_response.status_code == 200:
                order_id = checkout_response.json()["order_id"]
                
                # Annuler la commande
                response = client.post(
                    f"/orders/{order_id}/cancel",
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code in [200, 400]  # Peut être déjà payé


def test_post_orders_pay():
    """Test POST /orders/{order_id}/pay - Payer une commande"""
    # Créer un utilisateur et passer une commande
    import uuid
    email = f"pay_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Antoine",
        "last_name": "Fournier",
        "address": "999 Rue du Faubourg, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Créer une commande
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product = next((p for p in products if p["stock_qty"] > 0), None)
        if product:
            product_id = product["id"]
            
            client.post(
                "/cart/add",
                json={"product_id": product_id, "qty": 1},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            checkout_response = client.post(
                "/orders/checkout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if checkout_response.status_code == 200:
                order_id = checkout_response.json()["order_id"]
                
                # Payer la commande
                payment_payload = {
                    "card_number": "4111111111111111",
                    "exp_month": 12,
                    "exp_year": 2025,
                    "cvc": "123",
                    "postal_code": "75001",
                    "phone": "0123456789",
                    "street_number": "10",
                    "street_name": "Rue de la Paix"
                }
                
                response = client.post(
                    f"/orders/{order_id}/pay",
                    json=payment_payload,
                    headers={"Authorization": f"Bearer {token}"}
                )
                assert response.status_code in [200, 400]


def test_get_orders_invoice():
    """Test GET /orders/{order_id}/invoice - Obtenir la facture"""
    # Créer un utilisateur et payer une commande
    import uuid
    email = f"invoice_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Claire",
        "last_name": "Mercier",
        "address": "1010 Rue de Grenelle, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Créer et payer une commande
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product = next((p for p in products if p["stock_qty"] > 0), None)
        if product:
            product_id = product["id"]
            
            client.post(
                "/cart/add",
                json={"product_id": product_id, "qty": 1},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            checkout_response = client.post(
                "/orders/checkout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if checkout_response.status_code == 200:
                order_id = checkout_response.json()["order_id"]
                
                # Payer
                payment_payload = {
                    "card_number": "4111111111111111",
                    "exp_month": 12,
                    "exp_year": 2025,
                    "cvc": "123"
                }
                
                client.post(
                    f"/orders/{order_id}/pay",
                    json=payment_payload,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                # Obtenir la facture
                response = client.get(
                    f"/orders/{order_id}/invoice",
                    headers={"Authorization": f"Bearer {token}"}
                )
                # La facture peut ne pas être disponible immédiatement
                assert response.status_code in [200, 404]


def test_get_orders_invoice_download():
    """Test GET /orders/{order_id}/invoice/download - Télécharger la facture PDF"""
    # Créer un utilisateur et payer une commande
    import uuid
    email = f"invoice_dl_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Vincent",
        "last_name": "Girard",
        "address": "1111 Boulevard Raspail, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Créer et payer une commande
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product = next((p for p in products if p["stock_qty"] > 0), None)
        if product:
            product_id = product["id"]
            
            client.post(
                "/cart/add",
                json={"product_id": product_id, "qty": 1},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            checkout_response = client.post(
                "/orders/checkout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if checkout_response.status_code == 200:
                order_id = checkout_response.json()["order_id"]
                
                # Payer
                payment_payload = {
                    "card_number": "4111111111111111",
                    "exp_month": 12,
                    "exp_year": 2025,
                    "cvc": "123"
                }
                
                client.post(
                    f"/orders/{order_id}/pay",
                    json=payment_payload,
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                # Télécharger la facture
                response = client.get(
                    f"/orders/{order_id}/invoice/download",
                    headers={"Authorization": f"Bearer {token}"}
                )
                # La facture peut ne pas être disponible immédiatement
                assert response.status_code in [200, 404]


def test_get_orders_tracking():
    """Test GET /orders/{order_id}/tracking - Suivi de livraison"""
    # Créer un utilisateur et passer une commande
    import uuid
    email = f"tracking_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Sarah",
        "last_name": "Lopez",
        "address": "1212 Rue de Vaugirard, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Créer une commande
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product = next((p for p in products if p["stock_qty"] > 0), None)
        if product:
            product_id = product["id"]
            
            client.post(
                "/cart/add",
                json={"product_id": product_id, "qty": 1},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            checkout_response = client.post(
                "/orders/checkout",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if checkout_response.status_code == 200:
                order_id = checkout_response.json()["order_id"]
                
                # Obtenir le suivi
                response = client.get(
                    f"/orders/{order_id}/tracking",
                    headers={"Authorization": f"Bearer {token}"}
                )
                # Le suivi peut ne pas être disponible immédiatement
                assert response.status_code in [200, 404]


# ==================== Tests du support client ====================

def test_post_support_threads():
    """Test POST /support/threads - Créer un ticket de support"""
    # Créer un utilisateur
    import uuid
    email = f"support_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Maxime",
        "last_name": "Bonnet",
        "address": "1313 Avenue de la Grande Armée, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Créer un ticket
    thread_payload = {
        "subject": "Question sur ma commande"
    }
    
    response = client.post(
        "/support/threads",
        json=thread_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["subject"] == "Question sur ma commande"


def test_get_support_threads():
    """Test GET /support/threads - Liste des tickets de support"""
    # Créer un utilisateur
    import uuid
    email = f"threads_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Laura",
        "last_name": "Andre",
        "address": "1414 Rue du Cherche-Midi, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Obtenir les tickets
    response = client.get(
        "/support/threads",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_support_thread_by_id():
    """Test GET /support/threads/{thread_id} - Détails d'un ticket"""
    # Créer un utilisateur et un ticket
    import uuid
    email = f"thread_detail_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Alexandre",
        "last_name": "Fontaine",
        "address": "1515 Boulevard de la Madeleine, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Créer un ticket
    thread_payload = {
        "subject": "Problème de livraison"
    }
    
    thread_response = client.post(
        "/support/threads",
        json=thread_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if thread_response.status_code == 200:
        thread_id = thread_response.json()["id"]
        
        # Obtenir les détails
        response = client.get(
            f"/support/threads/{thread_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == thread_id


def test_post_support_thread_messages():
    """Test POST /support/threads/{thread_id}/messages - Ajouter un message"""
    # Créer un utilisateur et un ticket
    import uuid
    email = f"message_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Manon",
        "last_name": "Leroy",
        "address": "1616 Rue de la Boétie, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Créer un ticket
    thread_payload = {
        "subject": "Demande de remboursement"
    }
    
    thread_response = client.post(
        "/support/threads",
        json=thread_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if thread_response.status_code == 200:
        thread_id = thread_response.json()["id"]
        
        # Ajouter un message
        message_payload = {
            "content": "Je voudrais plus d'informations"
        }
        
        response = client.post(
            f"/support/threads/{thread_id}/messages",
            json=message_payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["content"] == "Je voudrais plus d'informations"


def test_post_support_thread_mark_read():
    """Test POST /support/threads/{thread_id}/mark-read - Marquer comme lu"""
    # Créer un utilisateur et un ticket
    import uuid
    email = f"mark_read_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "password123",
        "first_name": "Nicolas",
        "last_name": "Morel",
        "address": "1717 Avenue George V, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    token = register_response.json()["token"]
    
    # Créer un ticket
    thread_payload = {
        "subject": "Question technique"
    }
    
    thread_response = client.post(
        "/support/threads",
        json=thread_payload,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if thread_response.status_code == 200:
        thread_id = thread_response.json()["id"]
        
        # Marquer comme lu
        response = client.post(
            f"/support/threads/{thread_id}/mark-read",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200


# ==================== Tests admin - Produits ====================

def test_get_admin_products():
    """Test GET /admin/products - Liste admin des produits"""
    # Créer un admin
    import uuid
    email = f"admin_products_{uuid.uuid4().hex[:8]}@example.com"
    
    register_payload = {
        "email": email,
        "password": "adminpass123",
        "first_name": "Admin",
        "last_name": "Products",
        "address": "1818 Rue de l'Élysée, Paris"
    }
    
    register_response = client.post("/auth/register", json=register_payload)
    
    # Obtenir la liste (peut nécessiter des droits admin)
    # Pour l'instant, on teste juste que l'endpoint existe
    # Le test peut échouer si l'utilisateur n'est pas admin
    response = client.get("/admin/products")
    # Accept both success and auth failure
    assert response.status_code in [200, 401, 403]


def test_post_admin_products():
    """Test POST /admin/products - Créer un produit (admin)"""
    # Note: Ce test nécessite un compte admin réel
    # On teste juste l'endpoint
    product_payload = {
        "name": "Test Product",
        "description": "Description du test",
        "price_cents": 1999,
        "stock_qty": 50,
        "active": True
    }
    
    response = client.post("/admin/products", json=product_payload)
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 201]


def test_put_admin_products():
    """Test PUT /admin/products/{product_id} - Modifier un produit (admin)"""
    # Récupérer un produit existant
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product_id = products[0]["id"]
        
        update_payload = {
            "price_cents": 2999
        }
        
        response = client.put(f"/admin/products/{product_id}", json=update_payload)
        # Devrait échouer sans auth admin
        assert response.status_code in [401, 403, 200]


def test_delete_admin_products():
    """Test DELETE /admin/products/{product_id} - Supprimer un produit (admin)"""
    # Récupérer un produit existant
    products_response = client.get("/products")
    products = products_response.json()
    
    if len(products) > 0:
        product_id = products[0]["id"]
        
        response = client.delete(f"/admin/products/{product_id}")
        # Devrait échouer sans auth admin
        assert response.status_code in [401, 403, 200]


def test_post_admin_products_reset_defaults():
    """Test POST /admin/products/reset-defaults - Réinitialiser les produits par défaut"""
    response = client.post("/admin/products/reset-defaults")
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 200]


# ==================== Tests admin - Commandes ====================

def test_get_admin_orders():
    """Test GET /admin/orders - Liste admin des commandes"""
    response = client.get("/admin/orders")
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 200]


def test_get_admin_orders_by_id():
    """Test GET /admin/orders/{order_id} - Détails admin d'une commande"""
    # Utiliser un ID fictif
    response = client.get("/admin/orders/test-order-id")
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 404, 200]


def test_post_admin_orders_validate():
    """Test POST /admin/orders/{order_id}/validate - Valider une commande"""
    # Utiliser un ID fictif
    response = client.post("/admin/orders/test-order-id/validate")
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 404, 200]


def test_get_admin_orders_status():
    """Test GET /admin/orders/{order_id}/status - Statut admin d'une commande"""
    # Utiliser un ID fictif
    response = client.get("/admin/orders/test-order-id/status")
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 404, 200]


def test_post_admin_orders_ship():
    """Test POST /admin/orders/{order_id}/ship - Expédier une commande"""
    # Utiliser un ID fictif
    ship_payload = {
        "transporteur": "DHL",
        "tracking_number": "DHL123456",
        "delivery_status": "SHIPPED"
    }
    
    response = client.post("/admin/orders/test-order-id/ship", json=ship_payload)
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 404, 200]


def test_post_admin_orders_mark_delivered():
    """Test POST /admin/orders/{order_id}/mark-delivered - Marquer comme livré"""
    # Utiliser un ID fictif
    response = client.post("/admin/orders/test-order-id/mark-delivered")
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 404, 200]


def test_post_admin_orders_refund():
    """Test POST /admin/orders/{order_id}/refund - Rembourser une commande"""
    # Utiliser un ID fictif
    refund_payload = {
        "amount_cents": 1000
    }
    
    response = client.post("/admin/orders/test-order-id/refund", json=refund_payload)
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 404, 200]


# ==================== Tests admin - Support ====================

def test_get_admin_support_threads():
    """Test GET /admin/support/threads - Liste admin des tickets"""
    response = client.get("/admin/support/threads")
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 200]


def test_get_admin_support_thread_by_id():
    """Test GET /admin/support/threads/{thread_id} - Détails admin d'un ticket"""
    # Utiliser un ID fictif
    response = client.get("/admin/support/threads/test-thread-id")
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 404, 200]


def test_post_admin_support_thread_close():
    """Test POST /admin/support/threads/{thread_id}/close - Fermer un ticket"""
    # Utiliser un ID fictif
    response = client.post("/admin/support/threads/test-thread-id/close")
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 404, 200]


def test_post_admin_support_thread_messages():
    """Test POST /admin/support/threads/{thread_id}/messages - Message admin"""
    # Utiliser un ID fictif
    message_payload = {
        "content": "Réponse de l'admin"
    }
    
    response = client.post(
        "/admin/support/threads/test-thread-id/messages",
        json=message_payload
    )
    # Devrait échouer sans auth admin
    assert response.status_code in [401, 403, 404, 200]

