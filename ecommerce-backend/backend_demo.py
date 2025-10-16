from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional
import uuid
import time
import hashlib
from persistent_storage import persistent_storage

# =========================
# ========== Domain =======
# =========================

class OrderStatus(Enum):
    CREE = auto()
    VALIDEE = auto()
    PAYEE = auto()
    EXPEDIEE = auto()
    LIVREE = auto()
    ANNULEE = auto()
    REMBOURSEE = auto()

class DeliveryStatus(Enum):
    PREPAREE = "PRÉPARÉE"
    EN_COURS = "EN_COURS"
    LIVREE = "LIVRÉE"

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    first_name: str
    last_name: str
    address: str
    is_admin: bool = False

    def update_profile(self, **fields):
        for k, v in fields.items():
            if hasattr(self, k) and k not in {"id", "email", "is_admin", "password_hash"}:
                setattr(self, k, v)

@dataclass
class Product:
    id: str
    name: str
    description: str
    price_cents: int
    stock_qty: int
    active: bool = True

@dataclass
class CartItem:
    product_id: str
    quantity: int

@dataclass
class Cart:
    user_id: str
    items: Dict[str, CartItem] = field(default_factory=dict)  # key: product_id

    def add(self, product: Product, qty: int = 1):
        if qty <= 0:
            raise ValueError("Quantité invalide.")
        if not product.active:
            raise ValueError("Produit inactif.")
        if product.stock_qty < qty:
            raise ValueError("Stock insuffisant.")
        if product.id in self.items:
            self.items[product.id].quantity += qty
        else:
            self.items[product.id] = CartItem(product_id=product.id, quantity=qty)

    def remove(self, product_id: str, qty: int = 1):
        if product_id not in self.items:
            return
        if qty <= 0:
            del self.items[product_id]
            return
        self.items[product_id].quantity -= qty
        if self.items[product_id].quantity <= 0:
            del self.items[product_id]

    def clear(self):
        self.items.clear()

    def total_cents(self, product_repo: "ProductRepository") -> int:
        total = 0
        for it in self.items.values():
            p = product_repo.get(it.product_id)
            # Ignore items whose product is missing, inactive, or whose ID no longer matches
            # the item product_id (simulates a deleted/replaced product).
            if p is None or not p.active or p.id != it.product_id:
                continue
            total += p.price_cents * it.quantity
        return total

@dataclass
class InvoiceLine:
    product_id: str
    name: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int

@dataclass
class Invoice:
    id: str
    order_id: str
    user_id: str
    lines: List[InvoiceLine]
    total_cents: int
    issued_at: float  # epoch timestamp

@dataclass
class Payment:
    id: str
    order_id: str
    user_id: str
    amount_cents: int
    provider: str  # ex: "CB"
    provider_ref: str | None
    succeeded: bool
    created_at: float
    idempotency_key: str | None = None
    card_last4: str | None = None

@dataclass
class Delivery:
    id: str
    order_id: str
    transporteur: str  # ex: "Colissimo", "Chronopost", "UPS"
    tracking_number: Optional[str]
    address: str
    delivery_status: DeliveryStatus

@dataclass
class MessageThread:
    id: str
    user_id: str
    order_id: Optional[str]
    subject: str
    messages: List["Message"] = field(default_factory=list)
    closed: bool = False
    unread_count: int = 0  # Nombre de messages non lus par le client

@dataclass
class Message:
    id: str
    thread_id: str
    author_user_id: Optional[str]  # None = agent support
    body: str
    created_at: float
    read_by_client: bool = False  # True si le client a lu ce message

@dataclass
class OrderItem:
    product_id: str
    name: str
    unit_price_cents: int
    quantity: int

@dataclass
class Order:
    id: str
    user_id: str
    items: List[OrderItem]
    status: OrderStatus
    created_at: float
    validated_at: Optional[float] = None
    paid_at: Optional[float] = None
    shipped_at: Optional[float] = None
    delivered_at: Optional[float] = None
    cancelled_at: Optional[float] = None
    refunded_at: Optional[float] = None
    delivery: Optional[Delivery] = None
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None

    def total_cents(self) -> int:
        return sum(i.unit_price_cents * i.quantity for i in self.items)

