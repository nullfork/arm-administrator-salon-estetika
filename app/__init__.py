from flask import Flask
from config import Config
from app.extensions import db, migrate, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app import models
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.clients import clients_bp
    from app.routes.masters import masters_bp
    from app.routes.services import services_bp
    from app.routes.appointments import appointments_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(masters_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(appointments_bp)

    return app