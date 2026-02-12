import logging
import sqlite3
from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from db.connection import get_db

logger = logging.getLogger(__name__)


def create_user(email, password, role="user"):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (email, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (email, generate_password_hash(password, method="pbkdf2:sha256"), role, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        db.commit()
        return True, None
    except sqlite3.IntegrityError:
        return False, "A user with this email already exists."


def get_user_by_email(email):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id):
    db = get_db()
    row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


def verify_password(stored_hash, password):
    return check_password_hash(stored_hash, password)


def get_all_users():
    db = get_db()
    rows = db.execute("SELECT email, role, created_at FROM users ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def create_default_admin():
    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE role = 'admin'").fetchone()
    if not existing:
        db.execute(
            "INSERT INTO users (email, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ("admin@admin.com", generate_password_hash("admin123", method="pbkdf2:sha256"), "admin", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        db.commit()
        logger.info("Default admin created: admin@admin.com / admin123")
