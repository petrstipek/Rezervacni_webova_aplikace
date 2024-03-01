from flask import Blueprint, jsonify, flash, request, redirect, url_for, json
from flaskr.extensions import db
from urllib.parse import urlparse
import sqlite3
from flaskr.models import DostupneHodiny, MaVypsane
from sqlalchemy import func
from datetime import date, time

reservations_api_bp = Blueprint('reservations_api', __name__, template_folder='templates')

@reservations_api_bp.route('/delete-reservation/<reservation_id>', methods=['DELETE', 'POST'])
def delete_reservation(reservation_id):
    cur = db.cursor()

    referer_url = request.headers.get('Referer', 'default_fallback_url')
    parsed_url = urlparse(referer_url)
    path = parsed_url.path
    last_part_url = path.strip('/').split('/')[-1]

    try:   
        lessons_ids = db.execute("SELECT ID_hodiny from prirazeno WHERE ID_rezervace = ?", (reservation_id)).fetchall()
        
        for lesson_id_tuple in lessons_ids:
            lesson_id = lesson_id_tuple[0]
            cur.execute("UPDATE Dostupne_hodiny SET stav = 'volno' WHERE ID_hodiny = ?", (lesson_id,))

        cur.execute("DELETE FROM rezervace WHERE ID_rezervace = ?", (reservation_id,))
        db.execute("DELETE from prirazeno WHERE ID_rezervace = ?", (reservation_id))
        db.execute("DELETE from ma_vyuku WHERE ID_rezervace = ?", (reservation_id))
        db.commit()

        if cur.rowcount > 0:
            response = {"message": "Reservation deleted successfully"}
            status_code = 200
        else:
            response = {"error": "Reservation not found"}
            status_code = 404
    except sqlite3.Error as e:
        response = {"error": str(e)}
        status_code = 500
    
    if last_part_url == "reservations-admin":
        flash("Dostupná hodina byla úspěšně smazána!", category="success")
        return redirect(url_for("administration.reservations_admin"))
    else:
        return jsonify(response), status_code
    
@reservations_api_bp.route('/get-reservation-details/<reservation_identifiers>', defaults={'identifier': None})
@reservations_api_bp.route('/get-reservation-details/<reservation_identifiers>/<identifier>')
def get_reservation_details(reservation_identifiers, identifier):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    def query_db_and_construct_response(sql_query, params):
        offset = (page - 1) * per_page
        
        paginated_sql_query = f"{sql_query} LIMIT ? OFFSET ?"
        paginated_params = params + (per_page, offset)

        query_result = db.execute(paginated_sql_query, paginated_params).fetchall()
        
        if query_result:
            columns = ["ID_rezervace", "ID_osoba", "typ_rezervace", "termin", "platba", "cas_zacatku", "doba_vyuky", "jazyk", "pocet_zaku"]
            results_list = [{column: row[i] for i, column in enumerate(columns)} for row in query_result]
            
            count_sql_query = f"SELECT COUNT(*) FROM ({sql_query})"
            total_items = db.execute(count_sql_query, params).fetchone()[0]
            total_pages = (total_items + per_page - 1) // per_page
            
            return jsonify({
                "reservations": results_list,
                "total_items": total_items,
                "total_pages": total_pages,
                "current_page": page
            })
        else:
            return jsonify({"error": "No reservations found"}), 404

    query_map = {
        "reservationID": ("SELECT * FROM rezervace WHERE rezervacni_kod = ?", (identifier,)),
        "name": ("SELECT * FROM rezervace LEFT JOIN Klient USING (ID_osoba) WHERE prijmeni = ?", (identifier,)),
        "email": ("SELECT * FROM rezervace LEFT JOIN Klient USING (ID_osoba) WHERE email = ?", (identifier,)),
        "tel-number": ("SELECT * FROM rezervace LEFT JOIN Klient USING (ID_osoba) WHERE tel_cislo = ?", (identifier,)),
        "all": ("SELECT * FROM rezervace LEFT JOIN Klient USING (ID_osoba)", ())
    }

    if reservation_identifiers in query_map:
        sql_query, params = query_map[reservation_identifiers]
        return query_db_and_construct_response(sql_query, params)
    else:
        return jsonify({"error": "Invalid reservation identifier"}), 400

@reservations_api_bp.route('/get-available-times/group')
def get_available_times_group():

    query_result_group = db.execute("""
        SELECT datum, cas_zacatku, (kapacita - obsazenost) as count
        FROM dostupne_hodiny
        WHERE stav = 'volno' AND typ_hodiny = 'group' AND obsazenost < kapacita
        GROUP BY datum, cas_zacatku
        ORDER BY datum, cas_zacatku;
    """).fetchall()

    available_times_group = {}

    for row in query_result_group:
        date_str = row['datum'].strftime('%Y-%m-%d')
        time_str = row['cas_zacatku'] 
        count = row['count']

        if date_str not in available_times_group:
            available_times_group[date_str] = []

        available_times_group[date_str].append((time_str, count))

    return jsonify(available_times_group)

@reservations_api_bp.route('/get-available-times/individual/<int:instructor_id>')
def get_available_times_individual_instructor(instructor_id):

    base_query = db.session.query(DostupneHodiny.datum, DostupneHodiny.cas_zacatku, func.count().label("count")).join(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny).filter(DostupneHodiny.stav == "volno").first()
    print(base_query)

    if instructor_id != 0:
        base_query = base_query.filter(MaVypsane.ID_osoba == instructor_id)
    
    query_result_ind = base_query.group_by(
        DostupneHodiny.datum, DostupneHodiny.cas_zacatku
    ).order_by(
        DostupneHodiny.datum, DostupneHodiny.cas_zacatku
    ).all()
    
    available_times_ind = {}
    for datum, cas_zacatku, count in query_result_ind:
        date_str = datum.strftime('%Y-%m-%d')
        time_str = cas_zacatku
        if date_str not in available_times_ind:
            available_times_ind[date_str] = []
        available_times_ind[date_str].append((time_str, count))
    
    print(available_times_ind)
    
    return jsonify(available_times_ind)
