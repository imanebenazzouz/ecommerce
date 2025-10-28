"""
API FastAPI (variante SQLite) pour environnement léger/local.

Objectif: fournir une implémentation autonome (fichier .db) pour tests rapides
ou démonstrations sans PostgreSQL. Non destinée à la production.
"""
# api_sqlite.py - Version SQLite pour éviter les problèmes PostgreSQL
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
import uuid
import io
import time
from datetime import datetime
import sqlite3
import json
import os

app = FastAPI(title="Ecommerce API (SQLite)")

# -------------------------------- CORS --------------------------------
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:5174",  # Vite dev server (port alternatif)
    "http://localhost:5175",  # Vite dev server (port actuel)
    "http://localhost:3000",  # React dev server alternatif
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:5175",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------- BASE DE DONNÉES SQLITE --------------------------------
DB_PATH = "ecommerce.db"

def init_db():
    """Initialise la base de données SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table des utilisateurs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            address TEXT,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des produits
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            image_url TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des commandes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Table des articles de commande
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Table des paniers
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialiser la base de données
init_db()

# -------------------------------- MODÈLES PYDANTIC --------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_admin: bool = False

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    image_url: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None
    is_active: bool = True

class CartItem(BaseModel):
    product_id: int
    quantity: int

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total: float
    status: str
    created_at: datetime

# -------------------------------- UTILITAIRES --------------------------------
def hash_password(password: str) -> str:
    """Hash simple du mot de passe (en production, utiliser bcrypt)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Vérification simple du mot de passe"""
    return hash_password(password) == hashed

def get_user_by_token(token: str) -> Optional[dict]:
    """Récupère l'utilisateur par token (simulation simple)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Simulation simple - en production, décoder le JWT
    try:
        user_id = int(token)
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'first_name': user[3],
                'last_name': user[4],
                'phone': user[5],
                'address': user[6],
                'is_admin': bool(user[7])
            }
    except:
        pass
    
    conn.close()
    return None

# -------------------------------- ENDPOINTS --------------------------------

@app.get("/")
async def root():
    return {"message": "API E-commerce SQLite", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "sqlite"}

# -------------------------------- AUTHENTIFICATION --------------------------------

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        
        # Créer l'utilisateur
        password_hash = hash_password(user.password)
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user.email, password_hash, user.first_name, user.last_name, user.phone, user.address))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        return UserResponse(
            id=user_id or 0,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            address=user.address,
            is_admin=False
        )
    finally:
        conn.close()

