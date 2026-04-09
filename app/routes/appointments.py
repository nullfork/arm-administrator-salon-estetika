from datetime import datetime, date, time, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.extensions import db
from app.models import Appointment, Client, Master, Service


appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


def parse_datetime_local(value: str):
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M")
    except (TypeError, ValueError):
        return None


def get_day_range(selected_date: date):
    start_dt = datetime.combine(selected_date, time.min)
    end_dt = datetime.combine(selected_date, time.max)
    return start_dt, end_dt


def has_time_conflict(master_id: int, start_time: datetime, end_time: datetime, exclude_id: int | None = None):
    query = Appointment.query.filter(
        Appointment.master_id == master_id,
        Appointment.status != Appointment.STATUS_CANCELLED,
        Appointment.start_time < end_time,
        Appointment.end_time > start_time,
    )

    if exclude_id:
        query = query.filter(Appointment.id != exclude_id)

    return db.session.query(query.exists()).scalar()


def get_status_choices():
    return [
        Appointment.STATUS_PLANNED,
        Appointment.STATUS_CONFIRMED,
        Appointment.STATUS_COMPLETED,
        Appointment.STATUS_CANCELLED,
        Appointment.STATUS_NO_SHOW,
    ]


def build_list_redirect(selected_date: date):
    return redirect(url_for("appointments.list_appointments", date=selected_date.isoformat()))


@appointments_bp.route("/")
@login_required
def list_appointments():
    selected_date_str = request.args.get("date")
    selected_status = request.args.get("status", "").strip()
    selected_master = request.args.get("master_id", "").strip()
    search_query = request.args.get("q", "").strip()

    if selected_date_str:
        try:
            selected_date = date.fromisoformat(selected_date_str)
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()

    start_dt, end_dt = get_day_range(selected_date)

    query = (
        Appointment.query
        .join(Client)
        .join(Master)
        .join(Service)
        .filter(
            Appointment.start_time >= start_dt,
            Appointment.start_time <= end_dt
        )
    )

    if selected_status:
        query = query.filter(Appointment.status == selected_status)

    if selected_master:
        try:
            query = query.filter(Appointment.master_id == int(selected_master))
        except ValueError:
            pass

    if search_query:
        query = query.filter(
            or_(
                Client.full_name.ilike(f"%{search_query}%"),
                Client.phone.ilike(f"%{search_query}%"),
                Master.full_name.ilike(f"%{search_query}%"),
                Service.name.ilike(f"%{search_query}%"),
                Appointment.notes.ilike(f"%{search_query}%"),
            )
        )

    appointments = query.order_by(Appointment.start_time.asc()).all()
    masters = Master.query.order_by(Master.full_name.asc()).all()

    return render_template(
        "appointments/list.html",
        appointments=appointments,
        masters=masters,
        selected_date=selected_date.isoformat(),
        selected_status=selected_status,
        selected_master=selected_master,
        search_query=search_query,
        status_choices=get_status_choices(),
        status_labels=Appointment.STATUS_LABELS,
    )


@appointments_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_appointment():
    clients = Client.query.order_by(Client.full_name.asc()).all()
    masters = Master.query.filter_by(is_active=True).order_by(Master.full_name.asc()).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name.asc()).all()

    if request.method == "POST":
        client_id = request.form.get("client_id", "").strip()
        master_id = request.form.get("master_id", "").strip()
        service_id = request.form.get("service_id", "").strip()
        start_time_raw = request.form.get("start_time", "").strip()
        notes = request.form.get("notes", "").strip() or None

        if not client_id or not master_id or not service_id or not start_time_raw:
            flash("Все обязательные поля должны быть заполнены.", "danger")
            return render_template(
                "appointments/form.html",
                appointment=None,
                clients=clients,
                masters=masters,
                services=services,
                status_choices=get_status_choices(),
                status_labels=Appointment.STATUS_LABELS,
            )

        start_time = parse_datetime_local(start_time_raw)
        if not start_time:
            flash("Некорректный формат даты и времени.", "danger")
            return render_template(
                "appointments/form.html",
                appointment=None,
                clients=clients,
                masters=masters,
                services=services,
                status_choices=get_status_choices(),
                status_labels=Appointment.STATUS_LABELS,
            )

        client = db.session.get(Client, int(client_id))
        master = db.session.get(Master, int(master_id))
        service = db.session.get(Service, int(service_id))

        if not client or not master or not service:
            flash("Клиент, мастер или услуга не найдены.", "danger")
            return render_template(
                "appointments/form.html",
                appointment=None,
                clients=clients,
                masters=masters,
                services=services,
                status_choices=get_status_choices(),
                status_labels=Appointment.STATUS_LABELS,
            )

        end_time = start_time + timedelta(minutes=service.duration_min)

        if has_time_conflict(master.id, start_time, end_time):
            flash("У выбранного мастера уже есть запись на это время.", "danger")
            return render_template(
                "appointments/form.html",
                appointment=None,
                clients=clients,
                masters=masters,
                services=services,
                status_choices=get_status_choices(),
                status_labels=Appointment.STATUS_LABELS,
            )

        appointment = Appointment(
            client_id=client.id,
            master_id=master.id,
            service_id=service.id,
            start_time=start_time,
            end_time=end_time,
            status=Appointment.STATUS_PLANNED,
            price_at_booking=service.base_price,
            notes=notes,
            created_by=current_user.id,
        )

        db.session.add(appointment)
        db.session.commit()

        flash("Запись успешно создана.", "success")
        return build_list_redirect(start_time.date())

    return render_template(
        "appointments/form.html",
        appointment=None,
        clients=clients,
        masters=masters,
        services=services,
        status_choices=get_status_choices(),
        status_labels=Appointment.STATUS_LABELS,
    )


