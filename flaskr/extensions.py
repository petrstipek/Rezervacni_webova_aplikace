from flask_mail import Mail
from flask_login import LoginManager

mail = Mail()
login_manager = LoginManager()

recaptcha_private = "6LfLHYgpAAAAAK7iUJgezJJnuYEkkYny9KbmVdUA"
recaptcha_public  = "6LfLHYgpAAAAADs4MstYrx2WJV1_hPNhN2GSrpHd"