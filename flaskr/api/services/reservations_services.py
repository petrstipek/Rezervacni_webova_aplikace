from flaskr.db import get_db
import sqlite3
import datetime

def delete_reservation_by_reservation_code(reservation_id):
    db = get_db()
    cur = db.cursor()
    
    try:
        cur.execute("SELECT 1 FROM rezervace WHERE rezervacni_kod = ?", (reservation_id,))
        if cur.fetchone() is None:
            return False, "Rezervace nebyla nalezena!"
        query_result = db.execute("SELECT * FROM rezervace WHERE rezervacni_kod = ?", (reservation_id,)).fetchone()
        reservation_id = query_result["ID_rezervace"]

        if query_result["typ_rezervace"] == "individual":
            lesson_ids = cur.execute("SELECT ID_hodiny from prirazeno WHERE ID_rezervace = ?", (reservation_id,)).fetchall()
            for lesson_id_tuple in lesson_ids:
                cur.execute("UPDATE Dostupne_hodiny SET stav = 'volno' WHERE ID_hodiny = ?", (lesson_id_tuple[0],))
            
            cur.execute("DELETE FROM rezervace WHERE ID_rezervace = ?", (reservation_id,))
            cur.execute("DELETE from prirazeno WHERE ID_rezervace = ?", (reservation_id,))
            cur.execute("DELETE from ma_vyuku WHERE ID_rezervace = ?", (reservation_id,))
            db.commit()
        elif query_result["typ_rezervace"] == "group":
            student_count = query_result["pocet_zaku"]
            lesson = db.execute("SELECT ID_hodiny from prirazeno WHERE ID_rezervace = ?", (reservation_id,)).fetchone()
            lesson_occupancy = lesson["obsazenost"]
            new_availability = lesson_occupancy - student_count
            db.execute("UPDATE Dostupne_hodiny SET obsazenost = ? WHERE ID_hodiny = ?", (new_availability, lesson_id_tuple[0],))

            cur.execute("DELETE FROM rezervace WHERE ID_rezervace = ?", (reservation_id,))
            cur.execute("DELETE from prirazeno WHERE ID_rezervace = ?", (reservation_id,))
            cur.execute("DELETE from ma_vyuku WHERE ID_rezervace = ?", (reservation_id,))

            db.commit()

        return True, "Ok"
    except sqlite3.Error as e:
        db.rollback()
        return False, "nok"
    
def delete_reservation_by_reservation_id(reservation_id):
    db = get_db()
    cur = db.cursor()
    
    try:
        cur.execute("SELECT 1 FROM rezervace WHERE ID_rezervace = ?", (reservation_id,))
        if cur.fetchone() is None:
            return False, "Rezervace nebyla nalezena!"

        lesson_ids = cur.execute("SELECT ID_hodiny from prirazeno WHERE ID_rezervace = ?", (reservation_id,)).fetchall()
        for lesson_id_tuple in lesson_ids:
            cur.execute("UPDATE Dostupne_hodiny SET stav = 'volno' WHERE ID_hodiny = ?", (lesson_id_tuple[0],))
        
        cur.execute("DELETE FROM rezervace WHERE ID_rezervace = ?", (reservation_id,))
        cur.execute("DELETE from prirazeno WHERE ID_rezervace = ?", (reservation_id,))
        cur.execute("DELETE from ma_vyuku WHERE ID_rezervace = ?", (reservation_id,))
        db.commit()

        return True, "Ok"
    except sqlite3.Error as e:
        db.rollback()
        return False, "nok"
    
