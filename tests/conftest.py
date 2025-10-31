import uuid
import pytest

# In-memory fake repositories to avoid real DB usage


class FakeUserRepo:
    def __init__(self):
        self.users_by_id = {}
        self.users_by_email = {}

    def create(self, user_data):
        user_id = str(uuid.uuid4())
        user = type("User", (), {})()
        user.id = user_id
        user.email = user_data["email"]
        user.password_hash = user_data["password_hash"]
        user.first_name = user_data.get("first_name")
        user.last_name = user_data.get("last_name")
        user.address = user_data.get("address")
        user.is_admin = bool(user_data.get("is_admin", False))
        self.users_by_id[user_id] = user
        self.users_by_email[user.email] = user
        return user

    def get_by_email(self, email):
        return self.users_by_email.get(email)

    def get_by_id(self, user_id):
        return self.users_by_id.get(str(user_id))


class FakeProductRepo:
    def __init__(self):
        self.products = {}

    def create(self, product_data):
        pid = str(uuid.uuid4())
        product = type("Product", (), {})()
        product.id = pid
        product.name = product_data["name"]
        product.price_cents = product_data["price_cents"]
        product.stock_qty = product_data.get("stock_qty", 0)
        product.active = product_data.get("active", True)
        self.products[pid] = product
        return product

    def get_by_id(self, product_id):
        return self.products.get(str(product_id))

    def get_all_active(self):
        return [p for p in self.products.values() if p.active]

    def reserve_stock(self, product_id, quantity):
        p = self.get_by_id(product_id)
        if not p or p.stock_qty < quantity:
            return False
        p.stock_qty -= quantity
        return True

    def release_stock(self, product_id, quantity):
        p = self.get_by_id(product_id)
        if not p:
            return False
        p.stock_qty += quantity
        return True

    def update(self, product):
        # No-op for fake
        return product


class FakeCartRepo:
    def __init__(self):
        self.carts = {}

    def get_by_user_id(self, user_id):
        return self.carts.get(str(user_id))

    def create_cart(self, user_id):
        cart = type("Cart", (), {})()
        cart.id = str(uuid.uuid4())
        cart.user_id = str(user_id)
        cart.items = []
        self.carts[str(user_id)] = cart
        return cart

    def add_item(self, user_id, product_id, quantity):
        cart = self.get_by_user_id(user_id) or self.create_cart(user_id)
        # item structure
        item = type("CartItem", (), {})()
        item.product_id = str(product_id)
        item.quantity = int(quantity)
        # merge if exists
        for it in cart.items:
            if str(it.product_id) == str(product_id):
                it.quantity += quantity
                return True
        cart.items.append(item)
        return True

    def remove_item(self, user_id, product_id, quantity):
        cart = self.get_by_user_id(user_id)
        if not cart:
            return False
        for it in list(cart.items):
            if str(it.product_id) == str(product_id):
                if quantity == 0:
                    cart.items.remove(it)
                    return True
                it.quantity -= quantity
                if it.quantity <= 0:
                    cart.items.remove(it)
                return True
        return False

    def clear(self, user_id):
        cart = self.get_by_user_id(user_id)
        if not cart:
            return False
        cart.items = []
        return True


class FakeOrderRepo:
    def __init__(self):
        self.orders = {}

    def create(self, order_data):
        oid = str(uuid.uuid4())
        order = type("Order", (), {})()
        order.id = oid
        order.user_id = str(order_data["user_id"])
        raw_items = order_data.get("items", [])
        # Normalize to objects with attributes expected by OrderService later
        norm_items = []
        for it in raw_items:
            obj = type("OrderItem", (), {})()
            obj.product_id = str(it.get("product_id"))
            obj.name = it.get("name")
            obj.unit_price_cents = it.get("unit_price_cents", 0)
            obj.quantity = it.get("quantity", 0)
            norm_items.append(obj)
        order.items = norm_items
        order.status = order_data.get("status")
        order.payment_id = None
        order.invoice_id = None
        def total():
            return sum(getattr(i, "unit_price_cents", 0) * getattr(i, "quantity", 0) for i in order.items)
        order.total_cents = total
        self.orders[oid] = order
        return order

    def get_by_id(self, order_id):
        return self.orders.get(str(order_id))

    def list_by_user(self, user_id):
        return [o for o in self.orders.values() if o.user_id == str(user_id)]

    def update(self, order):
        self.orders[str(order.id)] = order
        return order


class FakePaymentRepo:
    def __init__(self):
        self.payments = {}

    def create(self, data):
        pid = str(uuid.uuid4())
        payment = type("Payment", (), {})()
        payment.id = pid
        for k, v in data.items():
            setattr(payment, k, v)
        self.payments[pid] = payment
        return payment

    def get_by_id(self, pid):
        return self.payments.get(str(pid))

    def get_by_order_id(self, order_id):
        return [p for p in self.payments.values() if getattr(p, "order_id", None) == str(order_id)]


