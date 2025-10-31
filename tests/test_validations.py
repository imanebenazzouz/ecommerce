import importlib.util


def _load_validations():
    spec = importlib.util.spec_from_file_location(
        "validations_mod",
        "/Users/imanebenazzouz/Desktop/ecommerce/ecommerce-backend/utils/validations.py",
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod


_v = _load_validations()
sanitize_numeric = _v.sanitize_numeric
validate_luhn = _v.validate_luhn
validate_card_number = _v.validate_card_number
validate_cvv = _v.validate_cvv
validate_expiry_month = _v.validate_expiry_month
validate_expiry_year = _v.validate_expiry_year
validate_expiry_date = _v.validate_expiry_date
validate_postal_code = _v.validate_postal_code
validate_phone = _v.validate_phone
validate_street_number = _v.validate_street_number
validate_street_name = _v.validate_street_name
validate_quantity = _v.validate_quantity


def test_sanitize_numeric():
    assert sanitize_numeric("A12-34 ") == "1234"


def test_card_validations():
    ok, _ = validate_card_number("4242 4242 4242 4242")
    assert ok
    bad, msg = validate_card_number("1234")
    assert not bad and msg
    assert validate_luhn("4242424242424242") is True


def test_cvv_and_expiry():
    assert validate_cvv("123")[0]
    assert not validate_cvv("12a")[0]
    assert validate_expiry_month(12)[0]
    assert not validate_expiry_month(0)[0]
    assert validate_expiry_year(2099)[0]
    assert not validate_expiry_year(1500)[0]
    assert validate_expiry_date(12, 2099)[0]


def test_contact_and_address():
    assert validate_postal_code("75001")[0]
    assert not validate_postal_code("75A01")[0]
    assert validate_phone("0612345678")[0]
    assert not validate_phone("0012345678")[0]
    assert validate_street_number("12")[0]
    assert not validate_street_number("12A")[0]
    assert validate_street_name("Rue de la Paix")[0]


def test_quantity():
    assert validate_quantity(1)[0]
    assert not validate_quantity(0)[0]


