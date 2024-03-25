from flask import Blueprint, render_template
from flask_login import login_required
from flaskr.auth.login_decorators import instructor_required

instructors_bp = Blueprint('instructor', __name__, template_folder='templates')

@instructors_bp.route('/reservations')
@login_required
@instructor_required
def instructors_reservations():
    return render_template("/blog/instructors/instructors_page.html")