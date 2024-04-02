from flask_mail import Message
from .extensions import mail

def send_reservation_confirmation(user_email, reservation_details):
    msg = Message("Reservation Confirmation", recipients=[user_email])
    msg.body = f"Hello, your reservation is confirmed. Details: {reservation_details}"
    mail.send(msg)

def send_registration_confirmation(user_email, reservation_details):
    msg = Message("Registrace - Ski škola Bublava", recipients=[user_email])
    msg.body = ""
    mail.send(msg)

def send_password_reset(user_email, reset_link):
    msg = Message("Obnovení hesla", recipients=[user_email])
    msg.body = f" {reset_link}"
    mail.send(msg)

def reservation_cancelation(user_email, reservation_details):
    msg = Message("Zrušení rezervace", recipients=[user_email])
    msg.body = f" {reservation_details}"
    mail.send(msg)

    