"""
Compatibilité pour les tests: expose quelques symboles attendus par tests/unit/test_api_endpoints.py
"""
from .api import (
    app,
    current_user,
    require_admin,
)

# Adapteurs simples vers les repositories utilisés dans api.py
from .database.repositories_simple import (
    PostgreSQLProductRepository,
    PostgreSQLCartRepository,
    PostgreSQLOrderRepository,
)

__all__ = [
    "app",
    "current_user",
    "require_admin",
    "PostgreSQLProductRepository",
    "PostgreSQLCartRepository",
    "PostgreSQLOrderRepository",
]

"""
API FastAPI unifiée regroupant authentification, catalogue, panier, commandes,
paiements et endpoints admin. Utilise les repositories PostgreSQL et un
service d'auth JWT pour centraliser la logique d'accès et de sécurité.
"""
# api_unified.py
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
from database.repositories_simple import (
    PostgreSQLUserRepository, PostgreSQLProductRepository, 
    PostgreSQLCartRepository, PostgreSQLOrderRepository,
    PostgreSQLInvoiceRepository, PostgreSQLPaymentRepository,
    PostgreSQLThreadRepository
)

# Import des services métier
from services.auth_service import AuthService

# Import des modèles
from database.models import User, Product, Order, OrderItem, Delivery, Invoice, Payment, MessageThread, Message
from enums import OrderStatus, DeliveryStatus

app = FastAPI(title="Ecommerce API (Unified)")

# -------------------------------- CORS --------------------------------
import os

# Configuration CORS sécurisée
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:5174",  # Vite dev server (port alternatif)
    "http://localhost:3000",  # React dev server alternatif
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",  # Vite dev server (port alternatif)
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

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    address: str = Field(..., min_length=1)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    price_cents: int = Field(..., gt=0)
    stock_qty: int = Field(..., ge=0)
    active: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = Field(None, gt=0)
    stock_qty: Optional[int] = Field(None, ge=0)
    active: Optional[bool] = None

class CartItemAdd(BaseModel):
    product_id: str
    qty: int = Field(..., gt=0)

class PaymentRequest(BaseModel):
    card_number: str = Field(..., min_length=13, max_length=19)
    exp_month: int = Field(..., ge=1, le=12)
    exp_year: int = Field(..., ge=2024)
    cvc: str = Field(..., min_length=3, max_length=4)

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1)

# -------------------------------- Dépendances --------------------------------

def get_user_repo(db: Session = Depends(get_db)) -> PostgreSQLUserRepository:
    return PostgreSQLUserRepository(db)

def get_product_repo(db: Session = Depends(get_db)) -> PostgreSQLProductRepository:
    return PostgreSQLProductRepository(db)

def get_cart_repo(db: Session = Depends(get_db)) -> PostgreSQLCartRepository:
    return PostgreSQLCartRepository(db)

def get_order_repo(db: Session = Depends(get_db)) -> PostgreSQLOrderRepository:
    return PostgreSQLOrderRepository(db)

def get_invoice_repo(db: Session = Depends(get_db)) -> PostgreSQLInvoiceRepository:
    return PostgreSQLInvoiceRepository(db)

def get_payment_repo(db: Session = Depends(get_db)) -> PostgreSQLPaymentRepository:
    return PostgreSQLPaymentRepository(db)

def get_thread_repo(db: Session = Depends(get_db)) -> PostgreSQLThreadRepository:
    return PostgreSQLThreadRepository(db)

def get_auth_service(user_repo: PostgreSQLUserRepository = Depends(get_user_repo)) -> AuthService:
    return AuthService(user_repo)

def current_user(authorization: str = Header(None), auth_service: AuthService = Depends(get_auth_service)) -> User:
    """Récupère l'utilisateur actuel depuis le token JWT"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    
    token = authorization.split(" ")[1]
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    # Récupérer l'utilisateur depuis la base de données
    user_repo = PostgreSQLUserRepository(next(get_db()))
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    
    return user

def require_admin(user: User = Depends(current_user)) -> User:
    """Vérifie que l'utilisateur est administrateur"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
    return user

# -------------------------------- Routes d'authentification --------------------------------

