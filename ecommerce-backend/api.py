# api.py
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

# Import du moteur métier
from backend_demo import (
    UserRepository, ProductRepository, CartRepository, OrderRepository,
    InvoiceRepository, PaymentRepository, ThreadRepository, SessionManager,
    AuthService, CatalogService, CartService, BillingService, DeliveryService,
    PaymentGateway, OrderService, CustomerService, Product, OrderStatus, DeliveryStatus, Delivery,
    MessageThread, Message
)

app = FastAPI(title="Ecommerce API (TP)")

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
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Méthodes spécifiques
    allow_headers=[
        "Authorization", 
        "Content-Type", 
        "Accept",
        "Origin",
        "X-Requested-With"
    ],  # Headers spécifiques
)

# --------------------------- Initialisation mémoire ---------------------------
users = UserRepository()
products = ProductRepository()
carts = CartRepository()
orders = OrderRepository()
invoices = InvoiceRepository()
payments = PaymentRepository()
threads = ThreadRepository()
sessions = SessionManager()

auth = AuthService(users, sessions)
catalog = CatalogService(products)
cart_svc = CartService(carts, products)
billing = BillingService(invoices)
delivery_svc = DeliveryService()
gateway = PaymentGateway()
order_svc = OrderService(orders, products, carts, payments, invoices, billing, delivery_svc, gateway, users)
support_svc = CustomerService(threads, users)

# Jeu de données de base
if not products.list_active():
    p1 = Product(id=str(uuid.uuid4()), name="T-Shirt Logo", description="Coton bio", price_cents=1999, stock_qty=100)
    p2 = Product(id=str(uuid.uuid4()), name="Sweat Capuche", description="Molleton", price_cents=4999, stock_qty=50)
    products.add(p1)
    products.add(p2)
    try:
        auth.register("admin@example.com", "admin", "Admin", "Root", "1 Rue du BO", is_admin=True)
        auth.register("client@example.com", "secret", "Alice", "Martin", "12 Rue des Fleurs")
    except Exception:
        pass


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
def current_user(authorization: Optional[str] = Header(default=None)):
    uid = current_user_id(authorization)
    u = users.get(uid)
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

# ---------- Authentification ----------
@app.post("/auth/register", response_model=UserOut)
def register(inp: RegisterIn):
    try:
        u = auth.register(inp.email, inp.password, inp.first_name, inp.last_name, inp.address)
        return UserOut(**u.__dict__)
    except ValueError as e:
        # Messages d'erreur sécurisés sans détails internes
        error_message = str(e)
        if "Email déjà utilisé" in error_message:
            raise HTTPException(400, "Cette adresse email est déjà utilisée")
        elif "Mot de passe" in error_message:
            raise HTTPException(400, "Mot de passe invalide")
        else:
            raise HTTPException(400, "Erreur lors de l'inscription")

@app.post("/auth/login", response_model=TokenOut)
def login(inp: LoginIn):
    try:
        token = auth.login(inp.email, inp.password)
        return TokenOut(token=token)
    except ValueError as e:
        # Ne pas révéler si l'email existe ou pas
        raise HTTPException(401, "Identifiants invalides")

@app.post("/auth/logout")
def logout(uid: str = Depends(current_user_id), authorization: Optional[str] = Header(default=None)):
    token = authorization.split(" ", 1)[1].strip()
    auth.logout(token)
    return {"ok": True}

# Voir son profil
@app.get("/auth/me", response_model=UserOut)
def me(u = Depends(current_user)):
    return UserOut(**u.__dict__)

# ---- Mettre à jour son profil ----
@app.put("/auth/profile", response_model=UserOut)
def update_profile(inp: UserUpdateIn, u = Depends(current_user)):
    if inp.first_name is not None:
        u.first_name = inp.first_name
    if inp.last_name is not None:
        u.last_name = inp.last_name
    if inp.address is not None:
        u.address = inp.address

    if hasattr(users, "update"):
        users.update(u)

    return UserOut(**u.__dict__)

# ---------- Produits (public) ----------
@app.get("/products", response_model=list[ProductOut])
def list_products():
    return [ProductOut(**p.__dict__) for p in catalog.list_products()]

