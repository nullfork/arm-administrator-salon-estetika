from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required

from app.extensions import db
from app.models import Appointment, Payment


payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


def generate_receipt_no() -> str:
    return f"RCPT-{datetime.now().strftime('%Y%m%d%H%M%S')}"


@payments_bp.route("/create/<int:appointment_id>", methods=["GET", "POST"])
@login_required
def create_payment(appointment_id):
    appointment = db.session.get(Appointment, appointment_id)
    if not appointment:
        abort(404)

    if appointment.status == Appointment.STATUS_CANCELLED:
        flash("Нельзя оформить оплату для отменённой записи.", "warning")
        return redirect(url_for("appointments.list_appointments", date=appointment.start_time.date().isoformat()))

    if appointment.payment:
        flash("Оплата по этой записи уже оформлена.", "info")
        return redirect(url_for("payments.receipt", payment_id=appointment.payment.id))

    if request.method == "POST":
        amount_raw = request.form.get("amount", "").strip()
        payment_method = request.form.get("payment_method", "").strip()

        if not amount_raw or not payment_method:
            flash("Необходимо указать сумму и способ оплаты.", "danger")
            return render_template(
                "payments/form.html",
                appointment=appointment,
                payment_methods=[
                    Payment.METHOD_CASH,
                    Payment.METHOD_CARD,
                    Payment.METHOD_TRANSFER,
                ],
            )

        try:
            amount = float(amount_raw)
        except ValueError:
            flash("Сумма оплаты должна быть числом.", "danger")
            return render_template(
                "payments/form.html",
                appointment=appointment,
                payment_methods=[
                    Payment.METHOD_CASH,
                    Payment.METHOD_CARD,
                    Payment.METHOD_TRANSFER,
                ],
            )

        if amount <= 0:
            flash("Сумма оплаты должна быть больше нуля.", "danger")
            return render_template(
                "payments/form.html",
                appointment=appointment,
                payment_methods=[
                    Payment.METHOD_CASH,
                    Payment.METHOD_CARD,
                    Payment.METHOD_TRANSFER,
                ],
            )

        payment = Payment(
            appointment_id=appointment.id,
            amount=amount,
            payment_method=payment_method,
            payment_status=Payment.STATUS_PAID,
            receipt_no=generate_receipt_no(),
        )

        appointment.status = Appointment.STATUS_COMPLETED

        db.session.add(payment)
        db.session.commit()

        flash("Оплата успешно проведена.", "success")
        return redirect(url_for("payments.receipt", payment_id=payment.id))

    return render_template(
        "payments/form.html",
        appointment=appointment,
        payment_methods=[
            Payment.METHOD_CASH,
            Payment.METHOD_CARD,
            Payment.METHOD_TRANSFER,
        ],
    )


@payments_bp.route("/receipt/<int:payment_id>")
@login_required
def receipt(payment_id):
    payment = db.session.get(Payment, payment_id)
    if not payment:
        abort(404)

    return render_template("payments/receipt.html", payment=payment)