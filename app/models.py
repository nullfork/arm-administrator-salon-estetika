from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))

    users = db.relationship("User", back_populates="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"



class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    role = db.relationship("Role", back_populates="users")
    created_appointments = db.relationship(
        "Appointment",
        back_populates="creator",
        lazy=True,
        foreign_keys="Appointment.created_by"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"



class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120))
    birth_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    appointments = db.relationship("Appointment", back_populates="client", lazy=True)

    def __repr__(self):
        return f"<Client {self.full_name}>"



class Master(db.Model):
    __tablename__ = "masters"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    specialty = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    percent_rate = db.Column(db.Float, default=40.0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    appointments = db.relationship("Appointment", back_populates="master", lazy=True)

    def __repr__(self):
        return f"<Master {self.full_name}>"



class ServiceCategory(db.Model):
    __tablename__ = "service_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))

    services = db.relationship("Service", back_populates="category", lazy=True)

    def __repr__(self):
        return f"<ServiceCategory {self.name}>"



class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("service_categories.id"),
        nullable=False
    )
    name = db.Column(db.String(150), nullable=False, index=True)
    duration_min = db.Column(db.Integer, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    category = db.relationship("ServiceCategory", back_populates="services")
    appointments = db.relationship("Appointment", back_populates="service", lazy=True)

    def __repr__(self):
        return f"<Service {self.name}>"



class Appointment(db.Model):
    __tablename__ = "appointments"

    STATUS_PLANNED = "planned"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_NO_SHOW = "no_show"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    master_id = db.Column(db.Integer, db.ForeignKey("masters.id"), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default=STATUS_PLANNED, nullable=False, index=True)
    price_at_booking = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    cancel_reason = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    client = db.relationship("Client", back_populates="appointments")
    master = db.relationship("Master", back_populates="appointments")
    service = db.relationship("Service", back_populates="appointments")
    creator = db.relationship(
        "User",
        back_populates="created_appointments",
        foreign_keys=[created_by]
    )
    payment = db.relationship(
        "Payment",
        back_populates="appointment",
        uselist=False,
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.Index("idx_appointments_master_start", "master_id", "start_time"),
        db.Index("idx_appointments_status_start", "status", "start_time"),
    )

    def __repr__(self):
        return f"<Appointment {self.id}: {self.start_time}>"



class Payment(db.Model):
    __tablename__ = "payments"

    METHOD_CASH = "cash"
    METHOD_CARD = "card"
    METHOD_TRANSFER = "transfer"

    STATUS_PAID = "paid"
    STATUS_REFUNDED = "refunded"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(
        db.Integer,
        db.ForeignKey("appointments.id"),
        nullable=False,
        unique=True
    )
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False, default=METHOD_CARD)
    payment_status = db.Column(db.String(20), nullable=False, default=STATUS_PAID)
    receipt_no = db.Column(db.String(50), unique=True, nullable=False, index=True)
    paid_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    appointment = db.relationship("Appointment", back_populates="payment")

    def __repr__(self):
        return f"<Payment {self.receipt_no}>"