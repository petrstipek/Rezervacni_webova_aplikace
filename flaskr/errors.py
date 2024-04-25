from flask import Flask, redirect, url_for, flash

app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    flash("Při zpracování požadavku nastala chyba!", category="danger")
    return redirect(url_for('reservations.main_page')), 404

@app.errorhandler(500)
def internal_server_error(e):
    flash("Při zpracování požadavku nastala chyba!", category="danger")
    return redirect(url_for('reservations.main_page')), 500

@app.route('/error')
def error_page():
    flash("Při zpracování požadavku nastala chyba!", category="danger")
    return "An error occurred", 200

