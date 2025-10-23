#!/usr/bin/env python3
"""
API Ecommerce avec PostgreSQL (connexion directe psycopg2)
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid
import time
from datetime import datetime
import psycopg2
import os

app = FastAPI(title="Ecommerce API (PostgreSQL Direct)")

# -------------------------------- CORS --------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:5173", "http://localhost:5174", "http://localhost:3000",
    "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://127.0.0.1:3000",
    "http://localhost:5178", "http://localhost:5181", "http://127.0.0.1:5181",
    "http://localhost:5182", "http://127.0.0.1:5182", "http://localhost:5183", "http://127.0.0.1:5183",
]

if os.getenv("PRODUCTION_ORIGINS"):
    ALLOWED_ORIGINS.extend(os.getenv("PRODUCTION_ORIGINS").split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)

# --------------------------- Configuration base de données ---------------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce:ecommerce123@127.0.0.1:5432/ecommerce")

def get_db_connection():
    """Obtient une connexion à la base de données"""
    return psycopg2.connect(DATABASE_URL)

def init_database():
    """Initialise la base de données et les tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Créer les tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                address TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price_cents INTEGER NOT NULL,
                stock_qty INTEGER NOT NULL DEFAULT 0,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carts (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart_items (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                cart_id UUID NOT NULL REFERENCES carts(id),
                product_id UUID NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id),
                status VARCHAR(50) NOT NULL DEFAULT 'CREE',
                total_cents INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                order_id UUID NOT NULL REFERENCES orders(id),
                product_id UUID NOT NULL REFERENCES products(id),
                name VARCHAR(255) NOT NULL,
                unit_price_cents INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Initialiser les données d'exemple
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO users (email, password_hash, first_name, last_name, address, is_admin)
                VALUES 
                    ('admin@example.com', 'admin', 'Admin', 'Root', '1 Rue du BO', TRUE),
                    ('client@example.com', 'secret', 'Alice', 'Martin', '12 Rue des Fleurs', FALSE)
            """)
        
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO products (name, description, price_cents, stock_qty, active)
                VALUES 
                    ('T-Shirt Logo', 'Coton bio', 1999, 100, TRUE),
                    ('Sweat Capuche', 'Molleton', 4999, 50, TRUE)
            """)
        
        conn.commit()
        print("✅ Base de données initialisée avec succès")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de l'initialisation: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

# Initialiser la base de données au démarrage
init_database()

# --------------------------- Session Manager ---------------------------
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

def current_user(authorization: Optional[str] = Header(default=None)):
    uid = current_user_id(authorization)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, email, first_name, last_name, address, is_admin FROM users WHERE id = %s", (uid,))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(401, "Session invalide (user)")
        
        return {
            "id": str(user_data[0]),
            "email": user_data[1],
            "first_name": user_data[2],
            "last_name": user_data[3],
            "address": user_data[4],
            "is_admin": user_data[5]
        }
    finally:
        cursor.close()
        conn.close()

def require_admin(user = Depends(current_user)):
    if not user["is_admin"]:
        raise HTTPException(403, "Accès réservé aux administrateurs")
    return user

# ------------------------------- Routes --------------------------------

@app.get("/")
def root():
    return {"message": "Ecommerce API (PostgreSQL Direct) is running!", "version": "1.0"}

@app.post("/init-data")
def initialize_data():
    """Réinitialise les données d'exemple"""
    try:
        init_database()
        return {"message": "Données d'exemple initialisées avec succès"}
    except Exception as e:
        raise HTTPException(500, f"Erreur lors de l'initialisation: {str(e)}")

