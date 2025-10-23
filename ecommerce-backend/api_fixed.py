# api_fixed.py
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
from database.database import get_db, SessionLocal, create_tables
from sqlalchemy.orm import Session
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

app = FastAPI(title="Ecommerce API (TP)")

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

# SessionManager simple
class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id: str) -> str:
        import time
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
        # Créer des utilisateurs d'exemple
        admin_data = {
            "email": "admin@example.com",
            "password_hash": "hashed_admin_password",  # En production, utiliser bcrypt
            "first_name": "Admin",
            "last_name": "Root",
            "address": "1 Rue du BO",
            "is_admin": True
        }
        user_data = {
            "email": "client@example.com", 
            "password_hash": "hashed_client_password",  # En production, utiliser bcrypt
            "first_name": "Alice",
            "last_name": "Martin",
            "address": "12 Rue des Fleurs",
            "is_admin": False
        }
        user_repo.create(admin_data)
        user_repo.create(user_data)

# ------------------------------- Helpers --------------------------------
def validate_token_format(token: str) -> bool:
    """Valider le format du token JWT"""
    import re
    # JWT format: header.payload.signature (3 parties séparées par des points)
    jwt_pattern = r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$'
    return bool(re.match(jwt_pattern, token))

def current_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Token manquant (Authorization: Bearer <token>)")
    
    token = authorization.split(" ", 1)[1].strip()
    
    # Valider le format du token
    if not validate_token_format(token):
        raise HTTPException(401, "Format de token invalide")
    
    uid = sessions.get_user_id(token)
    if not uid:
        raise HTTPException(401, "Session invalide ou expirée")
    return uid