# =========================
# ====== Repositories =====
# =========================

class UserRepository:
    def __init__(self):
        self._by_id: Dict[str, User] = {}
        self._by_email: Dict[str, User] = {}

    def add(self, user: User):
        self._by_id[user.id] = user
        self._by_email[user.email.lower()] = user

    def get(self, user_id: str) -> Optional[User]:
        return self._by_id.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self._by_email.get(email.lower())

class ProductRepository:
    def __init__(self):
        self._by_id: Dict[str, Product] = {}

    def add(self, product: Product):
        self._by_id[product.id] = product

    def get(self, product_id: str) -> Optional[Product]:
        return self._by_id.get(product_id)

    def list_active(self) -> List[Product]:
        return [p for p in self._by_id.values() if p.active]

    def reserve_stock(self, product_id: str, qty: int):
        p = self.get(product_id)
        if not p or p.stock_qty < qty:
            raise ValueError("Stock insuffisant.")
        p.stock_qty -= qty

    def release_stock(self, product_id: str, qty: int):
        p = self.get(product_id)
        if p:
            p.stock_qty += qty

class CartRepository:
    def __init__(self):
        self._by_user: Dict[str, Cart] = {}

    def get_or_create(self, user_id: str) -> Cart:
        if user_id not in self._by_user:
            self._by_user[user_id] = Cart(user_id=user_id)
        return self._by_user[user_id]

    def clear(self, user_id: str):
        self.get_or_create(user_id).clear()

class OrderRepository:
    def __init__(self):
        self._by_id: Dict[str, Order] = {}
        self._by_user: Dict[str, List[str]] = {}
        self._load_from_storage()

    def _load_from_storage(self):
        """Charge les commandes depuis le stockage persistant"""
        try:
            orders_data = persistent_storage.get_all_items("orders")
            for order_data in orders_data:
                order = self._dict_to_order(order_data)
                self._by_id[order.id] = order
                self._by_user.setdefault(order.user_id, []).append(order.id)
        except Exception as e:
            print(f"Erreur lors du chargement des commandes: {e}")

    def _order_to_dict(self, order: Order) -> Dict:
        """Convertit une commande en dictionnaire pour la sauvegarde"""
        return {
            'id': order.id,
            'user_id': order.user_id,
            'items': [
                {
                    'product_id': item.product_id,
                    'name': item.name,
                    'unit_price_cents': item.unit_price_cents,
                    'quantity': item.quantity
                }
                for item in order.items
            ],
            'status': order.status.name,
            'created_at': order.created_at,
            'validated_at': order.validated_at,
            'shipped_at': order.shipped_at,
            'delivered_at': order.delivered_at,
            'cancelled_at': order.cancelled_at,
            'refunded_at': order.refunded_at,
            'payment_id': order.payment_id,
            'invoice_id': order.invoice_id,
            'delivery': self._delivery_to_dict(order.delivery) if order.delivery else None
        }

    def _dict_to_order(self, data: Dict) -> Order:
        """Convertit un dictionnaire en commande"""
        order = Order(
            id=data['id'],
            user_id=data['user_id'],
            items=[
                OrderItem(
                    product_id=item['product_id'],
                    name=item['name'],
                    unit_price_cents=item['unit_price_cents'],
                    quantity=item['quantity']
                )
                for item in data['items']
            ],
            status=OrderStatus[data['status']],
            created_at=data['created_at'],
            validated_at=data.get('validated_at'),
            shipped_at=data.get('shipped_at'),
            delivered_at=data.get('delivered_at'),
            cancelled_at=data.get('cancelled_at'),
            refunded_at=data.get('refunded_at'),
            payment_id=data.get('payment_id'),
            invoice_id=data.get('invoice_id'),
            delivery=self._dict_to_delivery(data.get('delivery')) if data.get('delivery') else None
        )
        return order

    def _delivery_to_dict(self, delivery: Delivery) -> Dict:
        """Convertit une livraison en dictionnaire"""
        return {
            'id': delivery.id,
            'order_id': delivery.order_id,
            'transporteur': delivery.transporteur,
            'tracking_number': delivery.tracking_number,
            'address': delivery.address,
            'delivery_status': delivery.delivery_status.value
        }

    def _dict_to_delivery(self, data: Dict) -> Delivery:
        """Convertit un dictionnaire en livraison"""
        return Delivery(
            id=data['id'],
            order_id=data['order_id'],
            transporteur=data['transporteur'],
            tracking_number=data.get('tracking_number'),
            address=data['address'],
            delivery_status=DeliveryStatus(data['delivery_status'])
        )

    def add(self, order: Order):
        self._by_id[order.id] = order
        self._by_user.setdefault(order.user_id, []).append(order.id)
        persistent_storage.save_item("orders", order.id, self._order_to_dict(order))

    def get(self, order_id: str) -> Optional[Order]:
        return self._by_id.get(order_id)

    def list_by_user(self, user_id: str) -> List[Order]:
        return [self._by_id[oid] for oid in self._by_user.get(user_id, [])]

    def update(self, order: Order):
        self._by_id[order.id] = order
        persistent_storage.save_item("orders", order.id, self._order_to_dict(order))

