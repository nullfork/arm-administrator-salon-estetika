from sqlalchemy import or_
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required

from app.extensions import db
from app.models import Service, ServiceCategory

services_bp = Blueprint("services", __name__, url_prefix="/services")


@services_bp.route("/")
@login_required
def list_services():
    search_query = request.args.get("q", "").strip()

    query = Service.query.join(ServiceCategory)

    if search_query:
        query = query.filter(
            or_(
                Service.name.ilike(f"%{search_query}%"),
                ServiceCategory.name.ilike(f"%{search_query}%")
            )
        )

    services = query.order_by(Service.name.asc()).all()

    return render_template(
        "services/list.html",
        services=services,
        search_query=search_query
    )


@services_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_service():
    categories = ServiceCategory.query.order_by(ServiceCategory.name.asc()).all()

    if request.method == "POST":
        category_id = request.form.get("category_id", "").strip()
        name = request.form.get("name", "").strip()
        duration_min = request.form.get("duration_min", "").strip()
        base_price = request.form.get("base_price", "").strip()
        description = request.form.get("description", "").strip() or None
        is_active = request.form.get("is_active") == "on"

        if not category_id or not name or not duration_min or not base_price:
            flash("Поля 'Категория', 'Название', 'Длительность' и 'Цена' обязательны.", "danger")
            return render_template("services/form.html", service=None, categories=categories)

        try:
            category_id_value = int(category_id)
            duration_min_value = int(duration_min)
            base_price_value = float(base_price)
        except ValueError:
            flash("Длительность должна быть целым числом, а цена — числом.", "danger")
            return render_template("services/form.html", service=None, categories=categories)

        category = db.session.get(ServiceCategory, category_id_value)
        if not category:
            flash("Выбранная категория не найдена.", "danger")
            return render_template("services/form.html", service=None, categories=categories)

        service = Service(
            category_id=category_id_value,
            name=name,
            duration_min=duration_min_value,
            base_price=base_price_value,
            description=description,
            is_active=is_active
        )

        db.session.add(service)
        db.session.commit()

        flash("Услуга успешно добавлена.", "success")
        return redirect(url_for("services.list_services"))

    return render_template("services/form.html", service=None, categories=categories)


@services_bp.route("/<int:service_id>/edit", methods=["GET", "POST"])
@login_required
def edit_service(service_id):
    service = db.session.get(Service, service_id)
    if not service:
        abort(404)

    categories = ServiceCategory.query.order_by(ServiceCategory.name.asc()).all()

    if request.method == "POST":
        category_id = request.form.get("category_id", "").strip()
        name = request.form.get("name", "").strip()
        duration_min = request.form.get("duration_min", "").strip()
        base_price = request.form.get("base_price", "").strip()
        description = request.form.get("description", "").strip() or None
        is_active = request.form.get("is_active") == "on"

        if not category_id or not name or not duration_min or not base_price:
            flash("Поля 'Категория', 'Название', 'Длительность' и 'Цена' обязательны.", "danger")
            return render_template("services/form.html", service=service, categories=categories)

        try:
            category_id_value = int(category_id)
            duration_min_value = int(duration_min)
            base_price_value = float(base_price)
        except ValueError:
            flash("Длительность должна быть целым числом, а цена — числом.", "danger")
            return render_template("services/form.html", service=service, categories=categories)

        category = db.session.get(ServiceCategory, category_id_value)
        if not category:
            flash("Выбранная категория не найдена.", "danger")
            return render_template("services/form.html", service=service, categories=categories)

        service.category_id = category_id_value
        service.name = name
        service.duration_min = duration_min_value
        service.base_price = base_price_value
        service.description = description
        service.is_active = is_active

        db.session.commit()

        flash("Данные услуги успешно обновлены.", "success")
        return redirect(url_for("services.list_services"))

    return render_template("services/form.html", service=service, categories=categories)


@services_bp.route("/<int:service_id>/delete", methods=["POST"])
@login_required
def delete_service(service_id):
    service = db.session.get(Service, service_id)
    if not service:
        abort(404)

    if service.appointments:
        flash(
            "Нельзя удалить услугу, у которой есть связанные записи. "
            "Сначала удалите или отмените записи.",
            "warning"
        )
        return redirect(url_for("services.list_services"))

    db.session.delete(service)
    db.session.commit()

    flash("Услуга успешно удалена.", "info")
    return redirect(url_for("services.list_services"))