@app.post("/auth/register")
async def register(user_data: UserRegister, auth_service: AuthService = Depends(get_auth_service)):
    """Inscription d'un nouvel utilisateur"""
    try:
        user = auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            address=user_data.address
        )
        
        # Créer un token pour l'utilisateur
        access_token = auth_service.create_access_token(data={"sub": str(user.id)})
        
        return {
            "message": "Utilisateur créé avec succès",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_admin": user.is_admin
            },
            "access_token": access_token,
            "token_type": "bearer"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login")
async def login(login_data: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    """Connexion d'un utilisateur"""
    user = auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    access_token = auth_service.create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin
        }
    }

@app.post("/auth/logout")
async def logout():
    """Déconnexion (côté client)"""
    return {"message": "Déconnexion réussie"}

@app.get("/auth/me")
async def get_current_user(user: User = Depends(current_user)):
    """Récupère les informations de l'utilisateur connecté"""
    return {
        "id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "address": user.address,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat()
    }

@app.put("/auth/profile")
async def update_profile(
    user_data: UserUpdate, 
    user: User = Depends(current_user),
    user_repo: PostgreSQLUserRepository = Depends(get_user_repo)
):
    """Met à jour le profil de l'utilisateur connecté"""
    update_data = user_data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
    
    updated_user = user_repo.update(user.id, update_data)
    return {
        "message": "Profil mis à jour avec succès",
        "user": {
            "id": str(updated_user.id),
            "email": updated_user.email,
            "first_name": updated_user.first_name,
            "last_name": updated_user.last_name,
            "address": updated_user.address,
            "is_admin": updated_user.is_admin
        }
    }

# -------------------------------- Routes produits --------------------------------

@app.get("/products")
async def get_products(product_repo: PostgreSQLProductRepository = Depends(get_product_repo)):
    """Récupère tous les produits actifs"""
    products = product_repo.get_all_active()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "price_cents": p.price_cents,
            "stock_qty": p.stock_qty,
            "active": p.active
        }
        for p in products
    ]

@app.get("/products/{product_id}")
async def get_product(product_id: str, product_repo: PostgreSQLProductRepository = Depends(get_product_repo)):
    """Récupère un produit par son ID"""
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {
        "id": str(product.id),
        "name": product.name,
        "description": product.description,
        "price_cents": product.price_cents,
        "stock_qty": product.stock_qty,
        "active": product.active
    }

# -------------------------------- Routes panier --------------------------------

@app.get("/cart")
async def get_cart(user: User = Depends(current_user), cart_repo: PostgreSQLCartRepository = Depends(get_cart_repo)):
    """Récupère le panier de l'utilisateur connecté"""
    cart = cart_repo.get_by_user_id(user.id)
    if not cart:
        return {"items": [], "total_cents": 0}
    
    items = []
    total_cents = 0
    
    for item in cart.items:
        product = item.product
        item_total = product.price_cents * item.quantity
        total_cents += item_total
        
        items.append({
            "id": str(item.id),
            "product_id": str(product.id),
            "name": product.name,
            "unit_price_cents": product.price_cents,
            "quantity": item.quantity,
            "total_cents": item_total
        })
    
    return {
        "items": items,
        "total_cents": total_cents
    }

@app.post("/cart/add")
async def add_to_cart(
    item_data: CartItemAdd,
    user: User = Depends(current_user),
    cart_repo: PostgreSQLCartRepository = Depends(get_cart_repo),
    product_repo: PostgreSQLProductRepository = Depends(get_product_repo)
):
    """Ajoute un produit au panier"""
    # Vérifier que le produit existe et est actif
    product = product_repo.get_by_id(item_data.product_id)
    if not product or not product.active:
        raise HTTPException(status_code=404, detail="Produit non trouvé ou inactif")
    
    # Vérifier le stock
    if product.stock_qty < item_data.qty:
        raise HTTPException(status_code=400, detail="Stock insuffisant")
    
    # Ajouter au panier
    cart_repo.add_item(user.id, item_data.product_id, item_data.qty)
    
    return {"message": "Produit ajouté au panier"}

@app.post("/cart/remove")
async def remove_from_cart(
    item_data: CartItemAdd,
    user: User = Depends(current_user),
    cart_repo: PostgreSQLCartRepository = Depends(get_cart_repo)
):
    """Retire un produit du panier"""
    cart_repo.remove_item(user.id, item_data.product_id, item_data.qty)
    return {"message": "Produit retiré du panier"}

@app.delete("/cart/clear")
async def clear_cart(user: User = Depends(current_user), cart_repo: PostgreSQLCartRepository = Depends(get_cart_repo)):
    """Vide le panier"""
    cart_repo.clear(user.id)
    return {"message": "Panier vidé"}