# ---------- Authentification ----------
@app.post("/auth/register", response_model=UserOut)
def register(inp: RegisterIn):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Vérifier si l'email existe déjà
        cursor.execute("SELECT id FROM users WHERE email = %s", (inp.email,))
        if cursor.fetchone():
            raise HTTPException(400, "Cette adresse email est déjà utilisée")
        
        # Créer l'utilisateur
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, address, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, email, first_name, last_name, address, is_admin
        """, (inp.email, inp.password, inp.first_name, inp.last_name, inp.address, False))
        
        user_data = cursor.fetchone()
        conn.commit()
        
        return UserOut(
            id=str(user_data[0]),
            email=user_data[1],
            first_name=user_data[2],
            last_name=user_data[3],
            address=user_data[4],
            is_admin=user_data[5]
        )
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, f"Erreur lors de l'inscription: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.post("/auth/login", response_model=TokenOut)
def login(inp: LoginIn):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s AND password_hash = %s", (inp.email, inp.password))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(401, "Identifiants invalides")
        
        token = sessions.create_session(str(user_data[0]))
        return TokenOut(token=token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(401, "Identifiants invalides")
    finally:
        cursor.close()
        conn.close()

@app.post("/auth/logout")
def logout(uid: str = Depends(current_user_id), authorization: Optional[str] = Header(default=None)):
    token = authorization.split(" ", 1)[1].strip()
    sessions.logout(token)
    return {"ok": True}

@app.get("/auth/me", response_model=UserOut)
def me(user = Depends(current_user)):
    return UserOut(**user)

# ---------- Produits (public) ----------
@app.get("/products", response_model=list[ProductOut])
def list_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, name, description, price_cents, stock_qty, active FROM products WHERE active = TRUE")
        products = cursor.fetchall()
        
        return [ProductOut(
            id=str(p[0]),
            name=p[1],
            description=p[2] or "",
            price_cents=p[3],
            stock_qty=p[4],
            active=p[5]
        ) for p in products]
    finally:
        cursor.close()
        conn.close()

# ---------- Panier ----------
@app.get("/cart", response_model=CartOut)
def view_cart(uid: str = Depends(current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Récupérer ou créer le panier
        cursor.execute("SELECT id FROM carts WHERE user_id = %s", (uid,))
        cart_data = cursor.fetchone()
        
        if not cart_data:
            cursor.execute("INSERT INTO carts (user_id) VALUES (%s) RETURNING id", (uid,))
            cart_id = cursor.fetchone()[0]
            conn.commit()
        else:
            cart_id = cart_data[0]
        
        # Récupérer les articles du panier
        cursor.execute("""
            SELECT product_id, quantity FROM cart_items 
            WHERE cart_id = %s
        """, (cart_id,))
        
        items = {}
        for item in cursor.fetchall():
            items[str(item[0])] = CartItemOut(
                product_id=str(item[0]),
                quantity=item[1]
            )
        
        return CartOut(user_id=uid, items=items)
    finally:
        cursor.close()
        conn.close()

@app.post("/cart/add")
def add_to_cart(inp: CartAddIn, uid: str = Depends(current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Vérifier que le produit existe et est actif
        cursor.execute("SELECT id, stock_qty FROM products WHERE id = %s AND active = TRUE", (inp.product_id,))
        product_data = cursor.fetchone()
        
        if not product_data:
            raise HTTPException(404, "Produit introuvable")
        
        if product_data[1] < inp.qty:
            raise HTTPException(400, "Stock insuffisant")
        
        # Récupérer ou créer le panier
        cursor.execute("SELECT id FROM carts WHERE user_id = %s", (uid,))
        cart_data = cursor.fetchone()
        
        if not cart_data:
            cursor.execute("INSERT INTO carts (user_id) VALUES (%s) RETURNING id", (uid,))
            cart_id = cursor.fetchone()[0]
        else:
            cart_id = cart_data[0]
        
        # Vérifier si l'article existe déjà dans le panier
        cursor.execute("SELECT id, quantity FROM cart_items WHERE cart_id = %s AND product_id = %s", (cart_id, inp.product_id))
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Mettre à jour la quantité
            new_quantity = existing_item[1] + inp.qty
            cursor.execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (new_quantity, existing_item[0]))
        else:
            # Ajouter un nouvel article
            cursor.execute("""
                INSERT INTO cart_items (cart_id, product_id, quantity)
                VALUES (%s, %s, %s)
            """, (cart_id, inp.product_id, inp.qty))
        
        conn.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, f"Erreur lors de l'ajout au panier: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.post("/cart/remove")
def remove_from_cart(inp: CartAddIn, uid: str = Depends(current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Récupérer le panier
        cursor.execute("SELECT id FROM carts WHERE user_id = %s", (uid,))
        cart_data = cursor.fetchone()
        
        if not cart_data:
            raise HTTPException(404, "Panier introuvable")
        
        cart_id = cart_data[0]
        
        # Récupérer l'article du panier
        cursor.execute("SELECT id, quantity FROM cart_items WHERE cart_id = %s AND product_id = %s", (cart_id, inp.product_id))
        item_data = cursor.fetchone()
        
        if not item_data:
            raise HTTPException(404, "Article introuvable dans le panier")
        
        new_quantity = item_data[1] - inp.qty
        if new_quantity <= 0:
            # Supprimer l'article
            cursor.execute("DELETE FROM cart_items WHERE id = %s", (item_data[0],))
        else:
            # Mettre à jour la quantité
            cursor.execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (new_quantity, item_data[0]))
        
        conn.commit()
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, str(e))
    finally:
        cursor.close()
        conn.close()

# ---------- Commandes ----------
@app.post("/orders/checkout", response_model=OrderOut)
def checkout(uid: str = Depends(current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Récupérer le panier
        cursor.execute("SELECT id FROM carts WHERE user_id = %s", (uid,))
        cart_data = cursor.fetchone()
        
        if not cart_data:
            raise HTTPException(400, "Panier vide")
        
        cart_id = cart_data[0]
        
        # Récupérer les articles du panier
        cursor.execute("""
            SELECT ci.product_id, ci.quantity, p.name, p.price_cents, p.stock_qty
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            WHERE ci.cart_id = %s
        """, (cart_id,))
        
        cart_items = cursor.fetchall()
        
        if not cart_items:
            raise HTTPException(400, "Panier vide")
        
        # Calculer le total et vérifier le stock
        total_cents = 0
        order_items = []
        
        for item in cart_items:
            product_id, quantity, name, price_cents, stock_qty = item
            
            if stock_qty < quantity:
                raise HTTPException(400, f"Stock insuffisant pour {name}")
            
            line_total = price_cents * quantity
            total_cents += line_total
            
            order_items.append({
                "product_id": str(product_id),
                "name": name,
                "unit_price_cents": price_cents,
                "quantity": quantity
            })
        
        # Créer la commande
        cursor.execute("""
            INSERT INTO orders (user_id, status, total_cents)
            VALUES (%s, %s, %s)
            RETURNING id, created_at
        """, (uid, "CREE", total_cents))
        
        order_data = cursor.fetchone()
        order_id = order_data[0]
        created_at = order_data[1]
        
        # Créer les articles de commande
        for item in order_items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, name, unit_price_cents, quantity)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item["product_id"], item["name"], item["unit_price_cents"], item["quantity"]))
            
            # Réserver le stock
            cursor.execute("""
                UPDATE products SET stock_qty = stock_qty - %s WHERE id = %s
            """, (item["quantity"], item["product_id"]))
        
        # Vider le panier
        cursor.execute("DELETE FROM cart_items WHERE cart_id = %s", (cart_id,))
        
        conn.commit()
        
        return OrderOut(
            id=str(order_id),
            user_id=uid,
            items=order_items,
            status="CREE",
            total_cents=total_cents,
            created_at=created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(400, f"Erreur lors de la commande: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/orders", response_model=list[OrderOut])
def my_orders(uid: str = Depends(current_user_id)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, user_id, status, total_cents, created_at
            FROM orders WHERE user_id = %s
            ORDER BY created_at DESC
        """, (uid,))
        
        orders = cursor.fetchall()
        result = []
        
        for order in orders:
            order_id, user_id, status, total_cents, created_at = order
            
            # Récupérer les articles de la commande
            cursor.execute("""
                SELECT product_id, name, unit_price_cents, quantity
                FROM order_items WHERE order_id = %s
            """, (order_id,))
            
            items = []
            for item in cursor.fetchall():
                items.append({
                    "product_id": str(item[0]),
                    "name": item[1],
                    "unit_price_cents": item[2],
                    "quantity": item[3]
                })
            
            result.append(OrderOut(
                id=str(order_id),
                user_id=str(user_id),
                items=items,
                status=status,
                total_cents=total_cents,
                created_at=created_at
            ))
        
        return result
    finally:
        cursor.close()
        conn.close()

