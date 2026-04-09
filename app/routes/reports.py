from datetime import date, datetime, time

from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func, case

from app.models import Appointment, Master, Payment, Service


reports_bp = Blueprint("reports", __name__, url_prefix="/reports")


def parse_date(value: str, default: date) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return default


def get_datetime_range(date_from: date, date_to: date):
    start_dt = datetime.combine(date_from, time.min)
    end_dt = datetime.combine(date_to, time.max)
    return start_dt, end_dt


@reports_bp.route("/")
@login_required
def index():
    today = date.today()
    first_day = today.replace(day=1)

    date_from = parse_date(request.args.get("date_from"), first_day)
    date_to = parse_date(request.args.get("date_to"), today)
    selected_date = parse_date(request.args.get("selected_date"), today)

    start_dt, end_dt = get_datetime_range(date_from, date_to)
    day_start, day_end = get_datetime_range(selected_date, selected_date)

    revenue_rows = (
        Payment.query
        .join(Appointment, Payment.appointment_id == Appointment.id)
        .join(Service, Appointment.service_id == Service.id)
        .with_entities(
            Service.name.label("service_name"),
            func.count(Payment.id).label("payments_count"),
            func.sum(Payment.amount).label("total_amount"),
        )
        .filter(Payment.paid_at >= start_dt, Payment.paid_at <= end_dt)
        .group_by(Service.name)
        .order_by(func.sum(Payment.amount).desc())
        .all()
    )

    masters_rows = (
        Payment.query
        .join(Appointment, Payment.appointment_id == Appointment.id)
        .join(Master, Appointment.master_id == Master.id)
        .with_entities(
            Master.full_name.label("master_name"),
            func.count(Payment.id).label("payments_count"),
            func.sum(Payment.amount).label("total_amount"),
            func.avg(Payment.amount).label("avg_amount"),
        )
        .filter(Payment.paid_at >= start_dt, Payment.paid_at <= end_dt)
        .group_by(Master.full_name)
        .order_by(func.sum(Payment.amount).desc())
        .all()
    )

    services_rows = (
        Appointment.query
        .join(Service, Appointment.service_id == Service.id)
        .with_entities(
            Service.name.label("service_name"),
            func.count(Appointment.id).label("appointments_count"),
            func.sum(
                case(
                    (Appointment.status == Appointment.STATUS_COMPLETED, 1),
                    else_=0
                )
            ).label("completed_count"),
        )
        .filter(Appointment.start_time >= start_dt, Appointment.start_time <= end_dt)
        .group_by(Service.name)
        .order_by(func.count(Appointment.id).desc())
        .all()
    )

    daily_rows = (
        Appointment.query
        .filter(Appointment.start_time >= day_start, Appointment.start_time <= day_end)
        .order_by(Appointment.start_time.asc())
        .all()
    )

    total_revenue = sum(float(row.total_amount or 0) for row in revenue_rows)
    total_payments = sum(int(row.payments_count or 0) for row in revenue_rows)
    total_daily_appointments = len(daily_rows)

    return render_template(
        "reports/index.html",
        date_from=date_from.isoformat(),
        date_to=date_to.isoformat(),
        selected_date=selected_date.isoformat(),
        revenue_rows=revenue_rows,
        masters_rows=masters_rows,
        services_rows=services_rows,
        daily_rows=daily_rows,
        total_revenue=total_revenue,
        total_payments=total_payments,
        total_daily_appointments=total_daily_appointments,
    )