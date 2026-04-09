from datetime import date, datetime, time, timedelta

from app import create_app
from app.extensions import db
from app.models import (
    Role,
    User,
    Master,
    Client,
    ServiceCategory,
    Service,
    Appointment,
    Payment,
)


app = create_app()


def get_or_create(model, defaults=None, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if instance:
        return instance, False

    params = dict(kwargs)
    if defaults:
        params.update(defaults)

    instance = model(**params)
    db.session.add(instance)
    return instance, True


def seed_roles():
    roles_data = [
        {
            "name": "admin",
            "description": "Администратор салона",
        },
        {
            "name": "director",
            "description": "Директор салона",
        },
    ]

    for role_data in roles_data:
        get_or_create(Role, **role_data)


def seed_users():
    admin_role = Role.query.filter_by(name="admin").first()
    director_role = Role.query.filter_by(name="director").first()

    users_data = [
        {
            "username": "admin",
            "email": "admin@estetika.local",
            "full_name": "Администратор Эстетика",
            "role_id": admin_role.id,
            "password": "admin123",
        },
        {
            "username": "director",
            "email": "director@estetika.local",
            "full_name": "Директор Эстетика",
            "role_id": director_role.id,
            "password": "director123",
        },
    ]

    for user_data in users_data:
        password = user_data.pop("password")
        user = User.query.filter_by(username=user_data["username"]).first()

        if not user:
            user = User(**user_data)
            user.set_password(password)
            db.session.add(user)


def seed_masters():
    masters_data = [
        {
            "full_name": "Петрова Мария Сергеевна",
            "specialty": "Мастер маникюра",
            "phone": "+79000000011",
            "email": "petrova@estetika.local",
            "percent_rate": 40.0,
            "is_active": True,
        },
        {
            "full_name": "Иванов Сергей Андреевич",
            "specialty": "Парикмахер",
            "phone": "+79000000012",
            "email": "ivanov@estetika.local",
            "percent_rate": 45.0,
            "is_active": True,
        },
        {
            "full_name": "Соколова Анна Викторовна",
            "specialty": "Косметолог",
            "phone": "+79000000013",
            "email": "sokolova@estetika.local",
            "percent_rate": 50.0,
            "is_active": True,
        },
        {
            "full_name": "Морозова Елена Игоревна",
            "specialty": "Бровист",
            "phone": "+79000000014",
            "email": "morozova@estetika.local",
            "percent_rate": 35.0,
            "is_active": True,
        },
    ]

    for master_data in masters_data:
        get_or_create(Master, full_name=master_data["full_name"], defaults=master_data)


def seed_categories_and_services():
    categories_data = [
        {
            "name": "Парикмахерские услуги",
            "description": "Стрижки, укладки, окрашивание",
        },
        {
            "name": "Ногтевой сервис",
            "description": "Маникюр, педикюр, покрытие",
        },
        {
            "name": "Косметология",
            "description": "Уход за лицом и кожей",
        },
        {
            "name": "Брови и ресницы",
            "description": "Оформление бровей и ресниц",
        },
    ]

    for category_data in categories_data:
        get_or_create(
            ServiceCategory,
            name=category_data["name"],
            defaults=category_data,
        )

    categories = {
        category.name: category
        for category in ServiceCategory.query.all()
    }

    services_data = [
        {
            "category_id": categories["Парикмахерские услуги"].id,
            "name": "Стрижка женская",
            "duration_min": 60,
            "base_price": 1800,
            "description": "Женская стрижка с укладкой",
            "is_active": True,
        },
        {
            "category_id": categories["Парикмахерские услуги"].id,
            "name": "Окрашивание волос",
            "duration_min": 120,
            "base_price": 3500,
            "description": "Окрашивание волос средней длины",
            "is_active": True,
        },
        {
            "category_id": categories["Ногтевой сервис"].id,
            "name": "Маникюр классический",
            "duration_min": 60,
            "base_price": 1500,
            "description": "Классический маникюр без покрытия",
            "is_active": True,
        },
        {
            "category_id": categories["Ногтевой сервис"].id,
            "name": "Маникюр с гель-лаком",
            "duration_min": 90,
            "base_price": 2200,
            "description": "Маникюр с покрытием гель-лак",
            "is_active": True,
        },
        {
            "category_id": categories["Косметология"].id,
            "name": "Чистка лица",
            "duration_min": 90,
            "base_price": 2800,
            "description": "Комплексная чистка лица",
            "is_active": True,
        },
        {
            "category_id": categories["Косметология"].id,
            "name": "Уходовая процедура для лица",
            "duration_min": 60,
            "base_price": 2500,
            "description": "Базовая уходовая процедура",
            "is_active": True,
        },
        {
            "category_id": categories["Брови и ресницы"].id,
            "name": "Оформление бровей",
            "duration_min": 45,
            "base_price": 1200,
            "description": "Коррекция и окрашивание бровей",
            "is_active": True,
        },
    ]

    for service_data in services_data:
        get_or_create(
            Service,
            name=service_data["name"],
            defaults=service_data,
        )


def seed_clients():
    clients_data = [
        {
            "full_name": "Иванова Анна Петровна",
            "phone": "+79000000101",
            "email": "anna@example.com",
            "birth_date": date(1995, 5, 14),
            "notes": "Предпочитает вечернее время записи",
        },
        {
            "full_name": "Смирнова Ольга Викторовна",
            "phone": "+79000000102",
            "email": "olga@example.com",
            "birth_date": date(1990, 8, 22),
            "notes": "Постоянный клиент ногтевого сервиса",
        },
        {
            "full_name": "Кузнецова Марина Сергеевна",
            "phone": "+79000000103",
            "email": "marina@example.com",
            "birth_date": date(1988, 11, 3),
            "notes": "Записывается на косметологические услуги",
        },
        {
            "full_name": "Павлова Екатерина Андреевна",
            "phone": "+79000000104",
            "email": "ekaterina@example.com",
            "birth_date": date(1998, 1, 17),
            "notes": "Просит напоминать о визите заранее",
        },
        {
            "full_name": "Соколова Дарья Игоревна",
            "phone": "+79000000105",
            "email": "darya@example.com",
            "birth_date": date(1993, 7, 9),
            "notes": "Предпочитает мастера Иванова С. А.",
        },
        {
            "full_name": "Романова Юлия Алексеевна",
            "phone": "+79000000106",
            "email": "yulia@example.com",
            "birth_date": date(1997, 3, 27),
            "notes": "Часто записывается онлайн",
        },
        {
            "full_name": "Федорова Наталья Игоревна",
            "phone": "+79000000107",
            "email": "natalya@example.com",
            "birth_date": date(1985, 12, 1),
            "notes": "Любит утренние визиты",
        },
    ]

    for client_data in clients_data:
        get_or_create(
            Client,
            phone=client_data["phone"],
            defaults=client_data,
        )


def reset_demo_schedule():
    Payment.query.delete()
    Appointment.query.delete()
    db.session.commit()


def dt_for(day_offset: int, hour: int, minute: int = 0) -> datetime:
    target_date = date.today() + timedelta(days=day_offset)
    return datetime.combine(target_date, time(hour=hour, minute=minute))


def create_demo_appointments():
    admin_user = User.query.filter_by(username="admin").first()

    clients = {client.full_name: client for client in Client.query.all()}
    masters = {master.full_name: master for master in Master.query.all()}
    services = {service.name: service for service in Service.query.all()}

    appointments_data = [
        {
            "client": "Иванова Анна Петровна",
            "master": "Иванов Сергей Андреевич",
            "service": "Стрижка женская",
            "start_time": dt_for(0, 10, 0),
            "status": Appointment.STATUS_CONFIRMED,
            "notes": "Клиент просил напомнить за 2 часа до визита",
            "cancel_reason": None,
            "payment": None,
        },
        {
            "client": "Смирнова Ольга Викторовна",
            "master": "Петрова Мария Сергеевна",
            "service": "Маникюр с гель-лаком",
            "start_time": dt_for(0, 12, 0),
            "status": Appointment.STATUS_PLANNED,
            "notes": "Предпочитает нюдовые оттенки покрытия",
            "cancel_reason": None,
            "payment": None,
        },
        {
            "client": "Кузнецова Марина Сергеевна",
            "master": "Соколова Анна Викторовна",
            "service": "Чистка лица",
            "start_time": dt_for(-1, 15, 0),
            "status": Appointment.STATUS_COMPLETED,
            "notes": "Повторный визит через 1 месяц",
            "cancel_reason": None,
            "payment": {
                "amount": 2800.0,
                "method": Payment.METHOD_CARD,
                "receipt_no": "RCPT-DEMO-001",
            },
        },
        {
            "client": "Павлова Екатерина Андреевна",
            "master": "Морозова Елена Игоревна",
            "service": "Оформление бровей",
            "start_time": dt_for(1, 11, 30),
            "status": Appointment.STATUS_CANCELLED,
            "notes": "Клиент переносит визит на следующую неделю",
            "cancel_reason": "Клиент отменил запись по личным обстоятельствам",
            "payment": None,
        },
        {
            "client": "Соколова Дарья Игоревна",
            "master": "Иванов Сергей Андреевич",
            "service": "Окрашивание волос",
            "start_time": dt_for(-2, 13, 0),
            "status": Appointment.STATUS_COMPLETED,
            "notes": "Использована щадящая краска",
            "cancel_reason": None,
            "payment": {
                "amount": 3500.0,
                "method": Payment.METHOD_CARD,
                "receipt_no": "RCPT-DEMO-002",
            },
        },
        {
            "client": "Романова Юлия Алексеевна",
            "master": "Петрова Мария Сергеевна",
            "service": "Маникюр классический",
            "start_time": dt_for(0, 15, 30),
            "status": Appointment.STATUS_NO_SHOW,
            "notes": "Клиент не пришёл, не ответил на звонок",
            "cancel_reason": None,
            "payment": None,
        },
        {
            "client": "Федорова Наталья Игоревна",
            "master": "Соколова Анна Викторовна",
            "service": "Уходовая процедура для лица",
            "start_time": dt_for(2, 10, 30),
            "status": Appointment.STATUS_PLANNED,
            "notes": "Нужно подготовить рекомендации по домашнему уходу",
            "cancel_reason": None,
            "payment": None,
        },
    ]

    for item in appointments_data:
        client = clients[item["client"]]
        master = masters[item["master"]]
        service = services[item["service"]]

        start_time = item["start_time"]
        end_time = start_time + timedelta(minutes=service.duration_min)

        appointment = Appointment(
            client_id=client.id,
            master_id=master.id,
            service_id=service.id,
            start_time=start_time,
            end_time=end_time,
            status=item["status"],
            price_at_booking=service.base_price,
            notes=item["notes"],
            cancel_reason=item["cancel_reason"],
            created_by=admin_user.id,
        )

        db.session.add(appointment)
        db.session.flush()

        if item["payment"]:
            payment = Payment(
                appointment_id=appointment.id,
                amount=item["payment"]["amount"],
                payment_method=item["payment"]["method"],
                payment_status=Payment.STATUS_PAID,
                receipt_no=item["payment"]["receipt_no"],
                paid_at=start_time + timedelta(hours=2),
            )
            db.session.add(payment)

    db.session.commit()


def seed_all():
    seed_roles()
    db.session.commit()

    seed_users()
    seed_masters()
    seed_categories_and_services()
    seed_clients()
    db.session.commit()

    reset_demo_schedule()
    create_demo_appointments()


if __name__ == "__main__":
    with app.app_context():
        seed_all()
        print("Демонстрационные данные успешно добавлены.")