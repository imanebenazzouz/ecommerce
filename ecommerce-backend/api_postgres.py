"""
API FastAPI basée sur PostgreSQL (ancienne variante d'exemple).

Contient des endpoints illustratifs avec repositories alternatifs et logique
simplifiée. À utiliser principalement comme référence ou pour des tests.
"""
# api_postgres.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid
import io
import time
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# Import des repositories PostgreSQL
from database.database import get_db, Session
from database.repositories import (
    PostgreSQLUserRepository, PostgreSQLProductRepository, 
    PostgreSQLCartRepository, PostgreSQLOrderRepository
)

# Import du moteur métier
from backend_demo import (
    AuthService, CatalogService, CartService, BillingService, DeliveryService,
    PaymentGateway, OrderService, CustomerService, Product, OrderStatus, DeliveryStatus, Delivery,
    MessageThread, Message
)

app = FastAPI(title="Ecommerce API (PostgreSQL)")

# -------------------------------- CORS --------------------------------
import os

# Configuration CORS sécurisée
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server alternatif
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://localhost:5178",   # Port alternatif Vite
    "http://localhost:5181",   # Port alternatif Vite
    "http://127.0.0.1:5181",   # Port alternatif Vite
    "http://localhost:5182",   # Port alternatif Vite
    "http://127.0.0.1:5182",   # Port alternatif Vite
    "http://localhost:5183",   # Port alternatif Vite
    "http://127.0.0.1:5183",   # Port alternatif Vite
]

# Ajouter les origines de production si définies
if os.getenv("PRODUCTION_ORIGINS"):
    ALLOWED_ORIGINS.extend(os.getenv("PRODUCTION_ORIGINS").split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------- Modèles Pydantic --------------------------------

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    address: str

class UserProfile(BaseModel):
    first_name: str
    last_name: str
    address: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price_cents: int = Field(gt=0, description="Prix en centimes")
    stock_qty: int = Field(ge=0, description="Quantité en stock")

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = Field(None, gt=0)
    stock_qty: Optional[int] = Field(None, ge=0)
    active: Optional[bool] = None

class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    items: List[CartItemAdd]

class PaymentRequest(BaseModel):
    order_id: str
    payment_method: str = "CB"

class MessageCreate(BaseModel):
    subject: str
    content: str

class MessageReply(BaseModel):
    content: str

# -------------------------------- Services --------------------------------

def get_user_repo(db: Session = Depends(get_db)):
    return PostgreSQLUserRepository(db)

def get_product_repo(db: Session = Depends(get_db)):
    return PostgreSQLProductRepository(db)

def get_cart_repo(db: Session = Depends(get_db)):
    return PostgreSQLCartRepository(db)

def get_order_repo(db: Session = Depends(get_db)):
    return PostgreSQLOrderRepository(db)

# -------------------------------- Authentification --------------------------------

def get_current_user(authorization: str = Header(None), user_repo: PostgreSQLUserRepository = Depends(get_user_repo)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token d'authentification manquant")
    
    token = authorization.split(" ")[1]
    # Ici vous devriez valider le JWT token
    # Pour simplifier, on va chercher l'utilisateur par email
    # Dans un vrai système, vous extrairiez l'email du token JWT
    raise HTTPException(status_code=501, detail="Authentification JWT non implémentée")

# -------------------------------- Routes API --------------------------------

@app.get("/")
async def root():
    return {"message": "Ecommerce API (PostgreSQL)", "version": "2.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "postgresql"}

# -------------------------------- Authentification --------------------------------

@app.post("/auth/login")
async def login(credentials: UserLogin, user_repo: PostgreSQLUserRepository = Depends(get_user_repo)):
    """Connexion utilisateur"""
    user = user_repo.get_by_email(credentials.email)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # Ici vous devriez vérifier le mot de passe avec bcrypt
    # Pour simplifier, on accepte n'importe quel mot de passe
    if credentials.password != "password":  # Mot de passe par défaut pour les tests
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    # Générer un token JWT (simplifié)
    token = f"fake_jwt_token_{user.id}"
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin
        }
    }

@app.post("/auth/register")
async def register(user_data: UserRegister, user_repo: PostgreSQLUserRepository = Depends(get_user_repo)):
    """Inscription utilisateur"""
    # Vérifier si l'utilisateur existe déjà
    existing_user = user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Un utilisateur avec cet email existe déjà")
    
    # Créer le nouvel utilisateur
    import bcrypt
    password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        password_hash=password_hash,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        address=user_data.address,
        is_admin=False
    )
    
    user_repo.add(new_user)
    
    return {"message": "Utilisateur créé avec succès", "user_id": new_user.id}

