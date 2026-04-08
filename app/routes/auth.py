from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_next_url():
    next_url = request.args.get("next")
    if next_url and next_url.startswith("/"):
        return next_url
    return url_for("main.index")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.is_active and user.check_password(password):
            login_user(user)
            flash("Вы успешно вошли в систему.", "success")
            return redirect(get_next_url())

        flash("Неверный логин или пароль.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("auth.login"))