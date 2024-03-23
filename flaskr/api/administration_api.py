from flask import Blueprint, jsonify, request
from flask_login import login_required
from flaskr.api.services.administration_services import *
from flaskr.api.services.reservations_services import delete_reservation_by_reservation_id
from flaskr.api.services.lessons_services import get_paginated_lessons

administration_api = Blueprint('administration-api', __name__, template_folder='templates')

#nove-funguje
@administration_api.route('/reservation/payment', methods=["POST"])
@login_required
def reservation_payment_status():
    try:
        reservation_id = request.args.get('reservation_id')
        reservation = get_reservation_payment_status(reservation_id)
        if not reservation:
            return jsonify({'status': 'error', 'message': 'Rezervace nenalezena!'}), 404
        payment_status = reservation[0]
        if payment_status == "nezaplaceno":
            mark_reservation_as_paid(reservation_id)
            return jsonify({'status': 'success', 'message': 'Rezervace označena jako zaplacená!'}), 200
        elif payment_status == "zaplaceno":
            return jsonify({'status': 'warning', 'message': 'Rezervace již je zaplacena'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Error!'}), 500
    
#nove-funguje
@administration_api.route('/reservation/<reservation_id>', methods=['DELETE'])
def delete_reservation_by_id(reservation_id):
    success, message = delete_reservation_by_reservation_id(reservation_id)
    if success:
        return jsonify({"success": True, "message": "Rezervace zrušena!"})
    else:
        return jsonify({"error": message}), 400 
    
#nove-funguje
@administration_api.route('/lesson/<int:lesson_id>', methods=["DELETE"])
@login_required
def delete_lesson_admin(lesson_id):
    try:
        lesson_status = get_lesson_status(lesson_id)
        if lesson_status and lesson_status[0] == "obsazeno":
            return jsonify({"error": True, "message": "Hodina je obsazena, nelze smazat, nejdřív smažte rezervaci."}), 400
        elif lesson_status and lesson_status[0] == "volno":
            delete_lesson(lesson_id)
            return jsonify({"success": True, "message": "Dostupná hodina byla úspěšně smazána!"})
    except Exception as e:
        return jsonify({"error": True, "message": "Nastala chyba."}), 500
    
#nove - funguje
@administration_api.route('/reservations', methods=['GET'])
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
    
@administration_api.route("/lessons")
def get_lessons():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    selected_date = request.args.get('date', None)
    lessons, total = get_paginated_lessons(page, per_page, selected_date)
    lessons_dict = [dict(row) for row in lessons]
    return jsonify({
        'lessons': lessons_dict,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    })