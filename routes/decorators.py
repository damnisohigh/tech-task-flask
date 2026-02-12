from functools import wraps

from flask import flash, url_for, redirect
from flask_login import login_required, current_user


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != "admin":
            flash("Access denied. Administrator privileges required.", "error")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated
