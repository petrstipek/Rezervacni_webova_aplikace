from flask import Blueprint, redirect, flash, url_for
from flask_login import login_required
from flaskr.api.services.instructor_services import *
from flaskr.api.administration_api import administration_api


admin_instructors_bp = Blueprint('admin_api_instructors', __name__, template_folder='templates')

@admin_instructors_bp.route('/delete_instructor_admin/<int:instructor_id>', methods=["POST"])
@login_required
def delete_instructor_admin(instructor_id):
    if instructor_has_lessons(instructor_id):
        flash("Instruktor má hodiny s aktivní rezervací!", category="danger")
    else:
        if delete_instructor_by_id(instructor_id):
            flash("Instruktor úspěšně odstraněn z databáze!", category="success")
        else:
            flash(f"Error: {delete_instructor_by_id(instructor_id)}", category="danger")
            pass
    
    return redirect(url_for("administration.instructors_admin"))


#nove
@administration_api.route("/instructors/<int:instructor_id>", methods=["DELETE"])
@login_required
def delete_instructor_admin(instructor_id):
    if instructor_has_lessons(instructor_id):
        flash("Instruktor má hodiny s aktivní rezervací!", category="danger")
    else:
        if delete_instructor_by_id(instructor_id):
            flash("Instruktor úspěšně odstraněn z databáze!", category="success")
        else:
            flash(f"Error: {delete_instructor_by_id(instructor_id)}", category="danger")
            pass
    
    return redirect(url_for("administration.instructors_admin"))