# Renvoie l'objet utilisateur courant
def current_user(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    uid = current_user_id(authorization)
    user_repo = PostgreSQLUserRepository(db)
    u = user_repo.get_by_id(uid)
    if not u:
        raise HTTPException(401, "Session invalide (user)")
    return u

# Vérifie que l'utilisateur est admin
def require_admin(u = Depends(current_user)):
    if not u.is_admin:
        raise HTTPException(403, "Accès réservé aux administrateurs")
    return u

# ------------------------------- PDF Generation --------------------------------
def generate_invoice_pdf(invoice_data, order_data, user_data, payment_data=None, delivery_data=None):
    """Génère un PDF de facture"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1f2937')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#374151')
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Contenu du PDF
    story = []
    
    # En-tête
    story.append(Paragraph("FACTURE", title_style))
    story.append(Spacer(1, 20))
    
    # Informations de la facture
    invoice_date = datetime.fromtimestamp(invoice_data['issued_at']).strftime("%d/%m/%Y %H:%M")
    story.append(Paragraph(f"<b>Numéro de facture:</b> {invoice_data['number']}", normal_style))
    story.append(Paragraph(f"<b>Date d'émission:</b> {invoice_date}", normal_style))
    story.append(Paragraph(f"<b>Commande:</b> #{order_data['id'][:8]}", normal_style))
    story.append(Spacer(1, 20))
    
    # Informations client
    story.append(Paragraph("FACTURÉ À:", heading_style))
    story.append(Paragraph(f"{user_data['first_name']} {user_data['last_name']}", normal_style))
    story.append(Paragraph(user_data['address'], normal_style))
    story.append(Spacer(1, 20))
    
    # Tableau des articles
    story.append(Paragraph("DÉTAIL DES ARTICLES", heading_style))
    
    # En-tête du tableau
    table_data = [['ID Produit', 'Nom', 'Prix unitaire', 'Quantité', 'Total']]
    
    # Lignes des articles
    total_cents = 0
    for line in invoice_data['lines']:
        unit_price = line['unit_price_cents'] / 100
        quantity = line['quantity']
        line_total = (line['unit_price_cents'] * quantity) / 100
        total_cents += line['unit_price_cents'] * quantity
        
        table_data.append([
            line['product_id'][:8],
            line['name'],
            f"{unit_price:.2f} €",
            str(quantity),
            f"{line_total:.2f} €"
        ])
    
    # Créer le tableau
    table = Table(table_data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 0.8*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Total
    total_euros = total_cents / 100
    story.append(Paragraph(f"<b>TOTAL: {total_euros:.2f} €</b>", ParagraphStyle(
        'TotalStyle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#1f2937')
    )))
    story.append(Spacer(1, 30))
    
    # Informations de paiement
    if payment_data:
        story.append(Paragraph("INFORMATIONS DE PAIEMENT", heading_style))
        story.append(Paragraph(f"<b>Montant payé:</b> {payment_data['amount_cents'] / 100:.2f} €", normal_style))
        story.append(Paragraph(f"<b>Statut:</b> {'PAYÉ' if payment_data['status'] == 'PAID' else 'ÉCHEC'}", normal_style))
        story.append(Paragraph(f"<b>Date de paiement:</b> {datetime.fromtimestamp(payment_data['created_at']).strftime('%d/%m/%Y %H:%M')}", normal_style))
        story.append(Spacer(1, 20))
    
    # Informations de livraison
    if delivery_data:
        story.append(Paragraph("INFORMATIONS DE LIVRAISON", heading_style))
        story.append(Paragraph(f"<b>Transporteur:</b> {delivery_data['transporteur']}", normal_style))
        if delivery_data.get('tracking_number'):
            story.append(Paragraph(f"<b>Numéro de suivi:</b> {delivery_data['tracking_number']}", normal_style))
        story.append(Paragraph(f"<b>Statut:</b> {delivery_data['delivery_status']}", normal_style))
        story.append(Spacer(1, 20))
    
    # Pied de page
    story.append(Spacer(1, 30))
    story.append(Paragraph("Merci pour votre achat !", ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#6b7280')
    )))
    
    # Construire le PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

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

# ---- Schéma pour mise à jour du profil ----
class UserUpdateIn(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None

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

class CartRemoveIn(BaseModel):
    product_id: str
    qty: int = Field(default=1, ge=0)

class CheckoutOut(BaseModel):
    order_id: str
    total_cents: int
    status: str

class PayIn(BaseModel):
    card_number: str
    exp_month: int
    exp_year: int
    cvc: str

class PaymentIn(BaseModel):
    order_id: str
    card_last4: str
    idempotency_key: str

class OrderItemOut(BaseModel):
    product_id: str
    name: str
    unit_price_cents: int
    quantity: int

class InvoiceLineOut(BaseModel):
    product_id: str
    name: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int

# ---- Schémas pour le suivi de livraison ----
class DeliveryOut(BaseModel):
    transporteur: str
    tracking_number: Optional[str]
    delivery_status: str

class DeliveryIn(BaseModel):
    transporteur: str
    tracking_number: Optional[str] = None
    delivery_status: str

class OrderOut(BaseModel):
    id: str
    user_id: str
    items: List[OrderItemOut]
    status: str
    total_cents: int
    delivery: Optional[DeliveryOut] = None

# ---- Schemas Admin (CRUD produits + remboursement) ----
class ProductCreateIn(BaseModel):
    name: str
    description: Optional[str] = ""
    price_cents: int = Field(ge=0)
    stock_qty: int = Field(ge=0)
    active: bool = True

class ProductUpdateIn(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price_cents: Optional[int] = Field(default=None, ge=0)
    stock_qty: Optional[int] = Field(default=None, ge=0)
    active: Optional[bool] = None

class RefundIn(BaseModel):
    amount_cents: Optional[int] = Field(default=None, ge=0)

class PaymentOut(BaseModel):
    id: str
    order_id: str
    amount_cents: int
    status: str
    created_at: float

class InvoiceOut(BaseModel):
    id: str
    order_id: str
    number: str
    lines: List[InvoiceLineOut]
    total_cents: int
    issued_at: float

# ---- Schémas pour le support client ----
class ThreadCreateIn(BaseModel):
    subject: str
    order_id: Optional[str] = None

class ThreadOut(BaseModel):
    id: str
    user_id: str
    order_id: Optional[str]
    subject: str
    closed: bool
    created_at: float
    unread_count: int = 0

class MessageCreateIn(BaseModel):
    content: str

class MessageOut(BaseModel):
    id: str
    thread_id: str
    author_user_id: Optional[str]
    content: str
    created_at: float
    author_name: Optional[str] = None

class ThreadDetailOut(BaseModel):
    id: str
    user_id: str
    order_id: Optional[str]
    subject: str
    closed: bool
    created_at: float
    unread_count: int = 0
    messages: List[MessageOut]

# ------------------------------- Routes --------------------------------

# Santé / test
@app.get("/")
def root():
    return {"message": "Ecommerce API is running!", "version": "1.0"}

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
        auth_service = AuthService(user_repo)
        u = auth_service.register(inp.email, inp.password, inp.first_name, inp.last_name, inp.address)
        return UserOut(
            id=str(u.id),
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            address=u.address,
            is_admin=u.is_admin
        )
    except ValueError as e:
        error_message = str(e)
        if "Email déjà utilisé" in error_message:
            raise HTTPException(400, "Cette adresse email est déjà utilisée")
        elif "Mot de passe" in error_message:
            raise HTTPException(400, "Mot de passe invalide")
        else:
            raise HTTPException(400, "Erreur lors de l'inscription")

@app.post("/auth/login", response_model=TokenOut)
def login(inp: LoginIn, db: Session = Depends(get_db)):
    try:
        user_repo = PostgreSQLUserRepository(db)
        auth_service = AuthService(user_repo)
        token = auth_service.login(inp.email, inp.password)
        return TokenOut(token=token)
    except ValueError as e:
        raise HTTPException(401, "Identifiants invalides")

@app.post("/auth/logout")
def logout(uid: str = Depends(current_user_id), authorization: Optional[str] = Header(default=None)):
    token = authorization.split(" ", 1)[1].strip()
    sessions.logout(token)
    return {"ok": True}

# Voir son profil
@app.get("/auth/me", response_model=UserOut)
def me(u = Depends(current_user)):
    return UserOut(
        id=str(u.id),
        email=u.email,
        first_name=u.first_name,
        last_name=u.last_name,
        address=u.address,
        is_admin=u.is_admin
    )

# ---- Mettre à jour son profil ----
@app.put("/auth/profile", response_model=UserOut)
def update_profile(inp: UserUpdateIn, u = Depends(current_user), db: Session = Depends(get_db)):
    if inp.first_name is not None:
        u.first_name = inp.first_name
    if inp.last_name is not None:
        u.last_name = inp.last_name
    if inp.address is not None:
        u.address = inp.address

    user_repo = PostgreSQLUserRepository(db)
    user_repo.update(u)

    return UserOut(
        id=str(u.id),
        email=u.email,
        first_name=u.first_name,
        last_name=u.last_name,
        address=u.address,
        is_admin=u.is_admin
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
    c = cart_repo.get_by_user_id(uid)
    if not c:
        return CartOut(user_id=uid, items={})
    
    items = {}
    for item in c.items:
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
        
        # Vérifier que le produit existe
        product = product_repo.get_by_id(inp.product_id)
        if not product:
            raise HTTPException(404, "Produit introuvable")
        
        if not product.active:
            raise HTTPException(400, "Produit non disponible")
        
        if product.stock_qty < inp.qty:
            raise HTTPException(400, "Stock insuffisant")
        
        cart_repo.add_item(uid, inp.product_id, inp.qty)
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Erreur lors de l'ajout au panier: {str(e)}")

@app.post("/cart/remove")
def remove_from_cart(inp: CartRemoveIn, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    try:
        cart_repo = PostgreSQLCartRepository(db)
        cart_repo.remove_item(uid, inp.product_id, inp.qty or 0)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(400, str(e))

# ---------- Commandes (client) ----------
@app.post("/orders/checkout", response_model=CheckoutOut)
def checkout(uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    try:
        order_repo = PostgreSQLOrderRepository(db)
        cart_repo = PostgreSQLCartRepository(db)
        
        # Récupérer le panier
        cart = cart_repo.get_by_user_id(uid)
        if not cart or not cart.items:
            raise HTTPException(400, "Panier vide")
        
        # Créer la commande
        order_data = {
            "user_id": uid,
            "status": OrderStatus.CREE
        }
        order = order_repo.create(order_data)
        
        # Ajouter les articles
        total_cents = 0
        for item in cart.items:
            order_item_data = {
                "order_id": str(order.id),
                "product_id": str(item.product_id),
                "name": item.product.name,
                "unit_price_cents": item.product.price_cents,
                "quantity": item.quantity
            }
            order_repo.add_item(order_item_data)
            total_cents += item.product.price_cents * item.quantity
        
        # Vider le panier
        cart_repo.clear_cart(uid)
        
        return CheckoutOut(
            order_id=str(order.id),
            total_cents=total_cents,
            status=order.status
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/orders", response_model=list[OrderOut])
def my_orders(uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    order_repo = PostgreSQLOrderRepository(db)
    orders = order_repo.get_by_user_id(uid)
    
    out = []
    for order in orders:
        delivery_info = None
        if order.delivery:
            delivery_info = DeliveryOut(
                transporteur=order.delivery.transporteur,
                tracking_number=order.delivery.tracking_number,
                delivery_status=order.delivery.delivery_status
            )
        
        out.append(OrderOut(
            id=str(order.id),
            user_id=str(order.user_id),
            items=[OrderItemOut(
                product_id=str(item.product_id),
                name=item.name,
                unit_price_cents=item.unit_price_cents,
                quantity=item.quantity
            ) for item in order.items],
            status=order.status,
            total_cents=sum(item.unit_price_cents * item.quantity for item in order.items),
            delivery=delivery_info
        ))
    return out

@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: str, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    order_repo = PostgreSQLOrderRepository(db)
    order = order_repo.get_by_id(order_id)
    
    if not order or str(order.user_id) != uid:
        raise HTTPException(404, "Commande introuvable")
    
    delivery_info = None
    if order.delivery:
        delivery_info = DeliveryOut(
            transporteur=order.delivery.transporteur,
            tracking_number=order.delivery.tracking_number,
            delivery_status=order.delivery.delivery_status
        )
    
    return OrderOut(
        id=str(order.id),
        user_id=str(order.user_id),
        items=[OrderItemOut(
            product_id=str(item.product_id),
            name=item.name,
            unit_price_cents=item.unit_price_cents,
            quantity=item.quantity
        ) for item in order.items],
        status=order.status,
        total_cents=sum(item.unit_price_cents * item.quantity for item in order.items),
        delivery=delivery_info
    )

# ====================== ADMIN: Produits ======================
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

@app.post("/admin/products", response_model=ProductOut, status_code=201)
def admin_create_product(inp: ProductCreateIn, u = Depends(require_admin), db: Session = Depends(get_db)):
    product_repo = PostgreSQLProductRepository(db)
    product_data = {
        "name": inp.name,
        "description": inp.description or "",
        "price_cents": inp.price_cents,
        "stock_qty": inp.stock_qty,
        "active": inp.active
    }
    product = product_repo.create(product_data)
    return ProductOut(
        id=str(product.id),
        name=product.name,
        description=product.description,
        price_cents=product.price_cents,
        stock_qty=product.stock_qty,
        active=product.active
    )

@app.put("/admin/products/{product_id}", response_model=ProductOut)
def admin_update_product(product_id: str, inp: ProductUpdateIn, u = Depends(require_admin), db: Session = Depends(get_db)):
    product_repo = PostgreSQLProductRepository(db)
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Produit introuvable")
    
    if inp.name is not None:
        product.name = inp.name
    if inp.description is not None:
        product.description = inp.description
    if inp.price_cents is not None:
        product.price_cents = inp.price_cents
    if inp.stock_qty is not None:
        product.stock_qty = inp.stock_qty
    if inp.active is not None:
        product.active = inp.active
    
    product_repo.update(product)
    return ProductOut(
        id=str(product.id),
        name=product.name,
        description=product.description,
        price_cents=product.price_cents,
        stock_qty=product.stock_qty,
        active=product.active
    )

@app.delete("/admin/products/{product_id}")
def admin_delete_product(product_id: str, u = Depends(require_admin), db: Session = Depends(get_db)):
    product_repo = PostgreSQLProductRepository(db)
    product = product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(404, "Produit introuvable")
    
    product.active = False
    product_repo.update(product)
    return {"ok": True}

# ====================== ADMIN: Commandes ======================
@app.get("/admin/orders", response_model=list[OrderOut])
def admin_list_orders(user_id: Optional[str] = None, u = Depends(require_admin), db: Session = Depends(get_db)):
    order_repo = PostgreSQLOrderRepository(db)
    
    if user_id:
        orders = order_repo.get_by_user_id(user_id)
    else:
        orders = order_repo.get_all()
    
    out = []
    for order in orders:
        delivery_info = None
        if order.delivery:
            delivery_info = DeliveryOut(
                transporteur=order.delivery.transporteur,
                tracking_number=order.delivery.tracking_number,
                delivery_status=order.delivery.delivery_status
            )
        
        out.append(OrderOut(
            id=str(order.id),
            user_id=str(order.user_id),
            items=[OrderItemOut(
                product_id=str(item.product_id),
                name=item.name,
                unit_price_cents=item.unit_price_cents,
                quantity=item.quantity
            ) for item in order.items],
            status=order.status,
            total_cents=sum(item.unit_price_cents * item.quantity for item in order.items),
            delivery=delivery_info
        ))
    return out

@app.get("/admin/orders/{order_id}", response_model=OrderOut)
def admin_get_order(order_id: str, u = Depends(require_admin), db: Session = Depends(get_db)):
    order_repo = PostgreSQLOrderRepository(db)
    order = order_repo.get_by_id(order_id)
    if not order:
        raise HTTPException(404, "Commande introuvable")
    
    delivery_info = None
    if order.delivery:
        delivery_info = DeliveryOut(
            transporteur=order.delivery.transporteur,
            tracking_number=order.delivery.tracking_number,
            delivery_status=order.delivery.delivery_status
        )
    
    return OrderOut(
        id=str(order.id),
        user_id=str(order.user_id),
        items=[OrderItemOut(
            product_id=str(item.product_id),
            name=item.name,
            unit_price_cents=item.unit_price_cents,
            quantity=item.quantity
        ) for item in order.items],
        status=order.status,
        total_cents=sum(item.unit_price_cents * item.quantity for item in order.items),
        delivery=delivery_info
    )

@app.post("/admin/orders/{order_id}/validate", response_model=OrderOut)
def admin_validate_order(order_id: str, u = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        order_repo = PostgreSQLOrderRepository(db)
        order = order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(404, "Commande introuvable")
        
        if order.status != OrderStatus.CREE:
            raise HTTPException(400, "Commande déjà traitée")
        
        order.status = OrderStatus.VALIDEE
        order_repo.update(order)
        
        delivery_info = None
        if order.delivery:
            delivery_info = DeliveryOut(
                transporteur=order.delivery.transporteur,
                tracking_number=order.delivery.tracking_number,
                delivery_status=order.delivery.delivery_status
            )
        
        return OrderOut(
            id=str(order.id),
            user_id=str(order.user_id),
            items=[OrderItemOut(
                product_id=str(item.product_id),
                name=item.name,
                unit_price_cents=item.unit_price_cents,
                quantity=item.quantity
            ) for item in order.items],
            status=order.status,
            total_cents=sum(item.unit_price_cents * item.quantity for item in order.items),
            delivery=delivery_info
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage de l'API e-commerce...")
    print("📡 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
