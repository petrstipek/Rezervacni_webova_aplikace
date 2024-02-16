import os, secrets
from flask import Flask
from flaskr.views import views
from flask_bootstrap import Bootstrap5
from flaskr.forms import CSRFProtect
from . import db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    #app.secret_key = 'tO$&!|0wkamvVia0?n$NqIRVWOG'
    bootstrap = Bootstrap5(app)
    csrf = CSRFProtect(app)

    foo = secrets.token_urlsafe(16)
    app.secret_key = foo

    app.register_blueprint(views, url_prefix="/")

    db.init_app(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    return app