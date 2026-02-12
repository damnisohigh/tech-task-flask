from flask import Blueprint, render_template, request, flash, url_for, redirect
from flask_login import login_user, logout_user, login_required, current_user

from db import create_user, get_user_by_email, verify_password
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user_dict = get_user_by_email(email)
        if user_dict and verify_password(user_dict["password_hash"], password):
            login_user(User(user_dict))
            flash(f"Welcome, {email}!", "success")
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)
            return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        password2 = request.form.get("password2", "")

        if not email or not password:
            flash("Please fill in all fields.", "error")
        elif password != password2:
            flash("Passwords do not match.", "error")
        elif len(password) < 4:
            flash("Password must be at least 4 characters.", "error")
        else:
            ok, err = create_user(email, password)
            if ok:
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for("auth.login"))
            else:
                flash(err, "error")

    return render_template("auth/register.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
