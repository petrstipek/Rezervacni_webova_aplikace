from flask_mail import Mail
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

mail = Mail()
login_manager = LoginManager()
database = SQLAlchemy()

recaptcha_private = "6LdmUpQpAAAAAEzCoZWnmEffNUxHCWB_adG1N608"
recaptcha_public = "6LdmUpQpAAAAALHcMy_U6mDJ78OJuptLW9muSk23"
verify_url = "https://www.google.com/recaptcha/api/siteverify"