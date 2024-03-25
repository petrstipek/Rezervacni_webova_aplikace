from flask import Blueprint, jsonify, request
from flaskr.api.services.reservations_services import *
from flaskr.api.services.users_services import get_paginated_reservation_details
from flask_login import login_required

users_api_bp = Blueprint('users_api', __name__, template_folder='templates')

@users_api_bp.route('/reservations', methods=['GET'])
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