@appointments_bp.route("/<int:appointment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        abort(404)

    clients = Client.query.order_by(Client.full_name.asc()).all()
    masters = Master.query.filter_by(is_active=True).order_by(Master.full_name.asc()).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.name.asc()).all()

    if request.method == "POST":
        client_id = request.form.get("client_id", "").strip()
        master_id = request.form.get("master_id", "").strip()
        service_id = request.form.get("service_id", "").strip()
        start_time_raw = request.form.get("start_time", "").strip()
        status = request.form.get("status", "").strip()
        notes = request.form.get("notes", "").strip() or None
        cancel_reason = request.form.get("cancel_reason", "").strip() or None

        if not client_id or not master_id or not service_id or not start_time_raw or not status:
            flash("Все обязательные поля должны быть заполнены.", "danger")
            return render_template(
                "appointments/form.html",
                appointment=appointment,
                clients=clients,
                masters=masters,
                services=services,
                status_choices=get_status_choices(),
                status_labels=Appointment.STATUS_LABELS,
            )

        start_time = parse_datetime_local(start_time_raw)
        if not start_time:
            flash("Некорректный формат даты и времени.", "danger")
            return render_template(
                "appointments/form.html",
                appointment=appointment,
                clients=clients,
                masters=masters,
                services=services,
                status_choices=get_status_choices(),
                status_labels=Appointment.STATUS_LABELS,
            )

        client = db.session.get(Client, int(client_id))
        master = db.session.get(Master, int(master_id))
        service = db.session.get(Service, int(service_id))

        if not client or not master or not service:
            flash("Клиент, мастер или услуга не найдены.", "danger")
            return render_template(
                "appointments/form.html",
                appointment=appointment,
                clients=clients,
                masters=masters,
                services=services,
                status_choices=get_status_choices(),
                status_labels=Appointment.STATUS_LABELS,
            )

        end_time = start_time + timedelta(minutes=service.duration_min)

        if status != Appointment.STATUS_CANCELLED and has_time_conflict(master.id, start_time, end_time, exclude_id=appointment.id):
            flash("У выбранного мастера уже есть запись на это время.", "danger")
            return render_template(
                "appointments/form.html",
                appointment=appointment,
                clients=clients,
                masters=masters,
                services=services,
                status_choices=get_status_choices(),
                status_labels=Appointment.STATUS_LABELS,
            )

        appointment.client_id = client.id
        appointment.master_id = master.id
        appointment.service_id = service.id
        appointment.start_time = start_time
        appointment.end_time = end_time
        appointment.status = status
        appointment.notes = notes
        appointment.cancel_reason = cancel_reason if status == Appointment.STATUS_CANCELLED else None
        appointment.price_at_booking = service.base_price

        db.session.commit()

        flash("Запись успешно обновлена.", "success")
        return build_list_redirect(start_time.date())

    return render_template(
        "appointments/form.html",
        appointment=appointment,
        clients=clients,
        masters=masters,
        services=services,
        status_choices=get_status_choices(),
        status_labels=Appointment.STATUS_LABELS,
    )


@appointments_bp.route("/<int:appointment_id>/cancel", methods=["POST"])
@login_required
def cancel_appointment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        abort(404)

    reason = request.form.get("cancel_reason", "").strip() or "Отменено пользователем"

    appointment.status = Appointment.STATUS_CANCELLED
    appointment.cancel_reason = reason

    db.session.commit()

    flash("Запись отменена.", "warning")
    return build_list_redirect(appointment.start_time.date())


@appointments_bp.route("/<int:appointment_id>/set-status/<string:new_status>", methods=["POST"])
@login_required
def set_status(appointment_id, new_status):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        abort(404)

    allowed_statuses = {
        Appointment.STATUS_PLANNED,
        Appointment.STATUS_CONFIRMED,
        Appointment.STATUS_COMPLETED,
        Appointment.STATUS_NO_SHOW,
    }

    if new_status not in allowed_statuses:
        abort(400)

    if appointment.status == Appointment.STATUS_CANCELLED:
        flash("Нельзя изменить статус отменённой записи.", "warning")
        return build_list_redirect(appointment.start_time.date())

    appointment.status = new_status

    if new_status != Appointment.STATUS_CANCELLED:
        appointment.cancel_reason = None

    db.session.commit()

    flash("Статус записи обновлён.", "success")
    return build_list_redirect(appointment.start_time.date())