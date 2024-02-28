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



    
