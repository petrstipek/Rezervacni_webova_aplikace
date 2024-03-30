from flask import Blueprint, redirect, flash, url_for, request, jsonify
from flask_login import login_required
from flaskr.api.services.instructor_services import *
from flaskr.api.administration_api import administration_api


admin_instructors_bp = Blueprint('admin_api_instructors', __name__, template_folder='templates')
instructors_api_bp = Blueprint('instructors_api', __name__, template_folder='templates')

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

@instructors_api_bp.route('/reservations', methods=['GET'])
@login_required
def get_reservations():
    identifier = None
    reservation_identifier = None
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    selected_date = request.args.get('selected_date', None)
    reservation_id = request.args.get('reservation_id')
    name = request.args.get('name')
    email = request.args.get('email')
    tel_number = request.args.get('tel_number')

    if reservation_id is not None:
        identifier = reservation_id
        reservation_identifier = "reservationID"
    elif name is not None:
        identifier = name
        reservation_identifier = "name"
    elif email is not None:
        identifier = email
        reservation_identifier = "email"
    elif tel_number is not None:
        identifier = tel_number
        reservation_identifier = "tel-number"

    data, error = get_paginated_reservation_details(page, per_page, identifier, reservation_identifier, selected_date)

    if error:
        response = {"error": error}
        status_code = 404 if error == "No reservations found!" else 400
        return jsonify(response), status_code
    else:
        return jsonify(data)
    
@instructors_api_bp.route("/details")
@login_required
def get_isntructor_details():
    instructor_id = request.args.get('instructor_id')
    instructor = get_instructor_details(instructor_id)
    return jsonify(instructor)