# api_postgres_simple.py
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
from database.database import get_db, Session, create_tables
from database.repositories_simple import (
    PostgreSQLUserRepository, PostgreSQLProductRepository, 
    PostgreSQLCartRepository, PostgreSQLOrderRepository,
    PostgreSQLInvoiceRepository, PostgreSQLPaymentRepository,
    PostgreSQLThreadRepository
)

# Import des modèles de base de données
from database.models import User, Product, Order, OrderItem, Delivery, Invoice, Payment, MessageThread, Message

app = FastAPI(title="Ecommerce API (PostgreSQL)")

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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization", 
        "Content-Type", 
        "Accept",
        "Origin",
        "X-Requested-With"
    ],
)

# --------------------------- Initialisation base de données ---------------------------
# Créer les tables si elles n'existent pas
create_tables()

# Session manager simple en mémoire pour l'authentification
class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id: str) -> str:
        token = f"token_{user_id}_{int(time.time())}"
        self.sessions[token] = {
            "user_id": user_id,
            "created_at": time.time()
        }
        return token
    
    def get_user_id(self, token: str) -> Optional[str]:
        if token in self.sessions:
            return self.sessions[token]["user_id"]
        return None
    
    def logout(self, token: str):
        if token in self.sessions:
            del self.sessions[token]

sessions = SessionManager()

# Fonction pour initialiser les données de base
def init_sample_data(db: Session):
    """Initialise les données d'exemple si elles n'existent pas"""
    product_repo = PostgreSQLProductRepository(db)
    user_repo = PostgreSQLUserRepository(db)
    
    # Vérifier si des produits existent déjà
    existing_products = product_repo.get_all_active()
    if not existing_products:
        # Créer des produits d'exemple
        p1_data = {
            "name": "T-Shirt Logo",
            "description": "Coton bio",
            "price_cents": 1999,
            "stock_qty": 100,
            "active": True
        }
        p2_data = {
            "name": "Sweat Capuche", 
            "description": "Molleton",
            "price_cents": 4999,
            "stock_qty": 50,
            "active": True
        }
        product_repo.create(p1_data)
        product_repo.create(p2_data)
    
    # Vérifier si des utilisateurs existent déjà
    existing_users = user_repo.get_all()
    if not existing_users:
        # Créer des utilisateurs d'exemple (mots de passe non hachés pour la démo)
        admin_data = {
            "email": "admin@example.com",
            "password_hash": "admin",  # En production, utiliser bcrypt
            "first_name": "Admin",
            "last_name": "Root",
            "address": "1 Rue du BO",
            "is_admin": True
        }
        user_data = {
            "email": "client@example.com", 
            "password_hash": "secret",  # En production, utiliser bcrypt
            "first_name": "Alice",
            "last_name": "Martin",
            "address": "12 Rue des Fleurs",
            "is_admin": False
        }
        user_repo.create(admin_data)
        user_repo.create(user_data)

# ------------------------------- Schemas --------------------------------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: str
    last_name: str
    address: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    address: str
    is_admin: bool

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    token: str

class ProductOut(BaseModel):
    id: str
    name: str
    description: str
    price_cents: int
    stock_qty: int
    active: bool

class CartItemOut(BaseModel):
    product_id: str
    quantity: int

class CartOut(BaseModel):
    user_id: str
    items: dict[str, CartItemOut]

class CartAddIn(BaseModel):
    product_id: str
    qty: int = Field(default=1, ge=1)

class OrderOut(BaseModel):
    id: str
    user_id: str
    items: List[dict]
    status: str
    total_cents: int
    created_at: datetime

# ------------------------------- Helpers --------------------------------
def validate_token_format(token: str) -> bool:
    """Valider le format du token"""
    return token.startswith("token_")

def current_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Token manquant (Authorization: Bearer <token>)")
    
    token = authorization.split(" ", 1)[1].strip()
    
    if not validate_token_format(token):
        raise HTTPException(401, "Format de token invalide")
    
    uid = sessions.get_user_id(token)
    if not uid:
        raise HTTPException(401, "Session invalide ou expirée")
    return uid

