from flask import Blueprint, jsonify, flash, request, redirect, url_for, json
from flaskr.db import get_db
from urllib.parse import urlparse
import sqlite3
from flaskr.api.services.reservations_services import *

reservations_api_bp = Blueprint('reservations_api', __name__, template_folder='templates')

@reservations_api_bp.route('/delete-reservation/<reservation_id>', methods=['DELETE', 'POST'])
def delete_reservation(reservation_id):
    referer_url = request.headers.get('Referer', 'default_fallback_url')
    parsed_url = urlparse(referer_url)
    path = parsed_url.path
    last_part_url = path.strip('/').split('/')[-1]

    success, message = delete_reservation_by_id(reservation_id)

    if last_part_url == "reservations-admin":
        flash(message, category="success" if success else "danger")
        return redirect(url_for("administration.reservations_admin"))
    else:
        response = {"message": message} if success else {"error": message}
        status_code = 200 if success else 404 if message == "Rezervace nebyla nalezena!" else 500
        return jsonify(response), status_code
    
@reservations_api_bp.route('/get-reservation-details/<reservation_identifiers>', defaults={'identifier': None})
@reservations_api_bp.route('/get-reservation-details/<reservation_identifiers>/<identifier>')
def get_reservation_details(reservation_identifiers, identifier):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    data, error = get_paginated_reservation_details(identifier, reservation_identifiers, page, per_page)
    if error:
        response = {"error": error}
        status_code = 404 if error == "Žádné rezervace nenalezeny!" else 400
        return jsonify(response), status_code
    else:
        return jsonify(data)

@reservations_api_bp.route('/get-available-times/group')
def get_available_times_group():
    query_result_group = fetch_available_group_times()
    available_times_group = format_available_times(query_result_group)
    return jsonify(available_times_group)

@reservations_api_bp.route('/get-available-times/individual/<int:instructor_id>')
def get_available_times_individual_instructor(instructor_id):
    query_result_ind = fetch_available_times_for_individual_instructor(instructor_id)
    available_times_ind = format_available_times(query_result_ind)
    return jsonify(available_times_ind)