# ---------- Panier ----------
@app.get("/cart", response_model=CartOut)
def view_cart(uid: str = Depends(current_user_id)):
    c = cart_svc.view_cart(uid)
    return CartOut(
        user_id=c.user_id,
        items={k: CartItemOut(product_id=v.product_id, quantity=v.quantity) for k, v in c.items.items()}
    )

@app.post("/cart/add")
def add_to_cart(inp: CartAddIn, uid: str = Depends(current_user_id)):
    try:
        cart_svc.add_to_cart(uid, inp.product_id, inp.qty)
        return {"ok": True}
    except ValueError as e:
        # Messages d'erreur sécurisés
        error_message = str(e)
        if "Produit introuvable" in error_message:
            raise HTTPException(404, "Produit introuvable")
        elif "Stock insuffisant" in error_message:
            raise HTTPException(400, "Stock insuffisant")
        elif "Produit inactif" in error_message:
            raise HTTPException(400, "Produit non disponible")
        else:
            raise HTTPException(400, "Erreur lors de l'ajout au panier")

@app.post("/cart/remove")
def remove_from_cart(inp: CartRemoveIn, uid: str = Depends(current_user_id)):
    try:
        cart_svc.remove_from_cart(uid, inp.product_id, inp.qty or 0)
        return {"ok": True}
    except ValueError as e:
        raise HTTPException(400, str(e))

# ---------- Commandes (client) ----------
@app.post("/orders/checkout", response_model=CheckoutOut)
def checkout(uid: str = Depends(current_user_id)):
    try:
        o = order_svc.checkout(uid)
        return CheckoutOut(order_id=o.id, total_cents=o.total_cents(), status=o.status.name)
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.post("/orders/{order_id}/pay")
def pay(order_id: str, inp: PayIn, uid: str = Depends(current_user_id)):
    try:
        p = order_svc.pay_by_card(order_id, inp.card_number, inp.exp_month, inp.exp_year, inp.cvc)
        return {"ok": True, "payment_id": p.id}
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.post("/payments", response_model=PaymentOut)
def process_payment(inp: PaymentIn, uid: str = Depends(current_user_id)):
    try:
        # Vérifier que la commande appartient à l'utilisateur
        order = order_svc.orders.get(inp.order_id)
        if not order or order.user_id != uid:
            raise HTTPException(404, "Commande introuvable")
        
        payment = order_svc.process_payment(inp.order_id, inp.card_last4, inp.idempotency_key)
        return PaymentOut(
            id=payment.id,
            order_id=payment.order_id,
            amount_cents=payment.amount_cents,
            status="PAID" if payment.succeeded else "FAILED",
            created_at=payment.created_at
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/orders", response_model=list[OrderOut])
def my_orders(uid: str = Depends(current_user_id)):
    out: list[OrderOut] = []
    for o in order_svc.view_orders(uid):
        delivery_info = None
        if o.delivery:
            delivery_info = DeliveryOut(
                transporteur=o.delivery.transporteur,
                tracking_number=o.delivery.tracking_number,
                delivery_status=o.delivery.delivery_status.value
            )
        
        out.append(OrderOut(
            id=o.id,
            user_id=o.user_id,
            items=[OrderItemOut(**i.__dict__) for i in o.items],
            status=o.status.name,
            total_cents=o.total_cents(),
            delivery=delivery_info
        ))
    return out

@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: str, uid: str = Depends(current_user_id)):
    order = order_svc.orders.get(order_id)
    if not order or order.user_id != uid:
        raise HTTPException(404, "Commande introuvable")
    
    delivery_info = None
    if order.delivery:
        delivery_info = DeliveryOut(
            transporteur=order.delivery.transporteur,
            tracking_number=order.delivery.tracking_number,
            delivery_status=order.delivery.delivery_status.value
        )
    
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        items=[OrderItemOut(**i.__dict__) for i in order.items],
        status=order.status.name,
        total_cents=order.total_cents(),
        delivery=delivery_info
    )

