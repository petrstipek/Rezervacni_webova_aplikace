import os, secrets
from flask import Flask
from flask_bootstrap import Bootstrap5
from flaskr.forms import CSRFProtect
from flaskr.extensions import mail
from . import db
from flaskr.extensions import login_manager, database
from flaskr.auth.auth import auth_bp
from flaskr.reservations.reservations import reservations_bp
from flaskr.administration.administration import administration_bp
from flaskr.information.information import information_bp
from flaskr.api.instructors_api import admin_instructors_bp
from flaskr.api.reservations_api import reservations_api_bp
from flaskr.extensions import recaptcha_private, recaptcha_public
from flaskr.api.administration_api import administration_api

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    bootstrap = Bootstrap5(app)
    csrf = CSRFProtect(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'database.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    database.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login_page_admin'

    foo = secrets.token_urlsafe(16)
    app.secret_key = foo

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(reservations_bp, url_prefixes="/reservations")
    app.register_blueprint(administration_bp, url_prefix="/administration")
    app.register_blueprint(information_bp, url_prefix="/information")

    app.register_blueprint(admin_instructors_bp, url_prefix="/admin-api-instructors")
    
    app.register_blueprint(reservations_api_bp, url_prefix="/reservations-api")
    app.register_blueprint(administration_api, url_prefix="/administration-api")

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'jl6701543@gmail.com'
    app.config['MAIL_PASSWORD'] = 'qqlg wnwf bsni lzqm '
    app.config['MAIL_DEFAULT_SENDER'] = 'jl6701543@gmail.com'

    mail.init_app(app)

    with app.app_context():
        database.create_all()

    app.config["RECAPTCHA_PUBLIC_KEY"] = recaptcha_public
    app.config["RECAPTCHA_PRIVATE_KEY"]= recaptcha_private


    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app