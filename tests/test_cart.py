def test_add_to_cart_and_total(cart_service, sample_products, sample_user):
    p1, _, _ = sample_products
    assert cart_service.add_to_cart(sample_user.id, p1.id, 2) is True
    total = cart_service.get_cart_total(sample_user.id)
    assert total == 2 * 1500


def test_add_inactive_or_missing_raises(cart_service, sample_products, sample_user):
    _, _, p3 = sample_products  # inactive
    try:
        cart_service.add_to_cart(sample_user.id, p3.id, 1)
        assert False
    except ValueError:
        pass
    try:
        cart_service.add_to_cart(sample_user.id, "missing", 1)
        assert False
    except ValueError:
        pass


def test_remove_and_clear_cart(cart_service, sample_products, sample_user):
    p1, _, _ = sample_products
    cart_service.add_to_cart(sample_user.id, p1.id, 1)
    assert cart_service.remove_from_cart(sample_user.id, p1.id, 1) is True
    # remove again should be no-op False
    assert cart_service.remove_from_cart(sample_user.id, p1.id, 1) is True  # service returns True
    assert cart_service.clear_cart(sample_user.id) is True
    assert cart_service.get_cart_total(sample_user.id) == 0


