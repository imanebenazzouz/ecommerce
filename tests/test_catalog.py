def test_list_active_products(catalog_service, sample_products):
    products = catalog_service.list_products()
    names = {p.name for p in products}
    assert "Widget" in names
    assert "Legacy" not in names  # inactive hidden


def test_reserve_and_release_stock(catalog_service, sample_products):
    p1, _, _ = sample_products
    assert catalog_service.reserve_stock(p1.id, 2) is True
    # underlying repo stock reduced
    assert catalog_service.product_repo.get_by_id(p1.id).stock_qty == 8
    assert catalog_service.release_stock(p1.id, 2) is True
    assert catalog_service.product_repo.get_by_id(p1.id).stock_qty == 10


def test_reserve_stock_insufficient_raises(catalog_service, sample_products):
    _, p2, _ = sample_products
    try:
        catalog_service.reserve_stock(p2.id, 1)
        assert False, "should raise"
    except ValueError:
        pass


