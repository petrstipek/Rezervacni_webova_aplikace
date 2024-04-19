from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app, Blueprint, redirect, flash, url_for, render_template
from flaskr.email.email import send_email, send_password_reset
from flaskr.auth.auth import auth_bp
from flaskr.forms import PasswordRenewalForm, PasswordResetForm
from flaskr.auth.services import check_email, change_password
from datetime import datetime, timedelta
from flaskr.extensions import database

@auth_bp.route('/renew-password', methods=["GET", "POST"])
def renew_password():
    form = PasswordRenewalForm()
    if form.validate_on_submit():
        email = form.email.data
        email_user_instance = check_email(email)
        if email_user_instance:
            send_reset_email(email_user_instance)
            flash("Na Vaší emailovou adresu byl odeslán odkaz pro obnovu hesla!", category="success")
            return redirect(url_for('auth.login'))

        else:
            flash("Email v systému neexistuje, zkuste to prosím znovu!", category="danger")
    return render_template('/auth/renew_password.html', form=form)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    send_password_reset(user.email, reset_url)
    #send_email("Obnova Hesla", 'jl6701543@gmail.com', 'felixgrent@gmail.com', 'text body emailu', 'Link pro obnovení rezervace je: '+ reset_url )

def validate_token(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=1800)
        return email
    except SignatureExpired:
        return 'expired'
    except BadSignature:
        return 'invalid'

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email_or_result = validate_token(token)
    if email_or_result in ['expired', 'invalid']:
        flash('Platnost odkazu vypršela, zkuste prosím heslo obnovit znovu!', 'warning')
        return redirect(url_for('auth.renew_password'))

    user = check_email(email_or_result)
    if not user:
        flash('Neplatný pokus o změnu hesla.', 'danger')
        return redirect(url_for('auth.renew_password'))

    form = PasswordResetForm()

    if user.last_password_change_attempt and datetime.now() - user.last_password_change_attempt < timedelta(hours=24):
        if user.password_change_attempts >= 3:
            flash('Můžete změnit heslo pouze 3krát za 24 hodin.', 'danger')
            return render_template('auth/reset_password.html', form=form, token=token)

    if form.validate_on_submit():
        if not user.last_password_change_attempt or datetime.now() - user.last_password_change_attempt > timedelta(hours=24):
            user.password_change_attempts = 0

        user.password_change_attempts += 1
        user.last_password_change_attempt = datetime.now()

        if user.password_change_attempts <= 3:
            if change_password(user.email, form.new_password.data):
                user.password_change_attempts = 0
                database.session.commit()
                flash("Vaše heslo bylo úspešně změněné a můžete se znovu přihlásit!", 'success')
                return redirect(url_for('auth.login'))
            else:
                flash("V obnově se vyskytla chyba, zkuste to prosím znovu!", 'danger')
        else:
            flash('Můžete změnit heslo pouze 3krát za 24 hodin.', 'danger')

        database.session.commit()

    return render_template('auth/reset_password.html', form=form, token=token)

