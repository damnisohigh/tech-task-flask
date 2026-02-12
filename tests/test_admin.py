import io


def test_admin_panel_as_admin(admin_client):
    resp = admin_client.get("/admin")
    assert resp.status_code == 200


def test_admin_panel_as_user(auth_client):
    resp = auth_client.get("/admin", follow_redirects=True)
    assert b"Access denied" in resp.data


def test_admin_panel_anonymous(client):
    resp = client.get("/admin", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]



def test_admin_logs(admin_client):
    resp = admin_client.get("/admin/logs")
    assert resp.status_code == 200
    assert b"logs" in resp.data.lower() or b"upload" in resp.data.lower()



def test_admin_users(admin_client):
    resp = admin_client.get("/admin/users")
    assert resp.status_code == 200
    assert b"admin@admin.com" in resp.data



def test_admin_data(admin_client, sample_csv):
    # Upload some data first via a separate authed client
    data = {"file": (io.BytesIO(sample_csv), "data.csv")}
    admin_client.post("/upload", data=data, content_type="multipart/form-data")
    resp = admin_client.get("/admin/data")
    assert resp.status_code == 200
