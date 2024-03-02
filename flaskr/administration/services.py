from flaskr.db import get_db

def instructor_exists(email):
    db = get_db()
    query_result = db.execute('SELECT * FROM Instruktor WHERE email = ?', (email, )).fetchone()
    return query_result is not None

def add_instructor(name, surname, email, tel_number, experience, date_birth, date_started):
    db = get_db()
    db.execute('INSERT INTO Instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', (name, surname, email, tel_number, experience, date_birth, date_started) )
    db.commit()

def get_available_instructors():
    db = get_db()
    query_result_instructors = db.execute("SELECT DISTINCT jmeno, prijmeni, ID_osoba from instruktor")
    available_instructors = [(0, "Instruktor")]
    for row in query_result_instructors:
        available_instructors.append((row["ID_osoba"] ,row["jmeno"] + " " + row["prijmeni"]))
    return available_instructors

def add_individual_lesson(db, date_str, time_start, instructor_id, lesson_type, capacity):
    query_result = db.execute('SELECT * from Dostupne_hodiny left join ma_vypsane using (ID_hodiny) WHERE datum = ? AND cas_zacatku = ? AND ID_osoba = ?', (date_str, time_start, instructor_id)).fetchone()
    if query_result:
        return False, "Lesson already exists for these parameters"
    cursor = db.execute('INSERT INTO Dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, kapacita) VALUES (?, ?, ?, ?, ?)', (date_str, time_start, "volno", lesson_type, capacity))
    last_row = cursor.lastrowid
    db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)',(int(instructor_id), last_row))
    db.commit()
    return True, "Lesson added successfully"

def add_group_lesson(db, date_str, time_start, instructor_ids, lesson_type, capacity):
    for instructor_id in instructor_ids:
        query_result = db.execute('SELECT * from Dostupne_hodiny left join ma_vypsane using (ID_hodiny) WHERE datum = ? AND cas_zacatku = ? AND ID_osoba != ?', (date_str, time_start, instructor_id)).fetchone()
        if query_result:
            return False, "Lesson already exists for these parameters - instructor: " + instructor_id
    cursor = db.execute('INSERT INTO Dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, kapacita, obsazenost) VALUES (?, ?, ?, ?, ?, ?)', (date_str, time_start, "volno", lesson_type, capacity, 0))
    last_row = cursor.lastrowid
    for instructor_id in instructor_ids:
        db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)',(int(instructor_id), last_row))
    db.commit()
    return True, "Lesson added successfully"

def get_reservations():
    db = get_db()
    query_result = db.execute('SELECT * FROM rezervace left join Klient USING (ID_osoba)').fetchall()
    return [dict(row) for row in query_result]

def get_reservation_payment_status(reservation_id):
    db = get_db()
    reservation = db.execute('SELECT platba FROM rezervace WHERE ID_rezervace = ?', (reservation_id,)).fetchone()
    return reservation

def mark_reservation_as_paid(reservation_id):
    db = get_db()
    db.execute('UPDATE rezervace SET platba = "zaplaceno" WHERE ID_rezervace = ?', (reservation_id,))
    db.commit()

def get_lesson_status(lesson_id):
    db = get_db()
    query_result = db.execute('SELECT stav FROM dostupne_hodiny WHERE ID_hodiny = ?', (lesson_id,)).fetchone()
    return query_result

def delete_lesson(lesson_id):
    db = get_db()
    db.execute('DELETE FROM dostupne_hodiny WHERE ID_hodiny = ?', (lesson_id,))
    db.execute('DELETE FROM ma_vypsane WHERE ID_hodiny = ?', (lesson_id,))
    db.commit()

def get_all_lessons():
    db = get_db()
    query_result = db.execute('SELECT * FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) left join Instruktor USING (ID_osoba)').fetchall()
    return [dict(row) for row in query_result]