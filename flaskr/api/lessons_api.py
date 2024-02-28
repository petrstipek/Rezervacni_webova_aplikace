from flask import Blueprint, jsonify, request
from flaskr.db import get_db


admin_lessons_bp = Blueprint('admin_api_lessons', __name__, template_folder='templates')

@admin_lessons_bp.route('/get-lessons')
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

