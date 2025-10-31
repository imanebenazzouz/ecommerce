def test_hash_and_verify_password(auth_service):
    hashed = auth_service.hash_password("secret")
    assert isinstance(hashed, str) and len(hashed) > 0
    assert auth_service.verify_password("secret", hashed)
    assert not auth_service.verify_password("wrong", hashed)


def test_register_and_login_success(auth_service):
    user = auth_service.register(
        email="new@example.com",
        password="pwd",
        first_name="New",
        last_name="User",
        address="10 Rue Test",
    )
    assert user.email == "new@example.com"
    token = auth_service.login("new@example.com", "pwd")
    assert token.startswith("token-")


def test_register_idempotent_same_email_same_password(auth_service):
    u1 = auth_service.register("dup@example.com", "aaa", "A", "B", "Addr")
    u2 = auth_service.register("dup@example.com", "aaa", "A", "B", "Addr")
    assert u1.id == u2.id


def test_login_invalid_credentials_raises(auth_service):
    try:
        auth_service.login("nouser@example.com", "x")
        assert False, "should raise"
    except ValueError:
        pass


