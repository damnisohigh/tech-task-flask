import logging
from datetime import datetime, timedelta

import pandas as pd

from db.connection import get_db, get_template_columns, get_numeric_columns

logger = logging.getLogger(__name__)


def extract_year(value):
    """
    Extracts year from a date value. Supports:
      - None / NaN -> None
      - datetime -> .year
      - int/float (Excel serial number) -> conversion
      - str ('31.01.2021', '2021-01-31') -> parsing
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    if isinstance(value, datetime):
        return value.year

    if isinstance(value, (int, float)):
        try:
            num = int(value)
            if 1 < num < 100000:
                dt = datetime(1899, 12, 30) + timedelta(days=num)
                if 1900 <= dt.year <= 2100:
                    return dt.year
        except (ValueError, OverflowError):
            pass
        return None

    if isinstance(value, str):
        for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(value.strip(), fmt).year
            except ValueError:
                continue
        try:
            return pd.to_datetime(value, dayfirst=True).year
        except Exception:
            pass

    return None


def extract_year_from_row(row):
    year = extract_year(row.get("start"))
    if year is None:
        year = extract_year(row.get("end"))
    return year


def insert_records(df):
    columns = get_template_columns()
    all_cols = ["year"] + columns
    placeholders = ", ".join(["?"] * len(all_cols))
    col_names = ", ".join(f'"{c}"' for c in all_cols)
    sql = f"INSERT INTO records ({col_names}) VALUES ({placeholders})"

    db = get_db()
    inserted = 0
    skipped = 0

    try:
        for _, row in df.iterrows():
            year = extract_year_from_row(row)
            if year is None:
                skipped += 1
                continue

            values = [year] + [row.get(col) for col in columns]
            clean = []
            for v in values:
                if isinstance(v, float) and pd.isna(v):
                    clean.append(None)
                elif hasattr(v, 'strftime'):
                    clean.append(v.strftime('%Y-%m-%d'))
                elif isinstance(v, pd.Timestamp):
                    clean.append(str(v.date()))
                else:
                    clean.append(v)
            values = clean
            db.execute(sql, values)
            inserted += 1

        db.commit()
        logger.info("Database: inserted %d, skipped %d (no valid date).", inserted, skipped)
        return inserted, skipped
    except Exception:
        db.rollback()
        raise


def clear_records():
    db = get_db()
    db.execute("DELETE FROM records")
    db.commit()
    logger.info("Database cleared.")


def get_aggregate_records():
    num_cols = get_numeric_columns()
    if not num_cols:
        return []

    sums = ", ".join(f'SUM("{c}") AS "{c}"' for c in num_cols)
    sql = f'SELECT "year", {sums} FROM records GROUP BY "year" ORDER BY "year"'

    db = get_db()
    cursor = db.execute(sql)
    rows = cursor.fetchall()

    result = []
    for row in rows:
        d = {"year": row["year"]}
        for c in num_cols:
            d[c] = row[c] if row[c] is not None else 0
        result.append(d)
    return result


def get_all_records():
    columns = ["year"] + get_template_columns()
    col_names = ", ".join(f'"{c}"' for c in columns)
    sql = f"SELECT {col_names} FROM records ORDER BY year"

    db = get_db()
    rows = db.execute(sql).fetchall()
    return [dict(r) for r in rows], columns
