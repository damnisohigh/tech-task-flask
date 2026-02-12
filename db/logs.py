import logging
from datetime import datetime

from db.connection import get_db

logger = logging.getLogger(__name__)


def add_upload_log(user_email, filename, status, error_type=None):
    db = get_db()
    db.execute(
        "INSERT INTO upload_logs (user_email, filename, upload_date, status, error_type) VALUES (?, ?, ?, ?, ?)",
        (user_email, filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status, error_type)
    )
    db.commit()


def get_all_upload_logs():
    db = get_db()
    rows = db.execute("SELECT * FROM upload_logs ORDER BY upload_date DESC").fetchall()
    return [dict(r) for r in rows]