class InvoiceRepository:
    def __init__(self):
        self._by_id: Dict[str, Invoice] = {}
        self._load_from_storage()

    def _load_from_storage(self):
        """Charge les factures depuis le stockage persistant"""
        try:
            invoices_data = persistent_storage.get_all_items("invoices")
            for invoice_data in invoices_data:
                invoice = self._dict_to_invoice(invoice_data)
                self._by_id[invoice.id] = invoice
        except Exception as e:
            print(f"Erreur lors du chargement des factures: {e}")

    def _invoice_to_dict(self, invoice: Invoice) -> Dict:
        """Convertit une facture en dictionnaire pour la sauvegarde"""
        return {
            'id': invoice.id,
            'order_id': invoice.order_id,
            'user_id': invoice.user_id,
            'lines': [
                {
                    'product_id': line.product_id,
                    'name': line.name,
                    'unit_price_cents': line.unit_price_cents,
                    'quantity': line.quantity,
                    'line_total_cents': line.line_total_cents
                }
                for line in invoice.lines
            ],
            'total_cents': invoice.total_cents,
            'issued_at': invoice.issued_at
        }

    def _dict_to_invoice(self, data: Dict) -> Invoice:
        """Convertit un dictionnaire en facture"""
        return Invoice(
            id=data['id'],
            order_id=data['order_id'],
            user_id=data['user_id'],
            lines=[
                InvoiceLine(
                    product_id=line['product_id'],
                    name=line['name'],
                    unit_price_cents=line['unit_price_cents'],
                    quantity=line['quantity'],
                    line_total_cents=line['line_total_cents']
                )
                for line in data['lines']
            ],
            total_cents=data['total_cents'],
            issued_at=data['issued_at']
        )

    def add(self, invoice: Invoice):
        self._by_id[invoice.id] = invoice
        persistent_storage.save_item("invoices", invoice.id, self._invoice_to_dict(invoice))

    def get(self, invoice_id: str) -> Optional[Invoice]:
        return self._by_id.get(invoice_id)

