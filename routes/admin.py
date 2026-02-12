from flask import Blueprint, render_template

from db import get_all_upload_logs, get_all_users, get_all_records
from routes.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@admin_required
def admin_panel():
    return render_template("admin/panel.html")


@admin_bp.route("/admin/logs")
@admin_required
def admin_logs():
    logs = get_all_upload_logs()
    return render_template("admin/logs.html", logs=logs)


@admin_bp.route("/admin/users")
@admin_required
def admin_users():
    users = get_all_users()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/admin/data")
@admin_required
def admin_data():
    records, columns = get_all_records()
    return render_template("admin/data.html", records=records, columns=columns)
