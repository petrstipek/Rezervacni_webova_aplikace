from flask import render_template, Blueprint
from flaskr.information.services import get_all_instructors

information_bp = Blueprint('information', __name__, template_folder='templates')

@information_bp.route('/our-instructors')
def instructors_page():
    instructors = get_all_instructors()

    return render_template("blog/user/instructors.html", active_page = "instructors", instructors=instructors)

@information_bp.route('/school')
def school_page():
    return render_template("blog/user/school.html", active_page = "school")

@information_bp.route('/prices')
def prices_page():
    return render_template("blog/user/prices.html", active_page = "prices")

@information_bp.route('/contact')
def contacts_page():
    return render_template("blog/user/contacts.html", active_page = "prices")