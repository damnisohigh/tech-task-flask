from db import create_user


def test_login_page(client):
    resp = client.get("/login")
    assert resp.status_code == 200
    assert b"login" in resp.data.lower() or b"email" in resp.data.lower()


def test_login_valid(client, app):
    with app.app_context():
        create_user("test@test.com", "pass1234")
    resp = client.post("/login", data={"email": "test@test.com", "password": "pass1234"}, follow_redirects=False)
    assert resp.status_code == 302
    assert "/" in resp.headers["Location"]


def test_login_invalid(client):
    resp = client.post("/login", data={"email": "bad@test.com", "password": "wrong"}, follow_redirects=True)
    assert b"Invalid email or password" in resp.data


def test_login_next_safe_redirect(client, app):
    with app.app_context():
        create_user("redir@test.com", "pass1234")
    resp = client.post("/login?next=/results", data={"email": "redir@test.com", "password": "pass1234"}, follow_redirects=False)
    assert resp.status_code == 302
    assert "/results" in resp.headers["Location"]


def test_login_blocks_open_redirect(client, app):
    with app.app_context():
        create_user("safe@test.com", "pass1234")
    resp = client.post("/login?next=http://evil.com", data={"email": "safe@test.com", "password": "pass1234"}, follow_redirects=False)
    assert resp.status_code == 302
    # Should NOT redirect to evil.com — should go to index
    assert "evil.com" not in resp.headers["Location"]


def test_register_page(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"register" in resp.data.lower() or b"password" in resp.data.lower()


def test_register_success(client):
    resp = client.post("/register", data={
        "email": "new@test.com", "password": "pass1234", "password2": "pass1234"
    }, follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_register_password_mismatch(client):
    resp = client.post("/register", data={
        "email": "mm@test.com", "password": "pass1234", "password2": "different"
    }, follow_redirects=True)
    assert b"Passwords do not match" in resp.data


def test_register_short_password(client):
    resp = client.post("/register", data={
        "email": "short@test.com", "password": "ab", "password2": "ab"
    }, follow_redirects=True)
    assert b"at least 4 characters" in resp.data


def test_register_duplicate_email(client, app):
    with app.app_context():
        create_user("dup@test.com", "pass1234")
    resp = client.post("/register", data={
        "email": "dup@test.com", "password": "pass1234", "password2": "pass1234"
    }, follow_redirects=True)
    assert b"already exists" in resp.data


def test_logout(auth_client):
    resp = auth_client.get("/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]