class PaymentRepository:
    def __init__(self):
        self._by_id: Dict[str, Payment] = {}
        self._by_idempotency: Dict[str, Payment] = {}  # idempotency_key -> Payment
        self._load_from_storage()

    def _load_from_storage(self):
        """Charge les paiements depuis le stockage persistant"""
        try:
            payments_data = persistent_storage.get_all_items("payments")
            for payment_data in payments_data:
                payment = self._dict_to_payment(payment_data)
                self._by_id[payment.id] = payment
                if payment.idempotency_key:
                    self._by_idempotency[payment.idempotency_key] = payment
        except Exception as e:
            print(f"Erreur lors du chargement des paiements: {e}")

    def _payment_to_dict(self, payment: Payment) -> Dict:
        """Convertit un paiement en dictionnaire pour la sauvegarde"""
        return {
            'id': payment.id,
            'order_id': payment.order_id,
            'user_id': payment.user_id,
            'amount_cents': payment.amount_cents,
            'provider': payment.provider,
            'provider_ref': payment.provider_ref,
            'succeeded': payment.succeeded,
            'created_at': payment.created_at,
            'idempotency_key': payment.idempotency_key,
            'card_last4': payment.card_last4
        }

    def _dict_to_payment(self, data: Dict) -> Payment:
        """Convertit un dictionnaire en paiement"""
        return Payment(
            id=data['id'],
            order_id=data['order_id'],
            user_id=data.get('user_id', 'unknown'),  # Valeur par défaut pour compatibilité
            amount_cents=data['amount_cents'],
            provider=data.get('provider', 'CB'),  # Valeur par défaut pour compatibilité
            provider_ref=data.get('provider_ref', None),
            succeeded=data['succeeded'],
            created_at=data['created_at'],
            idempotency_key=data.get('idempotency_key')
        )

    def add(self, payment: Payment):
        self._by_id[payment.id] = payment
        if payment.idempotency_key:
            self._by_idempotency[payment.idempotency_key] = payment
        persistent_storage.save_item("payments", payment.id, self._payment_to_dict(payment))

    def get(self, payment_id: str) -> Optional[Payment]:
        return self._by_id.get(payment_id)
    
    def get_by_idempotency_key(self, idempotency_key: str) -> Optional[Payment]:
        return self._by_idempotency.get(idempotency_key)

class ThreadRepository:
    def __init__(self):
        self._by_id: Dict[str, MessageThread] = {}

    def add(self, thread: MessageThread):
        self._by_id[thread.id] = thread

    def get(self, thread_id: str) -> Optional[MessageThread]:
        return self._by_id.get(thread_id)

    def list_by_user(self, user_id: str) -> List[MessageThread]:
        return [t for t in self._by_id.values() if t.user_id == user_id]

# =========================
# ====== Services =========
# =========================

class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        """Hash password using bcrypt with salt"""
        import bcrypt
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        import bcrypt
        try:
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
        except Exception:
            return False

class SessionManager:
    """Gestion sécurisée des sessions avec JWT et expiration."""
    def __init__(self, secret_key: str = None):
        import os
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.session_duration = int(os.getenv("SESSION_DURATION", "3600"))  # 1 heure par défaut
        self._blacklisted_tokens: set = set()  # Tokens révoqués

    def create_session(self, user_id: str) -> str:
        """Créer une session JWT avec expiration"""
        import jwt
        from datetime import datetime, timedelta
        import uuid
        
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=self.session_duration),
            'iat': datetime.utcnow(),
            'jti': uuid.uuid4().hex,  # assurer l'unicité du token
            'type': 'access_token'
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def destroy_session(self, token: str):
        """Révoquer un token en l'ajoutant à la blacklist"""
        self._blacklisted_tokens.add(token)

    def get_user_id(self, token: str) -> Optional[str]:
        """Récupérer l'ID utilisateur depuis un token JWT"""
        import jwt
        from datetime import datetime
        
        try:
            # Vérifier si le token est blacklisté
            if token in self._blacklisted_tokens:
                return None
                
            # Décoder le JWT
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Vérifier l'expiration
            if datetime.utcnow().timestamp() > payload.get('exp', 0):
                return None
                
            return payload.get('user_id')
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

class AuthService:
    def __init__(self, users: UserRepository, sessions: SessionManager):
        self.users = users
        self.sessions = sessions

    def register(self, email: str, password: str, first_name: str, last_name: str, address: str, is_admin: bool=False) -> User:
        if self.users.get_by_email(email):
            raise ValueError("Email déjà utilisé.")
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=PasswordHasher.hash(password),
            first_name=first_name,
            last_name=last_name,
            address=address,
            is_admin=is_admin
        )
        self.users.add(user)
        return user

    def login(self, email: str, password: str) -> str:
        user = self.users.get_by_email(email)
        if not user or not PasswordHasher.verify(password, user.password_hash):
            raise ValueError("Identifiants invalides.")
        return self.sessions.create_session(user.id)

    def logout(self, token: str):
        self.sessions.destroy_session(token)

