from flask import Blueprint, render_template, request, jsonify, json, flash, redirect, url_for, session
from flaskr.forms import PersonalInformationForm, ReservationInformationForm, LoginForm, InstructorInsertForm, LessonInsertForm, ReservationInformationAdmin
from flaskr.db import get_db
from .email import send_reservation_confirmation
from datetime import datetime, timedelta
import sqlite3
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from urllib.parse import urlparse
import random, string
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from flaskr.extensions import login_manager, mail
from werkzeug.security import generate_password_hash
from flask_mail import Message

views = Blueprint("views", __name__)


@views.route('/lectures')
def lectures():
    db = get_db()

    unique_ids = db.execute('SELECT DISTINCT ID_osoba FROM ma_vypsane').fetchall()
    unique_ids = [row['ID_osoba'] for row in unique_ids]

    found = False
    for id_osoba in unique_ids:
        query_result = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where stav = "volno" and datum = "2024-02-21" and cas_zacatku = "16:00" AND ID_osoba = ? order by ID_osoba', (id_osoba,)).fetchone()    
        if query_result == None:
            continue
        
        query_result2 = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left  join Dostupne_hodiny using (ID_hodiny) where ID_osoba = ? and datum = "2024-02-21" and cas_zacatku = "17:00"', (id_osoba,)).fetchone()        
        if query_result2 == None:
            continue
        found = True
        id_instructor = query_result["ID_osoba"]
        id_lessons = (query_result["ID_hodiny"], query_result2["ID_hodiny"])
        print("id found ")
        print("id osoby")
        print(id_instructor)
        print("ID dostupne hodiny")
        print(id_lessons[0])
        print(id_lessons[1])
        break
    if not found:
        print("Nothing was found for the given conditions.")           
    return render_template("blog/lectures.html")





@views.route('/delete_lesson_admin/<int:lesson_id>', methods=["POST"])
@login_required
def delete_lesson_admin(lesson_id):
    db = get_db()
    print("jsem tady v lesson delte")
    print(type(lesson_id))

    try:
        query_result = db.execute('SELECT stav FROM dostupne_hodiny WHERE ID_hodiny = ?', (lesson_id,)).fetchone()

        if query_result and query_result["stav"] == "obsazeno":
            #flash("Hodina je obsazene, nelze proto smazat", category="danger")
            return jsonify({"error": True, "message": "Hodina je obsazene, nelze proto smazat"}), 400
        else:
            db.execute('DELETE FROM dostupne_hodiny WHERE ID_hodiny = ?', (lesson_id,))
            db.execute('DELETE FROM ma_vypsane WHERE ID_hodiny = ?', (lesson_id,))
            db.commit()
            return jsonify({"success": True, "message": "Dostupná hodina byla úspěšně smazána!"})
    except Exception as e:
        return jsonify({"error": True, "message": "An error occurred. Please try again."}), 500

@views.route('/handle_selection', methods=['POST'])
def handle_selection():
    selected_option = request.json['selectedOption']
    print(selected_option)
    return jsonify({"message": "Option processed successfully"})

@views.route('/get-available-times/<instructor_id>')
def get_available_times(instructor_id):
    db = get_db()
    query_resuslt_instructor_times = db.execute('select datum, cas_zacatku from dostupne_hodiny left join ma_vypsane using (ID_hodiny) where stav="volno" and typ_hodiny="ind" and ID_osoba= ? order by datum, cas_zacatku', (instructor_id))
    
    available_times_instructor = {}

    for row in query_resuslt_instructor_times:
        date_str = row['datum'].strftime('%Y-%m-%d')
        time_str = row['cas_zacatku']

        if date_str not in available_times_instructor:
            available_times_instructor[date_str] = []

        available_times_instructor[date_str].append((time_str))
    
    print(available_times_instructor)
    return json.dumps(available_times_instructor)

@views.route('/get-available-times/individual/<int:instructor_id>')
def get_available_times_individual_instructor(instructor_id):
    db = get_db()
    base_query = """
        SELECT datum, cas_zacatku, COUNT(*) as count
        FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny)
        WHERE stav = 'volno' AND typ_hodiny = 'ind'
    """
    
    if instructor_id != 0:
        base_query += " AND ID_osoba = ?"
        query_parameters = (instructor_id,)
        query_result_ind = db.execute(base_query + " GROUP BY datum, cas_zacatku ORDER BY datum, cas_zacatku", query_parameters).fetchall()
    else:
        query_result_ind = db.execute(base_query + " GROUP BY datum, cas_zacatku ORDER BY datum, cas_zacatku").fetchall()
    
    available_times_ind = {}
    for row in query_result_ind:
        date_str = row['datum'].strftime('%Y-%m-%d')
        time_str = row['cas_zacatku']
        count = row['count']
        
        if date_str not in available_times_ind:
            available_times_ind[date_str] = []
        
        available_times_ind[date_str].append((time_str, count))
    
    return jsonify(available_times_ind)

@views.route('/get-available-times/group')
def get_available_times_group():
    db = get_db()

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

@views.route('/get-reservation-details/<reservation_identifiers>', defaults={'identifier': None})
@views.route('/get-reservation-details/<reservation_identifiers>/<identifier>')
def get_reservation_details(reservation_identifiers, identifier):
    db = get_db()
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

@views.route('/mark-reservation-paid/<int:reservation_id>', methods=["POST"])
@login_required
def reservation_payment_status(reservation_id):
    db = get_db()
    reservation = db.execute('SELECT platba FROM rezervace WHERE ID_rezervace = ?', (reservation_id,)).fetchone()

    if not reservation:
        flash("Rezervace nenalezena!", category="danger")
    elif reservation["platba"] == "nezaplaceno":
        db.execute('UPDATE rezervace SET platba = "zaplaceno" WHERE ID_rezervace = ?', (reservation_id,))
        db.commit()
        flash("Rezervace označena jako zaplacená!", category="success")
    else:
        flash("Rezervace již je zaplacena", category="warning")

    return redirect(url_for("administration.reservations_admin"))
    
@views.route('/delete-reservation/<reservation_id>', methods=['DELETE', 'POST'])
def delete_reservation(reservation_id):
    db = get_db()
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
        return redirect(url_for("reservations.reservations_admin"))
    else:
        return jsonify(response), status_code

@views.route('/get-lessons')
def get_lessons():
    db = get_db()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 1, type=int)
    selected_date = request.args.get('date', None)

    if selected_date:
        query_result = db.execute('SELECT ID_hodiny, datum, cas_zacatku, prijmeni, stav, typ_hodiny, obsazenost FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) left join Instruktor USING (ID_osoba) WHERE datum = ? LIMIT ? OFFSET ?', (selected_date, per_page, (page - 1) * per_page)).fetchall()
        total = db.execute('SELECT COUNT(*) FROM dostupne_hodiny WHERE datum = ?', (selected_date,)).fetchone()[0]
    else:
        query_result = db.execute('SELECT ID_hodiny, datum, cas_zacatku, prijmeni, stav, typ_hodiny, obsazenost FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) left join Instruktor USING (ID_osoba) LIMIT ? OFFSET ?', (per_page, (page - 1) * per_page)).fetchall()
        total = db.execute('SELECT COUNT(*) FROM dostupne_hodiny').fetchone()[0]

    lessons_dict = [dict(row) for row in query_result]

    return jsonify({
        'lessons': lessons_dict,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    })