@app.post("/orders/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: str, uid: str = Depends(current_user_id)):
    try:
        order = order_svc.request_cancellation(uid, order_id)
        
        delivery_info = None
        if order.delivery:
            delivery_info = DeliveryOut(
                transporteur=order.delivery.transporteur,
                tracking_number=order.delivery.tracking_number,
                delivery_status=order.delivery.delivery_status.value
            )
        
        return OrderOut(
            id=order.id,
            user_id=order.user_id,
            items=[OrderItemOut(**i.__dict__) for i in order.items],
            status=order.status.name,
            total_cents=order.total_cents(),
            delivery=delivery_info
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/orders/{order_id}/invoice", response_model=InvoiceOut)
def get_invoice(order_id: str, uid: str = Depends(current_user_id)):
    order = order_svc.orders.get(order_id)
    if not order or order.user_id != uid:
        raise HTTPException(404, "Commande introuvable")
    
    if not order.invoice_id:
        raise HTTPException(404, "Facture non trouvée")
    
    invoice = order_svc.invoices.get(order.invoice_id)
    if not invoice:
        raise HTTPException(404, "Facture introuvable")
    
    return InvoiceOut(
        id=invoice.id,
        order_id=invoice.order_id,
        number=invoice.id,  # Simple: utiliser l'ID comme numéro
        lines=[InvoiceLineOut(**i.__dict__) for i in invoice.lines],
        total_cents=invoice.total_cents,
        issued_at=invoice.issued_at
    )

@app.get("/orders/{order_id}/invoice/download")
def download_invoice_pdf(order_id: str, uid: str = Depends(current_user_id)):
    """Télécharge la facture en PDF"""
    try:
        # Récupérer la commande
        order = orders.get(order_id)
        if not order or order.user_id != uid:
            raise HTTPException(404, "Commande introuvable")
        
        if not order.invoice_id:
            raise HTTPException(404, "Facture non trouvée")
        
        # Récupérer la facture
        invoice = invoices.get(order.invoice_id)
        if not invoice:
            raise HTTPException(404, "Facture introuvable")
        
        # Récupérer l'utilisateur
        user = users.get(uid)
        if not user:
            raise HTTPException(404, "Utilisateur introuvable")
    
        # Récupérer les données de paiement
        payment_data = None
        if order.payment_id:
            payment = payments.get(order.payment_id)
            if payment:
                payment_data = {
                    'amount_cents': payment.amount_cents,
                    'status': 'PAID' if payment.succeeded else 'FAILED',
                    'created_at': payment.created_at
                }
        
        # Récupérer les données de livraison
        delivery_data = None
        if order.delivery:
            delivery_data = {
                'transporteur': order.delivery.transporteur,
                'tracking_number': order.delivery.tracking_number,
                'delivery_status': order.delivery.delivery_status.value
            }
        
        # Préparer les données pour le PDF
        invoice_data = {
            'id': invoice.id,
            'number': invoice.id[:8],
            'issued_at': invoice.issued_at,
            'lines': [
                {
                    'product_id': line.product_id,
                    'name': line.name,
                    'unit_price_cents': line.unit_price_cents,
                    'quantity': line.quantity,
                    'line_total_cents': line.line_total_cents
                }
                for line in invoice.lines
            ]
        }
        
        order_data = {
            'id': order.id,
            'total_cents': order.total_cents()
        }
        
        user_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'address': user.address
        }
        
        # Générer le PDF
        pdf_buffer = generate_invoice_pdf(invoice_data, order_data, user_data, payment_data, delivery_data)
        
        # Retourner le fichier PDF
        filename = f"facture_{order_id[:8]}.pdf"
        return Response(
            content=pdf_buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        print(f"Erreur dans download_invoice_pdf: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Erreur génération PDF: {str(e)}")

@app.get("/test-pdf")
def test_pdf_generation():
    """Endpoint de test pour la génération PDF"""
    try:
        # Test simple avec reportlab directement
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Ajouter un paragraphe simple
        story.append(Paragraph("Test PDF", styles['Title']))
        story.append(Spacer(1, 20))
        story.append(Paragraph("Ceci est un test de génération PDF.", styles['Normal']))
        
        # Construire le PDF
        doc.build(story)
        buffer.seek(0)
        
        # Retourner le fichier PDF
        filename = "test_facture.pdf"
        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        print(f"Erreur dans test_pdf_generation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Erreur génération PDF: {str(e)}")

@app.get("/orders/{order_id}/tracking", response_model=DeliveryOut)
def get_order_tracking(order_id: str, uid: str = Depends(current_user_id)):
    order = order_svc.orders.get(order_id)
    if not order or order.user_id != uid:
        raise HTTPException(404, "Commande introuvable")
    
    if not order.delivery:
        raise HTTPException(404, "Informations de livraison non disponibles")
    
    return DeliveryOut(
        transporteur=order.delivery.transporteur,
        tracking_number=order.delivery.tracking_number,
        delivery_status=order.delivery.delivery_status.value
    )


# ====================== ADMIN: Produits ======================
@app.get("/admin/products", response_model=list[ProductOut])
def admin_list_products(u = Depends(require_admin)):
    all_products = products.list_all() if hasattr(products, "list_all") else products.list_active()
    return [ProductOut(**p.__dict__) for p in all_products]

@app.post("/admin/products", response_model=ProductOut, status_code=201)
def admin_create_product(inp: ProductCreateIn, u = Depends(require_admin)):
    p = Product(
        id=str(uuid.uuid4()),
        name=inp.name,
        description=inp.description or "",
        price_cents=inp.price_cents,
        stock_qty=inp.stock_qty,
        active=inp.active,
    )
    products.add(p)
    return ProductOut(**p.__dict__)

@app.put("/admin/products/{product_id}", response_model=ProductOut)
def admin_update_product(product_id: str, inp: ProductUpdateIn, u = Depends(require_admin)):
    p = products.get(product_id)
    if not p:
        raise HTTPException(404, "Produit introuvable")
    if inp.name is not None: p.name = inp.name
    if inp.description is not None: p.description = inp.description
    if inp.price_cents is not None: p.price_cents = inp.price_cents
    if inp.stock_qty is not None: p.stock_qty = inp.stock_qty
    if inp.active is not None: p.active = inp.active
    if hasattr(products, "update"): products.update(p)
    return ProductOut(**p.__dict__)

@app.delete("/admin/products/{product_id}")
def admin_delete_product(product_id: str, u = Depends(require_admin)):
    p = products.get(product_id)
    if not p:
        raise HTTPException(404, "Produit introuvable")
    if hasattr(products, "delete"):
        products.delete(product_id)
    else:
        p.active = False
        if hasattr(products, "update"): products.update(p)
    return {"ok": True}


# ====================== ADMIN: Commandes ======================
@app.get("/admin/orders", response_model=list[OrderOut])
def admin_list_orders(user_id: Optional[str] = None, u = Depends(require_admin)):
    out: list[OrderOut] = []
    if hasattr(orders, "list_all"):
        order_list = orders.list_all()
    else:
        if user_id and hasattr(orders, "list_by_user"):
            order_list = orders.list_by_user(user_id)
        elif hasattr(orders, "_by_user") and hasattr(orders, "list_by_user"):
            order_list = []
            for uid in orders._by_user.keys():
                order_list.extend(orders.list_by_user(uid))
        else:
            order_list = []

    if user_id:
        order_list = [o for o in order_list if o.user_id == user_id]

    for o in order_list:
        delivery_info = None
        if o.delivery:
            delivery_info = DeliveryOut(
                transporteur=o.delivery.transporteur,
                tracking_number=o.delivery.tracking_number,
                delivery_status=o.delivery.delivery_status.value
            )
        
        out.append(OrderOut(
            id=o.id,
            user_id=o.user_id,
            items=[OrderItemOut(**i.__dict__) for i in o.items],
            status=o.status.name,
            total_cents=o.total_cents(),
            delivery=delivery_info
        ))
    return out

@app.get("/admin/orders/{order_id}", response_model=OrderOut)
def admin_get_order(order_id: str, u = Depends(require_admin)):
    order = order_svc.orders.get(order_id)
    if not order:
        raise HTTPException(404, "Commande introuvable")
    
    delivery_info = None
    if order.delivery:
        delivery_info = DeliveryOut(
            transporteur=order.delivery.transporteur,
            tracking_number=order.delivery.tracking_number,
            delivery_status=order.delivery.delivery_status.value
        )
    
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        items=[OrderItemOut(**i.__dict__) for i in order.items],
        status=order.status.name,
        total_cents=order.total_cents(),
        delivery=delivery_info
    )

@app.post("/admin/orders/{order_id}/validate", response_model=OrderOut)
def admin_validate_order(order_id: str, u = Depends(require_admin)):
    try:
        o = order_svc.backoffice_validate_order(u.id, order_id)
        
        delivery_info = None
        if o.delivery:
            delivery_info = DeliveryOut(
                transporteur=o.delivery.transporteur,
                tracking_number=o.delivery.tracking_number,
                delivery_status=o.delivery.delivery_status.value
            )
        
        return OrderOut(
            id=o.id,
            user_id=o.user_id,
            items=[OrderItemOut(**i.__dict__) for i in o.items],
            status=o.status.name,
            total_cents=o.total_cents(),
            delivery=delivery_info
        )
    except (PermissionError, ValueError) as e:
        raise HTTPException(400, str(e))

@app.post("/admin/orders/{order_id}/ship", response_model=OrderOut)
def admin_ship_order(order_id: str, u = Depends(require_admin)):
    try:
        o = order_svc.backoffice_ship_order(u.id, order_id)
        
        delivery_info = None
        if o.delivery:
            delivery_info = DeliveryOut(
                transporteur=o.delivery.transporteur,
                tracking_number=o.delivery.tracking_number,
                delivery_status=o.delivery.delivery_status.value
            )
        
        return OrderOut(
            id=o.id,
            user_id=o.user_id,
            items=[OrderItemOut(**i.__dict__) for i in o.items],
            status=o.status.name,
            total_cents=o.total_cents(),
            delivery=delivery_info
        )
    except (PermissionError, ValueError) as e:
        raise HTTPException(400, str(e))

@app.post("/admin/orders/{order_id}/mark-delivered", response_model=OrderOut)
def admin_mark_delivered(order_id: str, u = Depends(require_admin)):
    try:
        o = order_svc.backoffice_mark_delivered(u.id, order_id)
        
        delivery_info = None
        if o.delivery:
            delivery_info = DeliveryOut(
                transporteur=o.delivery.transporteur,
                tracking_number=o.delivery.tracking_number,
                delivery_status=o.delivery.delivery_status.value
            )
        
        return OrderOut(
            id=o.id,
            user_id=o.user_id,
            items=[OrderItemOut(**i.__dict__) for i in o.items],
            status=o.status.name,
            total_cents=o.total_cents(),
            delivery=delivery_info
        )
    except (PermissionError, ValueError) as e:
        raise HTTPException(400, str(e))

@app.post("/admin/orders/{order_id}/refund", response_model=OrderOut)
def admin_refund_order(order_id: str, inp: RefundIn, u = Depends(require_admin)):
    try:
        o = order_svc.backoffice_refund(u.id, order_id, amount_cents=inp.amount_cents)
        
        delivery_info = None
        if o.delivery:
            delivery_info = DeliveryOut(
                transporteur=o.delivery.transporteur,
                tracking_number=o.delivery.tracking_number,
                delivery_status=o.delivery.delivery_status.value
            )
        
        return OrderOut(
            id=o.id,
            user_id=o.user_id,
            items=[OrderItemOut(**i.__dict__) for i in o.items],
            status=o.status.name,
            total_cents=o.total_cents(),
            delivery=delivery_info
        )
    except (PermissionError, ValueError) as e:
        raise HTTPException(400, str(e))

@app.post("/admin/orders/{order_id}/tracking", response_model=DeliveryOut)
def admin_update_tracking(order_id: str, inp: DeliveryIn, u = Depends(require_admin)):
    try:
        # Vérifier que la commande existe
        order = order_svc.orders.get(order_id)
        if not order:
            raise HTTPException(404, "Commande introuvable")
        
        # Valider le statut de livraison
        try:
            delivery_status = DeliveryStatus(inp.delivery_status)
        except ValueError:
            raise HTTPException(400, f"Statut de livraison invalide. Valeurs acceptées: {[s.value for s in DeliveryStatus]}")
        
        # Créer ou mettre à jour les informations de livraison
        if order.delivery:
            # Mettre à jour l'existant
            order.delivery.transporteur = inp.transporteur
            order.delivery.tracking_number = inp.tracking_number
            order.delivery.delivery_status = delivery_status
        else:
            # Créer une nouvelle livraison
            order.delivery = Delivery(
                id=str(uuid.uuid4()),
                order_id=order_id,
                transporteur=inp.transporteur,
                tracking_number=inp.tracking_number,
                address=order_svc.users.get(order.user_id).address,  # Utiliser l'adresse de l'utilisateur
                delivery_status=delivery_status
            )
        
        # Sauvegarder la commande
        order_svc.orders.update(order)
        
        return DeliveryOut(
            transporteur=order.delivery.transporteur,
            tracking_number=order.delivery.tracking_number,
            delivery_status=order.delivery.delivery_status.value
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, str(e))


# ====================== SUPPORT CLIENT ======================
@app.post("/support/threads", response_model=ThreadOut, status_code=201)
def create_support_thread(inp: ThreadCreateIn, uid: str = Depends(current_user_id)):
    """Créer un nouveau fil de discussion de support"""
    try:
        # Vérifier que la commande existe si order_id est fourni et non vide
        if inp.order_id and inp.order_id.strip():
            order = orders.get(inp.order_id)
            if not order or order.user_id != uid:
                raise HTTPException(404, "Commande introuvable")
        
        thread = support_svc.open_thread(uid, inp.subject, inp.order_id)
        return ThreadOut(
            id=thread.id,
            user_id=thread.user_id,
            order_id=thread.order_id,
            subject=thread.subject,
            closed=thread.closed,
            created_at=time.time(),
            unread_count=thread.unread_count
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

@app.get("/support/threads", response_model=List[ThreadOut])
def list_support_threads(uid: str = Depends(current_user_id)):
    """Lister les fils de discussion de l'utilisateur"""
    user_threads = threads.list_by_user(uid)
    return [
        ThreadOut(
            id=thread.id,
            user_id=thread.user_id,
            order_id=thread.order_id,
            subject=thread.subject,
            closed=thread.closed,
            created_at=time.time(),
            unread_count=thread.unread_count
        )
        for thread in user_threads
    ]

@app.get("/support/threads/{thread_id}", response_model=ThreadDetailOut)
def get_support_thread(thread_id: str, uid: str = Depends(current_user_id)):
    """Récupérer un fil de discussion avec ses messages"""
    thread = threads.get(thread_id)
    if not thread:
        raise HTTPException(404, "Fil de discussion introuvable")
    
    # Vérifier que l'utilisateur peut accéder à ce thread
    if thread.user_id != uid:
        raise HTTPException(403, "Accès refusé à ce fil de discussion")
    
    # Préparer les messages avec les noms des auteurs
    messages_out = []
    for msg in thread.messages:
        author_name = None
        if msg.author_user_id:
            author = users.get(msg.author_user_id)
            if author:
                author_name = f"{author.first_name} {author.last_name}"
            else:
                author_name = "Utilisateur supprimé"
        else:
            author_name = "Support"
        
        messages_out.append(MessageOut(
            id=msg.id,
            thread_id=msg.thread_id,
            author_user_id=msg.author_user_id,
            content=msg.body,
            created_at=msg.created_at,
            author_name=author_name
        ))
    
    return ThreadDetailOut(
        id=thread.id,
        user_id=thread.user_id,
        order_id=thread.order_id,
        subject=thread.subject,
        closed=thread.closed,
        created_at=time.time(),
        unread_count=thread.unread_count,
        messages=messages_out
    )

@app.post("/support/threads/{thread_id}/mark-read")
def mark_thread_as_read(thread_id: str, uid: str = Depends(current_user_id)):
    """Marquer tous les messages d'un thread comme lus"""
    try:
        support_svc.mark_thread_as_read(thread_id, uid)
        return {"message": "Messages marqués comme lus"}
    except ValueError as e:
        raise HTTPException(404, str(e))
    except PermissionError as e:
        raise HTTPException(403, str(e))

@app.post("/support/threads/{thread_id}/messages", response_model=MessageOut, status_code=201)
def post_support_message(thread_id: str, inp: MessageCreateIn, uid: str = Depends(current_user_id)):
    """Poster un message dans un fil de discussion"""
    try:
        thread = threads.get(thread_id)
        if not thread:
            raise HTTPException(404, "Fil de discussion introuvable")
        
        # Vérifier que l'utilisateur peut poster dans ce thread
        if thread.user_id != uid:
            raise HTTPException(403, "Accès refusé à ce fil de discussion")
        
        # Vérifier que le thread n'est pas fermé
        if thread.closed:
            raise HTTPException(400, "Ce fil de discussion est fermé")
        
        message = support_svc.post_message(thread_id, uid, inp.content)
        
        # Récupérer le nom de l'auteur
        author = users.get(uid)
        author_name = f"{author.first_name} {author.last_name}" if author else "Utilisateur"
        
        return MessageOut(
            id=message.id,
            thread_id=message.thread_id,
            author_user_id=message.author_user_id,
            content=message.body,
            created_at=message.created_at,
            author_name=author_name
        )
    except ValueError as e:
        raise HTTPException(400, str(e))

# ====================== ADMIN: Support ======================
@app.get("/admin/support/threads", response_model=List[ThreadDetailOut])
def admin_list_support_threads(u = Depends(require_admin)):
    """Lister tous les fils de discussion (admin)"""
    all_threads = list(threads._by_id.values())
    result = []
    
    for thread in all_threads:
        # Préparer les messages avec les noms des auteurs
        messages_out = []
        for msg in thread.messages:
            author_name = None
            if msg.author_user_id:
                author = users.get(msg.author_user_id)
                if author:
                    author_name = f"{author.first_name} {author.last_name}"
                else:
                    author_name = "Utilisateur supprimé"
            else:
                author_name = "Support"
            
            messages_out.append(MessageOut(
                id=msg.id,
                thread_id=msg.thread_id,
                author_user_id=msg.author_user_id,
                content=msg.body,
                created_at=msg.created_at,
                author_name=author_name
            ))
        
        result.append(ThreadDetailOut(
            id=thread.id,
            user_id=thread.user_id,
            order_id=thread.order_id,
            subject=thread.subject,
            closed=thread.closed,
            created_at=time.time(),
            messages=messages_out
        ))
    
    return result

@app.post("/admin/support/threads/{thread_id}/close")
def admin_close_support_thread(thread_id: str, u = Depends(require_admin)):
    """Fermer un fil de discussion (admin)"""
    try:
        support_svc.close_thread(thread_id, u.id)
        return {"ok": True, "message": "Fil de discussion fermé"}
    except ValueError as e:
        raise HTTPException(404, str(e))
    except PermissionError as e:
        raise HTTPException(403, str(e))

@app.get("/admin/support/threads/{thread_id}", response_model=ThreadDetailOut)
def admin_get_support_thread(thread_id: str, u = Depends(require_admin)):
    """Récupérer un fil de discussion spécifique (admin)"""
    thread = threads.get(thread_id)
    if not thread:
        raise HTTPException(404, "Fil de discussion introuvable")
    
    # Préparer les messages avec les noms des auteurs
    messages_out = []
    for msg in thread.messages:
        author_name = None
        if msg.author_user_id:
            author = users.get(msg.author_user_id)
            if author:
                author_name = f"{author.first_name} {author.last_name}"
            else:
                author_name = "Utilisateur supprimé"
        else:
            author_name = "Support"
        
        messages_out.append(MessageOut(
            id=msg.id,
            thread_id=msg.thread_id,
            author_user_id=msg.author_user_id,
            content=msg.body,
            created_at=msg.created_at,
            author_name=author_name
        ))
    
    return ThreadDetailOut(
        id=thread.id,
        user_id=thread.user_id,
        order_id=thread.order_id,
        subject=thread.subject,
        closed=thread.closed,
        created_at=time.time(),
        unread_count=thread.unread_count,
        messages=messages_out
    )

@app.post("/admin/support/threads/{thread_id}/messages", response_model=MessageOut, status_code=201)
def admin_post_support_message(thread_id: str, inp: MessageCreateIn, u = Depends(require_admin)):
    """Poster un message en tant qu'agent support (admin)"""
    try:
        thread = threads.get(thread_id)
        if not thread:
            raise HTTPException(404, "Fil de discussion introuvable")
        
        # Vérifier que le thread n'est pas fermé
        if thread.closed:
            raise HTTPException(400, "Ce fil de discussion est fermé")
        
        # Poster le message en tant qu'agent (author_user_id = None)
        message = support_svc.post_message(thread_id, None, inp.content)
        
        return MessageOut(
            id=message.id,
            thread_id=message.thread_id,
            author_user_id=message.author_user_id,
            content=message.body,
            created_at=message.created_at,
            author_name="Support"
        )
    except ValueError as e:
        raise HTTPException(400, str(e))