class CatalogService:
    def __init__(self, products: ProductRepository):
        self.products = products

    def list_products(self) -> List[Product]:
        return self.products.list_active()

class CartService:
    def __init__(self, carts: CartRepository, products: ProductRepository):
        self.carts = carts
        self.products = products

    def add_to_cart(self, user_id: str, product_id: str, qty: int = 1):
        product = self.products.get(product_id)
        if not product:
            raise ValueError("Produit introuvable.")
        self.carts.get_or_create(user_id).add(product, qty)

    def remove_from_cart(self, user_id: str, product_id: str, qty: int = 1):
        self.carts.get_or_create(user_id).remove(product_id, qty)

    def view_cart(self, user_id: str) -> Cart:
        return self.carts.get_or_create(user_id)

    def cart_total(self, user_id: str) -> int:
        return self.carts.get_or_create(user_id).total_cents(self.products)

class PaymentGateway:
    """Simulation d'un prestataire CB (à remplacer par Stripe/Adyen/etc.)."""
    def charge_card(self, card_last4: str, amount_cents: int, idempotency_key: str) -> Dict:
        # MOCK: succès si carte ne finit pas par '0000'
        ok = card_last4 != "0000"
        return {
            "success": ok,
            "transaction_id": str(uuid.uuid4()) if ok else None,
            "failure_reason": None if ok else "CARTE_REFUSEE"
        }

    def refund(self, transaction_id: str, amount_cents: int) -> Dict:
        return {
            "success": True,
            "refund_id": str(uuid.uuid4())
        }

class BillingService:
    def __init__(self, invoices: InvoiceRepository):
        self.invoices = invoices

    def issue_invoice(self, order: Order) -> Invoice:
        lines = [
            InvoiceLine(
                product_id=i.product_id,
                name=i.name,
                unit_price_cents=i.unit_price_cents,
                quantity=i.quantity,
                line_total_cents=i.unit_price_cents * i.quantity
            )
            for i in order.items
        ]
        inv = Invoice(
            id=str(uuid.uuid4()),
            order_id=order.id,
            user_id=order.user_id,
            lines=lines,
            total_cents=sum(l.line_total_cents for l in lines),
            issued_at=time.time()
        )
        self.invoices.add(inv)
        return inv

class DeliveryService:
    def prepare_delivery(self, order: Order, address: str, transporteur: str = "Colissimo") -> Delivery:
        delivery = Delivery(
            id=str(uuid.uuid4()),
            order_id=order.id,
            transporteur=transporteur,
            tracking_number=None,
            address=address,
            delivery_status=DeliveryStatus.PREPAREE
        )
        return delivery

    def ship(self, delivery: Delivery) -> Delivery:
        delivery.delivery_status = DeliveryStatus.EN_COURS
        delivery.tracking_number = delivery.tracking_number or f"TRK-{uuid.uuid4().hex[:10].upper()}"
        return delivery

    def mark_delivered(self, delivery: Delivery) -> Delivery:
        delivery.delivery_status = DeliveryStatus.LIVREE
        return delivery