# -------------------------------- Routes commandes --------------------------------

@app.post("/orders/checkout")
async def checkout(
    user: User = Depends(current_user),
    cart_repo: PostgreSQLCartRepository = Depends(get_cart_repo),
    order_repo: PostgreSQLOrderRepository = Depends(get_order_repo),
    product_repo: PostgreSQLProductRepository = Depends(get_product_repo)
):
    """Crée une commande depuis le panier"""
    cart = cart_repo.get_by_user_id(user.id)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Panier vide")
    
    # Vérifier le stock et réserver
    for item in cart.items:
        if item.product.stock_qty < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuffisant pour {item.product.name}")
        
        # Réserver le stock
        product_repo.reserve_stock(item.product.id, item.quantity)
    
    # Créer la commande
    order_data = {
        "user_id": user.id,
        "status": OrderStatus.CREE,
        "items": [
            {
                "product_id": item.product.id,
                "name": item.product.name,
                "unit_price_cents": item.product.price_cents,
                "quantity": item.quantity
            }
            for item in cart.items
        ]
    }
    
    order = order_repo.create(order_data)
    
    # Vider le panier
    cart_repo.clear(user.id)
    
    return {
        "message": "Commande créée avec succès",
        "order_id": str(order.id),
        "status": order.status
    }

@app.get("/orders")
async def get_orders(user: User = Depends(current_user), order_repo: PostgreSQLOrderRepository = Depends(get_order_repo)):
    """Récupère les commandes de l'utilisateur connecté"""
    orders = order_repo.get_by_user_id(user.id)
    
    return [
        {
            "id": str(order.id),
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "total_cents": sum(item.unit_price_cents * item.quantity for item in order.items),
            "items_count": len(order.items)
        }
        for order in orders
    ]

@app.get("/orders/{order_id}")
async def get_order(
    order_id: str,
    user: User = Depends(current_user),
    order_repo: PostgreSQLOrderRepository = Depends(get_order_repo)
):
    """Récupère une commande spécifique"""
    order = order_repo.get_by_id(order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    return {
        "id": str(order.id),
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "validated_at": order.validated_at.isoformat() if order.validated_at else None,
        "shipped_at": order.shipped_at.isoformat() if order.shipped_at else None,
        "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
        "items": [
            {
                "id": str(item.id),
                "product_id": str(item.product_id),
                "name": item.name,
                "unit_price_cents": item.unit_price_cents,
                "quantity": item.quantity,
                "total_cents": item.unit_price_cents * item.quantity
            }
            for item in order.items
        ],
        "total_cents": sum(item.unit_price_cents * item.quantity for item in order.items)
    }

@app.post("/orders/{order_id}/pay")
async def pay_order(
    order_id: str,
    payment_data: PaymentRequest,
    user: User = Depends(current_user),
    order_repo: PostgreSQLOrderRepository = Depends(get_order_repo),
    payment_repo: PostgreSQLPaymentRepository = Depends(get_payment_repo)
):
    """Effectue le paiement d'une commande"""
    order = order_repo.get_by_id(order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.status != OrderStatus.CREE:
        raise HTTPException(status_code=400, detail="Commande déjà payée ou invalide")
    
    # Simulation de paiement (carte qui finit par 0000 = échec)
    if payment_data.card_number.endswith("0000"):
        raise HTTPException(status_code=400, detail="Paiement refusé")
    
    # Créer le paiement
    total_cents = sum(item.unit_price_cents * item.quantity for item in order.items)
    payment_data_dict = {
        "order_id": order.id,
        "amount_cents": total_cents,
        "status": "SUCCEEDED",
        "payment_method": "card"
    }
    
    payment = payment_repo.create(payment_data_dict)
    
    # Mettre à jour la commande
    order_repo.update_status(order.id, OrderStatus.PAYEE)
    
    return {
        "message": "Paiement effectué avec succès",
        "payment_id": str(payment.id),
        "order_status": OrderStatus.PAYEE
    }

@app.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    user: User = Depends(current_user),
    order_repo: PostgreSQLOrderRepository = Depends(get_order_repo),
    product_repo: PostgreSQLProductRepository = Depends(get_product_repo)
):
    """Annule une commande"""
    order = order_repo.get_by_id(order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.status in [OrderStatus.EXPEDIEE, OrderStatus.LIVREE]:
        raise HTTPException(status_code=400, detail="Commande déjà expédiée, impossible d'annuler")
    
    # Restituer le stock
    for item in order.items:
        product_repo.release_stock(item.product_id, item.quantity)
    
    # Annuler la commande
    order_repo.update_status(order.id, OrderStatus.ANNULEE)
    
    return {"message": "Commande annulée"}

# -------------------------------- Routes admin --------------------------------

@app.get("/admin/products")
async def admin_get_products(admin: User = Depends(require_admin), product_repo: PostgreSQLProductRepository = Depends(get_product_repo)):
    """Récupère tous les produits (admin)"""
    products = product_repo.get_all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "price_cents": p.price_cents,
            "stock_qty": p.stock_qty,
            "active": p.active,
            "created_at": p.created_at.isoformat()
        }
        for p in products
    ]

