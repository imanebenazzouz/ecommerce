# api_fixed.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, cast
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
    "http://localhost:5175",  # Vite dev server (port alternatif)
    "http://localhost:5176",  # Vite dev server (port alternatif)
    "http://localhost:3000",  # React dev server alternatif
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",  # Vite dev server (port alternatif)
    "http://127.0.0.1:5175",  # Vite dev server (port alternatif)
    "http://127.0.0.1:5176",  # Vite dev server (port alternatif)
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
production_origins = os.getenv("PRODUCTION_ORIGINS")
if production_origins:
    ALLOWED_ORIGINS.extend(production_origins.split(","))

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

# Utilisation du service d'authentification JWT

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
        # Créer des utilisateurs d'exemple avec des mots de passe hashés correctement
        auth_service = AuthService(user_repo)
        
        # Créer l'admin
        admin_data = {
            "email": "admin@example.com",
            "password_hash": auth_service.hash_password("admin"),  # Hash correct du mot de passe
            "first_name": "Admin",
            "last_name": "Root",
            "address": "1 Rue du BO",
            "is_admin": True
        }
        
        # Créer le client
        user_data = {
            "email": "client@example.com", 
            "password_hash": auth_service.hash_password("secret"),  # Hash correct du mot de passe
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

def current_user_id(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Token manquant (Authorization: Bearer <token>)")
    
    token = authorization.split(" ", 1)[1].strip()
    
    # Valider le format du token
    if not validate_token_format(token):
        raise HTTPException(401, "Format de token invalide")
    
    # Utiliser le service d'authentification JWT
    user_repo = PostgreSQLUserRepository(db)
    auth_service = AuthService(user_repo)
    try:
        payload = auth_service.verify_token(token)
        if not payload or "sub" not in payload:
            raise HTTPException(401, "Token invalide ou expiré")
        return payload["sub"]
    except Exception as e:
        raise HTTPException(401, "Token invalide ou expiré")

# Renvoie l'objet utilisateur courant
def current_user(authorization: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    try:
        uid = current_user_id(authorization, db)
        user_repo = PostgreSQLUserRepository(db)
        u = user_repo.get_by_id(uid)
        if not u:
            raise HTTPException(401, "Session invalide (user)")
        return u
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(401, "Session invalide")

# Vérifie que l'utilisateur est admin
def require_admin(u: User = Depends(current_user)):
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

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "postgresql"}

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
            email=str(u.email),
            first_name=str(u.first_name),
            last_name=str(u.last_name),
            address=str(u.address),
            is_admin=bool(u.is_admin)
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
        user = auth_service.authenticate_user(inp.email, inp.password)
        if not user:
            raise HTTPException(401, "Identifiants invalides")
        
        # Créer un token JWT
        token = auth_service.create_access_token(data={"sub": str(user.id)})
        return TokenOut(token=token)
    except ValueError as e:
        raise HTTPException(401, "Identifiants invalides")

@app.post("/auth/logout")
def logout(uid: str = Depends(current_user_id)):
    # Avec JWT, pas besoin de gérer la déconnexion côté serveur
    # Le token sera simplement ignoré côté client
    return {"ok": True}

# Voir son profil
@app.get("/auth/me", response_model=UserOut)
def me(u: User = Depends(current_user)):
    return UserOut(
        id=str(u.id),
        email=str(u.email),
        first_name=str(u.first_name),
        last_name=str(u.last_name),
        address=str(u.address),
        is_admin=bool(u.is_admin)
    )

# ---- Mettre à jour son profil ----
@app.put("/auth/profile", response_model=UserOut)
def update_profile(inp: UserUpdateIn, u: User = Depends(current_user), db: Session = Depends(get_db)):
    user_repo = PostgreSQLUserRepository(db)
    
    # Mettre à jour les champs fournis
    if inp.first_name is not None:
        u.first_name = inp.first_name  # type: ignore
    if inp.last_name is not None:
        u.last_name = inp.last_name  # type: ignore
    if inp.address is not None:
        u.address = inp.address  # type: ignore
    
    # Utiliser la méthode update du repository
    updated_user = user_repo.update(u)

    return UserOut(
        id=str(updated_user.id),
        email=str(updated_user.email),
        first_name=str(updated_user.first_name),
        last_name=str(updated_user.last_name),
        address=str(updated_user.address),
        is_admin=bool(updated_user.is_admin)
    )

# ---------- Produits (public) ----------
@app.get("/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    try:
        product_repo = PostgreSQLProductRepository(db)
        products = product_repo.get_all_active()
        return [ProductOut(
            id=str(p.id),
            name=cast(str, p.name),
            description=cast(str, p.description),
            price_cents=cast(int, p.price_cents),
            stock_qty=cast(int, p.stock_qty),
            active=cast(bool, p.active)
        ) for p in products]
    except Exception as e:
        # Erreur lors du chargement des produits
        raise HTTPException(500, "Erreur lors du chargement des produits")

@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Récupère un produit spécifique par son ID"""
    try:
        product_repo = PostgreSQLProductRepository(db)
        product = product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(404, "Produit introuvable")
        
        return ProductOut(
            id=str(product.id),
            name=cast(str, product.name),
            description=cast(str, product.description),
            price_cents=cast(int, product.price_cents),
            stock_qty=cast(int, product.stock_qty),
            active=cast(bool, product.active)
        )
    except HTTPException:
        raise
    except Exception as e:
        # Erreur lors de la récupération du produit
        raise HTTPException(500, "Erreur lors de la récupération du produit")

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

@app.post("/cart/clear")
def clear_cart(uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Vide complètement le panier de l'utilisateur"""
    try:
        cart_repo = PostgreSQLCartRepository(db)
        success = cart_repo.clear_cart(uid)
        if not success:
            raise HTTPException(400, "Erreur lors du vidage du panier")
        return {"ok": True, "message": "Panier vidé avec succès"}
    except Exception as e:
        raise HTTPException(400, str(e))

# ---------- Commandes (client) ----------
@app.post("/orders/checkout", response_model=CheckoutOut)
def checkout(uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    try:
        order_repo = PostgreSQLOrderRepository(db)
        cart_repo = PostgreSQLCartRepository(db)
        product_repo = PostgreSQLProductRepository(db)
        
        # Récupérer le panier
        cart = cart_repo.get_by_user_id(uid)
        if not cart or not cart.items:
            raise HTTPException(400, "Panier vide")
        
        # Vérifier le stock et réserver les produits
        for item in cart.items:
            product = product_repo.get_by_id(str(item.product_id))
            if not product:
                raise HTTPException(400, f"Produit {item.product.name} introuvable")
            
            if not product.active:
                raise HTTPException(400, f"Produit {item.product.name} non disponible")
            
            if product.stock_qty < item.quantity:
                raise HTTPException(400, f"Stock insuffisant pour {item.product.name}")
        
        # Créer la commande
        order_data = {
            "user_id": uid,
            "status": OrderStatus.CREE
        }
        order = order_repo.create(order_data)
        
        # Ajouter les articles et mettre à jour le stock
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
            
            # Mettre à jour le stock du produit
            product = product_repo.get_by_id(str(item.product_id))
            product.stock_qty -= item.quantity
            
            # Inactiver le produit si le stock devient 0
            if product.stock_qty <= 0:
                product.active = False  # type: ignore
                # Produit inactivé automatiquement (stock épuisé)
            
            product_repo.update(product)
        
        # Vider le panier
        cart_repo.clear_cart(uid)
        
        return CheckoutOut(
            order_id=str(order.id),
            total_cents=total_cents,
            status=str(order.status)
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
            status=str(order.status),
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
        status=cast(str, order.status),
        total_cents=sum(item.unit_price_cents * item.quantity for item in order.items),
        delivery=delivery_info
    )

# ====================== ADMIN: Produits ======================
@app.get("/admin/products", response_model=list[ProductOut])
def admin_list_products(u = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        product_repo = PostgreSQLProductRepository(db)
        products = product_repo.get_all()
        return [ProductOut(
            id=str(p.id),
            name=cast(str, p.name),
            description=cast(str, p.description),
            price_cents=cast(int, p.price_cents),
            stock_qty=cast(int, p.stock_qty),
            active=cast(bool, p.active)
        ) for p in products]
    except Exception as e:
        raise HTTPException(500, f"Erreur lors du chargement des produits: {str(e)}")

@app.post("/admin/products", response_model=ProductOut, status_code=201)
def admin_create_product(inp: ProductCreateIn, u = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        # Validation des données
        if not inp.name or not inp.name.strip():
            raise HTTPException(400, "Le nom du produit est obligatoire")
        if inp.price_cents < 0:
            raise HTTPException(400, "Le prix ne peut pas être négatif")
        if inp.stock_qty < 0:
            raise HTTPException(400, "Le stock ne peut pas être négatif")
            
        product_repo = PostgreSQLProductRepository(db)
        product_data = {
            "name": inp.name.strip(),
            "description": inp.description or "",
            "price_cents": inp.price_cents,
            "stock_qty": inp.stock_qty,
            "active": inp.active
        }
        product = product_repo.create(product_data)
        return ProductOut(
            id=str(product.id),
            name=cast(str, product.name),
            description=cast(str, product.description),
            price_cents=cast(int, product.price_cents),
            stock_qty=cast(int, product.stock_qty),
            active=cast(bool, product.active)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erreur lors de la création du produit: {str(e)}")

@app.put("/admin/products/{product_id}", response_model=ProductOut)
def admin_update_product(product_id: str, inp: ProductUpdateIn, u = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        product_repo = PostgreSQLProductRepository(db)
        product = product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(404, "Produit introuvable")
        
        # Validation des données
        if inp.name is not None and (not inp.name or not inp.name.strip()):
            raise HTTPException(400, "Le nom du produit ne peut pas être vide")
        if inp.price_cents is not None and inp.price_cents < 0:
            raise HTTPException(400, "Le prix ne peut pas être négatif")
        if inp.stock_qty is not None and inp.stock_qty < 0:
            raise HTTPException(400, "Le stock ne peut pas être négatif")
        
        if inp.name is not None:
            product.name = inp.name.strip()  # type: ignore
        if inp.description is not None:
            product.description = inp.description  # type: ignore
        if inp.price_cents is not None:
            product.price_cents = inp.price_cents  # type: ignore
        if inp.stock_qty is not None:
            product.stock_qty = inp.stock_qty  # type: ignore
        if inp.active is not None:
            product.active = inp.active  # type: ignore
        
        product_repo.update(product)
        return ProductOut(
            id=str(product.id),
            name=cast(str, product.name),
            description=cast(str, product.description),
            price_cents=cast(int, product.price_cents),
            stock_qty=cast(int, product.stock_qty),
            active=cast(bool, product.active)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erreur lors de la mise à jour du produit: {str(e)}")

@app.delete("/admin/products/{product_id}")
def admin_delete_product(product_id: str, u = Depends(require_admin), db: Session = Depends(get_db)):
    try:
        product_repo = PostgreSQLProductRepository(db)
        
        # Vérifier que le produit existe avant de le supprimer
        product = product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(404, "Produit introuvable")
        
        # Supprimer complètement le produit (et ses éléments de panier associés)
        success = product_repo.delete(product_id)
        if not success:
            raise HTTPException(500, "Erreur lors de la suppression du produit")
        
        return {"ok": True, "message": "Produit supprimé définitivement"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Erreur lors de la suppression du produit: {str(e)}")

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
            status=str(order.status),
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
        status=cast(str, order.status),
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
        
        # Vérifier que la commande peut être validée
        if str(order.status) not in [OrderStatus.CREE, OrderStatus.PAYEE]:
            raise HTTPException(400, f"Commande déjà traitée (statut actuel: {order.status})")
        
        # Mettre à jour le statut et le timestamp
        order.status = OrderStatus.VALIDEE  # type: ignore
        order.validated_at = datetime.utcnow()  # type: ignore
        order_repo.update(order)
        
        # Rafraîchir l'objet pour avoir les dernières données
        db.refresh(order)
        
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
            status=str(order.status),
            total_cents=sum(item.unit_price_cents * item.quantity for item in order.items),
            delivery=delivery_info
        )
    except HTTPException:
        raise
    except Exception as e:
        # Erreur lors de la validation de la commande
        raise HTTPException(400, f"Erreur lors de la validation: {str(e)}")

# ====================== ANNULATION DE COMMANDE ======================
@app.post("/orders/{order_id}/cancel")
def cancel_order(order_id: str, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Annule une commande avec remboursement automatique si payée"""
    try:
        order_repo = PostgreSQLOrderRepository(db)
        product_repo = PostgreSQLProductRepository(db)
        payment_repo = PostgreSQLPaymentRepository(db)
        
        order = order_repo.get_by_id(order_id)
        if not order or str(order.user_id) != uid:
            raise HTTPException(404, "Commande introuvable")
        
        # Vérifier que la commande peut être annulée
        if str(order.status) not in [OrderStatus.CREE, OrderStatus.PAYEE]:
            raise HTTPException(400, "Cette commande ne peut pas être annulée")
        
        # Vérifier si la commande a été payée
        was_paid = order.status == OrderStatus.PAYEE
        refund_info = None
        
        if was_paid:
            # Récupérer les paiements pour la commande
            payments = payment_repo.get_by_order_id(order_id)
            if payments:
                # Marquer les paiements comme remboursés
                for payment in payments:
                    payment.status = "REFUNDED"  # type: ignore
                db.commit()
                
                # Calculer le montant total remboursé
                total_refunded = sum(p.amount_cents for p in payments)
                refund_info = {
                    "refunded": True,
                    "amount_cents": total_refunded,
                    "message": f"Remboursement automatique de {total_refunded/100:.2f}€ effectué"
                }
                # Remboursement automatique effectué
        
        # Remettre le stock en place pour chaque article
        for item in order.items:
            product = product_repo.get_by_id(str(item.product_id))
            if product:
                # Remettre le stock
                product.stock_qty += item.quantity
                
                # Réactiver le produit s'il était inactif à cause du stock
                if not product.active and product.stock_qty > 0:
                    product.active = True  # type: ignore
                    # Produit réactivé automatiquement (stock restauré)
                
                product_repo.update(product)
        
        # Mettre à jour le statut de la commande
        order.status = OrderStatus.ANNULEE  # type: ignore
        order.cancelled_at = datetime.utcnow()  # type: ignore
        order_repo.update(order)
        
        response = {"ok": True, "message": "Commande annulée avec succès"}
        if refund_info:
            response.update(refund_info)
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

# ====================== PAIEMENTS ======================
@app.post("/orders/{order_id}/pay")
def pay_order(order_id: str, payment_data: PayIn, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Simule un paiement pour une commande"""
    try:
        order_repo = PostgreSQLOrderRepository(db)
        payment_repo = PostgreSQLPaymentRepository(db)
        
        order = order_repo.get_by_id(order_id)
        if not order or str(order.user_id) != uid:
            raise HTTPException(404, "Commande introuvable")
        
        if str(order.status) != OrderStatus.CREE:
            raise HTTPException(400, "Commande déjà payée ou traitée")
        
        # Validation du numéro de carte
        card_number = payment_data.card_number.replace(" ", "").replace("-", "")
        
        # Vérifier que la carte ne se termine pas par 0000
        if card_number.endswith("0000"):
            raise HTTPException(402, "Paiement refusé : carte invalide")
        
        # Vérifier que la carte fait exactement 16 chiffres
        if len(card_number) != 16 or not card_number.isdigit():
            raise HTTPException(402, "Paiement refusé : numéro de carte invalide")
        
        # Calculer le montant total
        total_cents = sum(item.unit_price_cents * item.quantity for item in order.items)
        
        # Simuler le paiement (réussi si validation passée)
        payment_data_dict = {
            "order_id": order_id,
            "amount_cents": total_cents,
            "status": "SUCCEEDED",
            "payment_method": "CARD"
        }
        
        payment = payment_repo.create(payment_data_dict)
        
        # Mettre à jour le statut de la commande
        order.status = OrderStatus.PAYEE  # type: ignore
        order.payment_id = payment.id
        order_repo.update(order)
        
        return {
            "payment_id": str(payment.id),
            "status": "SUCCEEDED",
            "amount_cents": total_cents
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

# ====================== FACTURES ======================
@app.get("/orders/{order_id}/invoice", response_model=InvoiceOut)
def get_invoice(order_id: str, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Récupère la facture d'une commande"""
    try:
        order_repo = PostgreSQLOrderRepository(db)
        invoice_repo = PostgreSQLInvoiceRepository(db)
        
        order = order_repo.get_by_id(order_id)
        if not order or str(order.user_id) != uid:
            raise HTTPException(404, "Commande introuvable")
        
        # Créer la facture si elle n'existe pas
        invoice = invoice_repo.get_by_order_id(order_id)
        if not invoice:
            # Créer la facture
            total_cents = sum(item.unit_price_cents * item.quantity for item in order.items)
            invoice_data = {
                "order_id": order_id,
                "user_id": str(order.user_id),
                "total_cents": total_cents
            }
            invoice = invoice_repo.create(invoice_data)
        
        # Construire les lignes de facture
        lines = []
        for item in order.items:
            lines.append(InvoiceLineOut(
                product_id=str(item.product_id),
                name=item.name,
                unit_price_cents=item.unit_price_cents,
                quantity=item.quantity,
                line_total_cents=item.unit_price_cents * item.quantity
            ))
        
        return InvoiceOut(
            id=str(invoice.id),
            order_id=str(invoice.order_id),
            number=f"INV-{str(invoice.id)[:8].upper()}",
            lines=lines,
            total_cents=cast(int, invoice.total_cents),
            issued_at=invoice.created_at.timestamp()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/orders/{order_id}/invoice/download")
def download_invoice_pdf(order_id: str, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Télécharge la facture en PDF"""
    try:
        order_repo = PostgreSQLOrderRepository(db)
        invoice_repo = PostgreSQLInvoiceRepository(db)
        payment_repo = PostgreSQLPaymentRepository(db)
        
        order = order_repo.get_by_id(order_id)
        if not order or str(order.user_id) != uid:
            raise HTTPException(404, "Commande introuvable")
        
        # Récupérer la facture
        invoice = invoice_repo.get_by_order_id(order_id)
        if not invoice:
            raise HTTPException(404, "Facture introuvable")
        
        # Récupérer les données nécessaires
        user = order.user
        payments = payment_repo.get_by_order_id(order_id)
        
        # Construire les données de la facture
        invoice_data = {
            "id": str(invoice.id),
            "number": f"INV-{str(invoice.id)[:8].upper()}",
            "issued_at": invoice.created_at.timestamp(),
            "lines": [
                {
                    "product_id": str(item.product_id),
                    "name": item.name,
                    "unit_price_cents": item.unit_price_cents,
                    "quantity": item.quantity
                }
                for item in order.items
            ]
        }
        
        order_data = {
            "id": str(order.id),
            "user_id": str(order.user_id),
            "status": order.status
        }
        
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "address": user.address
        }
        
        payment_data = None
        if payments:
            payment = payments[0]  # Prendre le premier paiement
            payment_data = {
                "amount_cents": payment.amount_cents,
                "status": payment.status,
                "created_at": payment.created_at.timestamp()
            }
        
        delivery_data = None
        if order.delivery:
            delivery_data = {
                "transporteur": order.delivery.transporteur,
                "tracking_number": order.delivery.tracking_number,
                "delivery_status": order.delivery.delivery_status
            }
        
        # Générer le PDF
        pdf_buffer = generate_invoice_pdf(invoice_data, order_data, user_data, payment_data, delivery_data)
        
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=facture_{order_id[:8]}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

# ====================== SUIVI DE LIVRAISON ======================
@app.get("/orders/{order_id}/tracking", response_model=DeliveryOut)
def get_order_tracking(order_id: str, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Récupère le suivi de livraison d'une commande"""
    try:
        order_repo = PostgreSQLOrderRepository(db)
        
        order = order_repo.get_by_id(order_id)
        if not order or str(order.user_id) != uid:
            raise HTTPException(404, "Commande introuvable")
        
        if not order.delivery:
            raise HTTPException(404, "Informations de livraison non disponibles")
        
        return DeliveryOut(
            transporteur=order.delivery.transporteur,
            tracking_number=order.delivery.tracking_number,
            delivery_status=order.delivery.delivery_status
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

# ====================== SUPPORT CLIENT ======================
@app.post("/support/threads", response_model=ThreadOut)
def create_support_thread(thread_data: ThreadCreateIn, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Crée un nouveau fil de support"""
    try:
        thread_repo = PostgreSQLThreadRepository(db)
        
        thread_data_dict = {
            "user_id": uid,
            "order_id": thread_data.order_id,
            "subject": thread_data.subject
        }
        
        thread = thread_repo.create(thread_data_dict)
        
        return ThreadOut(
            id=str(thread.id),
            user_id=str(thread.user_id),
            order_id=str(thread.order_id) if thread.order_id is not None else None,
            subject=str(thread.subject),
            closed=bool(thread.closed),
            created_at=thread.created_at.timestamp(),
            unread_count=0
        )
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/support/threads", response_model=List[ThreadOut])
def list_support_threads(uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Liste les fils de support de l'utilisateur"""
    try:
        thread_repo = PostgreSQLThreadRepository(db)
        
        threads = thread_repo.get_by_user_id(uid)
        
        return [
            ThreadOut(
                id=str(thread.id),
                user_id=str(thread.user_id),
                order_id=str(thread.order_id) if thread.order_id is not None else None,
                subject=str(thread.subject),
                closed=bool(thread.closed),
                created_at=thread.created_at.timestamp(),
                unread_count=0  # TODO: implémenter le comptage des messages non lus
            )
            for thread in threads
        ]
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/support/threads/{thread_id}", response_model=ThreadDetailOut)
def get_support_thread(thread_id: str, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Récupère un fil de support avec ses messages"""
    try:
        thread_repo = PostgreSQLThreadRepository(db)
        
        thread = thread_repo.get_by_id(thread_id)
        if not thread or str(thread.user_id) != uid:
            raise HTTPException(404, "Fil de discussion introuvable")
        
        # Récupérer les messages
        messages = []
        for message in thread.messages:
            messages.append(MessageOut(
                id=str(message.id),
                thread_id=str(message.thread_id),
                author_user_id=str(message.author_user_id) if message.author_user_id is not None else None,
                content=str(message.content),
                created_at=message.created_at.timestamp(),
                author_name=message.author.first_name + " " + message.author.last_name if message.author else "Support"
            ))
        
        return ThreadDetailOut(
            id=str(thread.id),
            user_id=str(thread.user_id),
            order_id=str(thread.order_id) if thread.order_id is not None else None,
            subject=str(thread.subject),
            closed=bool(thread.closed),
            created_at=thread.created_at.timestamp(),
            unread_count=0,
            messages=messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/support/threads/{thread_id}/messages", response_model=MessageOut)
def post_support_message(thread_id: str, message_data: MessageCreateIn, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Ajoute un message à un fil de support"""
    try:
        thread_repo = PostgreSQLThreadRepository(db)
        
        thread = thread_repo.get_by_id(thread_id)
        if not thread or str(thread.user_id) != uid:
            raise HTTPException(404, "Fil de discussion introuvable")
        
        if bool(thread.closed):
            raise HTTPException(400, "Ce fil de discussion est fermé")
        
        message_data_dict = {
            "author_user_id": uid,
            "content": message_data.content
        }
        
        message = thread_repo.add_message(thread_id, message_data_dict)
        
        return MessageOut(
            id=str(message.id),
            thread_id=str(message.thread_id),
            author_user_id=str(message.author_user_id) if message.author_user_id is not None else None,
            content=str(message.content),
            created_at=message.created_at.timestamp(),
            author_name=message.author.first_name + " " + message.author.last_name if message.author else "Support"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/support/threads/{thread_id}/mark-read")
def mark_support_thread_as_read(thread_id: str, uid: str = Depends(current_user_id), db: Session = Depends(get_db)):
    """Marque un fil de support comme lu"""
    try:
        thread_repo = PostgreSQLThreadRepository(db)
        
        thread = thread_repo.get_by_id(thread_id)
        if not thread or str(thread.user_id) != uid:
            raise HTTPException(404, "Fil de discussion introuvable")
        
        # Pour l'instant, on retourne juste un succès
        # Dans une implémentation complète, on pourrait marquer les messages comme lus
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

# ====================== ADMIN SUPPORT ======================
@app.get("/admin/support/threads", response_model=List[ThreadOut])
def admin_list_support_threads(u = Depends(require_admin), db: Session = Depends(get_db)):
    """Liste tous les fils de support (admin)"""
    try:
        thread_repo = PostgreSQLThreadRepository(db)
        
        threads = thread_repo.get_all()
        
        return [
            ThreadOut(
                id=str(thread.id),
                user_id=str(thread.user_id),
                order_id=str(thread.order_id) if thread.order_id is not None else None,
                subject=cast(str, thread.subject),
                closed=cast(bool, thread.closed),
                created_at=thread.created_at.timestamp(),
                unread_count=0
            )
            for thread in threads
        ]
    except Exception as e:
        raise HTTPException(400, str(e))

@app.get("/admin/support/threads/{thread_id}", response_model=ThreadDetailOut)
def admin_get_support_thread(thread_id: str, u = Depends(require_admin), db: Session = Depends(get_db)):
    """Récupère un fil de support (admin)"""
    try:
        thread_repo = PostgreSQLThreadRepository(db)
        
        thread = thread_repo.get_by_id(thread_id)
        if not thread:
            raise HTTPException(404, "Fil de discussion introuvable")
        
        # Récupérer les messages
        messages = []
        for message in thread.messages:
            messages.append(MessageOut(
                id=str(message.id),
                thread_id=str(message.thread_id),
                author_user_id=str(message.author_user_id) if message.author_user_id is not None else None,
                content=str(message.content),
                created_at=message.created_at.timestamp(),
                author_name=message.author.first_name + " " + message.author.last_name if message.author else "Support"
            ))
        
        return ThreadDetailOut(
            id=str(thread.id),
            user_id=str(thread.user_id),
            order_id=str(thread.order_id) if thread.order_id is not None else None,
            subject=str(thread.subject),
            closed=bool(thread.closed),
            created_at=thread.created_at.timestamp(),
            unread_count=0,
            messages=messages
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/admin/support/threads/{thread_id}/close")
def admin_close_support_thread(thread_id: str, u = Depends(require_admin), db: Session = Depends(get_db)):
    """Ferme un fil de support (admin)"""
    try:
        thread_repo = PostgreSQLThreadRepository(db)
        
        thread = thread_repo.get_by_id(thread_id)
        if not thread:
            raise HTTPException(404, "Fil de discussion introuvable")
        
        thread.closed = True  # type: ignore
        db.commit()
        
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/admin/support/threads/{thread_id}/messages", response_model=MessageOut)
def admin_post_support_message(thread_id: str, message_data: MessageCreateIn, u = Depends(require_admin), db: Session = Depends(get_db)):
    """Ajoute un message admin à un fil de support"""
    try:
        thread_repo = PostgreSQLThreadRepository(db)
        
        thread = thread_repo.get_by_id(thread_id)
        if not thread:
            raise HTTPException(404, "Fil de discussion introuvable")
        
        message_data_dict = {
            "author_user_id": None,  # Message admin
            "content": message_data.content
        }
        
        message = thread_repo.add_message(thread_id, message_data_dict)
        
        return MessageOut(
            id=str(message.id),
            thread_id=str(message.thread_id),
            author_user_id=str(message.author_user_id) if message.author_user_id is not None else None,
            content=cast(str, message.content),
            created_at=message.created_at.timestamp(),
            author_name="Support Admin"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))

# ====================== DIAGNOSTIC COMMANDES ======================
@app.get("/admin/orders/{order_id}/status")
def admin_get_order_status(order_id: str, u = Depends(require_admin), db: Session = Depends(get_db)):
    """Récupère le statut détaillé d'une commande pour diagnostic"""
    try:
        order_repo = PostgreSQLOrderRepository(db)
        payment_repo = PostgreSQLPaymentRepository(db)
        
        order = order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(404, "Commande introuvable")
        
        # Récupérer les paiements
        payments = payment_repo.get_by_order_id(order_id)
        
        # Informations de livraison
        delivery_info = None
        if order.delivery:
            delivery_info = {
                "transporteur": order.delivery.transporteur,
                "tracking_number": order.delivery.tracking_number,
                "delivery_status": order.delivery.delivery_status,
                "created_at": order.delivery.created_at.timestamp()
            }
        
        return {
            "order_id": str(order.id),
            "user_id": str(order.user_id),
            "status": str(order.status),
            "created_at": order.created_at.timestamp(),
            "validated_at": order.validated_at.timestamp() if order.validated_at else None,
            "shipped_at": order.shipped_at.timestamp() if order.shipped_at else None,
            "delivered_at": order.delivered_at.timestamp() if order.delivered_at else None,
            "cancelled_at": order.cancelled_at.timestamp() if order.cancelled_at else None,
            "refunded_at": order.refunded_at.timestamp() if order.refunded_at else None,
            "payment_id": str(order.payment_id) if order.payment_id else None,
            "payments": [
                {
                    "id": str(p.id),
                    "amount_cents": p.amount_cents,
                    "status": p.status,
                    "created_at": p.created_at.timestamp()
                } for p in payments
            ],
            "delivery": delivery_info,
            "items_count": len(order.items),
            "total_cents": sum(item.unit_price_cents * item.quantity for item in order.items)
        }
    except HTTPException:
        raise
    except Exception as e:
        # Erreur diagnostic commande
        raise HTTPException(400, f"Erreur diagnostic: {str(e)}")

# ====================== ADMIN: LIVRAISON ======================
@app.post("/admin/orders/{order_id}/ship")
def admin_ship_order(order_id: str, delivery_data: DeliveryIn, u = Depends(require_admin), db: Session = Depends(get_db)):
    """Marque une commande comme expédiée"""
    try:
        order_repo = PostgreSQLOrderRepository(db)
        
        order = order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(404, "Commande introuvable")
        
        # Vérifier que la commande peut être expédiée
        if str(order.status) not in [OrderStatus.VALIDEE, OrderStatus.PAYEE]:
            raise HTTPException(400, f"Commande non expédiable (statut actuel: {order.status})")
        
        # Créer les informations de livraison
        from database.models import Delivery
        delivery = Delivery(
            order_id=order.id,
            transporteur=delivery_data.transporteur,
            tracking_number=delivery_data.tracking_number,
            address=order.user.address,
            delivery_status=delivery_data.delivery_status
        )
        db.add(delivery)
        
        # Mettre à jour le statut de la commande
        order.status = OrderStatus.EXPEDIEE  # type: ignore
        order.shipped_at = datetime.utcnow()  # type: ignore
        order_repo.update(order)
        
        db.commit()
        
        return {"ok": True, "message": f"Commande {order_id} expédiée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        # Erreur lors de l'expédition de la commande
        raise HTTPException(400, f"Erreur lors de l'expédition: {str(e)}")

@app.post("/admin/orders/{order_id}/mark-delivered")
def admin_mark_delivered(order_id: str, u = Depends(require_admin), db: Session = Depends(get_db)):
    """Marque une commande comme livrée"""
    try:
        order_repo = PostgreSQLOrderRepository(db)
        
        order = order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(404, "Commande introuvable")
        
        # Vérifier que la commande peut être marquée comme livrée
        if str(order.status) != OrderStatus.EXPEDIEE:
            raise HTTPException(400, f"Commande non expédiée (statut actuel: {order.status})")
        
        # Mettre à jour le statut de la commande
        order.status = OrderStatus.LIVREE  # type: ignore
        order.delivered_at = datetime.utcnow()  # type: ignore
        order_repo.update(order)
        
        # Mettre à jour le statut de livraison
        if order.delivery:
            order.delivery.delivery_status = "LIVREE"
            db.commit()
        
        return {"ok": True, "message": f"Commande {order_id} marquée comme livrée"}
    except HTTPException:
        raise
    except Exception as e:
        # Erreur lors du marquage de livraison
        raise HTTPException(400, f"Erreur lors du marquage de livraison: {str(e)}")

@app.post("/admin/orders/{order_id}/refund")
def admin_refund_order(order_id: str, refund_data: RefundIn, u = Depends(require_admin), db: Session = Depends(get_db)):
    """Rembourse une commande"""
    try:
        order_repo = PostgreSQLOrderRepository(db)
        payment_repo = PostgreSQLPaymentRepository(db)
        product_repo = PostgreSQLProductRepository(db)
        
        order = order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(404, "Commande introuvable")
        
        # Vérifier que la commande peut être remboursée
        if str(order.status) not in [OrderStatus.PAYEE, OrderStatus.EXPEDIEE, OrderStatus.LIVREE]:
            raise HTTPException(400, f"Commande non remboursable (statut actuel: {order.status})")
        
        # Récupérer le paiement
        payments = payment_repo.get_by_order_id(order_id)
        if not payments:
            raise HTTPException(400, "Aucun paiement trouvé")
        
        # Remettre le stock en place pour chaque article
        for item in order.items:
            product = product_repo.get_by_id(str(item.product_id))
            if product:
                # Remettre le stock
                product.stock_qty += item.quantity
                
                # Réactiver le produit s'il était inactif à cause du stock
                if not product.active and product.stock_qty > 0:
                    product.active = True  # type: ignore
                    # Produit réactivé automatiquement (remboursement)
                
                product_repo.update(product)
        
        # Mettre à jour le statut de la commande
        order.status = OrderStatus.REMBOURSEE  # type: ignore
        order.refunded_at = datetime.utcnow()  # type: ignore
        order_repo.update(order)
        
        # Mettre à jour le statut du paiement
        for payment in payments:
            payment.status = "REFUNDED"  # type: ignore
        db.commit()
        
        return {"ok": True, "message": f"Commande {order_id} remboursée avec succès"}
    except HTTPException:
        raise
    except Exception as e:
        # Erreur lors du remboursement de la commande
        raise HTTPException(400, f"Erreur lors du remboursement: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    # Démarrage de l'API e-commerce
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
