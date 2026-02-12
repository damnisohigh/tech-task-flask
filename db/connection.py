import logging

import pandas as pd
from flask import g, current_app

logger = logging.getLogger(__name__)

_TEXT_HINT_COLUMNS = {
    "advertiser", "brand", "start", "end", "format", "platform",
    "name", "date", "type", "category", "description", "status",
}


def _get_db_path():
    try:
        return current_app.config["DATABASE"]
    except RuntimeError:
        import os
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.db")


def _get_template_path():
    try:
        return current_app.config["TEMPLATE_PATH"]
    except RuntimeError:
        import os
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "template.csv")


def get_db():
    import sqlite3
    if "db" not in g:
        g.db = sqlite3.connect(_get_db_path())
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_template_columns():
    df = pd.read_csv(_get_template_path(), nrows=0)
    return [c.strip().lower() for c in df.columns]


def get_numeric_columns():
    df = pd.read_csv(_get_template_path())
    df.columns = [c.strip().lower() for c in df.columns]
    if len(df) == 0:
        return [c for c in df.columns if c not in _TEXT_HINT_COLUMNS]
    numeric = []
    for c in df.columns:
        converted = pd.to_numeric(df[c], errors="coerce")
        if converted.notna().sum() > len(df) * 0.5:
            numeric.append(c)
    return numeric


def get_text_columns():
    all_cols = get_template_columns()
    num_cols = set(get_numeric_columns())
    return [c for c in all_cols if c not in num_cols]


def _col_type(col_name):
    return "REAL" if col_name in get_numeric_columns() else "TEXT"


def init_db():
    db = get_db()

    # Users
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        );
    """)

    # Upload logs
    db.execute("""
        CREATE TABLE IF NOT EXISTS upload_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            filename TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            status TEXT NOT NULL,
            error_type TEXT
        );
    """)

    # Records
    columns = get_template_columns()
    col_defs = ",\n    ".join(
        f'"{col}" {_col_type(col)}' for col in columns
    )
    db.execute(f"""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "year" INTEGER,
            {col_defs}
        );
    """)

    db.commit()
    logger.info("Database initialized.")
