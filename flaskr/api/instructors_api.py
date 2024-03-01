from flask import Blueprint, redirect, flash, url_for
from flask_login import login_required
from flaskr.extensions import db


admin_instructors_bp = Blueprint('admin_api_instructors', __name__, template_folder='templates')

@admin_instructors_bp.route('/delete_instructor_admin/<int:instructor_id>', methods=["POST"])
@login_required
def delete_instructor_admin(instructor_id):
    query_result = db.execute('SELECT * from ma_vyuku WHERE ID_osoba = ?', (instructor_id,)).fetchone()
    if query_result:
        flash("instructor has occupied lessons", category="danger")
        return redirect(url_for("administration.instructors_admin"))

    db.execute('DELETE FROM Instruktor WHERE ID_osoba = ?', (instructor_id,))
    db.commit()

    return redirect(url_for("administration.instructors_admin"))