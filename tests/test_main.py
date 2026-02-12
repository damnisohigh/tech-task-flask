import io


def test_index_requires_login(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_index_renders_when_authed(auth_client):
    resp = auth_client.get("/")
    assert resp.status_code == 200
    assert b"upload" in resp.data.lower()


def test_upload_valid_csv(auth_client, sample_csv):
    data = {"file": (io.BytesIO(sample_csv), "data.csv")}
    resp = auth_client.post("/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert resp.status_code == 200
    assert b"inserted" in resp.data.lower() or b"Records" in resp.data


def test_upload_invalid_format(auth_client):
    data = {"file": (io.BytesIO(b"hello"), "data.txt")}
    resp = auth_client.post("/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert b"Only .csv" in resp.data or b"allowed" in resp.data.lower()


def test_upload_missing_columns(auth_client):
    bad_csv = b"Wrong,Columns\n1,2\n"
    data = {"file": (io.BytesIO(bad_csv), "bad.csv")}
    resp = auth_client.post("/upload", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert b"Missing required columns" in resp.data


def test_upload_no_file(auth_client):
    resp = auth_client.post("/upload", data={}, content_type="multipart/form-data", follow_redirects=True)
    assert b"No file" in resp.data or b"no file" in resp.data.lower()


def test_results_page(auth_client, sample_csv):
    # Upload first so there's data
    data = {"file": (io.BytesIO(sample_csv), "data.csv")}
    auth_client.post("/upload", data=data, content_type="multipart/form-data")
    resp = auth_client.get("/results")
    assert resp.status_code == 200


def test_clear_records(admin_client, sample_csv):
    data = {"file": (io.BytesIO(sample_csv), "data.csv")}
    admin_client.post("/upload", data=data, content_type="multipart/form-data")
    resp = admin_client.post("/clear", follow_redirects=True)
    assert resp.status_code == 200
    assert b"cleared" in resp.data.lower()


def test_clear_records_denied_for_user(auth_client, sample_csv):
    data = {"file": (io.BytesIO(sample_csv), "data.csv")}
    auth_client.post("/upload", data=data, content_type="multipart/form-data")
    resp = auth_client.post("/clear", follow_redirects=True)
    assert resp.status_code == 200
    assert b"access denied" in resp.data.lower()
