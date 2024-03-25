from flask import Blueprint, render_template
from flask_login import login_required
from flaskr.auth.login_decorators import client_required

users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/reservations')
@login_required
@client_required
def users_reservations():
    return render_template("/blog/user/user_page.html")