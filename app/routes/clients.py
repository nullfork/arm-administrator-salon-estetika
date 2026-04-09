from datetime import date

from sqlalchemy import or_
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required

from app.extensions import db
from app.models import Client

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")


def parse_birth_date(value: str):
    value = (value or "").strip()
    if not value:
        return None, None

    try:
        return date.fromisoformat(value), None
    except ValueError:
        return None, "Некорректный формат даты рождения. Используйте встроенный выбор даты."


@clients_bp.route("/")
@login_required
def list_clients():
    search_query = request.args.get("q", "").strip()

    query = Client.query

    if search_query:
        query = query.filter(
            or_(
                Client.full_name.ilike(f"%{search_query}%"),
                Client.phone.ilike(f"%{search_query}%")
            )
        )

    clients = query.order_by(Client.full_name.asc()).all()

    return render_template(
        "clients/list.html",
        clients=clients,
        search_query=search_query
    )


@clients_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_client():
    if request.method == "POST":
        form_data = {
            "full_name": request.form.get("full_name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "email": request.form.get("email", "").strip(),
            "birth_date": request.form.get("birth_date", "").strip(),
            "notes": request.form.get("notes", "").strip(),
        }

        if not form_data["full_name"] or not form_data["phone"]:
            flash("Поля 'ФИО' и 'Телефон' обязательны.", "danger")
            return render_template("clients/form.html", client=None, form_data=form_data)

        birth_date, birth_date_error = parse_birth_date(form_data["birth_date"])
        if birth_date_error:
            flash(birth_date_error, "danger")
            return render_template("clients/form.html", client=None, form_data=form_data)

        existing_client = Client.query.filter_by(phone=form_data["phone"]).first()
        if existing_client:
            flash("Клиент с таким номером телефона уже существует.", "danger")
            return render_template("clients/form.html", client=None, form_data=form_data)

        client = Client(
            full_name=form_data["full_name"],
            phone=form_data["phone"],
            email=form_data["email"] or None,
            birth_date=birth_date,
            notes=form_data["notes"] or None,
        )

        db.session.add(client)
        db.session.commit()

        flash("Клиент успешно добавлен.", "success")
        return redirect(url_for("clients.list_clients"))

    return render_template("clients/form.html", client=None, form_data=None)


@clients_bp.route("/<int:client_id>/edit", methods=["GET", "POST"])
@login_required
def edit_client(client_id):
    client = db.session.get(Client, client_id)
    if not client:
        abort(404)

    if request.method == "POST":
        form_data = {
            "full_name": request.form.get("full_name", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "email": request.form.get("email", "").strip(),
            "birth_date": request.form.get("birth_date", "").strip(),
            "notes": request.form.get("notes", "").strip(),
        }

        if not form_data["full_name"] or not form_data["phone"]:
            flash("Поля 'ФИО' и 'Телефон' обязательны.", "danger")
            return render_template("clients/form.html", client=client, form_data=form_data)

        birth_date, birth_date_error = parse_birth_date(form_data["birth_date"])
        if birth_date_error:
            flash(birth_date_error, "danger")
            return render_template("clients/form.html", client=client, form_data=form_data)

        existing_client = Client.query.filter(
            Client.phone == form_data["phone"],
            Client.id != client.id
        ).first()

        if existing_client:
            flash("Другой клиент с таким номером телефона уже существует.", "danger")
            return render_template("clients/form.html", client=client, form_data=form_data)

        client.full_name = form_data["full_name"]
        client.phone = form_data["phone"]
        client.email = form_data["email"] or None
        client.birth_date = birth_date
        client.notes = form_data["notes"] or None

        db.session.commit()

        flash("Данные клиента успешно обновлены.", "success")
        return redirect(url_for("clients.list_clients"))

    return render_template("clients/form.html", client=client, form_data=None)


@clients_bp.route("/<int:client_id>/delete", methods=["POST"])
@login_required
def delete_client(client_id):
    client = db.session.get(Client, client_id)
    if not client:
        abort(404)

    if client.appointments:
        flash(
            "Нельзя удалить клиента, у которого есть связанные записи. "
            "Сначала удалите или отмените записи.",
            "warning"
        )
        return redirect(url_for("clients.list_clients"))

    db.session.delete(client)
    db.session.commit()

    flash("Клиент успешно удалён.", "info")
    return redirect(url_for("clients.list_clients"))