class FakeInvoiceRepo:
    def __init__(self):
        self.invoices = {}

    def create(self, data):
        iid = str(uuid.uuid4())
        invoice = type("Invoice", (), {})()
        invoice.id = iid
        for k, v in data.items():
            setattr(invoice, k, v)
        self.invoices[iid] = invoice
        return invoice


class FakeDeliveryService:
    def prepare_delivery(self, order_id):
        d = type("Delivery", (), {})()
        d.id = str(uuid.uuid4())
        return d

    def ship_order(self, order_id):
        d = type("Delivery", (), {})()
        d.id = str(uuid.uuid4())
        return d

    def mark_delivered(self, order_id):
        return True


class FakeBillingService:
    def __init__(self, invoice_repo: FakeInvoiceRepo):
        self.invoice_repo = invoice_repo

    def issue_invoice(self, order):
        return self.invoice_repo.create({"order_id": order.id, "total_cents": order.total_cents()})


@pytest.fixture
def product_repo():
    return FakeProductRepo()


@pytest.fixture
def user_repo():
    return FakeUserRepo()


@pytest.fixture
def cart_repo():
    return FakeCartRepo()


@pytest.fixture
def order_repo():
    return FakeOrderRepo()


@pytest.fixture
def payment_repo():
    return FakePaymentRepo()


@pytest.fixture
def invoice_repo():
    return FakeInvoiceRepo()


def _load_module_from_path(name: str, path: str):
    import importlib.util, sys, os
    backend_root = "/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend"
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    sys.modules[name] = module
    return module


@pytest.fixture
def auth_service(user_repo):
    mod = _load_module_from_path(
        "auth_service_mod",
        "/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend/services/auth_service.py",
    )
    return mod.AuthService(user_repo=user_repo)


@pytest.fixture
def catalog_service(product_repo):
    mod = _load_module_from_path(
        "catalog_service_mod",
        "/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend/services/catalog_service.py",
    )
    return mod.CatalogService(product_repo=product_repo)


@pytest.fixture
def cart_service(cart_repo, product_repo):
    mod = _load_module_from_path(
        "cart_service_mod",
        "/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend/services/cart_service.py",
    )
    return mod.CartService(cart_repo=cart_repo, product_repo=product_repo)


@pytest.fixture
def payment_service(payment_repo, order_repo):
    mod = _load_module_from_path(
        "payment_service_mod",
        "/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend/services/payment_service.py",
    )
    # Monkeypatch gateway to deterministic behavior
    svc = mod.PaymentService(payment_repo=payment_repo, order_repo=order_repo)
    svc.gateway.charge_card = lambda card, m, y, c, amount, idempotency_key: {
        "success": not str(card).endswith("0000"),
        "transaction_id": str(uuid.uuid4()),
        "failure_reason": None,
    }
    return svc


@pytest.fixture
def order_service(order_repo, product_repo, cart_repo, payment_repo, invoice_repo, user_repo, payment_service):
    mod = _load_module_from_path(
        "order_service_mod",
        "/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend/services/order_service.py",
    )
    delivery = FakeDeliveryService()
    billing = FakeBillingService(invoice_repo)
    return mod.OrderService(
        order_repo=order_repo,
        product_repo=product_repo,
        cart_repo=cart_repo,
        payment_repo=payment_repo,
        invoice_repo=invoice_repo,
        user_repo=user_repo,
        payment_service=payment_service,
        delivery_service=delivery,
        billing_service=billing,
    )


@pytest.fixture
def sample_user(auth_service, user_repo):
    # Create a user via repo directly with a hashed password
    pwd_hash = auth_service.hash_password("secret")
    return user_repo.create({
        "email": "user@example.com",
        "password_hash": pwd_hash,
        "first_name": "U",
        "last_name": "Ser",
        "address": "1 Rue Exemple",
        "is_admin": False,
    })


@pytest.fixture
def admin_user(auth_service, user_repo):
    pwd_hash = auth_service.hash_password("admin")
    return user_repo.create({
        "email": "admin@example.com",
        "password_hash": pwd_hash,
        "first_name": "Ad",
        "last_name": "Min",
        "address": "99 Admin St",
        "is_admin": True,
    })


@pytest.fixture
def sample_products(product_repo):
    p1 = product_repo.create({"name": "Widget", "price_cents": 1500, "stock_qty": 10, "active": True})
    p2 = product_repo.create({"name": "Gadget", "price_cents": 2500, "stock_qty": 0, "active": True})
    p3 = product_repo.create({"name": "Legacy", "price_cents": 500, "stock_qty": 5, "active": False})
    return p1, p2, p3


