# api.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import uuid

# Import du moteur métier
from backend_demo import (
    UserRepository, ProductRepository, CartRepository, OrderRepository,
    InvoiceRepository, PaymentRepository, ThreadRepository, SessionManager,
    AuthService, CatalogService, CartService, BillingService, DeliveryService,
    PaymentGateway, OrderService, Product, OrderStatus, DeliveryStatus, Delivery
)

app = FastAPI(title="Ecommerce API (TP)")

# -------------------------------- CORS --------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server alternatif
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
def current_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Token manquant (Authorization: Bearer <token>)")
    token = authorization.split(" ", 1)[1].strip()
    uid = sessions.get_user_id(token)
    if not uid:
        raise HTTPException(401, "Session invalide")
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
    lines: List[OrderItemOut]
    total_cents: int
    issued_at: float


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
        raise HTTPException(400, str(e))

@app.post("/auth/login", response_model=TokenOut)
def login(inp: LoginIn):
    try:
        token = auth.login(inp.email, inp.password)
        return TokenOut(token=token)
    except ValueError as e:
        raise HTTPException(401, str(e))

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
        raise HTTPException(400, str(e))

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
        lines=[OrderItemOut(**i.__dict__) for i in invoice.lines],
        total_cents=invoice.total_cents,
        issued_at=invoice.issued_at
    )

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