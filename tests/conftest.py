import os
import shutil

import pytest

from config import TestConfig
from app import create_app
from db import init_db, create_default_admin, create_user


@pytest.fixture()
def app():
    cfg = TestConfig()
    application = create_app(cfg)

    with application.app_context():
        init_db()
        create_default_admin()

    yield application

    # cleanup
    os.close(cfg._db_fd)
    os.unlink(cfg.DATABASE)
    shutil.rmtree(cfg._upload_dir, ignore_errors=True)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_client(app):
    with app.app_context():
        create_user("user@test.com", "pass1234", role="user")

    c = app.test_client()
    c.post("/login", data={"email": "user@test.com", "password": "pass1234"})
    return c


@pytest.fixture()
def admin_client(app):
    c = app.test_client()
    c.post("/login", data={"email": "admin@admin.com", "password": "admin123"})
    return c


@pytest.fixture()
def sample_csv():
    return (
        b"Advertiser,Brand,Start,End,Format,Platform,Impr\n"
        b"Acme,Widget,01.01.2023,31.01.2023,Banner,Web,1000\n"
        b"Acme,Widget,01.06.2024,30.06.2024,Video,Mobile,2000\n"
    )