# -------------------------------- Produits --------------------------------

@app.get("/products")
async def get_products(product_repo: PostgreSQLProductRepository = Depends(get_product_repo)):
    """Liste des produits"""
    products = product_repo.get_all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price_cents": p.price_cents,
            "stock_qty": p.stock_qty,
            "active": p.active
        } for p in products
    ]

@app.get("/products/{product_id}")
async def get_product(product_id: str, product_repo: PostgreSQLProductRepository = Depends(get_product_repo)):
    """Détails d'un produit"""
    product = product_repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price_cents": product.price_cents,
        "stock_qty": product.stock_qty,
        "active": product.active
    }

# -------------------------------- Panier --------------------------------

@app.get("/cart")
async def get_cart(user_id: str = "test-user", cart_repo: PostgreSQLCartRepository = Depends(get_cart_repo)):
    """Récupérer le panier de l'utilisateur"""
    cart = cart_repo.get(user_id)
    return {
        "user_id": cart.user_id,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity
            } for item in cart.items.values()
        ]
    }

@app.post("/cart/add")
async def add_to_cart(
    item: CartItemAdd, 
    user_id: str = "test-user",
    cart_repo: PostgreSQLCartRepository = Depends(get_cart_repo),
    product_repo: PostgreSQLProductRepository = Depends(get_product_repo)
):
    """Ajouter un produit au panier"""
    # Récupérer le produit
    product = product_repo.get(item.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Récupérer le panier
    cart = cart_repo.get(user_id)
    
    # Ajouter l'article
    cart.add(product, item.quantity)
    
    # Sauvegarder le panier
    cart_repo.save(cart)
    
    return {"message": "Produit ajouté au panier"}

# -------------------------------- Commandes --------------------------------

@app.get("/orders")
async def get_orders(user_id: str = "test-user", order_repo: PostgreSQLOrderRepository = Depends(get_order_repo)):
    """Liste des commandes de l'utilisateur"""
    orders = order_repo.get_by_user(user_id)
    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status.name,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "items": [
                {
                    "product_id": item.product_id,
                    "name": item.name,
                    "unit_price_cents": item.unit_price_cents,
                    "quantity": item.quantity
                } for item in order.items
            ]
        } for order in orders
    ]

@app.get("/orders/{order_id}")
async def get_order(order_id: str, order_repo: PostgreSQLOrderRepository = Depends(get_order_repo)):
    """Détails d'une commande"""
    order = order_repo.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status.name,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "validated_at": order.validated_at.isoformat() if order.validated_at else None,
        "shipped_at": order.shipped_at.isoformat() if order.shipped_at else None,
        "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
        "items": [
            {
                "product_id": item.product_id,
                "name": item.name,
                "unit_price_cents": item.unit_price_cents,
                "quantity": item.quantity
            } for item in order.items
        ],
        "delivery": {
            "id": order.delivery.id,
            "transporteur": order.delivery.transporteur,
            "tracking_number": order.delivery.tracking_number,
            "address": order.delivery.address,
            "delivery_status": order.delivery.delivery_status.value
        } if order.delivery else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