class OrderService:
    def __init__(
        self,
        orders: OrderRepository,
        products: ProductRepository,
        carts: CartRepository,
        payments: PaymentRepository,
        invoices: InvoiceRepository,
        billing: BillingService,
        delivery_svc: DeliveryService,
        gateway: PaymentGateway,
        users: UserRepository
    ):
        self.orders = orders
        self.products = products
        self.carts = carts
        self.payments = payments
        self.invoices = invoices
        self.billing = billing
        self.delivery_svc = delivery_svc
        self.gateway = gateway
        self.users = users

    # ----- Front user flow -----
    def checkout(self, user_id: str) -> Order:
        cart = self.carts.get_or_create(user_id)
        if not cart.items:
            raise ValueError("Panier vide.")
        # Réserver le stock + construire la commande
        order_items: List[OrderItem] = []
        for it in cart.items.values():
            p = self.products.get(it.product_id)
            if not p or not p.active:
                raise ValueError("Produit indisponible.")
            if p.stock_qty < it.quantity:
                raise ValueError(f"Stock insuffisant pour {p.name}.")
            self.products.reserve_stock(p.id, it.quantity)
            order_items.append(OrderItem(
                product_id=p.id,
                name=p.name,
                unit_price_cents=p.price_cents,
                quantity=it.quantity
            ))
        order = Order(
            id=str(uuid.uuid4()),
            user_id=user_id,
            items=order_items,
            status=OrderStatus.CREE,
            created_at=time.time()
        )
        self.orders.add(order)
        # Vider le panier
        self.carts.clear(user_id)
        return order

    def pay_by_card(self, order_id: str, card_number: str, exp_month: int, exp_year: int, cvc: str) -> Payment:
        """Méthode legacy pour compatibilité"""
        card_last4 = card_number[-4:] if len(card_number) >= 4 else card_number
        idempotency_key = f"{order_id}_{int(time.time())}"
        return self.process_payment(order_id, card_last4, idempotency_key)

    def process_payment(self, order_id: str, card_last4: str, idempotency_key: str) -> Payment:
        """Nouvelle méthode avec idempotence"""
        order = self.orders.get(order_id)
        if not order:
            raise ValueError("Commande introuvable.")
        
        # Vérifier l'idempotence (scopée à la commande)
        existing_payment = self.payments.get_by_idempotency_key(idempotency_key)
        if existing_payment and existing_payment.order_id == order_id:
            return existing_payment
        
        if order.status not in {OrderStatus.CREE, OrderStatus.VALIDEE}:
            raise ValueError("Statut de commande incompatible avec le paiement.")
        
        amount = order.total_cents()
        res = self.gateway.charge_card(card_last4, amount, idempotency_key)
        
        payment = Payment(
            id=str(uuid.uuid4()),
            order_id=order.id,
            user_id=order.user_id,
            amount_cents=amount,
            provider="CB",
            provider_ref=res.get("transaction_id"),
            succeeded=res["success"],
            created_at=time.time(),
            idempotency_key=idempotency_key,
            card_last4=card_last4
        )
        
        self.payments.add(payment)
        
        if payment.succeeded:
            order.payment_id = payment.id
            order.status = OrderStatus.PAYEE
            order.paid_at = time.time()
            # Facture
            inv = self.billing.issue_invoice(order)
            order.invoice_id = inv.id
            self.orders.update(order)
        else:
            # En cas d'échec, on garde la commande en CREATED
            # Le stock reste réservé (sera libéré par expiration ou annulation)
            pass
        
        return payment

    def view_orders(self, user_id: str) -> List[Order]:
        return self.orders.list_by_user(user_id)

    def request_cancellation(self, user_id: str, order_id: str) -> Order:
        order = self.orders.get(order_id)
        if not order or order.user_id != user_id:
            raise ValueError("Commande introuvable.")
        if order.status in {OrderStatus.EXPEDIEE, OrderStatus.LIVREE}:
            raise ValueError("Trop tard pour annuler : commande expédiée.")
        order.status = OrderStatus.ANNULEE
        order.cancelled_at = time.time()
        # restituer le stock
        for it in order.items:
            self.products.release_stock(it.product_id, it.quantity)
        self.orders.update(order)
        return order

    # ----- Backoffice flow -----
    def backoffice_validate_order(self, admin_user_id: str, order_id: str) -> Order:
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")
        order = self.orders.get(order_id)
        if not order or order.status != OrderStatus.PAYEE:
            raise ValueError("La commande doit être payée pour être validée.")
        order.status = OrderStatus.VALIDEE
        order.validated_at = time.time()
        
        # Créer automatiquement les informations de livraison avec statut "PRÉPARÉE"
        if not order.delivery:
            user = self.users.get(order.user_id)
            address = user.address if user else "Unknown Address"
            order.delivery = self.delivery_svc.prepare_delivery(
                order,
                address=address,
                transporteur="Colissimo"  # Transporteur par défaut
            )
        
        self.orders.update(order)
        return order

    def backoffice_ship_order(self, admin_user_id: str, order_id: str) -> Order:
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")
        order = self.orders.get(order_id)
        if not order or order.status != OrderStatus.VALIDEE:
            raise ValueError("La commande doit être validée pour être expédiée.")
        # Utiliser la livraison existante si présente, sinon en préparer une nouvelle
        if order.delivery:
            delivery = self.delivery_svc.ship(order.delivery)
            order.delivery = delivery
        else:
            user = self.users.get(order.user_id)
            address = user.address if user else "Unknown Address"
            delivery = self.delivery_svc.prepare_delivery(order, address=address)
            delivery = self.delivery_svc.ship(delivery)
            order.delivery = delivery
        order.status = OrderStatus.EXPEDIEE
        order.shipped_at = time.time()
        self.orders.update(order)
        return order

    def backoffice_mark_delivered(self, admin_user_id: str, order_id: str) -> Order:
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")
        order = self.orders.get(order_id)
        if not order or order.status != OrderStatus.EXPEDIEE or not order.delivery:
            raise ValueError("Commande non expédiée.")
        self.delivery_svc.mark_delivered(order.delivery)
        order.status = OrderStatus.LIVREE
        order.delivered_at = time.time()
        self.orders.update(order)
        return order

    def backoffice_refund(self, admin_user_id: str, order_id: str, amount_cents: Optional[int] = None) -> Order:
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")
        order = self.orders.get(order_id)
        if not order or order.status not in {OrderStatus.PAYEE, OrderStatus.ANNULEE}:
            raise ValueError("Remboursement non autorisé au statut actuel.")
        amount = amount_cents or order.total_cents()
        # remboursement via le PSP mock
        payment = self.payments.get(order.payment_id) if order.payment_id else None
        if not payment or not payment.provider_ref:
            raise ValueError("Aucun paiement initial.")
        self.gateway.refund(payment.provider_ref, amount)
        order.status = OrderStatus.REMBOURSEE
        order.refunded_at = time.time()
        # restituer le stock si besoin
        for it in order.items:
            self.products.release_stock(it.product_id, it.quantity)
        self.orders.update(order)
        return order