@app.post("/admin/products")
async def admin_create_product(
    product_data: ProductCreate,
    admin: User = Depends(require_admin),
    product_repo: PostgreSQLProductRepository = Depends(get_product_repo)
):
    """Crée un nouveau produit (admin)"""
    product = product_repo.create(product_data.dict())
    return {
        "message": "Produit créé avec succès",
        "product": {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "price_cents": product.price_cents,
            "stock_qty": product.stock_qty,
            "active": product.active
        }
    }

@app.put("/admin/products/{product_id}")
async def admin_update_product(
    product_id: str,
    product_data: ProductUpdate,
    admin: User = Depends(require_admin),
    product_repo: PostgreSQLProductRepository = Depends(get_product_repo)
):
    """Met à jour un produit (admin)"""
    update_data = product_data.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
    
    product = product_repo.update(product_id, update_data)
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {
        "message": "Produit mis à jour avec succès",
        "product": {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
            "price_cents": product.price_cents,
            "stock_qty": product.stock_qty,
            "active": product.active
        }
    }

@app.delete("/admin/products/{product_id}")
async def admin_delete_product(
    product_id: str,
    admin: User = Depends(require_admin),
    product_repo: PostgreSQLProductRepository = Depends(get_product_repo)
):
    """Supprime un produit (admin)"""
    success = product_repo.delete(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return {"message": "Produit supprimé avec succès"}

@app.get("/admin/orders")
async def admin_get_orders(admin: User = Depends(require_admin), order_repo: PostgreSQLOrderRepository = Depends(get_order_repo)):
    """Récupère toutes les commandes (admin)"""
    orders = order_repo.get_all()
    return [
        {
            "id": str(order.id),
            "user_id": str(order.user_id),
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "total_cents": sum(item.unit_price_cents * item.quantity for item in order.items),
            "items_count": len(order.items)
        }
        for order in orders
    ]

@app.post("/admin/orders/{order_id}/validate")
async def admin_validate_order(
    order_id: str,
    admin: User = Depends(require_admin),
    order_repo: PostgreSQLOrderRepository = Depends(get_order_repo)
):
    """Valide une commande (admin)"""
    order = order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.status != OrderStatus.PAYEE:
        raise HTTPException(status_code=400, detail="Commande non payée")
    
    order_repo.update_status(order.id, OrderStatus.VALIDEE)
    return {"message": "Commande validée"}

@app.post("/admin/orders/{order_id}/ship")
async def admin_ship_order(
    order_id: str,
    admin: User = Depends(require_admin),
    order_repo: PostgreSQLOrderRepository = Depends(get_order_repo)
):
    """Expédie une commande (admin)"""
    order = order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.status != OrderStatus.VALIDEE:
        raise HTTPException(status_code=400, detail="Commande non validée")
    
    order_repo.update_status(order.id, OrderStatus.EXPEDIEE)
    return {"message": "Commande expédiée"}

@app.post("/admin/orders/{order_id}/mark-delivered")
async def admin_mark_delivered(
    order_id: str,
    admin: User = Depends(require_admin),
    order_repo: PostgreSQLOrderRepository = Depends(get_order_repo)
):
    """Marque une commande comme livrée (admin)"""
    order = order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    if order.status != OrderStatus.EXPEDIEE:
        raise HTTPException(status_code=400, detail="Commande non expédiée")
    
    order_repo.update_status(order.id, OrderStatus.LIVREE)
    return {"message": "Commande marquée comme livrée"}

# -------------------------------- Routes de santé --------------------------------

@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "API E-commerce",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
