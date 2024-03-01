from flask import Blueprint, jsonify, request
from flaskr.api.lessons_services import get_paginated_lessons

admin_lessons_bp = Blueprint('admin_api_lessons', __name__, template_folder='templates')

@admin_lessons_bp.route('/get-lessons')
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

