from datetime import date

from app import create_app
from app.extensions import db
from app.models import Role, User, Master, Client, ServiceCategory, Service


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
            "description": "Администратор салона"
        },
        {
            "name": "director",
            "description": "Директор салона"
        }
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
            "password": "admin123"
        },
        {
            "username": "director",
            "email": "director@estetika.local",
            "full_name": "Директор Эстетика",
            "role_id": director_role.id,
            "password": "director123"
        }
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
            "percent_rate": 40.0
        },
        {
            "full_name": "Иванов Сергей Андреевич",
            "specialty": "Парикмахер",
            "phone": "+79000000012",
            "email": "ivanov@estetika.local",
            "percent_rate": 45.0
        },
        {
            "full_name": "Соколова Анна Викторовна",
            "specialty": "Косметолог",
            "phone": "+79000000013",
            "email": "sokolova@estetika.local",
            "percent_rate": 50.0
        }
    ]

    for master_data in masters_data:
        get_or_create(Master, full_name=master_data["full_name"], defaults=master_data)


def seed_categories_and_services():
    categories_data = [
        {
            "name": "Парикмахерские услуги",
            "description": "Стрижки, укладки, окрашивание"
        },
        {
            "name": "Ногтевой сервис",
            "description": "Маникюр, педикюр, покрытие"
        },
        {
            "name": "Косметология",
            "description": "Уход за лицом и кожей"
        }
    ]

    for category_data in categories_data:
        get_or_create(
            ServiceCategory,
            name=category_data["name"],
            defaults=category_data
        )

    hair = ServiceCategory.query.filter_by(name="Парикмахерские услуги").first()
    nails = ServiceCategory.query.filter_by(name="Ногтевой сервис").first()
    cosmetology = ServiceCategory.query.filter_by(name="Косметология").first()

    services_data = [
        {
            "category_id": hair.id,
            "name": "Стрижка женская",
            "duration_min": 60,
            "base_price": 1800,
            "description": "Женская стрижка с укладкой"
        },
        {
            "category_id": hair.id,
            "name": "Окрашивание волос",
            "duration_min": 120,
            "base_price": 3500,
            "description": "Окрашивание волос средней длины"
        },
        {
            "category_id": nails.id,
            "name": "Маникюр классический",
            "duration_min": 60,
            "base_price": 1500,
            "description": "Классический маникюр без покрытия"
        },
        {
            "category_id": nails.id,
            "name": "Маникюр с гель-лаком",
            "duration_min": 90,
            "base_price": 2200,
            "description": "Маникюр с покрытием гель-лак"
        },
        {
            "category_id": cosmetology.id,
            "name": "Чистка лица",
            "duration_min": 90,
            "base_price": 2800,
            "description": "Комплексная чистка лица"
        },
        {
            "category_id": cosmetology.id,
            "name": "Уходовая процедура для лица",
            "duration_min": 60,
            "base_price": 2500,
            "description": "Базовая уходовая процедура"
        }
    ]

    for service_data in services_data:
        get_or_create(
            Service,
            name=service_data["name"],
            defaults=service_data
        )


def seed_clients():
    clients_data = [
        {
            "full_name": "Иванова Анна Петровна",
            "phone": "+79000000101",
            "email": "anna@example.com",
            "birth_date": date(1995, 5, 14),
            "notes": "Предпочитает вечернее время записи"
        },
        {
            "full_name": "Смирнова Ольга Викторовна",
            "phone": "+79000000102",
            "email": "olga@example.com",
            "birth_date": date(1990, 8, 22),
            "notes": "Постоянный клиент ногтевого сервиса"
        },
        {
            "full_name": "Кузнецова Марина Сергеевна",
            "phone": "+79000000103",
            "email": "marina@example.com",
            "birth_date": date(1988, 11, 3),
            "notes": "Записывается в основном на косметологию"
        },
        {
            "full_name": "Павлова Екатерина Андреевна",
            "phone": "+79000000104",
            "email": "ekaterina@example.com",
            "birth_date": date(1998, 1, 17),
            "notes": "Просит напоминать о визите заранее"
        },
        {
            "full_name": "Соколова Дарья Игоревна",
            "phone": "+79000000105",
            "email": "darya@example.com",
            "birth_date": date(1993, 7, 9),
            "notes": "Предпочитает мастера Иванова С. А."
        }
    ]

    for client_data in clients_data:
        get_or_create(
            Client,
            phone=client_data["phone"],
            defaults=client_data
        )


def seed_all():
    seed_roles()
    db.session.commit()

    seed_users()
    seed_masters()
    seed_categories_and_services()
    seed_clients()

    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        seed_all()
        print("Тестовые данные успешно добавлены.")