@app.post("/auth/login")
async def login(user: UserLogin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    db_user = cursor.fetchone()
    
    if not db_user or not verify_password(user.password, db_user[2]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    conn.close()
    
    return {
        "access_token": str(db_user[0]),  # ID utilisateur comme token simple
        "token_type": "bearer",
        "user": UserResponse(
            id=db_user[0],
            email=db_user[1],
            first_name=db_user[3],
            last_name=db_user[4],
            phone=db_user[5],
            address=db_user[6],
            is_admin=bool(db_user[7])
        )
    }

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    
    token = authorization.split(" ")[1]
    user = get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    return UserResponse(**user)

# -------------------------------- PRODUITS --------------------------------

@app.get("/products", response_model=List[ProductResponse])
async def get_products():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products WHERE is_active = 1")
    products = cursor.fetchall()
    conn.close()
    
    return [
        ProductResponse(
            id=p[0],
            name=p[1],
            description=p[2],
            price=p[3],
            stock=p[4],
            image_url=p[5],
            is_active=bool(p[6])
        ) for p in products
    ]

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    return ProductResponse(
        id=product[0],
        name=product[1],
        description=product[2],
        price=product[3],
        stock=product[4],
        image_url=product[5],
        is_active=bool(product[6])
    )

# -------------------------------- PANIER --------------------------------

@app.get("/cart")
async def get_cart(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    
    token = authorization.split(" ")[1]
    user = get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id, c.product_id, c.quantity, p.name, p.price, p.image_url
        FROM carts c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user['id'],))
    
    items = cursor.fetchall()
    conn.close()
    
    total = sum(item[4] * item[2] for item in items)
    
    return {
        "items": [
            {
                "id": item[0],
                "product_id": item[1],
                "quantity": item[2],
                "name": item[3],
                "price": item[4],
                "image_url": item[5],
                "subtotal": item[4] * item[2]
            } for item in items
        ],
        "total": total
    }

@app.post("/cart/add")
async def add_to_cart(item: CartItem, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    
    token = authorization.split(" ")[1]
    user = get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Vérifier si le produit existe
    cursor.execute("SELECT * FROM products WHERE id = ?", (item.product_id,))
    product = cursor.fetchone()
    
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    
    # Vérifier le stock
    if product[4] < item.quantity:
        raise HTTPException(status_code=400, detail="Stock insuffisant")
    
    # Vérifier si l'article est déjà dans le panier
    cursor.execute("SELECT id, quantity FROM carts WHERE user_id = ? AND product_id = ?", 
                   (user['id'], item.product_id))
    existing = cursor.fetchone()
    
    if existing:
        # Mettre à jour la quantité
        new_quantity = existing[1] + item.quantity
        cursor.execute("UPDATE carts SET quantity = ? WHERE id = ?", (new_quantity, existing[0]))
    else:
        # Ajouter un nouvel article
        cursor.execute("INSERT INTO carts (user_id, product_id, quantity) VALUES (?, ?, ?)",
                      (user['id'], item.product_id, item.quantity))
    
    conn.commit()
    conn.close()
    
    return {"message": "Article ajouté au panier"}

@app.delete("/cart/clear")
async def clear_cart(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    
    token = authorization.split(" ")[1]
    user = get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM carts WHERE user_id = ?", (user['id'],))
    conn.commit()
    conn.close()
    
    return {"message": "Panier vidé"}

# -------------------------------- COMMANDES --------------------------------

@app.post("/orders/checkout")
async def checkout(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    
    token = authorization.split(" ")[1]
    user = get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Récupérer le panier
    cursor.execute("""
        SELECT c.product_id, c.quantity, p.price
        FROM carts c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (user['id'],))
    
    cart_items = cursor.fetchall()
    
    if not cart_items:
        raise HTTPException(status_code=400, detail="Panier vide")
    
    # Calculer le total
    total = sum(item[1] * item[2] for item in cart_items)
    
    # Créer la commande
    cursor.execute("INSERT INTO orders (user_id, total, status) VALUES (?, ?, ?)",
                  (user['id'], total, 'pending'))
    order_id = cursor.lastrowid
    
    # Ajouter les articles de commande
    for item in cart_items:
        cursor.execute("""
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
        """, (order_id, item[0], item[1], item[2]))
        
        # Mettre à jour le stock
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                      (item[1], item[0]))
    
    # Vider le panier
    cursor.execute("DELETE FROM carts WHERE user_id = ?", (user['id'],))
    
    conn.commit()
    conn.close()
    
    return {"message": "Commande créée", "order_id": order_id, "total": total}

@app.get("/orders", response_model=List[OrderResponse])
async def get_orders(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    
    token = authorization.split(" ")[1]
    user = get_user_by_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user['id'],))
    orders = cursor.fetchall()
    conn.close()
    
    return [
        OrderResponse(
            id=order[0],
            user_id=order[1],
            total=order[2],
            status=order[3],
            created_at=datetime.fromisoformat(order[4])
        ) for order in orders
    ]

# -------------------------------- DONNÉES DE TEST --------------------------------

@app.post("/admin/seed")
async def seed_data():
    """Ajouter des données de test"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Produits de test
    products = [
        ("iPhone 15", "Dernier iPhone avec caméra 48MP", 999.99, 10, "https://example.com/iphone.jpg"),
        ("Samsung Galaxy S24", "Smartphone Android haut de gamme", 899.99, 8, "https://example.com/galaxy.jpg"),
        ("MacBook Pro", "Ordinateur portable professionnel", 1999.99, 5, "https://example.com/macbook.jpg"),
        ("AirPods Pro", "Écouteurs sans fil avec réduction de bruit", 249.99, 20, "https://example.com/airpods.jpg"),
        ("iPad Air", "Tablette polyvalente", 599.99, 12, "https://example.com/ipad.jpg")
    ]
    
    for product in products:
        cursor.execute("""
            INSERT OR IGNORE INTO products (name, description, price, stock, image_url)
            VALUES (?, ?, ?, ?, ?)
        """, product)
    
    conn.commit()
    conn.close()
    
    return {"message": "Données de test ajoutées"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
