import os, secrets
from flask import Flask
from flask_bootstrap import Bootstrap5
from flaskr.forms import CSRFProtect
from flaskr.extensions import mail
from flaskr.extensions import login_manager, database
from flaskr.auth.auth import auth_bp
from flaskr.reservations.reservations import reservations_bp
from flaskr.administration.administration import administration_bp
from flaskr.information.information import information_bp
from flaskr.api.reservations_api import reservations_api_bp
from flaskr.extensions import recaptcha_private, recaptcha_public
from flaskr.api.administration_api import administration_api
from flaskr.users.users import users_bp
from flaskr.instructors.instructors import instructors_bp
from flaskr.api.users_api import users_api_bp
from flaskr.api.instructors_api import instructors_api_bp
import errno



def create_application(test_config=None):
    application = Flask(__name__, instance_relative_config=True)
    application.config.from_mapping(
        SECRET_KEY='dev',
    )

    bootstrap = Bootstrap5(application)
    csrf = CSRFProtect(application)

    #Testovací databáze
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(application.instance_path, 'database.sqlite')
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    #Produkční databáze
    #application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://felixgrent:woxdep-pypxo0-woqdyW@rds-mysql-skiressys.c9sa6ogi4a00.eu-north-1.rds.amazonaws.com/rds-mysql-skiressys'
    
    database.init_app(application)
    login_manager.init_app(application)
    mail.init_app(application)

    login_manager.login_view = 'auth.login_page_admin'

    foo = secrets.token_urlsafe(16)
    application.secret_key = foo

    application.register_blueprint(auth_bp, url_prefix='/auth')
    application.register_blueprint(reservations_bp, url_prefix="/")
    application.register_blueprint(reservations_api_bp, url_prefix="/reservations-api")

    application.register_blueprint(administration_bp, url_prefix="/administration")
    application.register_blueprint(information_bp, url_prefix="/information")
    
    
    application.register_blueprint(administration_api, url_prefix="/administration-api")
    application.register_blueprint(users_api_bp, url_prefix="/users-api")
    application.register_blueprint(instructors_api_bp, url_prefix="/instructors-api")

    application.register_blueprint(instructors_bp, url_prefix="/instructor")
    application.register_blueprint(users_bp, url_prefix="/users")

    application.config['MAIL_SERVER'] = 'smtp.gmail.com'
    application.config['MAIL_PORT'] = 587
    application.config['MAIL_USE_TLS'] = True
    application.config['MAIL_USERNAME'] = 'jl6701543@gmail.com'
    application.config['MAIL_PASSWORD'] = 'qqlg wnwf bsni lzqm '
    application.config['MAIL_DEFAULT_SENDER'] = 'jl6701543@gmail.com'


    UPLOAD_FOLDER = 'static/uploads'
    application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    try:
        os.makedirs(os.path.join(application.root_path, application.config['UPLOAD_FOLDER']))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


    with application.app_context():
        database.create_all()

    application.config["RECAPTCHA_PUBLIC_KEY"] = recaptcha_public
    application.config["RECAPTCHA_PRIVATE_KEY"]= recaptcha_private

    if test_config is None:
        application.config.from_pyfile('config.py', silent=True)
    else:
        application.config.from_mapping(test_config)
    try:
        os.makedirs(application.instance_path)
    except OSError:
        pass

    return application