def get_paginated_reservation_details(identifier, identifier_type, page, per_page):
    db = get_db()
    #columns = ["ID_rezervace", "ID_osoba", "typ_rezervace", "termin", "platba", "cas_zacatku", "doba_vyuky", "jazyk", "pocet_zaku"]
    columns = ["jméno klienta", "příjmení klienta", "termín rezervace", "čas začátku", "doba výuky", "jméno instruktora", "příjmení instruktora"]
    query_map = {
    "reservationID": ("select K.jmeno, K.prijmeni, R.termin, R.cas_zacatku, R.doba_vyuky, I.jmeno, I.prijmeni  from rezervace R left join Klient K on R.ID_osoba = K.ID_osoba left join  ma_vyuku MV on R.ID_rezervace = MV.ID_rezervace left join Instruktor I on I.ID_osoba = MV.ID_osoba where R.rezervacni_kod = ? order by R.termin, R.cas_zacatku", (identifier,)),
    "name": ("select K.jmeno, K.prijmeni, R.termin, R.cas_zacatku, R.doba_vyuky, I.jmeno, I.prijmeni  from rezervace R left join Klient K on R.ID_osoba = K.ID_osoba left join  ma_vyuku MV on R.ID_rezervace = MV.ID_rezervace left join Instruktor I on I.ID_osoba = MV.ID_osoba where K.prijmeni = ? order by R.termin, R.cas_zacatku", (identifier,)),
    "email": ("select K.jmeno, K.prijmeni, R.termin, R.cas_zacatku, R.doba_vyuky, I.jmeno, I.prijmeni  from rezervace R left join Klient K on R.ID_osoba = K.ID_osoba left join  ma_vyuku MV on R.ID_rezervace = MV.ID_rezervace left join Instruktor I on I.ID_osoba = MV.ID_osoba where K.email = ? order by R.termin, R.cas_zacatku", (identifier,)),
    "tel-number": ("select K.jmeno, K.prijmeni, R.termin, R.cas_zacatku, R.doba_vyuky, I.jmeno, I.prijmeni  from rezervace R left join Klient K on R.ID_osoba = K.ID_osoba left join  ma_vyuku MV on R.ID_rezervace = MV.ID_rezervace left join Instruktor I on I.ID_osoba = MV.ID_osoba where K.tel_cislo = ? order by R.termin, R.cas_zacatku", (identifier,)),
    "all": ("select K.jmeno, K.prijmeni, R.termin, R.cas_zacatku, R.doba_vyuky, I.jmeno, I.prijmeni  from rezervace R left join Klient K on R.ID_osoba = K.ID_osoba left join  ma_vyuku MV on R.ID_rezervace = MV.ID_rezervace left join Instruktor I on I.ID_osoba = MV.ID_osoba where R.termin >= date('now') order by R.termin, R.cas_zacatku", ()),
}

    if identifier_type not in query_map:
        return None, "Invalid reservation identifier"

    sql_query, params = query_map[identifier_type]
    paginated_sql_query = f"{sql_query} LIMIT ? OFFSET ?"
    paginated_params = params + (per_page, (page - 1) * per_page)

    query_result = db.execute(paginated_sql_query, paginated_params).fetchall()
    total_items = db.execute(f"SELECT COUNT(*) FROM ({sql_query})", params).fetchone()[0]
    
    if query_result:
        results_list = [{column: row[i] for i, column in enumerate(columns)} for row in query_result]
        total_pages = (total_items + per_page - 1) // per_page
        return {
            "reservations": results_list,
            "total_items": total_items,
            "total_pages": total_pages,
            "current_page": page
        }, None
    else:
        return None, "Žádné rezervace nenalezeny!"
    
def fetch_available_group_times():
    db = get_db()
    query_result = db.execute("""
        SELECT datum, cas_zacatku, (kapacita - obsazenost) as count
        FROM dostupne_hodiny
        WHERE stav = 'volno' AND typ_hodiny = 'group' AND obsazenost < kapacita
        GROUP BY datum, cas_zacatku
        ORDER BY datum, cas_zacatku;
    """).fetchall()
    return query_result

def format_available_times(query_results):
    available_times = {}
    for row in query_results:
        date_str = row['datum'].strftime('%Y-%m-%d')
        time_str = row['cas_zacatku']
        count = row['count']
        
        if date_str not in available_times:
            available_times[date_str] = []
        
        available_times[date_str].append((time_str, count))
    
    return available_times

def fetch_available_times_for_individual_instructor(instructor_id=None):
    db = get_db()
    base_query = """
        SELECT datum, cas_zacatku, COUNT(*) as count
        FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny)
        WHERE stav = 'volno' AND typ_hodiny = 'ind'
    """
    parameters = ()
    if instructor_id and instructor_id != 0:
        base_query += " AND ID_osoba = ?"
        parameters = (instructor_id,)
    
    base_query += " GROUP BY datum, cas_zacatku ORDER BY datum, cas_zacatku"
    query_result = db.execute(base_query, parameters).fetchall()
    return query_result

def get_reservation_detail(identifier):
    db = get_db()
    query_result = db.execute("SELECT termin, cas_zacatku, pocet_zaku, doba_vyuky, platba FROM Rezervace LEFT JOIN Instruktor USING (ID_osoba) WHERE rezervacni_kod = ?", (identifier,)).fetchone()
    columns = ["Termín", "Čas začátku", "Počet žáků", "Doba výuky", "Stav platby"]
    if query_result:
        result_dict = {}
        for i, column in enumerate(columns):
            if isinstance(query_result[i], datetime.date):
                formatted_date = query_result[i].strftime('%d.%m.%Y')
                result_dict[column] = formatted_date
            else:
                result_dict[column] = query_result[i]
        return result_dict
    return False