# ---------- Admin ----------
@app.get("/admin/products", response_model=list[ProductOut])
def admin_list_products(u = Depends(require_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, name, description, price_cents, stock_qty, active FROM products")
        products = cursor.fetchall()
        
        return [ProductOut(
            id=str(p[0]),
            name=p[1],
            description=p[2] or "",
            price_cents=p[3],
            stock_qty=p[4],
            active=p[5]
        ) for p in products]
    finally:
        cursor.close()
        conn.close()

@app.get("/admin/orders", response_model=list[OrderOut])
def admin_list_orders(u = Depends(require_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, user_id, status, total_cents, created_at
            FROM orders
            ORDER BY created_at DESC
        """)
        
        orders = cursor.fetchall()
        result = []
        
        for order in orders:
            order_id, user_id, status, total_cents, created_at = order
            
            # Récupérer les articles de la commande
            cursor.execute("""
                SELECT product_id, name, unit_price_cents, quantity
                FROM order_items WHERE order_id = %s
            """, (order_id,))
            
            items = []
            for item in cursor.fetchall():
                items.append({
                    "product_id": str(item[0]),
                    "name": item[1],
                    "unit_price_cents": item[2],
                    "quantity": item[3]
                })
            
            result.append(OrderOut(
                id=str(order_id),
                user_id=str(user_id),
                items=items,
                status=status,
                total_cents=total_cents,
                created_at=created_at
            ))
        
        return result
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
