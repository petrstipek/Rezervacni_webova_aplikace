from flask import Blueprint, jsonify, request
from flaskr.api.services.reservations_services import *
from flaskr.api.administration_api import administration_api
from flaskr.email.email import send_reservation_cancelation

reservations_api_bp = Blueprint('reservations_api', __name__, template_folder='templates')

@reservations_api_bp.route('/reservation/<int:reservation_code>', methods=['DELETE'])
def delete_reservation_by_code(reservation_code):
    success, message, reservation_code, email, payment  = delete_reservation_by_reservation_code(reservation_code)
    if success:
        send_reservation_cancelation(email, reservation_code, payment)
        return jsonify({"success": True, "message": "Rezervace zrušena!"})
    else:
        return jsonify({"error": message}), 400 
    
@reservations_api_bp.route('/reservation/<reservation_identifier>')
def get_reservation(reservation_identifier):
    data = get_reservation_detail(reservation_identifier)
    if data:
        return jsonify(data)
    else:
        return jsonify({"error": "Při hledání rezervace nastala chyba"}), 404

@reservations_api_bp.route('/lessons/<int:instructor_id>/available-times')
@reservations_api_bp.route('/lessons/available-times')
def get_available_lessons(instructor_id = None):
    date = request.args.get('reservation_date')
    if instructor_id != None:
        query_result_ind = fetch_available_times_for_individual_instructor(instructor_id, date)
        available_times_ind = format_available_times(query_result_ind)
        return jsonify(available_times_ind)
    else:
        query_result_group = fetch_available_group_times()
        available_times_group = format_available_times(query_result_group)
        return jsonify(available_times_group)