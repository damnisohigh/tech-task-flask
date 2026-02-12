import os

from flask import Flask, url_for, redirect
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from config import Config
from db import get_user_by_id, init_db, create_default_admin, close_db
from models import User


def create_app(config=None):
    app = Flask(__name__)
    if config is None:
        app.config.from_object(Config)
    else:
        app.config.from_object(config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    CSRFProtect(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect(url_for("auth.login"))

    @login_manager.user_loader
    def load_user(user_id):
        user_dict = get_user_by_id(int(user_id))
        if user_dict:
            return User(user_dict)
        return None

    # Close DB connections on teardown
    app.teardown_appcontext(close_db)

    from routes import auth_bp, main_bp, admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        init_db()
        create_default_admin()
    app.run(debug=True, port=5000)
