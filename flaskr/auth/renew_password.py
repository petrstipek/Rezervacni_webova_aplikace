from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app, Blueprint, redirect, flash, url_for, render_template
from flaskr.email.email import send_email
from flaskr.auth.auth import auth_bp
from flaskr.forms import PasswordRenewalForm, PasswordResetForm
from flaskr.auth.services import check_email, change_password

@auth_bp.route('/renew-password', methods=["GET", "POST"])
def renew_password():
    form = PasswordRenewalForm()
    if form.validate_on_submit():
        email = form.email.data
        email_user_instance = check_email(email)
        if email_user_instance:
            send_reset_email(email_user_instance)
            flash("Na Vaší emailovou adresu byl odeslán odkaz pro obnovu hesla!", category="success")
        else:
            flash("Email v systému neexistuje, zkuste to prosím znovu!", category="danger")
    return render_template('/auth/renew_password.html', form=form)

def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def send_reset_email(user):
    token = generate_reset_token(user.email)
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    send_email("Obnova Hesla", 'jl6701543@gmail.com', 'felixgrent@gmail.com', 'text body emailu', 'Link pro obnovení rezervace je: '+ reset_url )

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
    result = validate_token(token)
    form = PasswordResetForm()
    if result == 'expired':
        flash('Platnost odkazu vypršela, zkuste si heslo obnovit znovu!', 'warning')
        return redirect(url_for('auth.renew_password'))
    elif result == 'invalid':
        flash('Platnost odkazu vypršela, zkuste si heslo obnovit znovu!', 'warning')
        return redirect(url_for('auth.renew_password'))
    else:
        email = result
        if form.validate_on_submit():
            password = form.new_password.data
            password_change = change_password(email, password)
            if password_change == True:
                flash("Vaše heslo bylo úspešně změněné a můžete se znovu přihlásit!", category="success")
            else:
                flash("V obnově se vyskytla chyba, zkuste to prosím znovu!", category="danger")
                return redirect(url_for('auth.renew_password'))

        return render_template('auth/reset_password.html', token=token, form=form)
