from flask import Blueprint

views = Blueprint("views", __name__)

@views.route('/')
def main_page():
    return "<h1>Main reservation page</h1>"

@views.route('/reservation-check')
def reservation_check():
    return "<h1>Reservation check page</h1>"

@views.route('/reservations-user')
def reservations_user():
    return "<h1>Reservations from user</h1>"

@views.route('/login-page-admin')
def login_page_admin():
    return "<h1>Login page admin</h1>"

@views.route('/admin-page')
def admin_page():
    return "<h1>Admin page</h1>"

@views.route('/lectures')
def lectures():
    return "<h1>Lectures page</h1>"

@views.route('/reservations-admin')
def reservations_admin():
    return "<h1>Reservations admin page</h1>"