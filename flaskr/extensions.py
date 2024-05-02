# FileName: extenstions.py
# Description: Defines the extensions used in the application.
# Author: Petr Štípek
# Date: 2024

from flask_mail import Mail
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

mail = Mail()
login_manager = LoginManager()
database = SQLAlchemy()

recaptcha_private = "6Ldfh6spAAAAADhvDry4Qm9fKZgx_Th_okQZbeW3"
recaptcha_public = "6Ldfh6spAAAAANtsZZU3rLBv85NBJQFz-71nYcX3"

verify_url = "https://www.google.com/recaptcha/api/siteverify"