def current_user(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    uid = current_user_id(authorization)
    user_repo = PostgreSQLUserRepository(db)
    user = user_repo.get_by_id(uid)
    if not user:
        raise HTTPException(401, "Session invalide (user)")
    return user

def require_admin(user = Depends(current_user)):
    if not user.is_admin:
        raise HTTPException(403, "Accès réservé aux administrateurs")
    return user

# ------------------------------- Routes --------------------------------

# Santé / test
@app.get("/")
def root():
    return {"message": "Ecommerce API (PostgreSQL) is running!", "version": "1.0"}

# Initialisation des données
@app.post("/init-data")
def initialize_data(db: Session = Depends(get_db)):
    """Initialise les données d'exemple dans la base de données"""
    try:
        init_sample_data(db)
        return {"message": "Données d'exemple initialisées avec succès"}
    except Exception as e:
        raise HTTPException(500, f"Erreur lors de l'initialisation: {str(e)}")

# ---------- Authentification ----------
@app.post("/auth/register", response_model=UserOut)
def register(inp: RegisterIn, db: Session = Depends(get_db)):
    try:
        user_repo = PostgreSQLUserRepository(db)
        
        # Vérifier si l'email existe déjà
        existing_user = user_repo.get_by_email(inp.email)
        if existing_user:
            raise HTTPException(400, "Cette adresse email est déjà utilisée")
        
        # Créer l'utilisateur
        user_data = {
            "email": inp.email,
            "password_hash": inp.password,  # En production, utiliser bcrypt
            "first_name": inp.first_name,
            "last_name": inp.last_name,
            "address": inp.address,
            "is_admin": False
        }
        
        user = user_repo.create(user_data)
        return UserOut(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            address=user.address,
            is_admin=user.is_admin
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Erreur lors de l'inscription: {str(e)}")

@app.post("/auth/login", response_model=TokenOut)
def login(inp: LoginIn, db: Session = Depends(get_db)):
    try:
        user_repo = PostgreSQLUserRepository(db)
        user = user_repo.get_by_email(inp.email)
        
        if not user or user.password_hash != inp.password:
            raise HTTPException(401, "Identifiants invalides")
        
        token = sessions.create_session(str(user.id))
        return TokenOut(token=token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(401, "Identifiants invalides")

@app.post("/auth/logout")
def logout(uid: str = Depends(current_user_id), authorization: Optional[str] = Header(default=None)):
    token = authorization.split(" ", 1)[1].strip()
    sessions.logout(token)
    return {"ok": True}

@app.get("/auth/me", response_model=UserOut)
def me(user = Depends(current_user)):
    return UserOut(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        address=user.address,
        is_admin=user.is_admin
    )

# ---------- Produits (public) ----------
@app.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    product_repo = PostgreSQLProductRepository(db)
    products = product_repo.get_all_active()
    return [ProductOut(
        id=str(p.id),
        name=p.name,
        description=p.description,
        price_cents=p.price_cents,
        stock_qty=p.stock_qty,
        active=p.active
    ) for p in products]

# ---------- Panier ----------
@app.get("/cart", response_model=CartOut)
def view_cart(uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    cart_repo = PostgreSQLCartRepository(db)
    cart = cart_repo.get_by_user_id(uid)
    
    if not cart:
        return CartOut(user_id=uid, items={})
    
    # Charger les articles du panier
    items = {}
    for item in cart.items:
        items[str(item.product_id)] = CartItemOut(
            product_id=str(item.product_id),
            quantity=item.quantity
        )
    
    return CartOut(user_id=uid, items=items)

@app.post("/cart/add")
def add_to_cart(inp: CartAddIn, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    try:
        cart_repo = PostgreSQLCartRepository(db)
        product_repo = PostgreSQLProductRepository(db)
        
        # Vérifier que le produit existe et est actif
        product = product_repo.get_by_id(inp.product_id)
        if not product or not product.active:
            raise HTTPException(404, "Produit introuvable")
        
        if product.stock_qty < inp.qty:
            raise HTTPException(400, "Stock insuffisant")
        
        # Ajouter au panier
        cart_repo.add_item(uid, inp.product_id, inp.qty)
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Erreur lors de l'ajout au panier: {str(e)}")

@app.post("/cart/remove")
def remove_from_cart(inp: CartAddIn, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    try:
        cart_repo = PostgreSQLCartRepository(db)
        cart_repo.remove_item(uid, inp.product_id, inp.qty)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, str(e))

# ---------- Commandes ----------
@app.post("/orders/checkout", response_model=OrderOut)
def checkout(uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    try:
        cart_repo = PostgreSQLCartRepository(db)
        order_repo = PostgreSQLOrderRepository(db)
        product_repo = PostgreSQLProductRepository(db)
        
        # Récupérer le panier
        cart = cart_repo.get_by_user_id(uid)
        if not cart or not cart.items:
            raise HTTPException(400, "Panier vide")
        
        # Calculer le total et vérifier le stock
        total_cents = 0
        order_items = []
        
        for item in cart.items:
            product = product_repo.get_by_id(str(item.product_id))
            if not product:
                raise HTTPException(400, f"Produit {item.product_id} introuvable")
            
            if product.stock_qty < item.quantity:
                raise HTTPException(400, f"Stock insuffisant pour {product.name}")
            
            line_total = product.price_cents * item.quantity
            total_cents += line_total
            
            order_items.append({
                "product_id": str(item.product_id),
                "name": product.name,
                "unit_price_cents": product.price_cents,
                "quantity": item.quantity
            })
        
        # Créer la commande
        order_data = {
            "user_id": uid,
            "status": "CREE",
            "items": order_items
        }
        
        order = order_repo.create(order_data)
        
        # Vider le panier
        cart_repo.clear(uid)
        
        # Réserver le stock
        for item in cart.items:
            product_repo.reserve_stock(str(item.product_id), item.quantity)
        
        return OrderOut(
            id=str(order.id),
            user_id=str(order.user_id),
            items=order_items,
            status=order.status,
            total_cents=total_cents,
            created_at=order.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Erreur lors de la commande: {str(e)}")

@app.get("/orders", response_model=list[OrderOut])
def my_orders(uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    order_repo = PostgreSQLOrderRepository(db)
    orders = order_repo.get_by_user_id(uid)
    
    result = []
    for order in orders:
        # Charger les articles de la commande
        items = []
        for item in order.items:
            items.append({
                "product_id": str(item.product_id),
                "name": item.name,
                "unit_price_cents": item.unit_price_cents,
                "quantity": item.quantity
            })
        
        # Calculer le total
        total_cents = sum(item.unit_price_cents * item.quantity for item in order.items)
        
        result.append(OrderOut(
            id=str(order.id),
            user_id=str(order.user_id),
            items=items,
            status=order.status,
            total_cents=total_cents,
            created_at=order.created_at
        ))
    
    return result

# ---------- Admin ----------
@app.get("/admin/products", response_model=list[ProductOut])
def admin_list_products(u = Depends(require_admin), db: Session = Depends(get_db)):
    product_repo = PostgreSQLProductRepository(db)
    products = product_repo.get_all()
    return [ProductOut(
        id=str(p.id),
        name=p.name,
        description=p.description,
        price_cents=p.price_cents,
        stock_qty=p.stock_qty,
        active=p.active
    ) for p in products]

@app.get("/admin/orders", response_model=list[OrderOut])
def admin_list_orders(u = Depends(require_admin), db: Session = Depends(get_db)):
    order_repo = PostgreSQLOrderRepository(db)
    orders = order_repo.get_all()
    
    result = []
    for order in orders:
        # Charger les articles de la commande
        items = []
        for item in order.items:
            items.append({
                "product_id": str(item.product_id),
                "name": item.name,
                "unit_price_cents": item.unit_price_cents,
                "quantity": item.quantity
            })
        
        # Calculer le total
        total_cents = sum(item.unit_price_cents * item.quantity for item in order.items)
        
        result.append(OrderOut(
            id=str(order.id),
            user_id=str(order.user_id),
            items=items,
            status=order.status,
            total_cents=total_cents,
            created_at=order.created_at
        ))
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
