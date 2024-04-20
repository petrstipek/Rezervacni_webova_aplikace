from flask import Blueprint, render_template
from flask_login import login_required
from flaskr.auth.login_decorators import instructor_required
from flask_login import current_user
from flaskr.extensions import database
from flaskr.models import Osoba

instructors_bp = Blueprint('instructor', __name__, template_folder='templates')

@instructors_bp.route('/reservations')
@login_required
@instructor_required
def instructors_reservations():
    user_id = current_user.get_id()
    user = database.session.query(Osoba).filter(Osoba.ID_osoba==user_id).first()
    return render_template("/blog/instructors/instructors_page.html", instructor_name=user.jmeno, active_page="instructors_reservations")