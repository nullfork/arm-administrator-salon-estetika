from sqlalchemy import or_
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required

from app.extensions import db
from app.models import Master

masters_bp = Blueprint("masters", __name__, url_prefix="/masters")


@masters_bp.route("/")
@login_required
def list_masters():
    search_query = request.args.get("q", "").strip()

    query = Master.query

    if search_query:
        query = query.filter(
            or_(
                Master.full_name.ilike(f"%{search_query}%"),
                Master.specialty.ilike(f"%{search_query}%"),
                Master.phone.ilike(f"%{search_query}%")
            )
        )

    masters = query.order_by(Master.full_name.asc()).all()

    return render_template(
        "masters/list.html",
        masters=masters,
        search_query=search_query
    )


@masters_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_master():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        specialty = request.form.get("specialty", "").strip()
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip() or None
        percent_rate = request.form.get("percent_rate", "").strip()
        is_active = request.form.get("is_active") == "on"

        if not full_name or not specialty:
            flash("Поля 'ФИО' и 'Специализация' обязательны.", "danger")
            return render_template("masters/form.html", master=None)

        try:
            percent_rate_value = float(percent_rate) if percent_rate else 40.0
        except ValueError:
            flash("Процент мастера должен быть числом.", "danger")
            return render_template("masters/form.html", master=None)

        master = Master(
            full_name=full_name,
            specialty=specialty,
            phone=phone,
            email=email,
            percent_rate=percent_rate_value,
            is_active=is_active
        )

        db.session.add(master)
        db.session.commit()

        flash("Мастер успешно добавлен.", "success")
        return redirect(url_for("masters.list_masters"))

    return render_template("masters/form.html", master=None)


@masters_bp.route("/<int:master_id>/edit", methods=["GET", "POST"])
@login_required
def edit_master(master_id):
    master = db.session.get(Master, master_id)
    if not master:
        abort(404)

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        specialty = request.form.get("specialty", "").strip()
        phone = request.form.get("phone", "").strip() or None
        email = request.form.get("email", "").strip() or None
        percent_rate = request.form.get("percent_rate", "").strip()
        is_active = request.form.get("is_active") == "on"

        if not full_name or not specialty:
            flash("Поля 'ФИО' и 'Специализация' обязательны.", "danger")
            return render_template("masters/form.html", master=master)

        try:
            percent_rate_value = float(percent_rate) if percent_rate else 40.0
        except ValueError:
            flash("Процент мастера должен быть числом.", "danger")
            return render_template("masters/form.html", master=master)

        master.full_name = full_name
        master.specialty = specialty
        master.phone = phone
        master.email = email
        master.percent_rate = percent_rate_value
        master.is_active = is_active

        db.session.commit()

        flash("Данные мастера успешно обновлены.", "success")
        return redirect(url_for("masters.list_masters"))

    return render_template("masters/form.html", master=master)


@masters_bp.route("/<int:master_id>/delete", methods=["POST"])
@login_required
def delete_master(master_id):
    master = db.session.get(Master, master_id)
    if not master:
        abort(404)

    if master.appointments:
        flash(
            "Нельзя удалить мастера, у которого есть связанные записи. "
            "Сначала удалите или отмените записи.",
            "warning"
        )
        return redirect(url_for("masters.list_masters"))

    db.session.delete(master)
    db.session.commit()

    flash("Мастер успешно удалён.", "info")
    return redirect(url_for("masters.list_masters"))