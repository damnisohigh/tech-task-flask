import os

from flask import Blueprint, render_template, request, flash, url_for, redirect, current_app
from flask_login import login_required, current_user

from routes.decorators import admin_required
from werkzeug.utils import secure_filename

from db import (
    insert_records, get_aggregate_records, clear_records,
    get_numeric_columns, add_upload_log,
)
from parser import parse_file

main_bp = Blueprint("main", __name__)


def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


@main_bp.route("/")
@login_required
def index():
    from db import get_template_columns, get_text_columns
    columns = get_template_columns()
    text_cols = set(get_text_columns())
    col_info = []
    for c in columns:
        if c in ("start", "end"):
            col_info.append({"name": c.title(), "type": "date"})
        elif c in text_cols:
            col_info.append({"name": c.title(), "type": "text"})
        else:
            col_info.append({"name": c.title(), "type": "number"})
    return render_template("main/upload.html", columns=col_info)


@main_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    if "file" not in request.files:
        flash("No file part", "error")
        return redirect(url_for("main.index"))

    file = request.files["file"]

    if file.filename == "":
        flash("No selected file", "error")
        return redirect(url_for("main.index"))

    if not allowed_file(file.filename):
        add_upload_log(current_user.email, file.filename, "error", "Unsupported format")
        flash("Only .csv, .xls, .xlsx files are allowed", "error")
        return redirect(url_for("main.index"))

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    df, error = parse_file(filepath)
    os.remove(filepath)

    if error:
        add_upload_log(current_user.email, file.filename, "error", error)
        flash(error, "error")
        return redirect(url_for("main.index"))

    try:
        inserted, skipped = insert_records(df)
    except Exception as e:
        add_upload_log(current_user.email, file.filename, "error", f"DB error: {e}")
        flash(f"Failed to save records: {e}", "error")
        return redirect(url_for("main.index"))

    add_upload_log(current_user.email, file.filename, "success",
                   f"Inserted: {inserted}, skipped: {skipped}" if skipped > 0 else None)
    flash(f"Records inserted: {inserted}" + (f", skipped: {skipped}" if skipped else ""), "success")
    return redirect(url_for("main.results"))


@main_bp.route("/results")
@login_required
def results():
    data = get_aggregate_records()
    numeric_columns = [c for c in get_numeric_columns() if c != "year"]
    return render_template("main/results.html", data=data, columns=numeric_columns)


@main_bp.route("/clear", methods=["POST"])
@admin_required
def clear():
    clear_records()
    flash("Records cleared", "success")
    return redirect(url_for("main.results"))
