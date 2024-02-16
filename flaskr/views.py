from flask import Blueprint, render_template, request, jsonify, json
from flaskr.forms import PersonalInformationForm

views = Blueprint("views", __name__)

available_times = {
    "02/16/2024": ["čas 14:00", "čas 15:00", "čas 16:00", "čas 17:00", "čas 18:00", "čas 19:00", "čas 20:00", "čas 21:00", "čas 22:00", "čas 23:00"],  # Added missing comma
    "02/17/2024": ["čas 18:00", "čas 19:00", "čas 20:00", "čas 21:00", "čas 22:00", "čas 23:00"],
    "02/18/2024": ["čas 11:00", "čas 12:00", "čas 18:00", "čas 19:00", "čas 20:00", "čas 21:00", "čas 22:00", "čas 23:00"]
}


@views.route('/', methods=["GET", "POST"])
def main_page():
    form = PersonalInformationForm()

    return render_template("blog/reservation_page.html", active_page = "reservation_page", form=form,  available_times=json.dumps(available_times))

@views.route('/reservation-check')
def reservation_check():
    return render_template("blog/reservation_check.html")

@views.route('/reservations-user')
def reservations_user():
    return render_template("blog/reservations_user.html")

@views.route('/login-page-admin')
def login_page_admin():
    return render_template("blog/login_admin.html")

@views.route('/admin-page')
def admin_page():
    return render_template("blog/admin_page.html")

@views.route('/lectures')
def lectures():
    return render_template("blog/lectures.html")

@views.route('/reservations-admin')
def reservations_admin():
    return render_template("blog/reservations_admin.html")

@views.route('/instructors')
def instructors_page():
    return render_template("blog/instructors.html", active_page = "instructors")

@views.route('/school')
def school_page():
    return render_template("blog/school.html", active_page = "school")

@views.route('prices')
def prices_page():
    return render_template("blog/prices.html", active_page = "prices")

@views.route('/submit-date-time', methods=['POST'])
def submit_date_time():
    data = request.json
    print(data)  # Or handle it as you see fit
    return jsonify({"status": "success"})