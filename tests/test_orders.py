import importlib.util


def _load_enums():
    spec = importlib.util.spec_from_file_location(
        "enums_mod", 
        "/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend/enums.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


OrderStatus = _load_enums().OrderStatus


def _fill_cart(cart_service, user_id, product, qty):
    assert cart_service.add_to_cart(user_id, product.id, qty)


def test_checkout_creates_order(order_service, cart_service, sample_products, sample_user):
    p1, _, _ = sample_products
    _fill_cart(cart_service, sample_user.id, p1, 2)
    order = order_service.checkout(sample_user.id)
    assert order.id
    assert order.status == OrderStatus.CREE
    assert order.total_cents() == 2 * p1.price_cents


def test_checkout_empty_cart_raises(order_service, sample_user):
    try:
        order_service.checkout(sample_user.id)
        assert False
    except ValueError:
        pass


def test_admin_validate_ship_deliver_flow(order_service, cart_service, sample_products, sample_user, admin_user):
    p1, _, _ = sample_products
    _fill_cart(cart_service, sample_user.id, p1, 1)
    order = order_service.checkout(sample_user.id)
    # validate
    order = order_service.backoffice_validate_order(admin_user.id, order.id)
    assert order.status == OrderStatus.VALIDEE
    # ship requires paid status; simulate payment first
    order.status = OrderStatus.PAYEE
    order_service.order_repo.update(order)
    order = order_service.backoffice_ship_order(admin_user.id, order.id)
    assert order.status == OrderStatus.EXPEDIEE
    order = order_service.backoffice_mark_delivered(admin_user.id, order.id)
    assert order.status == OrderStatus.LIVREE


def test_user_cancellation_releases_stock(order_service, cart_service, sample_products, sample_user):
    p1, _, _ = sample_products
    _fill_cart(cart_service, sample_user.id, p1, 1)
    order = order_service.checkout(sample_user.id)
    orig = order_service.product_repo.get_by_id(p1.id).stock_qty
    order = order_service.request_cancellation(sample_user.id, order.id)
    assert order.status == OrderStatus.ANNULEE
    # stock released
    assert order_service.product_repo.get_by_id(p1.id).stock_qty == orig + 1