class CustomerService:
    """Service client: fils de discussion & messages côté UI + réponses agents."""
    def __init__(self, threads: ThreadRepository, users: UserRepository):
        self.threads = threads
        self.users = users

    def open_thread(self, user_id: str, subject: str, order_id: Optional[str] = None) -> MessageThread:
        th = MessageThread(id=str(uuid.uuid4()), user_id=user_id, order_id=order_id, subject=subject)
        self.threads.add(th)
        return th

    def post_message(self, thread_id: str, author_user_id: Optional[str], body: str) -> Message:
        th = self.threads.get(thread_id)
        if not th or th.closed:
            raise ValueError("Fil introuvable ou fermé.")
        if author_user_id is not None and not self.users.get(author_user_id):
            raise ValueError("Auteur inconnu.")
        msg = Message(
            id=str(uuid.uuid4()),
            thread_id=thread_id,
            author_user_id=author_user_id,
            body=body,
            created_at=time.time()
        )
        th.messages.append(msg)
        
        # Si le message est de l'agent (author_user_id est None), incrémenter le compteur de messages non lus
        if author_user_id is None:
            th.unread_count += 1
        
        return msg

    def mark_thread_as_read(self, thread_id: str, user_id: str):
        """Marquer tous les messages d'un thread comme lus par le client"""
        th = self.threads.get(thread_id)
        if not th:
            raise ValueError("Fil introuvable.")
        if th.user_id != user_id:
            raise PermissionError("Accès refusé à ce fil.")
        
        # Marquer tous les messages comme lus et remettre le compteur à zéro
        for msg in th.messages:
            if msg.author_user_id is None:  # Message de l'agent
                msg.read_by_client = True
        th.unread_count = 0
        return th

    def close_thread(self, thread_id: str, admin_user_id: str):
        admin = self.users.get(admin_user_id)
        if not admin or not admin.is_admin:
            raise PermissionError("Droits insuffisants.")
        th = self.threads.get(thread_id)
        if not th:
            raise ValueError("Fil introuvable.")
        th.closed = True
        return th