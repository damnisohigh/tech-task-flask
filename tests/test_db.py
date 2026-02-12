import math
from datetime import datetime

import pandas as pd

from db import (
    extract_year,
    extract_year_from_row,
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_password,
    insert_records,
    get_aggregate_records,
    clear_records,
    get_all_records,
    add_upload_log,
    get_all_upload_logs,
    get_template_columns,
    get_numeric_columns,
)


def test_extract_year_string_dot(app):
    with app.app_context():
        assert extract_year("31.01.2021") == 2021


def test_extract_year_string_iso(app):
    with app.app_context():
        assert extract_year("2022-06-15") == 2022


def test_extract_year_datetime(app):
    with app.app_context():
        assert extract_year(datetime(2020, 3, 1)) == 2020


def test_extract_year_excel_serial(app):
    with app.app_context():
        # 44927 = 2023-01-01 in Excel serial
        assert extract_year(44927) == 2023


def test_extract_year_none(app):
    with app.app_context():
        assert extract_year(None) is None


def test_extract_year_nan(app):
    with app.app_context():
        assert extract_year(float("nan")) is None


def test_extract_year_from_row_start(app):
    with app.app_context():
        row = {"start": "01.01.2023", "end": "31.01.2023"}
        assert extract_year_from_row(row) == 2023


def test_extract_year_from_row_fallback_end(app):
    with app.app_context():
        row = {"start": None, "end": "15.06.2024"}
        assert extract_year_from_row(row) == 2024


def test_create_and_get_user(app):
    with app.app_context():
        ok, err = create_user("new@test.com", "secret")
        assert ok is True
        assert err is None

        user = get_user_by_email("new@test.com")
        assert user is not None
        assert user["email"] == "new@test.com"
        assert user["role"] == "user"


def test_create_user_duplicate(app):
    with app.app_context():
        create_user("dup@test.com", "pass")
        ok, err = create_user("dup@test.com", "pass2")
        assert ok is False
        assert "already exists" in err


def test_get_user_by_id(app):
    with app.app_context():
        create_user("byid@test.com", "pass")
        user = get_user_by_email("byid@test.com")
        fetched = get_user_by_id(user["id"])
        assert fetched["email"] == "byid@test.com"


def test_get_user_by_email_not_found(app):
    with app.app_context():
        assert get_user_by_email("nobody@test.com") is None


def test_verify_password_correct(app):
    with app.app_context():
        create_user("pw@test.com", "mypassword")
        user = get_user_by_email("pw@test.com")
        assert verify_password(user["password_hash"], "mypassword") is True


def test_verify_password_incorrect(app):
    with app.app_context():
        create_user("pw2@test.com", "mypassword")
        user = get_user_by_email("pw2@test.com")
        assert verify_password(user["password_hash"], "wrong") is False


def test_insert_and_aggregate(app):
    with app.app_context():
        df = pd.DataFrame({
            "advertiser": ["A", "B", "C"],
            "brand": ["X", "Y", "X"],
            "start": ["01.01.2023", "15.06.2023", "01.01.2024"],
            "end": ["31.01.2023", "30.06.2023", "31.01.2024"],
            "format": ["Banner", "Video", "Banner"],
            "platform": ["Web", "Mobile", "Web"],
            "impr": [100, 200, 300],
        })
        inserted, skipped = insert_records(df)
        assert inserted == 3
        assert skipped == 0

        agg = get_aggregate_records()
        years = {r["year"]: r for r in agg}
        assert years[2023]["impr"] == 300
        assert years[2024]["impr"] == 300


def test_clear_records(app):
    with app.app_context():
        df = pd.DataFrame({
            "advertiser": ["A"],
            "brand": ["X"],
            "start": ["01.01.2023"],
            "end": ["31.01.2023"],
            "format": ["Banner"],
            "platform": ["Web"],
            "impr": [100],
        })
        insert_records(df)
        clear_records()
        records, _ = get_all_records()
        assert len(records) == 0


def test_get_all_records(app):
    with app.app_context():
        df = pd.DataFrame({
            "advertiser": ["A", "B"],
            "brand": ["X", "Y"],
            "start": ["01.01.2023", "01.01.2024"],
            "end": ["31.01.2023", "31.01.2024"],
            "format": ["Banner", "Video"],
            "platform": ["Web", "Mobile"],
            "impr": [100, 200],
        })
        insert_records(df)
        records, columns = get_all_records()
        assert len(records) == 2
        assert "year" in columns


def test_upload_logs(app):
    with app.app_context():
        add_upload_log("user@test.com", "data.csv", "success")
        add_upload_log("user@test.com", "bad.csv", "error", "Missing columns")
        logs = get_all_upload_logs()
        assert len(logs) == 2
        assert logs[0]["status"] in ("success", "error")


def test_get_template_columns(app):
    with app.app_context():
        cols = get_template_columns()
        assert "advertiser" in cols
        assert "impr" in cols


def test_get_numeric_columns(app):
    with app.app_context():
        num = get_numeric_columns()
        assert isinstance(num, list)
