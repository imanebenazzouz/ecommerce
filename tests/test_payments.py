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


def prepare_paid_order(order_service, cart_service, sample_products, sample_user):
    p1, _, _ = sample_products
    cart_service.add_to_cart(sample_user.id, p1.id, 1)
    order = order_service.checkout(sample_user.id)
    return order


def test_process_payment_success(order_service, payment_service, cart_service, sample_products, sample_user):
    order = prepare_paid_order(order_service, cart_service, sample_products, sample_user)
    payment = order_service.pay_by_card(
        order.id,
        card_number="4242424242424242",
        exp_month=12,
        exp_year=2099,
        cvc="123",
        postal_code="75001",
        phone="0612345678",
        street_number="10",
        street_name="Rue Exemple",
    )
    assert payment.status == "PAID"
    assert order_service.order_repo.get_by_id(order.id).status == OrderStatus.PAYEE


def test_process_payment_failure_raises(order_service, payment_service, cart_service, sample_products, sample_user):
    order = prepare_paid_order(order_service, cart_service, sample_products, sample_user)
    try:
        order_service.pay_by_card(
            order.id,
            card_number="4111111111110000",  # ends with 0000 -> failure
            exp_month=12,
            exp_year=2099,
            cvc="123",
        )
        assert False
    except ValueError:
        pass


def test_refund_flow(order_service, payment_service, cart_service, sample_products, sample_user, admin_user):
    # Pay first
    order = prepare_paid_order(order_service, cart_service, sample_products, sample_user)
    order_service.pay_by_card(order.id, "4242424242424242", 12, 2099, "123")
    # Then refund as admin
    order.status = OrderStatus.PAYEE
    order_service.order_repo.update(order)
    refunded_order = order_service.backoffice_refund(admin_user.id, order.id)
    assert refunded_order.status == OrderStatus.REMBOURSEE


