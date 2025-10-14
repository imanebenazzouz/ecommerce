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
    PaymentGateway, OrderService, Product, OrderStatus
)

app = FastAPI(title="Ecommerce API (TP)")

# Configuration CORS pour permettre l'accès depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server alternatif
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,  # Permettre les cookies/credentials
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation mémoire
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

# Création d’un jeu de données de base
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


# -------------------- Helpers --------------------
def current_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Token manquant (Authorization: Bearer <token>)")
    token = authorization.split(" ", 1)[1].strip()
    uid = sessions.get_user_id(token)
    if not uid:
        raise HTTPException(401, "Session invalide")
    return uid


# -------------------- Schemas --------------------
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


class OrderItemOut(BaseModel):
    product_id: str
    name: str
    unit_price_cents: int
    quantity: int


class OrderOut(BaseModel):
    id: str
    user_id: str
    items: List[OrderItemOut]
    status: str
    total_cents: int


# -------------------- Routes --------------------

# Route de test
@app.get("/")
def root():
    return {"message": "Ecommerce API is running!", "version": "1.0"}

# Authentification
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


# Produits
@app.get("/products", response_model=list[ProductOut])
def list_products():
    return [ProductOut(**p.__dict__) for p in catalog.list_products()]


# Panier
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


# Commandes
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


@app.get("/orders", response_model=list[OrderOut])
def my_orders(uid: str = Depends(current_user_id)):
    out = []
    for o in order_svc.view_orders(uid):
        out.append(OrderOut(
            id=o.id,
            user_id=o.user_id,
            items=[OrderItemOut(**i.__dict__) for i in o.items],
            status=o.status.name,
            total_cents=o.total_cents(),
        ))
    return out